SELECT
    name,
    sql  
FROM sqlite_master
WHERE type = 'table'
    AND name IN (
        'lead_qualifications',
        'lead_qualifications_new'
    );
    