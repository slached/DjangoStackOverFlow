# Generated by Django 4.2.6 on 2023-12-05 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_myuser_watchedtags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discuss',
            name='topics',
            field=models.ManyToManyField(related_name='whole_topic', to='base.tag'),
        ),
    ]
