SELECT
    c.contact_id,
    c.first_name,
    c.last_name,
    i.interest_type
FROM contacts AS c
JOIN interests AS i
    ON c.contact_id = i.contact_id
ORDER BY c.contact_id DESC
LIMIT 5;
