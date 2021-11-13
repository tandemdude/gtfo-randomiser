CREATE TABLE IF NOT EXISTS credentials (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    discrim VARCHAR(4) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_challenges (
    loadout_date VARCHAR(10) PRIMARY KEY,
    p1 VARCHAR(25) NOT NULL,
    p2 VARCHAR(25) NOT NULL,
    p3 VARCHAR(25) NOT NULL,
    p4 VARCHAR(25) NOT NULL,
    stage VARCHAR(25) NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_challenges (
    loadout_date VARCHAR(10) PRIMARY KEY,
    p1 VARCHAR(25) NOT NULL,
    p2 VARCHAR(25) NOT NULL,
    p3 VARCHAR(25) NOT NULL,
    p4 VARCHAR(25) NOT NULL,
    stage VARCHAR(25) NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_runs (
    run_id SERIAL PRIMARY KEY,
    run_date VARCHAR(10) NOT NULL,
    run_time INTEGER NOT NULL,
    evidence_url VARCHAR(255) NOT NULL UNIQUE,
    run_verified BOOLEAN NOT NULL DEFAULT FALSE,
    user_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_runs (
    run_id SERIAL PRIMARY KEY,
    run_date VARCHAR(10) NOT NULL,
    run_time INTEGER NOT NULL,
    evidence_url VARCHAR(255) NOT NULL UNIQUE,
    run_verified BOOLEAN NOT NULL DEFAULT FALSE,
    user_id TEXT NOT NULL
);
