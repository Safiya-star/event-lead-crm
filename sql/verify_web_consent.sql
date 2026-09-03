SELECT
    c.contact_id,
    c.first_name,
    c.last_name,
    c.email_permission_status,
    ec.event_id,
    ec.consent_status,
    ec.consent_source,
    ec.consent_date
FROM contacts AS c
JOIN email_consents AS ec
    ON c.contact_id = ec.contact_id
ORDER BY ec.consent_id DESC
LIMIT 5;
