import sqlite3
from datetime import datetime
import pandas as pd

import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    csv_file_path = './data/game_info.csv'
    table_name = 'games'

    with current_app.open_resource(csv_file_path) as csv:
        df = pd.read_csv(csv)
        df.to_sql(table_name,db,if_exists='replace',index=False)

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

class GameEntry:
    def __init__(self, id: int, name: str, released: int, platforms: str, genres: str):
        self.id = id
        self.name = name
        self.released = released
        self.platforms = str.split(platforms or "", "||")
        self.genres = str.split(genres or "", "||")
    
    def to_json(self):
        return self.__dict__

class Result():
    def __init__(self):
        self.has_games = False
        self.game_entries = []

    def add_game(self, game_entry: GameEntry):
        self.has_games = True
        self.game_entries.append(game_entry.to_json())

    def to_json(self):
        return self.__dict__

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def game_to_result(sqlite_rows):
    result = Result()
    for row in sqlite_rows:
        game_entry = GameEntry(
            id=row['id'],
            name=row['name'],
            released=row['released'],
            platforms=row['platforms'],
            genres=row['genres']
        )
        result.add_game(game_entry)
    return result