from django.db import models
from django.utils.safestring import mark_safe
from pgvector.django import VectorField


class MajorArcana(models.Model):
    """Class to define the mayor cards deck."""

    CHOICES = (
        ("Positif", "Positif"),
        ("Negatif", "Negatif"),
        ("Neutral", "neutral"),
    )

    card_name = models.CharField(max_length=50)

    card_signification_gen = models.TextField(default="fr")

    card_signification_warnings = models.TextField(default="fr")

    card_signification_love = models.TextField(default="fr")

    card_signification_work = models.TextField(default="fr")

    card_image = models.ImageField(upload_to="MajorArcanaCards")
    card_polarity = models.CharField(max_length=10, choices=CHOICES, default="Positif")

    card_text_summarized = models.TextField(default="none")

    def card_text(self):
        return f"{self.card_signification_gen} {self.card_signification_love} {self.card_signification_work} {self.card_signification_warnings}"

    def __str__(self):
        return self.card_name

    def image_tag(self):

        return mark_safe(f'<img src="{self.card_image}" width="75" height="75" />')

    image_tag.short_description = "Image"


# VectorField is a custom field that allows you to store and query dense vectors.


class MajorArcanaVector(models.Model):
    """Class to define the mayor cards deck."""

    card_id = models.ForeignKey(MajorArcana, on_delete=models.CASCADE)
    content = models.TextField()  # Texte brut extrait du document
    embedding = VectorField(dimensions=384)  # Vecteur d'embedding (512 dimensions)
    metadata = models.JSONField(null=True, blank=True)  # Métadonnées optionnelles
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.card_id.card_name


class LeftDeck(models.Model):
    """Class to define the left deck."""

    card_id = models.ForeignKey(MajorArcana, on_delete=models.CASCADE)

    def __str__(self):
        return self.card_id.card_name


class RightDeck(models.Model):
    """Class to define the right deck."""

    card_id = models.ForeignKey(MajorArcana, on_delete=models.CASCADE)

    def __str__(self):
        return self.card_id.card_name
