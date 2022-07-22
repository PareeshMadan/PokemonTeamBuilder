from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), default="")
    ptype = db.Column(db.String(500), default="")
    sprite = db.Column(db.String, default="")

    def __repr__(self):
        return '<Pokemon %r>' % self.id

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
        return render_template("index.html", Pokemons=Pokemons)

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
    app.run(debug=True)