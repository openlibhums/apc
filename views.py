from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from plugins.apc import plugin_settings, logic, forms, models
from submission import models as submission_models
from security.decorators import has_journal, editor_user_required
from utils import setting_handler


@has_journal
@editor_user_required
def index(request):
    sections = submission_models.Section.objects.language().filter(
        journal=request.journal).prefetch_related('sectionapc')
    waiver_applications = models.WaiverApplication.objects.filter(article__journal=request.journal)
    modal = None

    form = forms.APCForm()

    if request.POST and 'section' in request.POST:
        form = forms.APCForm(request.POST)
        if form.is_valid():
            logic.handle_set_apc(request, form)
        else:
            modal = request.POST.get('section')

    template = 'apc/index.html'
    context = {
        'sections': sections,
        'form': form,
        'waiver_applications': waiver_applications,
        'modal': modal,
    }

    return render(request, template, context)


@has_journal
@editor_user_required
def settings(request):
    plugin = plugin_settings.get_self()
    enable_apcs = setting_handler.get_plugin_setting(plugin, 'enable_apcs', request.journal, create=True,
                                                     pretty='Enable APCs')

    if request.POST:
        apc_post = request.POST.get('enable_apcs')
        setting_handler.save_plugin_setting(plugin, 'enable_apcs', apc_post, request.journal)
        messages.add_message(request, messages.SUCCESS, 'Setting updated.')
        return redirect(reverse('apc_settings'))

    template = 'apc/settings.html'
    context = {
        'enable_apc': enable_apcs.value,
    }

    return render(request, template, context)
