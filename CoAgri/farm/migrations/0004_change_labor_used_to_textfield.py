# Generated manually for changing labor_used from ManyToManyField to TextField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0003_rename_budgeted_cost_to_per_acre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailyactivity',
            name='labor_used',
        ),
        migrations.AddField(
            model_name='dailyactivity',
            name='labor_used',
            field=models.TextField(blank=True, help_text='Names of laborers used, separated by commas'),
        ),
    ]