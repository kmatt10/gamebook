from flask import (
    Blueprint, request
)
from gamedb.db import get_db, game_to_result, GameEntry, Result

bp = Blueprint('games', __name__)

@bp.route('/games')
def games():
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=50, type=int)
    db = get_db()
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    offset = (page - 1) * page_size
    query = f"""
    SELECT id, name, released, 
        COALESCE(platforms, "Unknown") AS platforms, 
        COALESCE(genres, "Unknown") AS genres
    FROM games
    LIMIT ? OFFSET ?
    """
    games = db.execute(query, (page_size, offset)).fetchall()

    result = game_to_result(games)
    return result.to_json()