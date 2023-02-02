# Generated by Django 4.1.5 on 2023-01-09 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('time_create', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('card_type', models.CharField(choices=[('T', 'Term'), ('W', 'Word')], max_length=1)),
                ('transcription', models.TextField(blank=True)),
                ('translate', models.TextField(blank=True)),
                ('content', models.TextField(blank=True)),
                ('time_create', models.DateTimeField(auto_now_add=True)),
                ('time_last_show', models.DateTimeField(auto_now=True)),
                ('count_shows', models.IntegerField(default=0)),
                ('category', models.ManyToManyField(to='card.category')),
            ],
        ),
    ]
