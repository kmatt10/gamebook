from flask import (
    Blueprint, request
)
from gamedb.db import get_db, game_to_result, GameEntry, Result

class SearchQuery:
    def __init__(self, args):
        self.name = args.get('name', default=None, type=str)
        self.platform = args.get('platform', default=None, type=str)
        self.genre = args.get('genre', default=None, type=str)
        self.released = args.get('released', default=None, type=int)
        self.released_after = args.get('released_after', default=None, type=int)
        self.released_before = args.get('released_before', default=None, type=int)
        self.metacritic_min = args.get('metacritic_min', default=None, type=int)
        self.metacritic_max = args.get('metacritic_max', default=None, type=int)
        self.page = max(args.get('page', default=1, type=int),1)
        self.page_size = min(max(args.get('page_size', default=50, type=int),1),100)
        self.offset = (self.page - 1) * self.page_size

bp = Blueprint('games', __name__)

@bp.route('/games')
def games():
    search_args = SearchQuery(request.args)
    db = get_db()
    query = f"""
    SELECT id, name, released, 
        COALESCE(platforms, "Unknown") AS platforms, 
        COALESCE(genres, "Unknown") AS genres
    FROM games
    ORDER BY metacritic DESC
    LIMIT ? OFFSET ?
    """
    games = db.execute(query,
                       (search_args.page_size, 
                        search_args.offset)).fetchall()

    result = game_to_result(games)
    return result.to_json()

@bp.route('/search')
def search():
    search_args = SearchQuery(request.args)
    db = get_db()
    query = f"""
    SELECT id, name, released, 
        COALESCE(platforms, "Unknown") AS platforms, 
        COALESCE(genres, "Unknown") AS genres
    FROM games
    WHERE name LIKE ?
    ORDER BY metacritic DESC
    LIMIT ? OFFSET ?
    """

    games = db.execute(query, 
                       (search_args.name, 
                        search_args.page_size, 
                        search_args.offset)
                       ).fetchall()
    
    result = game_to_result(games)
    return result.to_json()