from django.db import models
from django.utils import timezone
from django.urls import reverse

from utils import notify_helpers, models as utils_models, notify_helpers


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
    section = models.OneToOneField('submission.Section')
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
    article = models.OneToOneField('submission.Article')
    section_apc = models.ForeignKey(SectionAPC)
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


class WaiverApplication(models.Model):
    article = models.OneToOneField('submission.Article')
    reviewer = models.ForeignKey('core.Account', blank=True, null=True)
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
                  '<p><a href="{j_url}{w_url}">Waiver Management</a>'.format(
                      user=request.user,
                      article=article.title,
                      j_url=request.journal_base_url,
                      w_url=reverse('apc_index'),
                  )
        notify_helpers.send_email_with_body_from_user(
            request,
            'New Waiver Application',
            request.journal.editor_emails,
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


class BillingStaffer(models.Model):
    journal = models.ForeignKey('journal.Journal')
    staffer = models.ForeignKey('core.Account')
    receives_notifications = models.BooleanField(default=True)

    class Meta:
        unique_together = ('staffer', 'journal')

    def __str__(self):
        return "[{code}] - {staffer} ({active})".format(
            code=self.journal.code,
            staffer=self.staffer.full_name(),
            active=self.receives_notifications,
        )

    def send_notification(self, request, article):
        description="Article {title} is ready for invoicing".format(
            title=article.title,
        )

        log_dict = {
            'level': 'Info', 
            'action_text': description,
            'types': 'APC Notication',
            'target': article,
        }

        notify_helpers.send_email_with_body_from_setting_template(
            request,
            'apc_article_ready_for_invoicing',
            'Article Ready for Invoicing',
            self.staffer.email,
            {'article': article, 'billing_staffer': self},
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
