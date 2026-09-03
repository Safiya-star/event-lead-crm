CREATE TABLE IF NOT EXISTS lead_qualifications (
    qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL, 
    age_range TEXT,
    income_range TEXT,
    marital_status TEXT,
    has_401k TEXT,
    financial_interest TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id)
);
