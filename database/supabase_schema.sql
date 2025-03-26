-- Create tables for your book club database
CREATE TABLE IF NOT EXISTS Clubs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    discord_channel BIGINT,
);

CREATE TABLE IF NOT EXISTS Members (
    id INTEGER PRIMARY KEY, -- TODO: Make into serial
    name TEXT NOT NULL,
    points INTEGER DEFAULT 0,
    books_read INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS MemberClubs (
    member_id INTEGER,
    club_id TEXT,
    PRIMARY KEY (member_id, club_id),
    FOREIGN KEY (member_id) REFERENCES Members(id),
    FOREIGN KEY (club_id) REFERENCES Clubs(id)
);

CREATE TABLE IF NOT EXISTS Books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    edition TEXT,
    year INTEGER,
    ISBN TEXT
);

CREATE TABLE IF NOT EXISTS Sessions (
    id TEXT PRIMARY KEY,
    club_id TEXT NOT NULL,
    book_id INTEGER,
    due_date Date,
    FOREIGN KEY (club_id) REFERENCES Clubs(id),
    FOREIGN KEY (book_id) REFERENCES Books(id)
);

CREATE TABLE IF NOT EXISTS Discussions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    date Date NOT NULL,
    location TEXT,
    FOREIGN KEY (session_id) REFERENCES Sessions(id)
);

CREATE TABLE IF NOT EXISTS ShameList (
    club_id TEXT,
    member_id INTEGER,
    PRIMARY KEY (club_id, member_id),
    FOREIGN KEY (club_id) REFERENCES Sessions(id),
    FOREIGN KEY (member_id) REFERENCES Members(id)
);