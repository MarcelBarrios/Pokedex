import requests
from models import db, Pokemon  # Assuming your models.py and app setup

# Configuration for PokeAPI
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/"
# Fetching the first 151 Pokemon for this example, adjust as needed
POKEMON_LIMIT = 151  # Kanto Pokedex


def fetch_pokemon_data_from_api(pokemon_id_or_name):
    """Fetches detailed data for a single Pokemon from PokeAPI."""
    try:
        response = requests.get(
            f"{POKEAPI_BASE_URL}pokemon/{pokemon_id_or_name.lower() if isinstance(pokemon_id_or_name, str) else pokemon_id_or_name}")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()

        # Fetch species data for description
        species_url = data['species']['url']
        species_response = requests.get(species_url)
        species_response.raise_for_status()
        species_data = species_response.json()

        # Find an English flavor text entry
        description = "No description available."
        for entry in species_data.get('flavor_text_entries', []):
            if entry['language']['name'] == 'en':
                description = entry['flavor_text'].replace(
                    '\n', ' ').replace('\f', ' ')  # Clean up text
                break

        types = [t['type']['name'] for t in data['types']]

        return {
            'id': data['id'],
            'name': data['name'],
            'type1': types[0] if len(types) > 0 else 'unknown',
            'type2': types[1] if len(types) > 1 else None,
            'hp': next((stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'hp'), None),
            'attack': next((stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'attack'), None),
            'defense': next((stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'defense'), None),
            'sp_attack': next((stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'special-attack'), None),
            'sp_defense': next((stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'special-defense'), None),
            'speed': next((stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'speed'), None),
            'height': data.get('height'),  # In decimetres
            'weight': data.get('weight'),  # In hectograms
            'sprite_url': data['sprites']['front_default'] if data['sprites'] else None,
            'description': description
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {pokemon_id_or_name}: {e}")
        return None
    except KeyError as e:
        print(
            f"KeyError while parsing data for {pokemon_id_or_name}: {e} - Data: {data}")
        return None


# Pass app_context or app if needed for config/db
def seed_pokemon_data(app_context=None):
    """
    Seeds the database with Pokemon data from PokeAPI.
    Fetches a list of Pokemon names/IDs first, then details for each.
    """
    print(f"Attempting to seed up to {POKEMON_LIMIT} Pokémon.")

    # Check if Pokemon table already has data to avoid re-seeding unnecessarily
    # This requires an app context to query the database.
    # This logic might be better in the CLI command itself.
    # For now, we'll assume it's run on an empty or intentionally reset DB.

    count = 0
    for i in range(1, POKEMON_LIMIT + 1):
        # Check if Pokemon already exists
        existing_pokemon = Pokemon.query.get(i)
        if existing_pokemon:
            print(
                f"Pokemon ID {i} ({existing_pokemon.name}) already exists. Skipping.")
            continue

        print(f"Fetching data for Pokemon ID: {i}")
        data = fetch_pokemon_data_from_api(i)

        if data:
            pokemon = Pokemon(
                id=data['id'],
                name=data['name'],
                type1=data['type1'],
                type2=data['type2'],
                hp=data['hp'],
                attack=data['attack'],
                defense=data['defense'],
                sp_attack=data['sp_attack'],
                sp_defense=data['sp_defense'],
                speed=data['speed'],
                height=data['height'],
                weight=data['weight'],
                sprite_url=data['sprite_url'],
                description=data['description']
            )
            db.session.add(pokemon)
            count += 1
            if count % 20 == 0:  # Commit in batches
                print(f"Committing batch at Pokemon ID {i}...")
                db.session.commit()
        else:
            print(
                f"Could not fetch or parse data for Pokemon ID: {i}. Skipping.")

    db.session.commit()  # Final commit for any remaining entries
    print(f"Successfully seeded {count} new Pokémon.")
    return count

# Example of how to run this independently (requires app context)
# if __name__ == '__main__':
#     from app import create_app
#     app = create_app()
#     with app.app_context():
#         seed_pokemon_data(app)
