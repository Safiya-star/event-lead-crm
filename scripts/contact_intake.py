# Import Path to work with file and folder locations
from pathlib import Path
# Import SQLite so Python can interact with the CRM database
import sqlite3

# define a reusable function to register a contact for an event
def register_for_event(conn, contact_id, event_id):
#Try to register the contact for the event and handle duplicate signups
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

# Define a resusable function to find an existing contact by email
def find_contact_by_email(conn,email):
    cursor = conn.execute(
        """
        SELECT contact_id, first_name, last_name, email_address
        FROM contacts
        WHERE LOWER (email_address) = ?
        """,
        (email,)
    )

    return cursor.fetchone()

# Define a reusable function to create a new contact
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

# Define a reusable function to find an existing contact by phone number
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

# Define a reusable function to create an interests record
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

# to save qualification answers to lead_qualification
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
# it will replace the answers with the newest subsession
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
    
# Normalization function for phone number
def normalize_phone(phone_number):
    return "".join(
        character
        for character in phone_number
        if character.isdigit()    #to keep only numbers
    )

# Create a function to create consent history record
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

# Find the main Event lead CRM project folder
project_root = Path(__file__).parent.parent
# Create the path to the SQLite database file
database_file = project_root /"database"/ "event_leads.db"

# Connect to the SQLite CRM database
conn = sqlite3.connect(database_file)

# Enable SQLite foreign key enforcement
conn.execute("PRAGMA foreign_keys = ON")

print("Connected to Event Lead CRM!")

# to create the rollback safety net
try:

    # Identify the source event here the contact was captured
    event_id = int(input("Enter source event ID:"))

    # Verify that the source event exists
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

    # Ask for an email address and normalize it by removing outside spaces and converting to lowercase
    email = input("Enter email address: ").strip().lower()

    # Search for an existing contact by email
    contact = find_contact_by_email(conn,email)

    # If the email matches an existing contact, retrieve their ID and register them for the event
    if contact:
        print("Contact found:")
        print(contact)

        contact_id = contact[0]
        
        register_for_event(conn, contact_id, event_id)

    # If email is not found, ask for a phone number and search for a matching contact
    else:
        print("Email not found")

    # Normalizes and input validate phone number during intake
        while True:
            phone_number = normalize_phone(
                input("Enter phone number: ").strip()
            )

            if len(phone_number) == 10:
                break
            print("Invalid phone number. Please enter a 10-digit phone number.")
            
        phone_contact = find_contact_by_phone(conn, phone_number)

    # If the phone number matches, retrieve the contact ID and register contact for event
        if phone_contact:
            print("Contact found by phone:")
            print(phone_contact)

            contact_id = phone_contact[0]
            
            register_for_event(conn, contact_id, event_id)

    # If no email or phone match exists, create a new contact and register them for the event
        else: 
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

# To collect the consent during intake
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

    # to get the current contact record to reflect consent
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

    # To ask for interests
    print("\nSelect interests:")
    print("1 - Entertainment")
    print("2 - Travel")
    print("3 - Financial Education")

    # To create input validation for interest choices
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
    # Convert the numbers to names
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

    # To save to the database
    for interest in selected_interests:
        add_interest(conn, contact_id, event_id, interest)

    print("Interests saved:", selected_interests)

    # To add qualifcation questions for Travel and Financial Education
    needs_qualification = (
        "Travel" in selected_interests
        or "Financial Education" in selected_interests
    )
    if needs_qualification:
        print("\nAdditional qualification questions:")

    # to crate input validation for age
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
        
        # to Create input validation
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

        # To create input validation for marital status
        valid_marital_statuses = [
            "Single",
            "Married",
            "Divorced",
            "Widowed"
        ]

        while True:
            marital_status = input(
                "Marital status (Single,Married, Divorced, Widowed): "
            ).strip().title()

            if marital_status in valid_marital_statuses:
                break
            print("Invalid marital status. Please choose one of the listed options.")

        # includes input validation for 401k
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

# To create a single commit for the entire intake
    conn.commit()
    print("Intake saved successfully")

except Exception as error:
    conn.rollback()
    print("intake failed. No changes were saved.")
    print("Error:", error)

finally:    #database connection gets closed whether success or fails
    conn.close()
