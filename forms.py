from django import forms
from django.forms.forms import NON_FIELD_ERRORS

from plugins.apc import models, plugin_settings as apc_plugin_settings
from core import models as core_models
from utils import setting_handler as core_setting_handler


class APCForm(forms.ModelForm):
    class Meta:
        model = models.SectionAPC
        exclude = ("section",)

    def save(self, section, commit=True):
        section_apc = super(APCForm, self).save(commit=False)
        section_apc.section = section

        if commit:
            section_apc.save()

        return section_apc


class WaiverResponse(forms.ModelForm):
    class Meta:
        model = models.WaiverApplication
        fields = ("response",)


class WaiverApplication(forms.ModelForm):
    class Meta:
        model = models.WaiverApplication
        fields = ("rationale",)


class APCSettingsForm(forms.Form):
    enable_apcs = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"id": "enable_apcs"}),
    )
    track_apcs = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"id": "track_apcs"}),
    )
    author_contribution_mode = forms.ChoiceField(
        choices=[
            ("", "None"),
            ("waiver", "Waiver"),
            ("vac", "Voluntary Author Contribution (VAC)"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "author_contribution_mode"}),
    )
    waiver_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"id": "waiver_text"}),
    )
    vac_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"id": "vac_text"}),
    )

    def __init__(self, *args, plugin=None, journal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin = plugin
        self.journal = journal
        for field_name, pretty in apc_plugin_settings.APC_SETTINGS.items():
            setting = core_setting_handler.get_plugin_setting(
                plugin,
                field_name,
                journal,
                create=True,
                pretty=pretty,
            )
            self.fields[field_name].label = setting.setting.pretty_name
            self.fields[field_name].help_text = setting.setting.description
            if not self.is_bound:
                if field_name in apc_plugin_settings.APC_BOOLEAN_SETTINGS:
                    self.initial[field_name] = setting.value == "on"
                else:
                    self.initial[field_name] = setting.value or ""

    def save(self):
        data = self.cleaned_data
        for field_name in apc_plugin_settings.APC_SETTINGS:
            if field_name in apc_plugin_settings.APC_BOOLEAN_SETTINGS:
                value = "on" if data[field_name] else ""
            else:
                value = data[field_name]
            core_setting_handler.save_plugin_setting(
                self.plugin,
                field_name,
                value,
                self.journal,
            )


class VACFilterForm(forms.Form):
    accepted = forms.ChoiceField(
        choices=[("", "All"), ("yes", "Accepted"), ("no", "Not Accepted")],
        required=False,
        label="Filter by acceptance",
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )
    contacted = forms.ChoiceField(
        choices=[("", "All"), ("yes", "Contacted"), ("no", "Not Contacted")],
        required=False,
        label="Filter by contacted",
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )


class BillingStafferForm(forms.ModelForm):
    class Meta:
        model = models.BillingStaffer
        fields = ("staffer", "type_of_notification", "receives_notifications")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(BillingStafferForm, self).__init__(*args, **kwargs)

        user_pks = self.request.journal.journal_users(objects=False)
        self.fields["staffer"].queryset = core_models.Account.objects.filter(
            pk__in=user_pks,
        )

    def clean(self):
        staffer = self.cleaned_data.get("staffer")
        type_of_notification = self.cleaned_data.get("type_of_notification")
        journal = self.request.journal

        if (
            not self.instance.pk
            and models.BillingStaffer.objects.filter(
                staffer=staffer,
                journal=journal,
                type_of_notification=type_of_notification,
            ).exists()
        ):
            self._errors[NON_FIELD_ERRORS] = self.error_class(
                ["A Billing Staffer with this user, journal and type already exists."]
            )

        return self.cleaned_data

    def save(self, commit=True):
        staffer = super(BillingStafferForm, self).save(commit=False)
        staffer.journal = self.request.journal

        if commit:
            staffer.save()

        return staffer
