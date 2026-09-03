DROP TABLE IF EXISTS interests;

CREATE TABLE interests (
    interest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    interest_type TEXT NOT NULL,
    interest_status TEXT,
    interest_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id),

    FOREIGN KEY (event_id)
        REFERENCES events(event_id)
);
