# Generated by Django 3.1.2 on 2020-10-29 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0005_auto_20201029_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobsetting',
            name='oc_host',
            field=models.CharField(max_length=255),
        ),
    ]
