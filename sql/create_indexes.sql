CREATE UNIQUE INDEX IF NOT EXISTS idx_event_signups_contact_event
ON event_signups(contact_id, event_id);