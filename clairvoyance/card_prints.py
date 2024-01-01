from random import randint as rand
from .models import MajorArcana


def response_card(name, chosed_card_deck, chosed_theme):
    """
    Draw the Tarot response, the last card.
    """

    card = _average_result_card(chosed_card_deck)

    themes = {
        "love": card.card_signification_love_fr,
        "work": card.card_signification_work_fr,
        "gen": card.card_signification_gen_fr,
    }

    return {
        "user_name": name,
        "card_image": card.card_image.url,
        "card_name": card.card_name_fr.capitalize(),
        "chosed_theme_signification": themes[chosed_theme],
        "warnings": card.card_signification_warnings_fr,
    }, card


def polarity_calcul(list_of_polarity):
    """
    Construct the message of polarity of deck cards
    """
    items_on_list = len(list_of_polarity)

    def percentage(items_on_list, count_list):
        return count_list * 100 / items_on_list

    how_positif = list_of_polarity.count("Positif")
    how_negatif = list_of_polarity.count("Negatif")
    percentage_positif = round(percentage(items_on_list, how_positif), 2)
    percentage_negatif = round(percentage(items_on_list, how_negatif), 2)

    if how_negatif != 0 and how_negatif < how_positif:
        return f"Résultat plutôt positif avec {str(percentage_positif)}% des cartes!!"

    elif how_positif != 0 and how_positif < how_negatif:
        return f"Résultat plutôt négatif avec {str(percentage_negatif)}% des cartes!!"

    return "Il ya un equilibre dans votre tirage!"


def _average_result_card(chosed_card_deck):
    """
    calcul and return the response card.
    """

    list_of_cards_ids = []
    for card in chosed_card_deck:
        card = MajorArcana.objects.get(card_name_fr=card)
        list_of_cards_ids.append(card.id)

    mean_card = round(sum(list_of_cards_ids) / len(list_of_cards_ids), 2)

    return MajorArcana.objects.get(id=mean_card)


# construire tableau
def _splitBy(li, n=1):
    """
    Generate the split of the cards list.
    """
    return [li[i : i + n] for i in range(1, len(li), n)]


def _create_cards_message(card, chosed_theme):
    """
    Draw a bouton card with the name.
    """

    msg = [
        "<div class='col'>"
        + "<div class='cta-inner text-center rounded'>"
        + "<a href='#'><img class='card' src='/static/img/cards/Back.jpg'"
        + "onmouseover="
        + '"this.src='
        + "'"
        + card.card_image.url
        + "'"
        + '"'
        + "onmouseout="
        + "this.src='/static/img/cards/Back.jpg'"
        + " alt=''/>"
        + "<span><p>"
        + card.card_name_fr.capitalize()
        + "</p>"
        + "<p>"
        + "Mise en Garde!"
        + "</p>"
        + card.card_signification_warnings_fr
        + "<p>"
        + "ce que signifie la carte!"
        + "</p>"
        + chosed_theme
        + "</span></a></div></div>"
    ]
    return msg[0]


def create_final_response(list_of_cards, name, list_of_polarity):
    """
    Construct the cards board and generate the response heads tittle.
    """

    column = 6

    card_board = _splitBy(list_of_cards, column)

    final_card_deck = []
    for i in card_board:
        l = "".join(i)
        final_card_deck.append(
            "<div class='row' height= '100%' text-align='center'>" + l + "</div>"
        )

    f = "".join(final_card_deck)

    polarity = polarity_calcul(list_of_polarity)

    return {
        "final_response_tittle": "<div class='col'><div class='cta-inner text-center rounded'>"
        + "<h4>"
        + name.capitalize()
        + " vois-ci votre réponse!"
        + "</h4>"
        + "<h4>"
        + polarity
        + "</h4>"
        + "<h6>"
        + "Afin de voir les mises en garde, survolez la carte avec la souris..."
        + "</h6>"
        + f
        + "</div>"
    }


def clairvoyante_sort_cards(name, chosed_card_deck, chosed_theme):
    """
    Construct the last response of sorted cards.
    """
    list_of_cards = []
    list_of_polarity = []

    for card in chosed_card_deck:
        card = MajorArcana.objects.get(card_name_fr=card)
        list_of_polarity.append(card.card_polarity)
        message_card = _create_cards_message(card, chosed_theme)
        list_of_cards.append(message_card)

    final = create_final_response(list_of_cards, name, list_of_polarity)

    response = response_card(name, chosed_card_deck, chosed_theme)

    final["response_card"] = response[0]
    return final, response[1]
