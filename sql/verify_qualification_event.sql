SELECT
    c.first_name,
    c.last_name,
    e.event_name,
    q.age_range,
    q.income_range,
    q.marital_status,
    q.has_401k,
    q.financial_interest
FROM lead_qualifications q  
JOIN contacts c   
    ON q.contact_id = c.contact_id
JOIN events e   
    ON q.event_id = e.event_id
ORDER BY q.qualification_id DESC;
