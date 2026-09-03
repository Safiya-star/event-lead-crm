CREATE TABLE IF NOT EXISTS email_consents (
    consent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    consent_status TEXT NOT NULL,
    consent_source TEXT,
    consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id)

    FOREIGN KEY (event_id)
        REFERENCES events(event_id)
);
