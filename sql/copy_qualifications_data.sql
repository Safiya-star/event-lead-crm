INSERT INTO lead_qualifications_new(
    qualification_id,
    contact_id,
    event_id,
    age_range,
    income_range,
    marital_status,
    has_401k,
    financial_interest,
    created_at,
    updated_at
)

SELECT
    qualification_id,
    contact_id,
    COALESCE(event_id, 1),
    age_range,
    income_range,
    marital_status,
    has_401k,
    financial_interest,
    created_at,
    updated_at
FROM lead_qualifications;
