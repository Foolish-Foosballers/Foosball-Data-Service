# Foosball-Data-Service

Microservice that will interface with our PostgreSQL database containing information about players and games.

## Database Schema

Our schema consists of four tables: `players`, `games`, `series`, and a relational table called `history`. Their contents are outlined below.

The `players` table contains both player information and player stats, and it has a primary key called `Id`. 
```
players: { *Id:               int,
            FirstName:        string,
            LastName:         string,
            Username:         string,
            Email:            string,
            SignupDate:       date,
            TotalTimePlayed:  int,
            GameWins:         int,
            TotalGamesPlayed: int,
            SeriesWins:       int,
            TotalPoints:      int,
            Shutouts:         int }
```
The `games` table contains information about a specific game, and it also has a primary key called `Id`. The winner string will either be `"left"` or `"right"`.
```
games:   { *Id:               int,
            EndTime:          date,
            Single:           bool,
            LeftScore:        int,
            RightScore:       int
            WinMargin:        int,
            Winner:           string }
```
The `series` table contains information about a series, which in this case is a best-of-three match between the same two teams, which will end in either two or three games. It also has a primary key called `Id`.
```
series:  { *Id:               int,
            NumGames:         int,
            LeftWins:         int,
            RightWins:        int }
```
Finally, the `history` table relates the games, players, and series together. It contains three foreign keys: `GameId` from `games`, `PlayerId` from `players`, and `SeriesId` from `series`. Its primary key is the combination of `GameId` and `PlayerId`. `Side` represents the side of the table the player is on, and can either be `"left"` or `"right"`.
```
history: { *GameId:           int,
           *PlayerId:         int,
            Side:             string,
           *SeriesId:         int }
```