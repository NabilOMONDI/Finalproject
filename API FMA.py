# API creation for FMA database
# intialise the API in the workbook before we use the SQL data base to expose the data

from flask import Flask, request, jsonify
from collections import defaultdict
import pymysql.cursors


app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kaiser123',
    'database': 'FMA',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.route('/')
def home():
    return "Welcome to Nabil's Music API based on FMA dataset"


@app.route('/tracks',method=['GET'])
def search_tracks_function():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        include_details = int(request.args.get('include_details', 0))
        search = request.args.get('search', '')
        offset = (page - 1) * per_page

        try:
              db_conn= pymysql.connect(**db_config)
              with db_conn.cursor as cursor:
                    base_query =''' SELECT
                    t.track_id,
                    t.track_title,
                    a.artist_name,
                    g.genre_handle,
                    g.genre_id,
                    a.album_handle
                    FROM track t
                    inner join genre g on t.genre_id= g.genre_id
                    inner join album a on t.album_id = a.album_id'''
                    if search:
                        base_query += "WHERE track_title like %s"
                        search= f"%{search}%"

                    base_query += " ORDER BY track_id LIMIT %s OFFSET %s"
                    if search:
                          cursor.execute(base_query,(search, per_page,offset))
                    else:
                          cursor.execute(base_query,(per_page,offset))
                    tracks= cursor.fetchall()

                    if not tracks:
                          return jsonify({"message":"no track found"}),404
                db_conn.close()
                return jsonify(tracks)
        except pymysql.MySQLError as e:
            return jsonify({'error':str(e)}),500