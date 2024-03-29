# Generated by Django 3.2 on 2023-08-20 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='occupation',
            field=models.CharField(max_length=70),
        ),
        migrations.AlterField(
            model_name='quoteinformation',
            name='expired',
            field=models.BooleanField(default=True),
        ),
    ]
