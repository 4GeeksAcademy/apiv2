# Generated by Django 3.1.6 on 2021-04-08 01:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('slug', models.SlugField(max_length=200, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('lang', models.CharField(blank=True, default='en', max_length=3)),
                ('url', models.URLField()),
                ('preview', models.URLField()),
                ('description', models.TextField()),
                ('interactive', models.BooleanField(default=False)),
                ('with_solutions', models.BooleanField(default=False)),
                ('with_video', models.BooleanField(default=False)),
                ('duration', models.IntegerField()),
                ('language', models.CharField(blank=True, max_length=200)),
                ('visibility',
                 models.CharField(choices=[('PUBLIC', 'Public'), ('UNLISTED', 'Unlisted'),
                                           ('PRIVATE', 'Private')],
                                  default='PUBLIC',
                                  max_length=20)),
                ('asset_type',
                 models.CharField(choices=[('PROJECT', 'Project'), ('EXERCISE', 'Exercise'),
                                           ('LESSON', 'Lesson'), ('LESSON', 'Video')],
                                  max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author',
                 models.ForeignKey(blank=True,
                                   default=None,
                                   null=True,
                                   on_delete=django.db.models.deletion.SET_NULL,
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
