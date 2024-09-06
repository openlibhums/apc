from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from utils import models as utils_models, notify_helpers

APC_VALUE_CHANGE = 'APC Value Change'


def waiver_status_choices():
    return (
        ('new', 'New'),
        ('review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )


def apc_status_choices():
    return (
        ('new', 'New'),
        ('waived', 'Waived'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('nonpay', 'Non Payment'),
    )


class SectionAPC(models.Model):
    section = models.OneToOneField(
        'submission.Section',
        on_delete=models.CASCADE,
    )
    value = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Decimal with two places eg. 200.00',
    )
    currency = models.CharField(
        max_length=25,
        help_text='The currency of the APC value eg. GBP or USD.',
    )

    class Meta:
        ordering = ('section__journal', 'value', 'currency')

    def __str__(self):
        return '{0} {1} {2}'.format(
            self.section,
            self.value,
            self.currency
        )


class ArticleAPC(models.Model):
    article = models.OneToOneField(
        'submission.Article',
        on_delete=models.CASCADE,
    )
    section_apc = models.ForeignKey(
        SectionAPC,
        on_delete=models.CASCADE,
    )
    value = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Decimal with two places eg. 200.00',
    )
    currency = models.CharField(
        max_length=25,
        help_text='The currency of the APC value eg. GBP or USD.',
    )
    recorded = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=25,
        choices=apc_status_choices(),
        default='new',
    )
    invoiced = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)

    def mark_as_paid(self):
        self.status = 'paid'
        self.completed = timezone.now()
        self.save()

    def mark_as_unpaid(self):
        self.status = 'nonpay'
        self.completed = timezone.now()
        self.save()

    def mark_as_invoiced(self):
        self.status = 'invoiced'
        self.invoiced = timezone.now()
        self.save()

    def mark_as_new(self):
        self.status = 'new'
        self.completed = None
        self.save()

    def value_change_log_entries(self):
        content_type = ContentType.objects.get_for_model(self)
        return utils_models.LogEntry.objects.filter(
            types=APC_VALUE_CHANGE,
            content_type=content_type,
            object_id=self.pk,
        )


class WaiverApplication(models.Model):
    article = models.OneToOneField(
        'submission.Article',
        on_delete=models.CASCADE,
    )
    reviewer = models.ForeignKey(
        'core.Account',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    status = models.CharField(
        max_length=25,
        choices=waiver_status_choices(),
        default='new',
    )
    rationale = models.TextField(
        null=True,
        verbose_name='Supporting Information',
    )

    made = models.DateTimeField(default=timezone.now)
    reviewed = models.DateTimeField(blank=True, null=True)
    response = models.TextField(null=True)

    class Meta:
        ordering = ('made', 'status')

    def __str__(self):
        return 'Waiver for Article {pk} - {status}.'.format(
            pk=self.article.pk,
            status=self.status,
        )

    def complete_application(self, article, request):
        self.article = article
        self.save()

        # Send email to editors
        message = '<p>{user} has requested a waiver for {article}.</p>' \
                  '<p><a href="{j_url}">Waiver Management</a>'.format(
                      user=request.user,
                      article=article.title,
                      j_url=request.journal.site_url(path=reverse('apc_index')),
                  )

        to = [
            bs.staffer.email for bs in BillingStaffer.objects.filter(
                journal=request.journal,
                type_of_notification='waiver',
                receives_notifications=True,
            )
        ]

        if not to:
            to = request.journal.editor_emails

        notify_helpers.send_email_with_body_from_user(
            request,
            'New Waiver Application',
            to,
            message,
        )

    def reviewer_display(self):
        if self.reviewer:
            return self.reviewer.full_name()
        else:
            return 'No reviewer assigned.'

    def reviewed_display(self):
        if self.reviewed:
            return self.reviewed
        else:
            return 'Waiver has not been reviewed.'


def type_of_notification_choices():
    return (
        ('ready', 'Ready for Invoicing'),
        ('invoiced', 'Invoice Sent'),
        ('paid', 'Invoice Paid'),
        ('waiver', 'Waiver Application'),
    )


class BillingStaffer(models.Model):
    journal = models.ForeignKey(
        'journal.Journal',
        on_delete=models.CASCADE,
    )
    staffer = models.ForeignKey(
        'core.Account',
        on_delete=models.CASCADE,
    )
    receives_notifications = models.BooleanField(default=True)
    type_of_notification = models.CharField(
        max_length=15,
        choices=type_of_notification_choices(),
        default='ready',
    )
    class Meta:
        unique_together = ('staffer', 'journal', 'type_of_notification')

    def __str__(self):
        return "[{code}] - {staffer} ({active})".format(
            code=self.journal.code,
            staffer=self.staffer.full_name(),
            active=self.receives_notifications,
        )

    def status_string(self):
        status_dict = dict(type_of_notification_choices())
        return status_dict[self.type_of_notification]

    def notification_setting_name(self):
        if self.type_of_notification == 'ready':
            return 'apc_article_ready_for_invoicing'
        elif self.type_of_notification == 'invoiced':
            return 'apc_article_invoice_sent'
        elif self.type_of_notification == 'waiver':
            return 'apc_article_waiver'
        else:
            return 'apc_article_invoice_paid'

    def notification_subject_setting_name(self):
        return 'subject_{}'.format(
            self.notification_setting_name()
        )

    def send_notification(self, request, article):
        description = "Article \"{title}\" apc status: {status}".format(
            title=article.title,
            status=self.status_string(),
        )
        log_dict = {
            'level': 'Info', 
            'action_text': description,
            'types': 'APC Notification',
            'target': article,
        }
        context = {
            'article': article,
            'billing_staffer': self,
            'apc_index_value': request.journal.site_url(
                path=reverse('apc_index')
            )
        }
        notify_helpers.send_email_with_body_from_setting_template(
            request,
            self.notification_setting_name(),
            self.notification_subject_setting_name(),
            self.staffer.email,
            context,
            log_dict=log_dict,
        )
        notify_helpers.send_slack(request, description, ['slack_editors'])


class Discount(models.Model):
    name = models.CharField(max_length=50)
    percentage = models.PositiveIntegerField()
    journal = models.ForeignKey(
        'journal.Journal',
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name
