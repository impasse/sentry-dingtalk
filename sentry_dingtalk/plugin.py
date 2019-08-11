from __future__ import absolute_import

import time
import json
import requests
import logging
import six
import sentry

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from sentry.exceptions import PluginError
from sentry.plugins.bases import notify
from sentry.http import is_valid_url, safe_urlopen
from sentry.utils.safe import safe_execute
from sentry_plugins.base import CorePluginMixin

from sentry.utils.http import absolute_uri
from django.core.urlresolvers import reverse

def validate_urls(value, **kwargs):
    output = []
    for url in value.split('\n'):
        url = url.strip()
        if not url:
            continue
        if not url.startswith(('http://', 'https://')):
            raise PluginError('Not a valid URL.')
        if not is_valid_url(url):
            raise PluginError('Not a valid URL.')
        output.append(url)
    return '\n'.join(output)


class DingtalkForm(notify.NotificationConfigurationForm):
    urls = forms.CharField(
        label=_('Dingtalk webhook url'),
        widget=forms.Textarea(attrs={
            'class': 'span6', 'placeholder': 'https://oapi.dingtalk.com/robot/send?access_token='}),
        help_text=_('Enter dingtalk webhook url.'))

    def clean_url(self):
        value = self.cleaned_data.get('url')
        return validate_urls(value)

 
class DingtalkPlugin(CorePluginMixin, notify.NotificationPlugin):
    author = 'shyling'
    author_url = 'https://github.com/impasse/sentry-dingtalk'
    version = sentry.VERSION
    description = "Integrates dingtalk webhook."
    resource_links = [
        ('Bug Tracker', 'https://github.com/impasse/sentry-dingtalk/issues'),
        ('Source', 'https://github.com/impasse/sentry-dingtalk'),
    ]

    slug = 'dingtalk'
    title = 'dingtalk'
    conf_title = title
    conf_key = 'dingtalk'  

    project_conf_form = DingtalkForm
    timeout = getattr(settings, 'SENTRY_DINGTALK_TIMEOUT', 3) 
    logger = logging.getLogger('sentry.plugins.dingtalk')

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('urls', project))

    def get_config(self, project, **kwargs):
        return [{
            'name': 'urls',
            'label': 'dingtalk webhook url',
            'type': 'textarea',
            'help': 'Enter dingtalk webhook url.',
            'placeholder': 'https://oapi.dingtalk.com/robot/send?access_token=',
            'validators': [validate_urls],
            'required': False
        }] 

    def get_webhook_urls(self, project):
        url = self.get_option('urls', project)
        if not url:
            return ''
        return url 

    def send_webhook(self, url, payload):
        return safe_urlopen(
            url=url,
            json=payload,
            timeout=self.timeout,
            verify_ssl=False,
        )

    def get_group_url(self, group):
        return absolute_uri(reverse('sentry-group', args=[
            group.organization.slug,
            group.project.slug,
            group.id,
        ]))

    def notify_users(self, group, event, *args,**kwargs): 
        fail_silently = kwargs.get('fail_silently',False)
        url = self.get_webhook_urls(group.project)
        project = group.project.name
        level = group.get_level_display()
        culprit = group.culprit
        link = group.get_absolute_url()
        server_name = event.get_tag('server_name')
        msg = event.get_legacy_message()

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": msg,
                "text": '''### {msg}\n
**Project:** {project_name}\n
**Server:** {server_name}\n
**Level:** {level}\n
**Culprit:** {culprit}\n
**URL:** [{link}]({link})\n
                '''.format(
                    project_name=project,
                    level=level,
                    culprit=culprit,
                    msg=msg,
                    server_name=server_name,
                    link=link,
                ),
            },
        }
        requests.post(url, json=data)

 
