from django.shortcuts import get_object_or_404

from submission import models as submission_models
from plugins.apc import forms


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
