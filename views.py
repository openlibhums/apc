from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from submission import models as submission_models
from security.decorators import has_journal, editor_user_required


@has_journal
@editor_user_required
def index(request):
    sections = submission_models.Section.objects.language().filter(journal=request.journal)

    template = 'apc/index.html'
    context = {
        'sections': sections,
    }

    return render(request, template, context)