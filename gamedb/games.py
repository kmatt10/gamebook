from flask import (
    Blueprint, request
)
from gamedb.db import get_db, game_to_result, GameEntry, Result

class QueryBuilder:
    def __init__(self, args):
        self.page = max(args.get('page', default=1, type=int),1)
        self.page_size = min(max(args.get('page_size', default=50, type=int),1),100)
        self.offset = (self.page - 1) * self.page_size
        self._parameter_args = []
        self._base_query = """SELECT id, name, released, 
            COALESCE(platforms, "Unknown") AS platforms, 
            COALESCE(genres, "Unknown") AS genres
            FROM games WHERE 1=1"""

    def build_query(self) -> str:
        raise NotImplementedError

    def parameter_args(self) -> tuple:
        return tuple(self._parameter_args)

class GameQuery(QueryBuilder):
    def __init__(self, args):
        super().__init__(args)
        self.id = args.get('id', default = None, type=int)

    def build_query(self) -> str:
        self._parameter_args = []
        query = self._base_query

        #TODO: Add logic for selecting by id

        query = query + " ORDER BY metacritic DESC LIMIT ? OFFSET ?"
        self._parameter_args.extend((self.page_size,self.offset))

        return query

    

class SearchQuery(QueryBuilder):
    def __init__(self, args):
        super().__init__(args)
        self.name = args.get('name', default=None, type=str)
        self.platform = args.get('platform', default=None, type=str)
        self.genre = args.get('genre', default=None, type=str)
        self.released = args.get('released', default=None, type=int)
        self.released_after = args.get('released_after', default=None, type=int)
        self.released_before = args.get('released_before', default=None, type=int)
        self.metacritic_min = args.get('metacritic_min', default=None, type=int)
        self.metacritic_max = args.get('metacritic_max', default=None, type=int)
        self.strict = args.get('strict', default=False, type=bool)
        
        self.wild_name = f'%{self.name}%' if self.name else None
        
    def build_query(self):
        self._parameter_args = []
        query = self._base_query

        if self.name:
            query = query + " AND name LIKE ?"
            self._parameter_args.append(self.name if self.strict else self.wild_name)

        #TODO: Add additional search fields

        if len(self._parameter_args) == 0:
            query = query + " AND 1=0"

        query = query + " ORDER BY metacritic DESC LIMIT ? OFFSET ?"
        self._parameter_args.extend((self.page_size,self.offset))
        
        return query

bp = Blueprint('games', __name__)

#TODO: Add handling of a direct game id reference
@bp.route('/games')
def games():
    game_query = GameQuery(request.args)
    db = get_db()
    games = db.execute(game_query.build_query(),
                       game_query.parameter_args()).fetchall()

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