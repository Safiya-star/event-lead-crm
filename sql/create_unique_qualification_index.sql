CREATE UNIQUE INDEX idx_qualifications_contact_event
ON lead_qualifications (
    contact_id,
    event_id
);
