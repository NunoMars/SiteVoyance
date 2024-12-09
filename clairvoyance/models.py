from django.db import models
from django.utils.safestring import mark_safe


class MajorArcana(models.Model):
    """Class to define the mayor cards deck."""

    CHOICES = (
        ("Positif", "Positif"),
        ("Negatif", "Negatif"),
        ("Neutral", "neutral"),
    )

    card_name_fr = models.CharField(max_length=50)

    card_signification_gen_fr = models.TextField(default="fr")

    card_signification_warnings_fr = models.TextField(default="fr")

    card_signification_love_fr = models.TextField(default="fr")

    card_signification_work_fr = models.TextField(default="fr")

    card_image = models.ImageField(upload_to="MajorArcanaCards")
    card_polarity = models.CharField(max_length=10, choices=CHOICES, default="Positif")

    card_text_summarized = models.TextField(default="none")

    def card_text(self):
        return f"{self.card_signification_gen_fr} {self.card_signification_love_fr} {self.card_signification_work_fr} {self.card_signification_warnings_fr}"

    def __str__(self):
        return self.card_name_fr

    def image_tag(self):

        return mark_safe(f'<img src="{self.card_image}" width="75" height="75" />')

    image_tag.short_description = "Image"


class LeftDeck(models.Model):
    """Class to define the left deck."""

    card_id = models.ForeignKey(MajorArcana, on_delete=models.CASCADE)

    def __str__(self):
        return self.card_id.card_name_fr


class RightDeck(models.Model):
    """Class to define the right deck."""

    card_id = models.ForeignKey(MajorArcana, on_delete=models.CASCADE)

    def __str__(self):
        return self.card_id.card_name_fr
