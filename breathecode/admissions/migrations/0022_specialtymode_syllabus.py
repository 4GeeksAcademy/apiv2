# Generated by Django 3.2.5 on 2021-07-27 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0021_auto_20210727_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialtymode',
            name='syllabus',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='admissions.syllabus'),
        ),
    ]
