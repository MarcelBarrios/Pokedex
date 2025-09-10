from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import or_

# Assuming User model for profile, caught_pokemon_association
from models import db, Pokemon, User
from forms import SearchForm  # We made this global, but can also instantiate here

main_bp = Blueprint('main', __name__)

POKEMON_PER_PAGE = 20  # For pagination


@main_bp.route('/')
@main_bp.route('/index')
def index():
    # --- ADD THIS DEBUG PRINT ---
    if current_user.is_authenticated:
        print(
            f"--- DEBUG: main.index - current_user: {current_user.username}, is_authenticated: {current_user.is_authenticated} ---")
    else:
        print(
            f"--- DEBUG: main.index - current_user: Anonymous, is_authenticated: {current_user.is_authenticated} ---")
    # --- END DEBUG PRINT ---

    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search_term', '').strip()
    query = Pokemon.query

    if search_term:
        # Search by name or ID (if numeric)
        if search_term.isdigit():
            query = query.filter(Pokemon.id == int(search_term))
        else:
            query = query.filter(Pokemon.name.ilike(f'%{search_term}%'))

    # Order by ID for consistent Pokedex order
    all_pokemon = query.order_by(Pokemon.id).paginate(
        page=page, per_page=POKEMON_PER_PAGE, error_out=False)

    return render_template('index.html', title='Pokedex Home', pokemons=all_pokemon, search_term=search_term)


@main_bp.route('/pokemon/<int:pokemon_id>')
def pokemon_detail(pokemon_id):
    pokemon = Pokemon.query.get_or_404(pokemon_id)
    is_caught = False
    if current_user.is_authenticated:
        # Check if the current user has caught this Pokemon
        # Accessing caught_pokemon directly on user object
        is_caught = current_user.caught_pokemon.filter(
            Pokemon.id == pokemon_id).first() is not None

    return render_template('pokemon_detail.html', title=pokemon.name.capitalize(), pokemon=pokemon, is_caught=is_caught)


@main_bp.route('/pokemon/<string:pokemon_name>')
def pokemon_detail_by_name(pokemon_name):
    pokemon = Pokemon.query.filter(db.func.lower(
        Pokemon.name) == pokemon_name.lower()).first_or_404()
    is_caught = False
    if current_user.is_authenticated:
        is_caught = current_user.caught_pokemon.filter(
            Pokemon.id == pokemon.id).first() is not None

    return render_template('pokemon_detail.html', title=pokemon.name.capitalize(), pokemon=pokemon, is_caught=is_caught)


# Could also be POST if form is more complex
@main_bp.route('/search', methods=['GET'])
def search_pokemon_route():
    search_term = request.args.get('search_term', '').strip()
    if not search_term:
        return redirect(url_for('main.index'))
    # Redirect to the index page with search_term as a query parameter
    # The index route will handle the actual filtering
    return redirect(url_for('main.index', search_term=search_term))


@main_bp.route('/profile')
@login_required
def profile():
    user = User.query.get_or_404(current_user.id)
    # caught_pokemon is a dynamic relationship, so we can paginate it
    page = request.args.get('page', 1, type=int)
    caught_list = user.caught_pokemon.order_by(Pokemon.id).paginate(
        page=page, per_page=POKEMON_PER_PAGE, error_out=False)
    return render_template('profile.html', title=f"{user.username}'s Profile", user=user, caught_list=caught_list)


@main_bp.route('/pokemon/<int:pokemon_id>/catch', methods=['POST'])
@login_required
def catch_pokemon(pokemon_id):
    pokemon = Pokemon.query.get_or_404(pokemon_id)
    if pokemon not in current_user.caught_pokemon:
        current_user.caught_pokemon.append(pokemon)
        db.session.commit()
        flash(f'You caught {pokemon.name.capitalize()}!', 'success')
    else:
        flash(
            f'You already have {pokemon.name.capitalize()} in your Pokedex.', 'info')
    return redirect(url_for('main.pokemon_detail', pokemon_id=pokemon_id))


@main_bp.route('/pokemon/<int:pokemon_id>/release', methods=['POST'])
@login_required
def release_pokemon(pokemon_id):
    pokemon = Pokemon.query.get_or_404(pokemon_id)
    if pokemon in current_user.caught_pokemon:
        current_user.caught_pokemon.remove(pokemon)
        db.session.commit()
        flash(f'You released {pokemon.name.capitalize()}.', 'success')
    else:
        flash(f'{pokemon.name.capitalize()} is not in your Pokedex.', 'info')
    return redirect(url_for('main.pokemon_detail', pokemon_id=pokemon_id))
