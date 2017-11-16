from flask import Flask
import os
import urlparse
import psycopg2

# Flask app
app = Flask(__name__)

# PostgreSQL connector
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cursor = conn.cursor()

query = "SELECT history.player_id, \
            (SELECT h.player_id, COUNT(*) FROM history AS h WHERE h.game_id = history.game_id AND h.player_id IS NOT history.player_id) AS num_games \
        FROM history"

@app.route("/")
def index():
    cursor.execute("SELECT * FROM test")
    result = cursor.fetchall()
    return str(result)

if __name__ == "__main__":
    app.run()