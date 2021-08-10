# Generated by Django 3.2.5 on 2021-07-27 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0019_certificatetimeslot_cohorttimeslot'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademySpecialtyMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpecialtyMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=100)),
                ('name', models.CharField(max_length=150)),
                ('schedule_type', models.CharField(choices=[('PART-TIME', 'Part-Time'), ('FULL-TIME', 'Full-Time')], default='PART-TIME', max_length=15)),
                ('description', models.TextField(max_length=450)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpecialtyModeTimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starting_at', models.DateTimeField()),
                ('ending_at', models.DateTimeField()),
                ('recurrent', models.BooleanField(default=True)),
                ('recurrency_type', models.CharField(choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly')], default='WEEKLY', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SyllabusVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', models.JSONField()),
                ('version', models.PositiveSmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='certificatetimeslot',
            name='academy',
        ),
        migrations.RemoveField(
            model_name='certificatetimeslot',
            name='certificate',
        ),
        migrations.RemoveField(
            model_name='cohort',
            name='syllabus',
        ),
        migrations.RemoveField(
            model_name='syllabus',
            name='certificate',
        ),
        migrations.RemoveField(
            model_name='syllabus',
            name='json',
        ),
        migrations.RemoveField(
            model_name='syllabus',
            name='version',
        ),
        migrations.AddField(
            model_name='syllabus',
            name='duration_in_days',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='duration_in_hours',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='logo',
            field=models.CharField(blank=True, default=None, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='week_hours',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.DeleteModel(
            name='AcademyCertificate',
        ),
    ]
