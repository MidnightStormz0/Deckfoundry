import requests

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from cards.models import Card

class Command(BaseCommand):
    help = "Import Scryfall bulk card data into the local database."

    def handle(self, *args, **options):
        self.stdout.write("Fetching Scryfall bulk data...")
        
        bulk_response = requests.get("https://api.scryfall.com/bulk-data", timeout=20)

        bulk_response.raise_for_status()

        bulk_data = bulk_response.json()["data"]
        self.stdout.write("Available Scryfall bulk data types:")
        for item in bulk_data:
            self.stdout.write(f" - name: {item.get('name')} | type: {item.get('type')} | updated_at: {item.get('updated_at')}")

        bulk_file = None

        for item in bulk_data:
            item_type = item.get("type")
            item_name = item.get("name")
            
            self.stdout.write(f" - name: {item_name} | type: {item_type} | updated_at: {item.get('updated_at')}")
            
            if item["type"] == "default_cards":
                bulk_file = item
                break
            
        if bulk_file is None:
            self.stdout.write("No default_cards data found in Scryfall bulk data.")
            return
            
        download_uri = bulk_file["download_uri"]
        self.stdout.write(f"Downloading card data from {download_uri}...")  
        cards_response = requests.get(download_uri, timeout=120)
        cards_response.raise_for_status()

        scryfall_cards = cards_response.json()

        self.stdout.write(f"Importing {len(scryfall_cards)} cards into the database...")

        created_count = 0
        updated_count = 0

        for card_data in scryfall_cards:
            image_url = ""

            if "image_uris" in card_data:
                image_url = card_data["image_uris"].get("normal", "")
                
            legalities = card_data.get("legalities", {})
            commander_legal = legalities.get("commander", "not_legal") == "legal"

            card, created = Card.objects.update_or_create(
                scryfall_id=card_data["id"],
                defaults={
                    "oracle_id": card_data.get("oracle_id"),
                    "name": card_data.get("name", ""),
                    "mana_cost": card_data.get("mana_cost", ""),
                    "cmc": card_data.get("cmc"),
                    "type_line": card_data.get("type_line", ""),
                    "oracle_text": card_data.get("oracle_text", ""),
                    "colors": card_data.get("colors", []),
                    "color_identity": card_data.get("color_identity", []),
                    "legalities": legalities,
                    "commander_legal": commander_legal,
                    "image_url": image_url,
                    "scryfall_uri": card_data.get("scryfall_uri", ""),
                    "released_at": parse_date(card_data["released_at"]) if card_data.get("released_at") else None,
                    "set_code": card_data.get("set_code", ""),
                    "rarity": card_data.get("rarity", ""),
                    "prices": card_data.get("prices", {}),
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(f"Import completed. Created: {created_count}, Updated: {updated_count}")