# Generated by Django 2.0.1 on 2018-01-22 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core_auth', '0003_socialprofile'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='socialprofile',
            unique_together={('user', 'provider')},
        ),
    ]
