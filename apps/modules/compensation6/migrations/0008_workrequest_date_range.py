# Generated manually for WorkRequest date range changes

from django.db import migrations, models
import django.db.models.deletion


def migrate_work_date_to_date_range(apps, schema_editor):
    """Migrate existing work_date to start_date and end_date"""
    WorkRequest = apps.get_model('compensation6', 'WorkRequest')
    for wr in WorkRequest.objects.all():
        if hasattr(wr, 'work_date') and wr.work_date:
            wr.start_date = wr.work_date
            wr.end_date = wr.work_date
            wr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('compensation6', '0007_alter_workrequest_options_and_more'),
    ]

    operations = [
        # Add new start_date and end_date fields
        migrations.AddField(
            model_name='workrequest',
            name='start_date',
            field=models.DateField(blank=True, help_text='Tanggal mulai penugasan kerja', null=True),
        ),
        migrations.AddField(
            model_name='workrequest',
            name='end_date',
            field=models.DateField(blank=True, help_text='Tanggal akhir penugasan kerja', null=True),
        ),
        
        # Migrate data from work_date to start_date and end_date
        migrations.RunPython(
            code=migrate_work_date_to_date_range,
            reverse_code=migrations.RunPython.noop
        ),
        
        # Make new fields required
        migrations.AlterField(
            model_name='workrequest',
            name='start_date',
            field=models.DateField(help_text='Tanggal mulai penugasan kerja'),
        ),
        migrations.AlterField(
            model_name='workrequest',
            name='end_date',
            field=models.DateField(help_text='Tanggal akhir penugasan kerja'),
        ),
        
        # Remove old work_date field
        migrations.RemoveField(
            model_name='workrequest',
            name='work_date',
        ),
        
        # Update Meta class ordering
        migrations.AlterModelOptions(
            name='workrequest',
            options={'ordering': ['-start_date', 'employee__name']},
        ),
    ]
