from django.db import models
from django.utils import timezone


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
        ('paid', 'Paid'),
        ('nonpay', 'Non Payment'),
    )


class SectionAPC(models.Model):
    section = models.OneToOneField('submission.Section')
    value = models.DecimalField(max_digits=6, decimal_places=2, help_text='Decimal with two places eg. 200.00')
    currency = models.CharField(max_length=25, help_text='The currency of the APC value eg. GBP or USD.')

    class Meta:
        ordering = ('section__journal', 'value', 'currency')


class ArticleAPC(models.Model):
    article = models.OneToOneField('submission.Article')
    section_apc = models.ForeignKey(SectionAPC)
    value = models.DecimalField(max_digits=6, decimal_places=2, help_text='Decimal with two places eg. 200.00')
    currency = models.CharField(max_length=25, help_text='The currency of the APC value eg. GBP or USD.')
    recorded = models.DateTimeField(default=timezone.now)

    status = models.CharField(max_length=25, choices=apc_status_choices(), default='new')
    completed = models.DateTimeField(blank=True, null=True)


class WaiverApplication(models.Model):
    article = models.OneToOneField('submission.Article')
    reviewer = models.ForeignKey('core.Account', blank=True, null=True)
    status = models.CharField(max_length=25, choices=waiver_status_choices(), default='new')
    rationale = models.TextField(null=True, verbose_name='Supporting Information')

    made = models.DateTimeField(default=timezone.now)
    reviewed = models.DateTimeField(blank=True, null=True)
    response = models.TextField(null=True)

    class Meta:
        ordering = ('made', 'status')

    def __str__(self):
        return 'Waiver for Article {pk} - {status}.'.format(pk=self.article.pk, status=self.status)

    def complete_application(self, article):
        self.article = article
        self.save()

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
