from django.urls import path, re_path

from .views import (
    ClairvoyanceView,
    user_history,
    CardDeckView,
    CardDetailView,
)


urlpatterns = [
    path("", ClairvoyanceView.as_view(), name="clairvoyance"),
    path("history", user_history, name="history"),
    path("card_deck", CardDeckView.as_view(), name="card_deck"),
    re_path(
        r"^card_detail/(?P<card>[0-9]+)/$", CardDetailView.as_view(), name="card_detail"
    ),
]
