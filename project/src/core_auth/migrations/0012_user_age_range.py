# Generated by Django 2.0.2 on 2018-03-05 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_auth', '0011_autherror'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='age_range',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]