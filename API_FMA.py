# API creation for FMA database
# intialise the API in the workbook before we use the SQL data base to expose the data
# flask --app API_FMA run --port 8080 --debug

from flask import Flask, request, jsonify
from collections import defaultdict
import pymysql.cursors
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kaiser123',
    'database': 'FMA',
    'cursorclass': pymysql.cursors.DictCursor
}

swaggerui_blueprint = get_swaggerui_blueprint(
    base_url='/docs',
    api_url='/static/FMA_API.yaml',
)

app.register_blueprint(swaggerui_blueprint)

@app.route('/')
def home():
    return "Welcome to Nabil's Music API based on FMA dataset"



# intial endpoint tracks with a search function on track id 
@app.route('/track', methods=['GET'])
def search_tracks_function():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search = request.args.get('search', '')
    offset = (page - 1) * per_page

    try:
        db_conn = pymysql.connect(**db_config)
        with db_conn.cursor() as cursor:
            base_query = '''
            SELECT
                t.track_id,
                t.track_title,
                a.artist_name,
                g.genre_handle,
                g.genre_id,
                a.album_handle
            FROM track t
            INNER JOIN genre g ON t.genre_id = g.genre_id
            INNER JOIN album a ON t.album_id = a.album_id
            '''
            if search:
                base_query += "WHERE t.track_title LIKE %s "
                search = f"%{search}%"
            base_query += "ORDER BY t.track_id LIMIT %s OFFSET %s"

            if search:
                cursor.execute(base_query, (search, per_page, offset))
            else:
                cursor.execute(base_query, (per_page, offset))

            tracks = cursor.fetchall()

            if not tracks:
                return jsonify({"message": "no track found"}), 404

        db_conn.close()
        return jsonify(tracks)

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500



# second endpoint  features, with include details 
@app.route('/feature', methods=['GET'])
def search_features_function():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    include_details = bool(int(request.args.get('include_details', 0)))
    offset = (page - 1) * per_page

    try:
        db_conn = pymysql.connect(**db_config)
        with db_conn.cursor() as cursor:
            base_query = '''
            SELECT
                t.track_id,
                t.track_title,
                a.artist_name,
                g.genre_handle,
                g.genre_id
            '''
            if include_details:
                base_query += ''',
                e.acousticness,
                e.danceability,
                e.energy,
                e.instrumentalness,
                e.liveness,
                e.speechiness,
                e.tempo,
                e.valence
                '''
            else:
                base_query += ''',
                e.acousticness,
                e.danceability
                '''
                
            base_query += '''
            FROM track t
            INNER JOIN echonest e ON t.track_id = e.track_id
            INNER JOIN genre g ON t.genre_id = g.genre_id
            INNER JOIN album a ON t.album_id = a.album_id
            ORDER BY t.track_id LIMIT %s OFFSET %s
            '''

            cursor.execute(base_query, (per_page, offset))
            features = cursor.fetchall()

            if not features:
                return jsonify({"message": "no features found"}), 404

        db_conn.close()
        return jsonify(features)

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/genre', methods=['GET'])
def genre_function():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page
    search = request.args.get('search', '')

    try:
        db_conn = pymysql.connect(**db_config)
        with db_conn.cursor() as cursor:
            base_query = '''
            SELECT *
            FROM genre_feature
            '''
            if search:
                base_query += 'WHERE genre_handle LIKE %s '
                search = f"%{search}%"
            
            base_query += "ORDER BY genre_handle LIMIT %s OFFSET %s"
            if search:
                cursor.execute(base_query, (search, per_page, offset))
            else:
                cursor.execute(base_query, (per_page, offset))
            
            genres = cursor.fetchall()

            if not genres:
                return jsonify({"message": "no genres found"}), 404

        db_conn.close()
        return jsonify(genres)
    
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500


# Endpoint to get a specific track by ID
@app.route('/track/<int:track_id>', methods=['GET'])
def get_track(track_id):
    try:
        db_conn = pymysql.connect(**db_config)
        with db_conn.cursor() as cursor:
            query = '''
            SELECT
                t.track_id,
                t.track_title,
                a.artist_name,
                g.genre_handle,
                g.genre_id,
                a.album_handle
            FROM track t
            INNER JOIN genre g ON t.genre_id = g.genre_id
            INNER JOIN album a ON t.album_id = a.album_id
            WHERE t.track_id = %s
            '''
            cursor.execute(query, (track_id,))
            track = cursor.fetchone()

            if not track:
                return jsonify({"message": "Track not found"}), 404

        db_conn.close()
        return jsonify(track)

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get a specific genre by ID
@app.route('/genre/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    try:
        db_conn = pymysql.connect(**db_config)
        with db_conn.cursor() as cursor:
            query = '''
            SELECT *
            FROM genre
            WHERE genre_id = %s
            '''
            cursor.execute(query, (genre_id,))
            genre = cursor.fetchone()

            if not genre:
                return jsonify({"message": "Genre not found"}), 404

        db_conn.close()
        return jsonify(genre)

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get features of a specific track by ID
@app.route('/feature/<int:track_id>', methods=['GET'])
def get_feature(track_id):
    try:
        db_conn = pymysql.connect(**db_config)
        with db_conn.cursor() as cursor:
            query = '''
            SELECT
                t.track_id,
                t.track_title,
                a.artist_name,
                g.genre_handle,
                g.genre_id,
                e.acousticness,
                e.danceability,
                e.energy,
                e.instrumentalness,
                e.liveness,
                e.speechiness,
                e.tempo,
                e.valence
            FROM track t
            INNER JOIN echonest e ON t.track_id = e.track_id
            INNER JOIN genre g ON t.genre_id = g.genre_id
            INNER JOIN album a ON t.album_id = a.album_id
            WHERE t.track_id = %s
            '''
            cursor.execute(query, (track_id,))
            feature = cursor.fetchone()

            if not feature:
                return jsonify({"message": "Feature not found"}), 404

        db_conn.close()
        return jsonify(feature)

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
