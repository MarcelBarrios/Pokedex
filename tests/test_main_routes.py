# pokedex_project/tests/test_main_routes.py
from flask import url_for
from models import Pokemon, User  # For checking data


def test_index_page(client):
    """Test the index page loads and shows some Pokemon."""
    # Ensure some Pokemon exist if your conftest doesn't seed them for every test.
    # Or rely on the app fixture's seeding.
    response = client.get(url_for('main.index'))
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')  # Decode first
    assert "Pokédex" in html_content  # Assert against the string
    # Assuming 'bulbasaur' was seeded by conftest's app fixture
    assert "Bulbasaur" in html_content  # Assert against the string


def test_pokemon_detail_page(client, app):  # Added app fixture for context
    """Test the Pokemon detail page loads."""
    # Assuming Pokemon with ID 1 (Bulbasaur) exists from conftest seeding
    with app.app_context():  # Need app context to generate URL if not in request context
        bulbasaur_url = url_for('main.pokemon_detail', pokemon_id=1)

    response = client.get(bulbasaur_url)
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')  # Decode first
    assert "Bulbasaur" in html_content  # Assert against the string
    assert "Base Stats" in html_content  # Assert against the string
    assert "Pokédex Entry" in html_content  # Assert against the string


def test_pokemon_detail_page_not_found(client, app):
    """Test getting a non-existent Pokemon returns 404."""
    with app.app_context():
        non_existent_url = url_for('main.pokemon_detail', pokemon_id=9999)
    response = client.get(non_existent_url)
    assert response.status_code == 404
    html_content = response.data.decode('utf-8')
    assert "Page Not Found" in html_content


def test_search_pokemon(client, app):
    """Test searching for a Pokemon."""
    # Assuming Bulbasaur (ID 1) exists
    response = client.get(url_for('main.index', search_term='Bulbasaur'))
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    assert "Bulbasaur" in html_content
    # Assuming Pikachu is not the only result or doesn't exist
    assert "Pikachu" not in html_content

    with app.app_context():
        search_url = url_for('main.index', search_term='NonExistentMon')
    response = client.get(search_url)
    assert response.status_code == 200
    html_content_non_existent = response.data.decode('utf-8')
    assert "No Pokémon found matching your search" in html_content_non_existent
    assert "Bulbasaur" not in html_content_non_existent


def test_profile_page_unauthenticated(client, app):
    """Test profile page redirects if not logged in."""
    with app.app_context():
        profile_url = url_for('main.profile')
        login_url = url_for('auth.login')

    response = client.get(profile_url)
    assert response.status_code == 302  # Redirect
    assert login_url in response.location  # Redirects to login


# Using the authenticated client
def test_profile_page_authenticated(auth_client, app):
    """Test profile page loads for an authenticated user."""
    with app.app_context():
        profile_url = url_for('main.profile')

    response = auth_client.get(profile_url)
    assert response.status_code == 200
    # Check for username in title/header
    html_content = response.data.decode('utf-8')  # Decode first
    assert "testuser's Pokedex" in html_content  # Assert against the string
    assert "My Caught Pokémon" in html_content  # Assert against the string

# Add more tests for catch/release functionality later
