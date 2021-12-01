import psycopg2


table_game_schedule = """
CREATE TABLE GameSchedule (
    Id INT NOT NULL PRIMARY KEY,
    HomeTeam VARCHAR(50) NOT NULL,
    AwayTeam VARCHAR(50) NOT NULL,
    Date DATE NOT NULL,
        )
"""
table_player_stats = """
CREATE TABLE PlayerStats (
    Id INT NOT NULL PRIMARY KEY,
    Player VARCHAR(50) NOT NULL,
    Team VARCHAR(50) NOT NULL,
    Opponent VARCHAR(50) NOT NULL,
    Date DATE NOT NULL,
    Points INT NULL,
    MP DECIMAL(18,4) NULL,
    FGM INT NULL,
    FGA INT NULL,
    FGperc DECIMAL(18,4) NULL,
    threePTM INT NULL,
    threePA INT NULL,
    threePperc DECIMAL(18,4) NULL,
    FTM INT NULL,
    FTA INT NULL,
    FTperc DECIMAL(18,4) NULL,
    ORB INT NULL,
    DRB INT NULL,
    REB INT NULL,
    AST INT NULL,
    STL INT NULL,
    BLK INT NULL,
    TurnOver INT NULL,
    PF INT NULL,
    PTS INT NULL,
    plus_minus INT NULL
        )
"""

query = """
DROP TABLE PlayerStats
 """

conn = psycopg2.connect(database="nba", user="user", password="pass")
cursor = conn.cursor()
cursor.execute(table_player_stats)
conn.commit()
