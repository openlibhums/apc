from django.shortcuts import get_object_or_404
from django.contrib import messages

from submission import models as submission_models
from plugins.apc import forms, models


def handle_set_apc(request, form):
    section_id = request.POST.get('section')
    section = get_object_or_404(submission_models.Section, pk=section_id, journal=request.journal)

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

    if request and article:
        try:
            section_apc = models.SectionAPC.objects.get(section=article.section)
        except models.SectionAPC.DoesNotExist:
            messages.add_message(request, messages.WARNING, 'APC Management is enabled but this section has no APC.')
            return

        models.ArticleAPC.objects.create(
            article=article,
            section_apc=section_apc,
            value=section_apc.value,
            currency=section_apc.currency,
        )
