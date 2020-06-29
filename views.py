from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from plugins.apc import plugin_settings, logic, forms, models
from submission import models as submission_models
from security.decorators import (
    has_journal,
    editor_user_required,
    article_author_required,
)
from utils import setting_handler


@has_journal
@editor_user_required
def index(request):
    sections = submission_models.Section.objects.language().filter(
        journal=request.journal).prefetch_related('sectionapc')
    waiver_applications = models.WaiverApplication.objects.filter(
        article__journal=request.journal,
        reviewed__isnull=True,
    )
    modal = None

    form = forms.APCForm()

    if request.POST and 'section' in request.POST:
        form = forms.APCForm(request.POST)
        if form.is_valid():
            logic.handle_set_apc(request, form)
        else:
            modal = request.POST.get('section')

    article_apcs = models.ArticleAPC.objects.filter(
        article__journal=request.journal,
        article__date_accepted__isnull=False
    )

    template = 'apc/index.html'
    context = {
        'sections': sections,
        'form': form,
        'waiver_applications': waiver_applications,
        'modal': modal,
        'articles_for_invoicing': article_apcs.filter(
            status='new',
        ),
        'articles_paid': article_apcs.filter(
            status='paid',
        ),
        'articles_unpaid': article_apcs.filter(
            status='nonpay',
        ),
        'articles_invoiced': article_apcs.filter(
            status='invoiced',
        )
    }

    return render(request, template, context)


@has_journal
@editor_user_required
def apc_action(request, apc_id, action):
    apc = get_object_or_404(
        models.ArticleAPC,
        pk=apc_id,
        article__journal=request.journal,
    )

    if request.POST and 'action' in request.POST:
        if action == 'paid':
            apc.mark_as_paid()
        elif action == 'unpaid':
            apc.mark_as_unpaid()
        elif action == 'new':
            apc.mark_as_new()
        elif action == 'invoiced':
            apc.mark_as_invoiced()
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'No suitable action found.',
            )
        messages.add_message(
            request,
            messages.SUCCESS,
            'APC Updated',
        )

        return redirect(reverse('apc_index'))

    elif action in ['paid', 'unpaid'] and apc.completed:
        messages.add_message(
            request,
            messages.ERROR,
            'APC has already been completed.',
        )
        return redirect(reverse('apc_index'))

    template = 'apc/apc_action.html'
    context = {
        'apc': apc,
        'action': action,
    }

    return render(request, template, context)


@has_journal
@editor_user_required
def settings(request):
    plugin = plugin_settings.get_self()
    enable_apcs = setting_handler.get_plugin_setting(
        plugin,
        'enable_apcs',
        request.journal,
        create=True,
        pretty='Enable APCs',
    )
    track_apcs = setting_handler.get_plugin_setting(
        plugin,
        'track_apcs',
        request.journal,
        create=True,
        pretty='Track APCs',
    )
    waiver_text = setting_handler.get_plugin_setting(
        plugin,
        'waiver_text',
        request.journal,
        create=True,
        pretty='Waiver Text',
    )
    enable_waivers = setting_handler.get_plugin_setting(
        plugin,
        'enable_waivers',
        request.journal,
        create=True,
        pretty='Enable Waivers',
    )

    if request.POST:
        apc_post = request.POST.get('enable_apcs')
        track_post = request.POST.get('track_apcs')
        text_post = request.POST.get('waiver_text')
        waivers_post = request.POST.get('enable_waivers')

        setting_handler.save_plugin_setting(
            plugin,
            'enable_apcs',
            apc_post,
            request.journal,
        )
        setting_handler.save_plugin_setting(
            plugin,
            'track_apcs',
            track_post,
            request.journal,
        )
        setting_handler.save_plugin_setting(
            plugin,
            'waiver_text',
            text_post,
            request.journal,
        )
        setting_handler.save_plugin_setting(
            plugin,
            'enable_waivers',
            waivers_post,
            request.journal,
        )

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
            application.status = logic.get_waiver_status_from_post(
                request.POST,
            )
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
    article = get_object_or_404(
        submission_models.Article,
        pk=article_id, journal=request.journal,
        waiverapplication__isnull=True,
    )
    form = forms.WaiverApplication()

    if request.POST:
        form = forms.WaiverApplication(request.POST)

        if form.is_valid():
            waiver = form.save(commit=False)
            waiver.complete_application(article, request)
            return redirect(
                reverse(
                    'core_dashboard_article',
                    kwargs={'article_id': article.pk},
                )
            )

    template = 'apc/make_waiver_application.html'
    context = {
        'article': article,
        'form': form,
    }

    return render(request, template, context)


@has_journal
@editor_user_required
def billing_staff(request):
    """
    Allows editors to view billing staff members.
    """
    billing_staffers = models.BillingStaffer.objects.filter(
        journal=request.journal,
    )

    template = 'apc/billing_staff.html'
    context = {
        'billing_staffers': billing_staffers,
    }

    return render(request, template, context)


@has_journal
@editor_user_required
def manage_billing_staff(request, billing_staffer_id=None):
    """
    Editors can add, edit or delete billing staff members.
    """

    # Grab the staffer if we have an ID, otherwise set to None.
    billing_staffer = get_object_or_404(
        models.BillingStaffer,
        journal=request.journal,
        pk=billing_staffer_id
    ) if billing_staffer_id else None

    form = forms.BillingStafferForm(
        instance=billing_staffer,
        request=request,
    )

    if request.POST:
        if billing_staffer and 'delete' in request.POST:
            billing_staffer.delete()
            messages.add_message(
                request, 
                messages.INFO,
                'Billing Staffer deleted.'
            )
            return redirect(
                reverse(
                    'apc_billing_staff',
                )
            )


        form = forms.BillingStafferForm(
            request.POST,
            instance=billing_staffer,
            request=request,
        )

        if form.is_valid():
            billing_staffer = form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Billing Staffer saved.'
            )
            return redirect(
                reverse(
                    'apc_billing_staff'
                )
            )

    template = 'apc/manage_billing_staff.html'
    context = {
        'billing_staffer': billing_staffer,
        'form': form,
    }

    return render(request, template, context)


@has_journal
@editor_user_required
def add_article(request):
    """
    A utility view that lets an editor select an article and add it to the APC
    Plugin if it was missed for whatever reason.
    :param request: HttpRequest
    :return: HttpResponse or HttpRedirect
    """
    journal_articles = submission_models.Article.objects.filter(
        journal=request.journal,
        articleapc__isnull=True,
        section__isnull=False,
        date_accepted__isnull=False,
    )

    if request.POST and 'article_to_add' in request.POST:
        article_id = request.POST.get('article_to_add')

        try:
            article = submission_models.Article.objects.get(
                pk=article_id,
                journal=request.journal,
                section__isnull=False,
                articleapc__isnull=True,
            )
            try:
                section_apc = models.SectionAPC.objects.get(
                    section=article.section,
                )
                models.ArticleAPC.objects.create(
                    article=article,
                    section_apc=section_apc,
                    value=section_apc.value,
                    currency=section_apc.currency,
                )
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'APC set for article.',
                )
            except models.SectionAPC.DoesNotExist:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'APC Management is enabled but this'
                    ' section has no APC.',
                )
        except submission_models.Article.DoesNotExist:
            messages.add_message(
                request,
                messages.ERROR,
                'No article found matching supplied ID.',
            )

        return redirect(
            reverse(
                'apc_add_article',
            )
        )

    template = 'apc/add_article.html'
    context = {
        'journal_articles': journal_articles,
    }

    return render(request, template, context)


