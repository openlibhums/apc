from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from plugins.apc import plugin_settings, logic, forms, models
from submission import models as submission_models
from security.decorators import has_journal, editor_user_required, article_author_required
from utils import setting_handler


@has_journal
@editor_user_required
def index(request):
    sections = submission_models.Section.objects.language().filter(
        journal=request.journal).prefetch_related('sectionapc')
    waiver_applications = models.WaiverApplication.objects.filter(article__journal=request.journal,
                                                                  reviewed__isnull=True)
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
    track_apcs = setting_handler.get_plugin_setting(plugin, 'track_apcs', request.journal, create=True,
                                                    pretty='Track APCs')
    waiver_text = setting_handler.get_plugin_setting(plugin, 'waiver_text', request.journal, create=True,
                                                     pretty='Waiver Text')
    enable_waivers = setting_handler.get_plugin_setting(plugin, 'enable_waivers', request.journal, create=True,
                                                        pretty='Enable Waivers')

    if request.POST:
        apc_post = request.POST.get('enable_apcs')
        track_post = request.POST.get('track_apcs')
        text_post = request.POST.get('waiver_text')
        waivers_post = request.POST.get('enable_waivers')

        setting_handler.save_plugin_setting(plugin, 'enable_apcs', apc_post, request.journal)
        setting_handler.save_plugin_setting(plugin, 'track_apcs', track_post, request.journal)
        setting_handler.save_plugin_setting(plugin, 'waiver_text', text_post, request.journal)
        setting_handler.save_plugin_setting(plugin, 'enable_waivers', waivers_post, request.journal)

        messages.add_message(request, messages.SUCCESS, 'Setting updated.')
        return redirect(reverse('apc_settings'))

    template = 'apc/settings.html'
    context = {
        'enable_apc': enable_apcs.value,
        'track_apcs': track_apcs.value,
        'enable_waivers': enable_waivers.value,
        'waiver_text': waiver_text.value,
    }

    return render(request, template, context)


@has_journal
@editor_user_required
def waiver_application(request, application_id):
    application = get_object_or_404(models.WaiverApplication,
                                    pk=application_id,
                                    article__journal=request.journal,
                                    reviewed__isnull=True)
    form = forms.WaiverResponse(instance=application)

    if request.POST and 'action' in request.POST:
        form = forms.WaiverResponse(request.POST, instance=application)

        if form.is_valid():
            application = form.save(commit=False)
            application.status = logic.get_waiver_status_from_post(request.POST)
            application.reviewed = timezone.now()
            application.reviewer = request.user
            application.save()
            return redirect(reverse('apc_index'))

    template = 'apc/waiver_application.html'
    context = {
        'application': application,
        'form': form,
    }

    return render(request, template, context)


@has_journal
@article_author_required
def make_waiver_application(request, article_id):
    article = get_object_or_404(submission_models.Article, pk=article_id, journal=request.journal,
                                waiverapplication__isnull=True)
    form = forms.WaiverApplication()

    if request.POST:
        form = forms.WaiverApplication(request.POST)

        if form.is_valid():
            waiver = form.save(commit=False)
            waiver.complete_application(article, request)
            return redirect(reverse('core_dashboard_article', kwargs={'article_id': article.pk}))

    template = 'apc/make_waiver_application.html'
    context = {
        'article': article,
        'form': form,
    }

    return render(request, template, context)
