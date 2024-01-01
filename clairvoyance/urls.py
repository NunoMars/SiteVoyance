from django.urls import path, re_path

from django.views.decorators.csrf import csrf_exempt
from .views import (
    ClairvoyanceView,
    clairvoyante,
    user_history,
    CardDeckView,
    CardDetailView,
)


urlpatterns = [
    path("", ClairvoyanceView.as_view(), name="clairvoyance"),
    re_path("clairvoyante", csrf_exempt(clairvoyante), name="clairvoyante"),
    path("history", user_history, name="history"),
    path("card_deck", CardDeckView.as_view(), name="card_deck"),
    re_path(
        r"^card_detail/(?P<card>[0-9]+)/$", CardDetailView.as_view(), name="card_detail"
    ),
]
