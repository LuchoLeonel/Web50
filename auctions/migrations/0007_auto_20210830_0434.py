# Generated by Django 3.2.6 on 2021-08-30 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_categoria_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='categories',
        ),
        migrations.AlterField(
            model_name='auction',
            name='title',
            field=models.CharField(max_length=20),
        ),
    ]
