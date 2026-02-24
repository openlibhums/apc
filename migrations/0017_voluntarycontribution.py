from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def migrate_enable_waivers(apps, schema_editor):
    """
    For any journal that has enable_waivers = 'on', set author_contribution_mode
    = 'waiver', provided author_contribution_mode is not already set.
    """
    SettingValue = apps.get_model('core', 'SettingValue')
    Setting = apps.get_model('core', 'Setting')

    try:
        waivers_setting = Setting.objects.get(
            name='enable_waivers',
            group__name='plugin:apc',
        )
        mode_setting = Setting.objects.get(
            name='author_contribution_mode',
            group__name='plugin:apc',
        )
    except Setting.DoesNotExist:
        return

    for sv in SettingValue.objects.filter(setting=waivers_setting, value='on'):
        SettingValue.objects.update_or_create(
            setting=mode_setting,
            journal=sv.journal,
            defaults={'value': 'waiver'},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0001_initial'),
        ('apc', '0016_merge_20240926_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoluntaryContribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, default=0, help_text='Decimal with two places eg. 200.00', max_digits=6)),
                ('currency', models.CharField(blank=True, default='', help_text='The currency of the APC value eg. GBP or USD.', max_length=25)),
                ('recorded', models.DateTimeField(default=django.utils.timezone.now)),
                ('contacted', models.BooleanField(default=False)),
                ('contacted_date', models.DateTimeField(blank=True, null=True)),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='submission.article')),
                ('section_apc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apc.sectionapc')),
            ],
            options={
                'ordering': ('-recorded',),
            },
        ),
        migrations.AlterField(
            model_name='billingstaffer',
            name='type_of_notification',
            field=models.CharField(
                choices=[
                    ('ready', 'Ready for Invoicing'),
                    ('invoiced', 'Invoice Sent'),
                    ('paid', 'Invoice Paid'),
                    ('waiver', 'Waiver Application'),
                    ('vac', 'Voluntary Contribution'),
                ],
                default='ready',
                max_length=15,
            ),
        ),
        migrations.RunPython(migrate_enable_waivers, migrations.RunPython.noop),
    ]
