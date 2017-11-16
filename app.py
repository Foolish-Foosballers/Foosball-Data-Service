from flask import Flask
import psycopg2

# Flask app
app = Flask(__name__)


query = "SELECT history.player_id, \
            (SELECT h.player_id, COUNT(*) FROM history AS h WHERE h.game_id = history.game_id AND h.player_id IS NOT history.player_id) AS num_games \
        FROM history"

@app.route("/")
def index():
    return "Hello Data Service"

if __name__ == "__main__":
    app.run()