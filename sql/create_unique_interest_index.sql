CREATE UNIQUE INDEX idx_interests_contact_event_type
ON interests (
    contact_id,
    event_id,
    interest_type
);
