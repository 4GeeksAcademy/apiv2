# Generated by Django 3.1.4 on 2021-01-22 01:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0014_auto_20201218_0534'),
        ('coursework', '0006_auto_20201209_0216'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabus',
            name='academy_owner',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='admissions.academy'),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]
