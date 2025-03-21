# Generated by Django 5.1.7 on 2025-03-10 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tooth',
            name='position',
            field=models.IntegerField(blank=True, help_text='Position within the quadrant (1-8)', null=True),
        ),
        migrations.AddField(
            model_name='tooth',
            name='quadrant',
            field=models.IntegerField(blank=True, choices=[(1, 'Upper Right'), (2, 'Upper Left'), (3, 'Lower Left'), (4, 'Lower Right')], null=True),
        ),
    ]
