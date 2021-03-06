# Generated by Django 3.1.1 on 2021-03-14 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rms', '0009_auto_20210314_1726'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rmsId', models.CharField(blank=True, max_length=40, null=True)),
                ('Date', models.DateField(blank=True, null=True)),
                ('dcenergy', models.FloatField(blank=True, null=True)),
                ('prthrs', models.FloatField(blank=True, null=True)),
                ('lpd', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SiteDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rmsId', models.CharField(blank=True, max_length=40, null=True)),
                ('regID', models.CharField(blank=True, max_length=40, null=True)),
                ('custName', models.CharField(blank=True, max_length=40, null=True)),
                ('custMob', models.IntegerField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('capacity', models.CharField(blank=True, max_length=10, null=True)),
                ('poNo', models.CharField(blank=True, max_length=100, null=True)),
                ('cmcY', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Mdtls',
        ),
        migrations.DeleteModel(
            name='siteDtls',
        ),
    ]
