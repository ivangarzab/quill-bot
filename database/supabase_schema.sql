-- Create tables for your book club database
CREATE TABLE IF NOT EXISTS Clubs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Members (
    id INTEGER PRIMARY KEY,  -- Keeping as INTEGER to match your existing data
    name TEXT NOT NULL,
    points INTEGER DEFAULT 0,
    numberOfBooksRead INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS MemberClubs (
    member_id INTEGER,
    club_id TEXT,
    PRIMARY KEY (member_id, club_id),
    FOREIGN KEY (member_id) REFERENCES Members(id),
    FOREIGN KEY (club_id) REFERENCES Clubs(id)
);

CREATE TABLE IF NOT EXISTS Books (
    id SERIAL PRIMARY KEY,  -- Changed to SERIAL for PostgreSQL
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    edition TEXT,
    year INTEGER,
    ISBN TEXT  -- Changed to TEXT as ISBNs can have hyphens and leading zeros
);

CREATE TABLE IF NOT EXISTS Sessions (
    id TEXT PRIMARY KEY,
    club_id TEXT NOT NULL,
    book_id INTEGER,
    dueDate TEXT,  -- Keeping as TEXT to match your existing data
    defaultChannel BIGINT,  -- Changed to BIGINT for Discord channel IDs
    FOREIGN KEY (club_id) REFERENCES Clubs(id),
    FOREIGN KEY (book_id) REFERENCES Books(id)
);

CREATE TABLE IF NOT EXISTS Discussions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    date TEXT NOT NULL,  -- Keeping as TEXT to match your existing data
    location TEXT,
    FOREIGN KEY (session_id) REFERENCES Sessions(id)
);

CREATE TABLE IF NOT EXISTS ShameList (
    session_id TEXT,
    member_id INTEGER,
    PRIMARY KEY (session_id, member_id),
    FOREIGN KEY (session_id) REFERENCES Sessions(id),
    FOREIGN KEY (member_id) REFERENCES Members(id)
);