# Generated by Django 3.2.5 on 2021-07-10 01:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0022_remove_cohorttimeslot_specialty_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialtymode',
            name='syllabus',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='admissions.syllabus'),
        ),
    ]
