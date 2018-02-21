PLUGIN_NAME = 'APC Manager'
DESCRIPTION = 'This plugin supports management of APCs in Janeway.'
AUTHOR = 'Andy Byers'
VERSION = '1.0'
SHORT_NAME = 'apc'
DISPLAY_NAME = 'apc'
MANAGER_URL = 'apc_index'

# Workflow Settings
IS_WORKFLOW_PLUGIN = False


from utils import models, setting_handler


def get_self():
    new_plugin, created = models.Plugin.objects.get_or_create(name=SHORT_NAME,
                                                              display_name=DISPLAY_NAME,
                                                              version=VERSION,
                                                              enabled=True)
    return new_plugin


def install():
    new_plugin, created = models.Plugin.objects.get_or_create(name=SHORT_NAME, version=VERSION, enabled=True)

    if created:
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        print('Plugin {0} is already installed.'.format(PLUGIN_NAME))


def hook_registry():
    # On site load, the load function is run for each installed plugin to generate
    # a list of hooks.
    pass
