# Generated by Django 4.2.6 on 2023-12-08 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_alter_discuss_topics_alter_discuss_views_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='discuss',
            name='is_watching_or_not',
            field=models.BooleanField(null=True),
        ),
    ]