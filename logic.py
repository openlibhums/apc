from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from submission import models as submission_models
from plugins.apc import forms, models, plugin_settings
from utils import setting_handler


def handle_set_apc(request, form):
    section_id = request.POST.get('section')
    section = get_object_or_404(
        submission_models.Section,
        pk=section_id,
        journal=request.journal,
    )

    if hasattr(section, 'sectionapc'):
        instance = section.sectionapc
        form = forms.APCForm(request.POST, instance=instance)

    return form.save(section=section)


def get_waiver_status_from_post(post):
    action = post.get('action')

    if action == 'waive':
        return 'accepted'

    return 'declined'


def set_apc(**kwargs):
    request = kwargs.get('request', None)
    article = kwargs.get('article', None)
    plugin = plugin_settings.get_self()

    if request and article:

        try:
            enable_apcs = setting_handler.get_plugin_setting(
                plugin,
                'enable_apcs',
                request.journal,
            )

            track_apcs = setting_handler.get_plugin_setting(
                plugin,
                'track_apcs',
                request.journal,
            )

            if enable_apcs.processed_value or track_apcs.processed_value:

                try:
                    section_apc = models.SectionAPC.objects.get(
                        section=article.section,
                    )
                except models.SectionAPC.DoesNotExist:
                    messages.add_message(
                        request,
                        messages.WARNING,
                        'APC Management is enabled but this'
                        ' section has no APC.')
                    return

                models.ArticleAPC.objects.create(
                    article=article,
                    section_apc=section_apc,
                    value=section_apc.value,
                    currency=section_apc.currency,
                )
        except (ObjectDoesNotExist, IndexError):
            pass

def notify_billing_staffers(**kwargs):
    request = kwargs.get('request', None)
    article = kwargs.get('article', None)
    billing_staffers = models.BillingStaffer.objects.filter(
        journal=request.journal,
        receives_notifications=True,
    )

    for billing_staffer in billing_staffers:
        billing_staffer.send_notification(request, article)


