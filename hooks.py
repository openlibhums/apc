from django.template.loader import render_to_string

from plugins.apc import plugin_settings
from utils import setting_handler
from submission import models as submission_models


def publication_fees(context):
    plugin = plugin_settings.get_self()
    request = context['request']

    enable_apcs = setting_handler.get_plugin_setting(
        plugin,
        'enable_apcs',
        request.journal,
        create=True,
        pretty='Enable APCs',
    )
    track_apcs = setting_handler.get_plugin_setting(
        plugin,
        'track_apcs',
        request.journal,
        create=True,
        pretty='Track APCs',
    )

    sections = submission_models.Section.objects.language().fallbacks(
        'en'
    ).filter(
        journal=request.journal,
        public_submissions=True,
    ).prefetch_related('sectionapc')

    if track_apcs.value == 'on':
        return ''
    elif enable_apcs.value == 'on':
        return render_to_string(
            'apc/publication_fees.html',
            {'sections': sections},
        )
    else:
        return ''


def waiver_info(context):
    plugin = plugin_settings.get_self()
    request = context['request']

    waiver_text = setting_handler.get_plugin_setting(
        plugin,
        'waiver_text',
        request.journal,
        create=True,
        pretty='Waiver Text',
    )
    enable_waivers = setting_handler.get_plugin_setting(
        plugin,
        'enable_waivers',
        request.journal,
        create=True,
        pretty='Enable Waivers',
    )

    if enable_waivers.value == 'on':
        return render_to_string(
            'apc/waiver_info.html',
            {'request': request, 'waiver_text': waiver_text.value},
        )
    else:
        return ''


def waiver_application(context):
    plugin = plugin_settings.get_self()
    request = context['request']
    article = context['article']

    waiver_text = setting_handler.get_plugin_setting(
        plugin,
        'waiver_text',
        request.journal,
        create=True,
        pretty='Waiver Text',
    )
    enable_waivers = setting_handler.get_plugin_setting(
        plugin,
        'enable_waivers',
        request.journal,
        create=True,
        pretty='Enable Waivers',
    )
    if enable_waivers.value == 'on':
        return render_to_string(
            'apc/article_waiver_app.html',
            {
                'request': request,
                'waiver_text': waiver_text.value,
                'article': article,
            },
        )
    else:
        return ''
