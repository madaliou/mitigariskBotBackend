# Generated by Django 3.1 on 2022-04-22 12:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20220422_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to=settings.AUTH_USER_MODEL),
        ),
    ]
