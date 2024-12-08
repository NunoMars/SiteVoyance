from .models import MajorArcana, LeftDeck, RightDeck
from random import randint as rand


def prepare_decks():
    """
    This function prepares the deck's for the game.
    It takes in a deck type and insert to a model.
    """

    LeftDeck.objects.all().delete()  # Remise a zero le deck
    RightDeck.objects.all().delete()  # remise a zero le deck

    shuffle_deck = MajorArcana.objects.order_by("?")
    cut_point = rand(7, len(shuffle_deck) - 7)
    left_deck = shuffle_deck[:cut_point]
    right_deck = shuffle_deck[cut_point:]

    for card in left_deck:
        LeftDeck.objects.create(card_id=card)

    for card in right_deck:
        RightDeck.objects.create(card_id=card)

    return LeftDeck.objects.all(), RightDeck.objects.all()
