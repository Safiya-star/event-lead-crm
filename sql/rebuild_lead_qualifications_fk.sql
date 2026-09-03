PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS lead_qualifications_new

CREATE TABLE lead_qualifications_new(
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

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id),

    FOREIGN KEY (event_id)
        REFERENCES events(event_id)
);

INSERT INTO lead_qualifications_new(
    qualifcation_id,
    contact_id,
    event_id,
    age_range,
    income_range,
    marital_status,
    has_401k,
    financial_interest,
    created_at,
    updated_at
)

SELECT
    qualification_id,
    contact_id,
    COALESCE(event_id,1),
    age_range,
    income_range,
    marital_status,
    has_401k,
    financial_interest,
    created_at,
    updated_at
FROM lead_qualifications;

DROP TABLE lead_qualifications;

ALTER TABLE lead_qualifications_new
RENAME TO lead_qualifications;

PRAGMA foreign_keys = ON;

