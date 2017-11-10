import numpy as np

allGames = [
    ("a", "b", 0, 1, 2),
    ("a", "c", 1, 1, 2),
    ("a", "d", 1, 1, 2),
    ("a", "e", 1, 1, 2),
    ("b", "a", 0, 1, 1),
    ("b", "c", 1, 1, 1),
    ("b", "d", 0, 1, 1),
    ("b", "e", 1, 1, 1),
    ("c", "a", 1, 2, 2),
    ("c", "b", 1, 2, 2),
    ("c", "d", 1, 2, 2),
    ("c", "e", 1, 2, 2),
    ("d", "a", 1, 1, 1),
    ("d", "b", 0, 1, 1),
    ("d", "c", 1, 1, 1),
    ("d", "e", 0, 1, 1),
    ("e", "a", 1, 2, 1),
    ("e", "b", 1, 2, 1),
    ("e", "c", 1, 2, 1),
    ("e", "d", 0, 2, 1)
]

playerGames = {}
for tup in allGames:
    player = tup[0]
    opponent = tup[1]
    oppGames = tup[2]
    numWins = tup[3]
    numLoss = tup[4]
    data = {opponent: oppGames, "wins": numWins, "losses": numLoss}
    if player in playerGames:
        playerGames[player].update(data)
    else:
        playerGames[player] = data

playerMatrix = np.ndarray(shape=(len(playerGames), len(playerGames)))
players = sorted(playerGames.keys())
rseq16 = np.ndarray(shape=(len(playerGames),1))
 
for i in range(len(playerGames)):
    playerId = players[i]
    player = playerGames[playerId]
    rightSide = 1 + (player["wins"] - player["losses"]) / 2.0
    rseq16[i] = rightSide
    for j in range(len(playerGames)):
        curOpp = players[j]
        if i == j:
            playerMatrix[i][j] = player["wins"] + player["losses"] + 2
        elif curOpp in player:
            playerMatrix[i][j] = -1*player[curOpp]
        else:
            playerMatrix[i][j] = 0
rankingsMatrix = np.linalg.solve(playerMatrix, rseq16)
rankings = {}
for i in range(len(players)):
    player = players[i]
    rankings[player] = rankingsMatrix[i][0]
print rankings
