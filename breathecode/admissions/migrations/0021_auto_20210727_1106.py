# Generated by Django 3.2.5 on 2021-07-27 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0020_auto_20210727_1106'),
        ('certificate', '0012_auto_20210727_1106'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Certificate',
        ),
        migrations.DeleteModel(
            name='CertificateTimeSlot',
        ),
        migrations.AddField(
            model_name='syllabusversion',
            name='syllabus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admissions.syllabus'),
        ),
        migrations.AddField(
            model_name='specialtymodetimeslot',
            name='academy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admissions.academy'),
        ),
        migrations.AddField(
            model_name='specialtymodetimeslot',
            name='specialty_mode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admissions.specialtymode'),
        ),
        migrations.AddField(
            model_name='academyspecialtymode',
            name='academy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admissions.academy'),
        ),
        migrations.AddField(
            model_name='academyspecialtymode',
            name='specialty_mode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admissions.specialtymode'),
        ),
        migrations.AddField(
            model_name='cohort',
            name='specialty_mode',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='admissions.specialtymode'),
        ),
        migrations.AddField(
            model_name='cohort',
            name='syllabus_version',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='admissions.syllabusversion'),
        ),
    ]
