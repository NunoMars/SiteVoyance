import contextlib
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from clairvoyance.logic import clairvoyant
from .models import MajorArcana
from accounts.models import CustomUser, History, DailySortedCards
from django.views.generic.base import TemplateView
from django.views import View


class IndexView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["first_title"] = "Benvenu/e dans mon monde"
        context["second_title"] = "TAROT T"
        return context


class ClairvoyanceView(View):
    template_name = "clairvoyance/clairvoyance.html"

    def get(self, request, *args, **kwargs):
        args = {"page_title": "Tarot"}
        return render(request, self.template_name, args)


class CardDeckView(View):
    template_name = "clairvoyance/card_deck.html"

    def get(self, request, *args, **kwargs):
        cards = MajorArcana.objects.all()
        lang = request.LANGUAGE_CODE

        context = {
            "lang": lang,
            "cards": cards,
        }
        return render(request, self.template_name, context)


class CardDetailView(View):
    template_name = "clairvoyance/card_detail.html"
    lang_fields = {
        "fr": "fr",
        "pt": "pt",
        "en": "en",
        "es": "es",
    }

    def get_queryset(self):
        lang = self.request.LANGUAGE_CODE

        field_suffix = self.lang_fields.get(lang, "fr")
        return MajorArcana.objects.all().values(
            f"card_name_{field_suffix}",
            f"card_signification_gen_{field_suffix}",
            f"card_signification_love_{field_suffix}",
            f"card_signification_work_{field_suffix}",
            f"card_signification_warnings_{field_suffix}",
            "card_image",
        )

    def get(self, request, card):
        queryset = self.get_queryset()
        if card_data := queryset.filter(id=card).first():
            return render(request, self.template_name, card_data)
        else:
            return render(request, "clairvoyance/card_not_found.html")


def clairvoyante(request):
    if not request.session.session_key:
        request.session.create()  # Créer une nouvelle session si nécessaire

    # Récupérer la clé de session
    session_key = request.session.session_key
    if request.method != "POST":
        return
    with contextlib.suppress(ValueError):
        input_value = request.POST.get("messageInput")
        result = clairvoyant(input_value, session_key)
        return JsonResponse(result)


@login_required
def user_history(request):
    user = request.user
    user_history = History.objects.filter(user=user)
    daily_user_card = DailySortedCards.objects.filter(user=user)

    context = {
        "user": user,
        "user_history": user_history,
        "daily_user_card": daily_user_card,
    }
    return render(request, "clairvoyance/history.html", context)


def contacts(request):
    return render(request, "clairvoyance/contacts.html")
