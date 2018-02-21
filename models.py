from django.db import models
from django.utils import timezone


def waiver_status_choices():
    return (
        ('new', 'New'),
        ('review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )


class SectionAPC(models.Model):
    section = models.OneToOneField('submission.Section')
    value = models.DecimalField(max_digits=6, decimal_places=2, help_text='Decimal with two places eg. 200.00')
    currency = models.CharField(max_length=25, help_text='The currency of the APC value eg. GBP or USD.')

    class Meta:
        ordering = ('section__journal', 'value', 'currency')


class WaiverApplication(models.Model):
    article = models.ForeignKey('submission.Article')
    reviewer = models.ForeignKey('core.Account', blank=True, null=True)
    status = models.CharField(max_length=25, choices=waiver_status_choices(), default='new')

    made = models.DateTimeField(default=timezone.now)
    reviewed = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('made', 'status')

    def __str__(self):
        return 'Waiver for Article {pk} - {status}.'.format(pk=self.article.pk, status=self.status)
