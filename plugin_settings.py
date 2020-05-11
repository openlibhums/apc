from plugins.apc import logic
from utils import models
from events import logic as event_logic

PLUGIN_NAME = 'APC Manager'
DESCRIPTION = 'This plugin supports management of APCs in Janeway.'
AUTHOR = 'Andy Byers'
VERSION = '1.0'
SHORT_NAME = 'apc'
DISPLAY_NAME = 'apc'
MANAGER_URL = 'apc_index'
JANEWAY_VERSION = "1.3.7"

# Workflow Settings
IS_WORKFLOW_PLUGIN = False


def get_self():
    new_plugin, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        display_name=DISPLAY_NAME,
        version=VERSION,
        enabled=True,
    )
    return new_plugin


def install():
    new_plugin, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        version=VERSION,
        enabled=True,
    )

    if created:
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        print('Plugin {0} is already installed.'.format(PLUGIN_NAME))


def hook_registry():
    """
    On site load, the load function is run for each installed
    plugin to generate a list of hooks.
    """
    return {
        'publication_fees':
        {'module': 'plugins.apc.hooks', 'function': 'publication_fees'},
        'submission_review':
        {'module': 'plugins.apc.hooks', 'function': 'waiver_info'},
        'core_article_footer':
        {'module': 'plugins.apc.hooks', 'function': 'waiver_application'}
    }


def register_for_events():
    event_logic.Events.register_for_event(
        event_logic.Events.ON_ARTICLE_SUBMITTED,
        logic.set_apc,
    )
