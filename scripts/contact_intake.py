"""
Command line contact intake utility for the Event Lead CRM.

This script provides a database-driven intake workflow for registering
contacts at events before or independently of the web-based intake form.

The workflow:
1. Validates the source event.
2. Searches for an existing contact by email.
3. Falls back to phone number matching when necessary.
4. Creates a new contact when no existing record is found.
5. Registers the contact for the selected event.
6. Records email consent history.
7. Captures areas of interest.
8. Collects conditional lead qualification information.
9. Commits the complete intake as a single database transaction.

If an error occurs during intake, the transaction is rolled back to prevent 
partially saved contact or event data.
"""

# Import Path to work with file and folder locations.
from pathlib import Path
# Import SQLite so Python can interact with the CRM database.
import sqlite3

#---------------------------------------------------------------------
# Event Registration
#---------------------------------------------------------------------

# Register a contact for an event while preventing duplicate signups.
def register_for_event(conn, contact_id, event_id):

    try:
        conn.execute(
            """
            INSERT INTO event_signups(
                contact_id,
                event_id,
                signup_source
            )
            VALUES (?,?,?)
            """,
            (
                contact_id,
                event_id,
                "Event Intake"
            )
        )
        print("Contact registered for event!")
    except sqlite3.IntegrityError:
        print("Contact is already registered for this event")

#-------------------------------------------------------------------
# Contact Lookup and Creation
#-------------------------------------------------------------------

# Find an existing contact using a normalized email address.
def find_contact_by_email(conn, email):
    cursor = conn.execute(
        """
        SELECT contact_id, first_name, last_name, email_address
        FROM contacts
        WHERE LOWER (email_address) = ?
        """,
        (email,)
    )

    return cursor.fetchone()

# Create a new contact and return the new contact ID.
def create_contact(conn, first_name, last_name, email, phone_number, state):
    cursor = conn.execute(
        """
        INSERT INTO contacts(
            first_name,
            last_name,
            email_address,
            phone_number,
            state,
            source
        )
        VALUES (?,?,?,?,?,?)
        """,
        (
            first_name,
            last_name,
            email,
            phone_number,
            state,
            "Event Intake"
        )
    )

    return cursor.lastrowid

# Find an existing contact by normalized phone number.
def find_contact_by_phone(conn, phone_number):
    cursor = conn.execute(
        """
        SELECT contact_id, first_name, last_name, email_address, phone_number
        FROM contacts
        WHERE phone_number = ?
        """,
        (phone_number,)
    )

    return cursor.fetchone()

#------------------------------------------------------------------
# Interest and Qualification Management
#------------------------------------------------------------------

# Add an event-specific interest record while preventing duplicates.
def add_interest(conn, contact_id, event_id, interest_type):
    sql = """
        INSERT INTO interests (
            contact_id,
            event_id,
            interest_type,
            interest_status
        )
        VALUES (?,?,?,?)
        """

    try:
        conn.execute(
            sql,
            (

                contact_id,
                event_id,
                interest_type,
                "Interested"
            )
        )
    except sqlite3.IntegrityError:
        print(
            f"{interest_type} interest already exists"
            "for this contact at this event."
        )

# Save or update event-specific qualification responses.
def save_qualification(
    conn,
    contact_id,
    event_id,
    age_range,
    income_range,
    marital_status,
    has_401k,
    financial_interest
):
    
# to insert answers into lead_qualifications and if already exists
# it will replace the answers with the newest submission.
    conn.execute(
        """
        INSERT INTO lead_qualifications (
            contact_id,
            event_id,
            age_range,
            income_range,
            marital_status,
            has_401k,
            financial_interest
        )
        VALUES (?,?,?,?,?,?,?)

        ON CONFLICT(contact_id, event_id)
        DO UPDATE SET
            age_range = excluded.age_range,
            income_range = excluded.income_range,
            marital_status = excluded.marital_status,
            has_401k = excluded.has_401k,
            financial_interest = excluded.financial_interest,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            contact_id,
            event_id,
            age_range,
            income_range,
            marital_status,
            has_401k,
            financial_interest
        )
    )

#-----------------------------------------------------------------
# Interest and Qualification Management
# ----------------------------------------------------------------
    
# Normalize phone numbers by keeping digits only.
def normalize_phone(phone_number):
    return "".join(
        character
        for character in phone_number
        if character.isdigit()    #to keep only numbers
    )

# Save a new email consent history record for the contact and event.
def save_email_consent(conn, contact_id, event_id, consent_status):
    conn.execute(
        """
        INSERT INTO email_consents(
            contact_id,
            event_id,
            consent_status,
            consent_source
        )
        VALUES (?,?,?,?)
        """,
        (
            contact_id,
            event_id,
            consent_status,
            "Event Intake"
        )
    )

#-----------------------------------------------------------------
# Project Paths and Database Connection
#-----------------------------------------------------------------

# Identify the Event Lead CRM project root.
project_root = Path(__file__).parent.parent

# Define the path to the local development database.
database_file = project_root / "database"/ "event_leads.db"

# Connect to the SQLite CRM database.
conn = sqlite3.connect(database_file)

# Enable SQLite foreign key enforcement.
conn.execute("PRAGMA foreign_keys = ON")

print("Connected to Event Lead CRM!")

#-----------------------------------------------------------------
# Contact Intake Transaction
#-----------------------------------------------------------------

# Process the complete intake as a single transaction so that 
# partial records are not saved if an error occurs.

try:

    # Validate the source event where the contact was captured.
    event_id = int(input("Enter source event ID:"))

    
    event = conn.execute(
        """
        SELECT event_id, event_name
        FROM events
        WHERE event_id = ?
        """,
        (event_id,)
    ).fetchone()

    if not event:
        print("Source event not found.")
        conn.close()  # close the database
        exit()        # stop running the program

    print("Source event:", event[1])

    # Match the contact using email or phone before creating a new record.
    email = input("Enter email address: ").strip().lower()

    contact = find_contact_by_email(conn, email)

    if contact:
        print("Contact found:")
        print(contact)

        contact_id = contact[0]
        
        register_for_event(conn, contact_id, event_id)

    else:
        print("Email not found")

        while True:
            phone_number = normalize_phone(
                input("Enter phone number: ").strip()
            )

            if len(phone_number) == 10:
                break
            print("Invalid phone number. Please enter a 10-digit phone number.")
            
        phone_contact = find_contact_by_phone(conn, phone_number)

        if phone_contact:
            print("Contact found by phone:")
            print(phone_contact)

            contact_id = phone_contact[0]
            
            register_for_event(conn, contact_id, event_id)

            print("No contact found by email or phone.")

            first_name = input("Enter first name:").strip()
            last_name = input("Enter last name:").strip()
            state = input("Enter state:"). strip()

            contact_id = create_contact(
                conn,
                first_name,
                last_name,
                email,
                phone_number,
                state
            )

            print("\nNew contact added to CRM!")
            print("New contact ID:", contact_id)

            register_for_event(conn, contact_id, event_id)

# Capture and store the contact's email communication preference.
    while True:
        consent_status = input(
            "Would you like to receive emails and updates? (Yes/No):"
        ).strip().title()

        if consent_status in ["Yes", "No"]:
            break
        print("Invalid response. Please enter Yes or No.")

    save_email_consent(
        conn,
        contact_id,
        event_id,
        consent_status
    )

    # Update the current contact record with the latest email consent 
    # status.
    conn.execute(
        """
        UPDATE contacts
        SET email_permission_status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE contact_id = ?
        """,
        (
            consent_status,
            contact_id
        )
    )

    # Collect and save the contact's selected areas of interest.
    print("\nSelect interests:")
    print("1 - Entertainment")
    print("2 - Travel")
    print("3 - Financial Education")

    # Create input validation for interest choices.
    while True:
        interest_choices = input(
            "Enter one or more choices separated by commas:"
        ).strip()

        choices = [
            choice.strip()
            for choice in interest_choices.split(",")
        ]

        if choices and all(choice in ["1", "2", "3"] for choice in choices):
            break  # leave the loop and continue the program

        print("Invalid selection.  Please enter 1, 2, or 3.")

    # Convert the numbers to names.
    interest_map = {
        "1": "Entertainment",
        "2": "Travel",
        "3": "Financial Education"
    }

    selected_interests = []

    for choice in interest_choices.split(","):
        choice = choice.strip()

        if choice in interest_map:
            selected_interests.append(interest_map[choice])

    # Save to the database.
    for interest in selected_interests:
        add_interest(conn, contact_id, event_id, interest)

    print("Interests saved:", selected_interests)

    # Collect qualification information when Travel or Financial
    # Education is selected.
    needs_qualification = (
        "Travel" in selected_interests
        or "Financial Education" in selected_interests
    )
    if needs_qualification:
        print("\nAdditional qualification questions:")

    # Create input validation for age.
        valid_age_ranges = [
            "18-24",
            "25-34",
            "35-44",
            "45-54",
            "55-64",
            "65+"
        ]

        while True:
            age_range = input(
                "Age range (18-24, 25-34, 35-44, 45-54, 55-64, 65+):"
            ).strip()

            if age_range in valid_age_ranges:
                break
            print("Invalid age range. Please choose one of the listed ranges.")
        
        # Create input validation.
        valid_income_ranges = [
            "Under $50k",
            "$50k-$74,999",
            "$75k- $99,999",
            "$100k-$149,999",
            "$150k+"
        ]

        while True:
            income_range = input(
                "Income range (Under $50k, $50k-$74,999, $75k-$99,999,)"
                "$100k- $149,999, $150k+:"
            ).strip()

            if income_range in valid_income_ranges:
                break
            print("Invalid income range. Please choose one of the listed ranges.")

        # Create input validation for marital status.
        valid_marital_statuses = [
            "Single",
            "Married",
            "Divorced",
            "Widowed"
        ]

        while True:
            marital_status = input(
                "Marital status (Single, Married, Divorced, Widowed): "
            ).strip().title()

            if marital_status in valid_marital_statuses:
                break
            print("Invalid marital status. Please choose one of the listed options.")

        # Input validation for 401k.
        if "Financial Education" in selected_interests:
            while True:
                has_401k = input(
                    "Do you currently have a 401(k)? (Yes/No):"
                ).strip().title()

                if has_401k in ["Yes", "No"]:
                    break 
                print("Invalid response. Please enter Yes or No.")

            financial_interest = input(
                "What area of financial education interests you?"
            ).strip()

        else:
            has_401k = None
            financial_interest = None

        save_qualification(
            conn,
            contact_id,
            event_id,
            age_range,
            income_range,
            marital_status,
            has_401k,
            financial_interest
            )

        print("Qualification information saved!")

# Create a single commit for the entire intake.
    conn.commit()
    print("Intake saved successfully")

except Exception as error:
    conn.rollback()
    print("intake failed. No changes were saved.")
    print("Error:", error)

# Database connection gets closed whether success or failure.
finally:    
    conn.close()
