from django.conf import settings as django_settings
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation

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


def record_vac_optin(**kwargs):
    request = kwargs.get('request', None)
    article = kwargs.get('article', None)
    plugin = plugin_settings.get_self()

    if not request or not article:
        return

    try:
        author_contribution_mode = setting_handler.get_plugin_setting(
            plugin,
            'author_contribution_mode',
            request.journal,
        ).processed_value
    except (ObjectDoesNotExist, IndexError, AttributeError):
        return

    if author_contribution_mode != 'vac':
        return

    if not request.POST.get('vac_optin'):
        return

    try:
        section_apc = models.SectionAPC.objects.get(section=article.section)
        vac_defaults = {
            'section_apc': section_apc,
            'value': section_apc.value,
            'currency': section_apc.currency,
        }
    except models.SectionAPC.DoesNotExist:
        vac_defaults = {
            'section_apc': None,
            'value': 0,
            'currency': '',
        }

    models.VoluntaryContribution.objects.get_or_create(
        article=article,
        defaults=vac_defaults,
    )


def notify_vac_handlers(**kwargs):
    request = kwargs.get('request', None)
    article = kwargs.get('article', None)

    if not request or not article:
        return

    try:
        article.voluntarycontribution
    except models.VoluntaryContribution.DoesNotExist:
        return

    billing_staffers = models.BillingStaffer.objects.filter(
        journal=request.journal,
        receives_notifications=True,
        type_of_notification='vac',
    )

    for billing_staffer in billing_staffers:
        billing_staffer.send_notification(request, article)


def notify_billing_staffers(**kwargs):
    request = kwargs.get('request', None)
    article = kwargs.get('article', None)
    type_of_notification = kwargs.get('type_of_notification', 'ready')

    billing_staffers = models.BillingStaffer.objects.filter(
        journal=request.journal,
        receives_notifications=True,
        type_of_notification=type_of_notification,
    )

    for billing_staffer in billing_staffers:
        billing_staffer.send_notification(request, article)
