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

    sections = submission_models.Section.objects.filter(
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
    return ''


def waiver_info(context):
    plugin = plugin_settings.get_self()
    request = context['request']

    author_contribution_mode = setting_handler.get_plugin_setting(
        plugin,
        'author_contribution_mode',
        request.journal,
        create=True,
        pretty='Author Contribution Mode',
    )

    mode = author_contribution_mode.value if author_contribution_mode else ''

    if mode == 'vac':
        vac_text = setting_handler.get_plugin_setting(
            plugin,
            'vac_text',
            request.journal,
            create=True,
            pretty='VAC Text',
        )
        return render_to_string(
            'apc/vac_optin.html',
            {'request': request, 'vac_text': vac_text.value if vac_text else ''},
        )
    elif mode == 'waiver':
        waiver_text = setting_handler.get_plugin_setting(
            plugin,
            'waiver_text',
            request.journal,
            create=True,
            pretty='Waiver Text',
        )
        return render_to_string(
            'apc/waiver_info.html',
            {'request': request, 'waiver_text': waiver_text.value},
        )
    return ''


def waiver_application(context):
    plugin = plugin_settings.get_self()
    request = context['request']
    article = context['article']

    author_contribution_mode = setting_handler.get_plugin_setting(
        plugin,
        'author_contribution_mode',
        request.journal,
        create=True,
        pretty='Author Contribution Mode',
    )

    if author_contribution_mode and author_contribution_mode.value == 'waiver':
        waiver_text = setting_handler.get_plugin_setting(
            plugin,
            'waiver_text',
            request.journal,
            create=True,
            pretty='Waiver Text',
        )
        return render_to_string(
            'apc/article_waiver_app.html',
            {
                'request': request,
                'waiver_text': waiver_text.value,
                'article': article,
            },
        )
    return ''
