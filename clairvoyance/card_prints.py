from random import randint as rand
from .models import MajorArcana


# construire tableau
def _splitBy(li, n=1):
    """
    Generate the split of the cards list.
    """
    return [li[i : i + n] for i in range(1, len(li), n)]


def _create_cards_message(card):
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
        + "</span></a></div></div>"
    ]
    return msg[0]


def shows_the_back_of_cards_and_propose_to_choose_five(list_of_cards):
    """
    Construct the cards board and generate the response heads tittle.
    """

    column = 6

    card_board = _splitBy(list_of_cards, column)

    final_card_deck = []
    for i in card_board:
        l = "".join(i)
        final_card_deck.append(
            f"<div class='row' height= '100%' text-align='center'>{l}</div>"
        )

    f = "".join(final_card_deck)

    return {
        "propose to choose": "<div class='col'><div class='cta-inner text-center rounded'>"
        + "<h4>"
        + " vois-ci votre réponse!"
        + "</h4>"
        + "<h4>"
        + "</h4>"
        + "<h6>"
        + "Afin de voir les mises en garde, survolez la carte avec la souris..."
        + "</h6>"
        + f
        + "</div>"
    }
