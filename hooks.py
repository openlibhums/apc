from django.template.loader import render_to_string

from plugins.apc import plugin_settings
from utils import setting_handler
from submission import models as submission_models


def publication_fees(context):
    plugin = plugin_settings.get_self()
    request = context['request']

    enable_apcs = setting_handler.get_plugin_setting(plugin, 'enable_apcs', request.journal, create=True,
                                                     pretty='Enable APCs')
    track_apcs = setting_handler.get_plugin_setting(plugin, 'track_apcs', request.journal, create=True,
                                                    pretty='Track APCs')

    sections = submission_models.Section.objects.language().fallbacks('en').filter(
        journal=request.journal, public_submissions=True).prefetch_related('sectionapc')

    if track_apcs.value == 'on':
        return ''
    elif enable_apcs.value == 'on':
        return render_to_string('apc/publication_fees.html', {'sections': sections})