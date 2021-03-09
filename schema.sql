CREATE SCHEMA IF NOT EXISTS randomiser;

CREATE TABLE IF NOT EXISTS randomiser.daily (
    loadout_date VARCHAR(10) PRIMARY KEY,
    player1 VARCHAR(20) NOT NULL,
    player2 VARCHAR(20) NOT NULL,
    player3 VARCHAR(20) NOT NULL,
    player4 VARCHAR(20) NOT NULL,
    stage VARCHAR(20) NOT NULL
);
