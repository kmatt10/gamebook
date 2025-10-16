from flask import Blueprint, request
from gamedb.db import get_db, game_to_result
from gamedb.QueryBuilder import GameQuery, SearchQuery

bp = Blueprint('games', __name__)

@bp.route('/games')
def games():
    game_query = GameQuery(request.args)
    db = get_db()
    games = db.execute(game_query.build_query(),
                       game_query.parameter_args()).fetchall()

    result = game_to_result(games)
    return result.to_json()

@bp.route('/games/<int:game_id>')
def game_by_id(game_id):
    db = get_db()
    game_query = GameQuery(request.args,game_id)
    game = db.execute(game_query.build_query(),
                      game_query.parameter_args()).fetchone()
    
    result = game_to_result(game)
    return result.to_json()

@bp.route('/search')
def search():
    search_args = SearchQuery(request.args)
    db = get_db()

    games = db.execute(search_args.build_query(), 
                       search_args.parameter_args()
                       ).fetchall()
    
    result = game_to_result(games)
    return result.to_json()