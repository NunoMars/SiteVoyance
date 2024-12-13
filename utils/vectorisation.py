# Vectoriser les données textuelles de MAjorArcana et les inserer dans la base de données

from sentence_transformers import SentenceTransformer
from clairvoyance.models import MajorArcana, MajorArcanaVector


def vectorize_major_arcana(card_id):
    """Vectorize the text data of MajorArcana and insert it into the database."""
    card = MajorArcana.objects.get(pk=card_id)
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    card_text = card.card_text()
    embedding = model.encode(card_text)
    MajorArcanaVector.objects.create(
        card_id=card,
        content=card_text,
        embedding=embedding,
        card_text=card_text,
    )
