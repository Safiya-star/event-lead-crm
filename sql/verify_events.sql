SELECT
    es.signup_id,
    es.consent_id,
    c.first_name,
    c.last_name,
    es.event_id,
    e.event_name,
    es.signup_source,
    es.signup_date
FROM event_signups AS es 
JOIN contacts AS c    
    ON es.contact_id = c.contact_id
JOIN events AS e
    ON es.event_id = e.event_id
ORDER BY es.signup_id DESC
LIMIT 5;
