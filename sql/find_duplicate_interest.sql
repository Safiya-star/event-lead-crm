SELECT
    contact_id,
    event_id,
    COUNT(*) duplicate_count
FROM lead_qualifications
GROUP BY
    contact_id,
    event_id
HAVING COUNT (*) > 1;
