# Generated by Django 2.0.1 on 2018-02-20 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_auth', '0008_auto_20180207_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]