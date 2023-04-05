import requests
import json

def get_land_cards_mtg_arena():
    scryfall_api_url = "https://api.scryfall.com/cards/search"
    land_cards = []

    # Fetch the first page of results
    params = {
        "q": "type:land legal:arena",
        "unique": "cards",
        "order": "name",
        "dir": "asc"
    }
    response = requests.get(scryfall_api_url, params=params)
    data = response.json()

    # Extract card names from the first page
    for card in data["data"]:
        land_cards.append(card["name"])

    # Fetch and process additional pages if available
    while data["has_more"]:
        next_page_url = data["next_page"]
        response = requests.get(next_page_url)
        data = response.json()

        for card in data["data"]:
            land_cards.append(card["name"])

    return land_cards

def save_land_cards_to_file(land_cards, filename="land_cards.txt"):
    with open(filename, "w") as file:
        for card in land_cards:
            file.write(f"{card}\n")

if __name__ == "__main__":
    land_cards = get_land_cards_mtg_arena()
    save_land_cards_to_file(land_cards)
    print("Land cards legal in MTG Arena have been saved to land_cards.txt")
