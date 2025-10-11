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
        self.strict = args.get('strict', default=False, type=bool)
        
        self.page = max(args.get('page', default=1, type=int),1)
        self.page_size = min(max(args.get('page_size', default=50, type=int),1),100)
        self.offset = (self.page - 1) * self.page_size
        self.wild_name = f'%{self.name}%' if self.name else None
        self._parameter_args = []
        self._base_query = """SELECT id, name, released, 
            COALESCE(platforms, "Unknown") AS platforms, 
            COALESCE(genres, "Unknown") AS genres
            FROM games WHERE 1=1
            """
        
    def build_query(self):
        self._parameter_args = []
        query = self._base_query

        if self.name:
            query = query + "AND name LIKE ?"
            self._parameter_args.append(self.name if self.strict else self.wild_name)

        #TODO: Add additional search fields

        query = query + " ORDER BY metacritic DESC LIMIT ? OFFSET ?"
        self._parameter_args.extend((self.page_size,self.offset))
        
        return query
    
    def parameter_args(self):
        return tuple(self._parameter_args)

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

    games = db.execute(search_args.build_query(), 
                       search_args.parameter_args()
                       ).fetchall()
    
    result = game_to_result(games)
    return result.to_json()