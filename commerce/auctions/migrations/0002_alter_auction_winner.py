# Generated by Django 3.2.6 on 2021-08-29 20:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='winner',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='auction_winner', to=settings.AUTH_USER_MODEL),
        ),
    ]
