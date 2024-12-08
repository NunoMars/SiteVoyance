from .models import LeftDeck, MajorArcana, RightDeck
from .prepare_decks_cards import prepare_decks
from .voyante_llm import voyante_chatbot
import json


def send_cards_choosed_deck_to_user(arg0):
    """
    Send the cards choosed by the user to the user.
    """
    deck = arg0.objects.all()

    # requeter dans MajorArcana pour avoir les images

    def _get_cards_from_majorarcana_table(deck):
        """
        Get the cards from the MajorArcana table.
        """

        cards_ids = [card.card_id_id for card in deck]

        cards = MajorArcana.objects.filter(id__in=cards_ids)

        return cards

    deck = _get_cards_from_majorarcana_table(deck)

    deck_data = [
        {
            "name": card.card_name_fr,
            "image_url": card.card_image.url,
        }
        for card in deck
    ]

    return {
        "subject": "propose to choose five cards",
        "message": deck_data,
    }


def clairvoyant(input_value):
    """
    Construct the bot response.
    """
    global user_name
    global chosed_theme

    rand_card = MajorArcana.objects.order_by("?")[0]

    print(f"Mesage envoyé de puis la view: {input_value}")
    input_value = json.loads(input_value)
    if input_value["subject"] == "name":
        user_name = input_value["name"]
        return {"subject": "menu", "user_name": user_name}

    elif input_value["subject"] == "Yes":
        return {"subject": "menu", "user_name": user_name}

    elif input_value["subject"] == "No":
        return {
            "subject": "No",
            "message": "Merci j'ai été ravie de vous aider!!",
        }

    elif input_value["subject"] == "one":
        return _get_response_one_card(rand_card)

    elif input_value["subject"] in ["love", "work", "gen", "one"]:
        chosed_theme = input_value

        return {"subject": "cut", "user_name": user_name}

    elif input_value["subject"] == "cut":

        decks = prepare_decks()
        len_left_deck = decks[0].count()
        len_right_deck = decks[1].count()
        return {
            "subject": "choose_deck",
            "len_left_deck": str(len_left_deck),
            "len_right_deck": str(len_right_deck),
        }

    elif input_value["subject"] == "left":
        return send_cards_choosed_deck_to_user(LeftDeck)

    elif input_value["subject"] == "right":
        return send_cards_choosed_deck_to_user(RightDeck)

    return voyante_chatbot(input_value)


def _get_response_one_card(rand_card):

    card_name = rand_card.card_name_fr
    card_signification_warnings = rand_card.card_signification_warnings_fr
    card_signification_love = rand_card.card_signification_love_fr
    card_signification_work = rand_card.card_signification_work_fr
    card_signification_gen = rand_card.card_signification_gen_fr

    return {
        "subject": "one_card",
        "user_name": user_name,
        "card_image": rand_card.card_image.url,
        "card_name": card_name,
        "card_signification_warnings": card_signification_warnings,
        "card_signification_love": card_signification_love,
        "card_signification_work": card_signification_work,
        "card_signification_gen": card_signification_gen,
    }
