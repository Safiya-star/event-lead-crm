DELETE FROM interests
WHERE interest_id NOT IN (
    SELECT MIN(interest_id)
    FROM interests
    GROUP BY contact_id, event_id, interest_type
);
