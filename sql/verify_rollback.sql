SELECT
    contact_id,
    first_name,
    last_name,
    email_address
FROM contacts
WHERE email_address = 'rollbacktest@example.com';
