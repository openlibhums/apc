from django import forms
from django.forms.forms import NON_FIELD_ERRORS

from plugins.apc import models
from core import models as core_models


class APCForm(forms.ModelForm):
    class Meta:
        model = models.SectionAPC
        exclude = ('section',)

    def save(self, section, commit=True):
        section_apc = super(APCForm, self).save(commit=False)
        section_apc.section = section

        if commit:
            section_apc.save()

        return section_apc


class WaiverResponse(forms.ModelForm):

    class Meta:
        model = models.WaiverApplication
        fields = ('response',)


class WaiverApplication(forms.ModelForm):

    class Meta:
        model = models.WaiverApplication
        fields = ('rationale',)


class BillingStafferForm(forms.ModelForm):

    class Meta:
        model = models.BillingStaffer
        fields = ('staffer', 'type_of_notification', 'receives_notifications')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(BillingStafferForm, self).__init__(*args, **kwargs)

        user_pks = self.request.journal.journal_users(objects=False)
        self.fields['staffer'].queryset = core_models.Account.objects.filter(
            pk__in=user_pks,
        )

    def clean(self):
        staffer = self.cleaned_data.get('staffer')
        type_of_notification = self.cleaned_data.get('type_of_notification')
        journal = self.request.journal

        if not self.instance.pk and models.BillingStaffer.objects.filter(
            staffer=staffer,
            journal=journal,
            type_of_notification=type_of_notification,
        ).exists():
            self._errors[NON_FIELD_ERRORS] = self.error_class(
                ['A Billing Staffer with this user, journal and type already exists.']
            )

        return self.cleaned_data

    def save(self, commit=True):
        staffer = super(BillingStafferForm, self).save(commit=False)
        staffer.journal = self.request.journal

        if commit:
            staffer.save()

        return staffer
