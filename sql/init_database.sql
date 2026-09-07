CREATE TABLE IF NOT EXISTS contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email_address TEXT,
    phone_number TEXT,
    state TEXT,
    email_status TEXT,
    email_permission_status TEXT,
    source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    event_date DATE,
    event_location TEXT,
    event_type TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_signups (
    signup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    signup_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    signup_source TEXT,

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id),

    FOREIGN KEY (event_id)
        REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS interests (
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

CREATE TABLE IF NOT EXISTS lead_qualifications (
    qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    age_range TEXT,
    income_range TEXT,
    marital_status TEXT,
    has_401k TEXT,
    financial_interest TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(contact_id, event_id),

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id),

    FOREIGN KEY (event_id)
        REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS email_consents (
    consent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    consent_status TEXT NOT NULL,
    consent_source TEXT,
    consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id),

    FOREIGN KEY (event_id)
        REFERENCES events(event_id)
);

-- Create a sample event for local development and portfolio review.
INSERT INTO events (
    event_name,
    event_date,
    event_location,
    event_type
)
SELECT
    'Demo Networking Event',
    '2026-09-01',
    'Phoenix, AZ',
    'Networking'
WHERE NOT EXISTS (
    SELECT 1
    FROM events
);
