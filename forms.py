from django import forms

from plugins.apc import models


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
