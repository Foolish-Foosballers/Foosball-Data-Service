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

def assertDatabase():
    """
    Confirm that the correct tables all exist and create them if they don't.
    """
    
    # Create side type to represent sides of table (left and right)
    cursor.execute("CREATE TYPE IF NOT EXISTS side AS ENUM ('left', 'right');")

    cursor.execute("CREATE TABLE IF NOT EXISTS players (\
                        Id int PRIMARY KEY,\
                        FirstName text,\
                        LastName text,\
                        Username text,\
                        Email text,\
                        SignupDate timestamp with time zone,\
                        TotalTimePlayed int,\
                        GameWins int,\
                        TotalGamesPlayed int,\
                        SeriesWins int,\
                        TotalPoints int,\
                        Shutouts int\
                   );")

    cursor.execute("CREATE TABLE IF NOT EXISTS games (\
                        Id int PRIMARY KEY,\
                        EndTime timestamp with time zone,\
                        Single bool,\
                        LeftScore int,\
                        RightScore int,\
                        WinMargin int,\
                        Winner side\
                   );")

    cursor.execute("CREATE TABLE IF NOT EXISTS series (\
                        Id int PRIMARY KEY,\
                        NumGames int,\
                        LeftWins int,\
                        RightWins int\
                   );")

    cursor.execute("CREATE TABLE IF NOT EXISTS history (\
                        GameId int REFERENCES games,\
                        PlayerId int REFERENCES players,\
                        Side side,\
                        SeriesId int REFERENCES series,\
                        PRIMARY KEY (GameId, PlayerId)\
                   );")
    
    cursor.execute("INSERT INTO players VALUES (\
                        (212570174, 'Sara', 'Stiklickas', 'sarastik', 'sara.stiklickas@ge.com', current_timestamp, 0, 0, 0, 0, 0, 0);")

@app.route("/")
def index():
    cursor.execute("SELECT * FROM players")
    result = cursor.fetchall()
    return "Results:\n" + str(result)

if __name__ == "__main__":
    assertDatabase()
    app.run()