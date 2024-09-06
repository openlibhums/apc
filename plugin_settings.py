from plugins.apc import logic
from utils import models
from events import logic as event_logic
from utils.install import update_settings

PLUGIN_NAME = 'APC Manager'
DESCRIPTION = 'This plugin supports management of APCs in Janeway.'
AUTHOR = 'Andy Byers'
VERSION = '1.2'
SHORT_NAME = 'apc'
DISPLAY_NAME = 'apc'
MANAGER_URL = 'apc_index'
JANEWAY_VERSION = "1.7.0"

# Workflow Settings
IS_WORKFLOW_PLUGIN = False

# Events
ON_INVOICE_SENT = 'on_invoice_sent'
ON_INVOICE_PAID = 'on_invoice_paid'


def get_self():
    defaults = {
        'version': VERSION,
        'display_name': DISPLAY_NAME,
        'enabled': True,
    }

    new_plugin, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        defaults=defaults,
    )
    return new_plugin


def install():
    defaults = {
        'version': VERSION,
        'display_name': DISPLAY_NAME,
        'enabled': True,
    }

    plugin, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        defaults=defaults,
    )

    update_settings(
        file_path='plugins/apc/install/settings.json'
    )

    if created:
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        if plugin.version != VERSION:
            plugin.version = VERSION
            plugin.save()
            print('Plugin {0} version updated.'.format(PLUGIN_NAME))
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
            {'module': 'plugins.apc.hooks', 'function': 'waiver_application'},
    }


def register_for_events():
    event_logic.Events.register_for_event(
        event_logic.Events.ON_ARTICLE_SUBMITTED,
        logic.set_apc,
    )

    event_logic.Events.register_for_event(
        event_logic.Events.ON_ARTICLE_ACCEPTED,
        logic.notify_billing_staffers,
    )

    event_logic.Events.register_for_event(
        ON_INVOICE_SENT,
        logic.notify_billing_staffers,
    )

    event_logic.Events.register_for_event(
        ON_INVOICE_PAID,
        logic.notify_billing_staffers,
    )
