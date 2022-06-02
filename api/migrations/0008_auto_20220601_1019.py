# Generated by Django 3.1 on 2022-06-01 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_solution_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.EmailField(blank=True, max_length=70, unique=True),
        ),
        migrations.AddField(
            model_name='company',
            name='first_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='phoneNumber',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='company',
            name='resourcePerson',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]
