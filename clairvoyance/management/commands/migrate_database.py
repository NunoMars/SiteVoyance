from django.core.management.base import BaseCommand
from clairvoyance.models import MajorArcana
import json


class Command(BaseCommand):
    help = "Peuplate database with a json file"

    def handle(self, *args, **options):
        with open("database_dumps/MajorArcana.json") as f:
            data = json.load(f)
            for i in data:
                MajorArcana.objects.create(
                    card_name=i["card_name"],
                    card_signification_gen=i["card_signification_gen"],
                    card_signification_warnings=i["card_signification_warnings"],
                    card_signification_love=i["card_signification_love"],
                    card_signification_work=i["card_signification_work"],
                    card_image=i["card_image"],
                    card_polarity=i["card_polarity"],
                )
                print(f'{i["card_name"]}" Cree en base de données!')

        self.stdout.write(self.style.SUCCESS("Successfully !!!"))
