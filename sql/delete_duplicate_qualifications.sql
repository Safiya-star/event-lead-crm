DELETE FROM lead_qualifications
WHERE qualification_id NOT IN (
    SELECT MAX(qualification_id)
    FROM lead_qualifications
    GROUP BY contact_id, event_id
);
