from django.template import Context
from django.test import TestCase

from plugins.apc import forms, hooks, models, plugin_settings
from utils import setting_handler
from utils.testing import helpers


class APCSettingsFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        helpers.create_press()
        cls.journal, _ = helpers.create_journals()
        plugin_settings.install()
        cls.plugin = plugin_settings.get_self()

    def _get_value(self, name):
        return setting_handler.get_plugin_setting(self.plugin, name, self.journal).value

    def _submit(self, data):
        form = forms.APCSettingsForm(data, plugin=self.plugin, journal=self.journal)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

    def _base_data(self, **overrides):
        data = {
            "enable_apcs": False,
            "track_apcs": False,
            "author_contribution_mode": "",
            "waiver_text": "",
            "vac_text": "",
        }
        data.update(overrides)
        return data

    def test_form_populates_initial_values_from_settings(self):
        setting_handler.save_plugin_setting(
            self.plugin, "enable_apcs", "on", self.journal
        )
        setting_handler.save_plugin_setting(
            self.plugin, "author_contribution_mode", "vac", self.journal
        )
        setting_handler.save_plugin_setting(
            self.plugin, "vac_text", "Please contribute", self.journal
        )
        form = forms.APCSettingsForm(plugin=self.plugin, journal=self.journal)
        self.assertTrue(form.initial["enable_apcs"])
        self.assertFalse(form.initial["track_apcs"])
        self.assertEqual(form.initial["author_contribution_mode"], "vac")
        self.assertEqual(form.initial["vac_text"], "Please contribute")

    def test_save_updates_settings(self):
        self._submit(
            self._base_data(
                enable_apcs=True,
                author_contribution_mode="vac",
                vac_text="Help us publish",
            )
        )
        self.assertEqual(self._get_value("enable_apcs"), "on")
        self.assertEqual(self._get_value("track_apcs"), "")
        self.assertEqual(self._get_value("author_contribution_mode"), "vac")
        self.assertEqual(self._get_value("vac_text"), "Help us publish")



class WaiverInfoHookTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        helpers.create_press()
        cls.journal, _ = helpers.create_journals()
        plugin_settings.install()
        cls.plugin = plugin_settings.get_self()

    def _context(self):
        return Context({"request": helpers.Request(journal=self.journal)})

    def test_no_mode_returns_empty_string(self):
        setting_handler.save_plugin_setting(
            self.plugin, "author_contribution_mode", "", self.journal
        )
        self.assertEqual(hooks.waiver_info(self._context()), "")

    def test_waiver_mode_renders_waiver_info(self):
        setting_handler.save_plugin_setting(
            self.plugin, "author_contribution_mode", "waiver", self.journal
        )
        setting_handler.save_plugin_setting(
            self.plugin, "waiver_text", "Apply for a waiver here", self.journal
        )
        result = hooks.waiver_info(self._context())
        self.assertIn("Waiver Information", result)
        self.assertIn("Apply for a waiver here", result)

    def test_vac_mode_renders_vac_optin(self):
        setting_handler.save_plugin_setting(
            self.plugin, "author_contribution_mode", "vac", self.journal
        )
        setting_handler.save_plugin_setting(
            self.plugin, "vac_text", "Support open access", self.journal
        )
        result = hooks.waiver_info(self._context())
        self.assertIn('name="vac_optin"', result)
        self.assertIn("Support open access", result)


class WaiverApplicationHookTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        helpers.create_press()
        cls.journal, _ = helpers.create_journals()
        plugin_settings.install()
        cls.plugin = plugin_settings.get_self()
        cls.article = helpers.create_article(cls.journal)

    def _context(self):
        return Context(
            {
                "request": helpers.Request(journal=self.journal),
                "article": self.article,
            }
        )

    def test_waiver_mode_renders_application_template(self):
        setting_handler.save_plugin_setting(
            self.plugin, "author_contribution_mode", "waiver", self.journal
        )
        models.WaiverApplication.objects.create(article=self.article)
        result = hooks.waiver_application(self._context())
        self.assertIn("Waiver Application", result)
        self.assertIn("active waiver request", result)

    def test_non_waiver_mode_returns_empty_string(self):
        for mode in ("vac", ""):
            setting_handler.save_plugin_setting(
                self.plugin, "author_contribution_mode", mode, self.journal
            )
            self.assertEqual(hooks.waiver_application(self._context()), "")
