from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# Association Table for User <-> Pokemon (Caught Pokemon)
caught_pokemon_association = db.Table('caught_pokemon',
                                      db.Column('user_id', db.Integer, db.ForeignKey(
                                          'users.id'), primary_key=True),
                                      db.Column('pokemon_id', db.Integer, db.ForeignKey(
                                          'pokemon.id'), primary_key=True)
                                      )


class User(UserMixin, db.Model):
    """User model for authentication and tracking caught Pokemon."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationship: A user can have many "caught" Pokemon
    caught_pokemon = db.relationship(
        'Pokemon',
        secondary=caught_pokemon_association,
        back_populates='caught_by_users',
        lazy='dynamic'  # Use 'dynamic' for queries like .count() or pagination
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Pokemon(db.Model):
    """Pokemon model to store Pokemon data."""

    __tablename__ = 'pokemon'

    # Pokemon's national Pokedex ID
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type1 = db.Column(db.String(50), nullable=False)
    type2 = db.Column(db.String(50), nullable=True)
    hp = db.Column(db.Integer, nullable=True)
    attack = db.Column(db.Integer, nullable=True)
    defense = db.Column(db.Integer, nullable=True)
    sp_attack = db.Column(db.Integer, nullable=True)
    sp_defense = db.Column(db.Integer, nullable=True)
    speed = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)  # In decimetres
    weight = db.Column(db.Integer, nullable=True)  # In hectograms
    # URL for the default sprite
    sprite_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Relationship: A Pokemon can be "caught" by many users
    caught_by_users = db.relationship(
        'User',
        secondary=caught_pokemon_association,
        back_populates='caught_pokemon'
    )

    def __repr__(self):
        return f"<Pokemon #{self.id}: {self.name.capitalize()}>"

    @classmethod
    def get_by_id_or_name(cls, identifier):
        """Gets a Pokemon by its ID or name."""
        if isinstance(identifier, int) or identifier.isdigit():
            return cls.query.get(int(identifier))
        return cls.query.filter(db.func.lower(cls.name) == identifier.lower()).first()


def connect_db(app):
    """Connect to the database."""
    db.app = app
    db.init_app(app)
