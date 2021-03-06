# Generated by Django 2.0.3 on 2018-04-12 20:46

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlbumGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('latlong', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AlbumYears',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('xorder', models.IntegerField()),
            ],
            options={
                'ordering': ('xorder', '-year'),
            },
        ),
        migrations.CreateModel(
            name='PhotoAlbum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=30)),
                ('path', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(db_index=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime(2018, 4, 12, 20, 46, 35, 342437))),
                ('group', models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='images.AlbumGroup')),
            ],
        ),
    ]
