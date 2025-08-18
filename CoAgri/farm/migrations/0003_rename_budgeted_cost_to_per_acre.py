# Generated manually for renaming budgeted_cost to budgeted_cost_per_acre

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0002_alter_plot_unique_together'),
    ]

    operations = [
        migrations.RenameField(
            model_name='farmplanstep',
            old_name='budgeted_cost',
            new_name='budgeted_cost_per_acre',
        ),
        migrations.AlterField(
            model_name='farmplanstep',
            name='budgeted_cost_per_acre',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Cost per acre in ₹', max_digits=12),
        ),
    ]