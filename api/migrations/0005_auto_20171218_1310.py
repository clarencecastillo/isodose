# Generated by Django 2.0 on 2017-12-18 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20171218_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='current_generation',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='trial',
            name='directory',
            field=models.CharField(max_length=240, null=True),
        ),
        migrations.AddField(
            model_name='trial',
            name='max_generation',
            field=models.IntegerField(null=True),
        ),
    ]
