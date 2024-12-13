# Generated by Django 5.1.4 on 2024-12-13 09:56

import pgvector.django.vector
from pgvector.django import VectorExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("clairvoyance", "0001_initial"),
    ]

    operations = [
        VectorExtension(),
        migrations.AlterField(
            model_name="majorarcanavector",
            name="embedding",
            field=pgvector.django.vector.VectorField(dimensions=384),
        ),
    ]