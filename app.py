from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import random
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

class Type(Enum):
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    ELECTRIC = "electric"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DARK = "dark"
    DRAGON = "dragon"
    STEEL = "steel"
    FAIRY = "fairy"


weaknessMap = { 
    Type.BUG: [Type.FIRE, Type.FLYING, Type.ROCK],
    Type.DARK: [Type.BUG, Type.FAIRY, Type.FIGHTING],
    Type.DRAGON: [Type.STEEL, Type.FAIRY],
    Type.ELECTRIC: [Type.GROUND],
    Type.FIGHTING: [Type.FAIRY, Type.FLYING, Type.PSYCHIC],
    Type.FAIRY: [Type.POISON, Type.STEEL],
    Type.FIRE: [Type.GROUND, Type.ROCK, Type.WATER],
    Type.FLYING: [Type.ELECTRIC, Type.ICE, Type.ROCK],
    Type.GHOST: [Type.DARK, Type.GHOST],
    Type.GRASS: [Type.BUG, Type.FIRE, Type.FLYING, Type.ICE, Type.POISON],
    Type.GROUND: [Type.GRASS, Type.ICE, Type.WATER],
    Type.ICE: [Type.FIGHTING, Type.FIRE, Type.ROCK, Type.STEEL],
    Type.NORMAL: [Type.FIGHTING],
    Type.POISON: [Type.GROUND, Type.PSYCHIC],
    Type.PSYCHIC: [Type.BUG, Type.DARK, Type.GHOST],
    Type.ROCK: [Type.FIGHTING, Type.GRASS, Type.GROUND, Type.STEEL, Type.WATER],
    Type.STEEL: [Type.FIGHTING, Type.FIRE, Type.GROUND],
    Type.WATER: [Type.ELECTRIC, Type.GRASS]
}

resistanceMap = { 
    Type.BUG: [Type.FIGHTING, Type.GROUND, Type.GRASS],
    Type.DARK: [Type.GHOST, Type.PSYCHIC, Type.DARK],
    Type.DRAGON: [Type.FIRE, Type.WATER, Type.GRASS, Type.ELECTRIC],
    Type.ELECTRIC: [Type.FLYING, Type.STEEL, Type.ELECTRIC],
    Type.FIGHTING: [Type.ROCK, Type.BUG, Type.DARK],
    Type.FAIRY: [Type.FIGHTING, Type.BUG, Type.DRAGON, Type.DARK],
    Type.FIRE: [Type.BUG, Type.STEEL, Type.FIRE, Type.GRASS, Type.ICE],
    Type.FLYING: [Type.FIGHTING, Type.GROUND, Type.BUG, Type.GRASS],
    Type.GHOST: [Type.NORMAL, Type.FIGHTING, Type.POISON, Type.BUG],
    Type.GRASS: [Type.GROUND, Type.WATER, Type.GRASS, Type.ELECTRIC],
    Type.GROUND: [Type.POISON, Type.ROCK, Type.ELECTRIC],
    Type.ICE: [Type.ICE],
    Type.NORMAL: [Type.GHOST],
    Type.POISON: [Type.FIGHTING, Type.POISON, Type.GRASS, Type.FAIRY],
    Type.PSYCHIC: [Type.FIGHTING, Type.PSYCHIC],
    Type.ROCK: [Type.NORMAL, Type.FLYING, Type.POISON, Type.FIRE],
    Type.STEEL: [Type.NORMAL, Type.FLYING, Type.POISON, Type.ROCK, Type.BUG, Type.STEEL, Type.GRASS, Type.PSYCHIC, Type.ICE, Type.DRAGON, Type.FAIRY],
    Type.WATER: [Type.STEEL, Type.FIRE, Type.WATER, Type.ICE]
}

pokemonSuggestions = {
    Type.BUG: ["charizard", "aerodactyl", "togekiss"],
    Type.DARK: ["scizor", "azumarill", "lucario"],
    Type.DRAGON: ["aggron", "sylveon", "clefable"],
    Type.ELECTRIC: ["hippowdown", "flygon", "garchomp"],
    Type.FIGHTING: ["sylveon", "staraptor", "espeon"],
    Type.FAIRY: ["venusaur", "metagross", "scizor"],
    Type.FIRE: ["garchomp", "tyranitar", "blastoise"],
    Type.FLYING: ["ampharos", "aerodactyl", "aggron"],
    Type.GHOST: ["absol", "bisharp", "tyranitar"],
    Type.GRASS: ["scizor", "charizard", "staraptor", "toxicroak"],
    Type.GROUND: ["sceptile", "blastoise", "shaymin"],
    Type.ICE: ["blaziken", "lucario", "greninja"],
    Type.NORMAL: ["aggron", "lucario", "skarmory"],
    Type.POISON: ["hippowdown", "aggron", "gengar"],
    Type.PSYCHIC: ["heatran", "empoleon", "jirachi"],
    Type.ROCK: ["lucario", "venusaur", "rhyperior"],
    Type.STEEL: ["lucario", "ampharos", "infernape"],
    Type.WATER: ["ampharos", "venusaur", "blastoise"]
}
class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), default="")
    ptype = db.Column(db.String(500), default="")
    sprite = db.Column(db.String, default="")

    def __repr__(self):
        return '<Pokemon %r>' % self.id

with app.app_context():
    db.create_all()

def create_pokemon_from_name_or_num(pokemon_name_or_num):
    response = requests.get('https://pokeapi.co/api/v2/pokemon/' + pokemon_name_or_num)
    sprite_url = response.json()['sprites']['front_default']
    ptype = response.json()['types'][0]['type']['name']
    
    if len(response.json()['types']) > 1:
        ptype = ptype + ", " + response.json()['types'][1]['type']['name']

    pokemon_name = response.json()['forms'][0]['name']

    return Pokemon(name=pokemon_name, ptype=ptype, sprite=sprite_url)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        pokemon_name = request.form['name']
        new_Pokemon = create_pokemon_from_name_or_num(request.form['name'])
    
        try:
            db.session.add(new_Pokemon)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your Pokemon'

    else:
        Pokemons = Pokemon.query.order_by(Pokemon.name).all()
        weaknessCount = {
            Type.NORMAL: 0,
            Type.FIRE:0,
            Type.WATER:0,
            Type.GRASS:0,
            Type.ELECTRIC:0,
            Type.ICE:0,
            Type.FIGHTING:0,
            Type.POISON:0,
            Type.GROUND:0,
            Type.FLYING:0,
            Type.PSYCHIC:0,
            Type.BUG:0,
            Type.ROCK:0,
            Type.GHOST:0,
            Type.DARK:0,
            Type.DRAGON:0,
            Type.STEEL:0,
            Type.FAIRY:0
        }

        for pman in Pokemons:
            weaknesses = []

            if ", " in pman.ptype:
                primaryType = pman.ptype[0:pman.ptype.index(", ")]
                secondaryType = pman.ptype[pman.ptype.index(", ") + 2:]
                firstWeaknesses = weaknessMap[Type(primaryType)]
                firstResistances = resistanceMap[Type(primaryType)]
                secondWeaknesses = weaknessMap[Type(secondaryType)]
                secondResistances = resistanceMap[Type(secondaryType)]

                totalWeaknesses = set(firstWeaknesses + secondWeaknesses)
                totalResistances = set(firstResistances + secondResistances)
                weaknesses = list(totalWeaknesses - totalResistances)
            else:
                weaknesses = weaknessMap[Type(pman.ptype)]

            for weakness in weaknesses:
                weaknessCount[weakness] = weaknessCount[weakness] + 1
        
        typesStrongAgainstTeam = []

        for weakness in weaknessCount:
            if weaknessCount[weakness] >= 3:
                typesStrongAgainstTeam.append(weakness.name)

        suggestedPokemonMap = {}

        for typeStrongAgainstTeam in typesStrongAgainstTeam:
            suggestedPokemonMap[typeStrongAgainstTeam] = pokemonSuggestions[Type(typeStrongAgainstTeam.lower())]

        return render_template("index.html", Pokemons=Pokemons, typesStrongAgainstTeam=typesStrongAgainstTeam, suggestedPokemonMap=suggestedPokemonMap)

@app.route('/delete/<int:id>')
def delete(id):
    Pokemon_to_delete = Pokemon.query.get_or_404(id)

    try:
        db.session.delete(Pokemon_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that Pokemon'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    Pokemon = Pokemon.query.get_or_404(id)
    if request.method == "POST":
        Pokemon.content = request.form['name']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your Pokemon'
    else:
        return render_template('update.html', Pokemon=Pokemon)

def delete_all_pokemon():
    Pokemons = Pokemon.query.order_by(Pokemon.name).all()

    try:
        for pokemon_to_delete in Pokemons:
            db.session.delete(pokemon_to_delete)
            db.session.commit()
        
        return False
    except:
        return True

@app.route('/randomize_team', methods=['GET'])
def randomize_team():
    if request.method == "GET":

        err = delete_all_pokemon()

        if err:
            return 'There was a problem deleting that Pokemon'

        random_pokemon_ids = [random.randint(1, 898) for _ in range(6)]
        for random_pokemon_id in random_pokemon_ids:
            new_Pokemon = create_pokemon_from_name_or_num(str(random_pokemon_id))
            try:
                db.session.add(new_Pokemon)
                db.session.commit()
            except:
                return 'There was an issue adding your Pokemon'
        return redirect('/')

    else:
        Pokemons = Pokemon.query.order_by(Pokemon.name).all()
        return render_template("index.html", Pokemons=Pokemons)

@app.route('/delete_team', methods=['POST'])
def delete_pokemon():
    if request.method == "POST":

        err = delete_all_pokemon()

        if err:
            return 'There was a problem deleting your Pokemon'

        return redirect('/')

    else:
        Pokemons = Pokemon.query.order_by(Pokemon.name).all()
        return render_template("index.html", Pokemons=Pokemons)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080,debug=True)