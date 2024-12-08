# Generated by Django 5.1.4 on 2024-12-08 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clairvoyance', '0007_majorarcana_card_signification_love_en_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_name_en',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_name_es',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_name_pt',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_gen_en',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_gen_es',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_gen_pt',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_love_en',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_love_es',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_love_pt',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_warnings_en',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_warnings_es',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_warnings_pt',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_work_en',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_work_es',
        ),
        migrations.RemoveField(
            model_name='majorarcana',
            name='card_signification_work_pt',
        ),
        migrations.AddField(
            model_name='majorarcana',
            name='card_text_summarized',
            field=models.TextField(default='none'),
        ),
    ]
