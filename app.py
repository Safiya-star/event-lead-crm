from pathlib import Path
import sqlite3
import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, Response

# Initialize Flask application
app = Flask(__name__)

# Define the path to the SQLite database file
project_root = Path(__file__).parent
database_file = Path(
    os.environ.get(
        "DATABASE_PATH",
        project_root /"event_leads.db"
    )
)

# to create the connection helper function
def get_db_connection():
    conn = sqlite3.connect(database_file, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# to open clean schema file and create any missing tables
def init_database():
    schema_file = project_root / "sql" / "init_database.sql"

    conn = get_db_connection()

    with open(schema_file, "r", encoding="utf-8") as file:
        conn.executescript(file.read())

    conn.commit()
    conn.close()

init_database

 # To create helper function to normalize phone number 
def normalize_phone(phone):
    if not phone:
        return None

    digits = ''.join(
       character for character in phone
       if character.isdigit()
    )

    if len(digits) != 10:
        return None

    return digits 

# to add allowed values for age ranges, income ranges, and marital statuses
VALID_AGE_RANGES = [
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55-64",
    "65+"
]

VALID_INCOME_RANGES = [
    "Under $50k",
    "$50k-$74,999",
    "$75k-$99,999",
    "$100k-$149,999",
    "$150k+"
]

VALID_MARITAL_STATUSES = [
    "Single",
    "Married",
    "Divorced",
    "Widowed"
]

# to create the success route
@app.route("/success")
def success():
    return render_template("success.html")

# Define the route for the home page
@app.route("/", methods=["GET", "POST"])
def home():

    # To direct protected admin requests to the event leads dashboard
    if request.method == "GET" and request.args.get("admin") == "1":
        return admin_leads()
    
    event_id = request.args.get("event_id")

    event = None

# To retrieve event details from the database based on the provided event_id
    if event_id:
        conn = get_db_connection()
        
        event = conn.execute(
            """
            SELECT event_id, event_name
            FROM events
            WHERE event_id = ?
            """,
            (event_id,)
        ).fetchone()

        conn.close()

# to block missing or invalid Event URLs
    if request.method == "GET" and not event:
        return "Invalid or missing event.", 400

# To handle form submission and process the data
    if request.method == "POST":
        #to collect form data and store it in the database
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        state = request.form.get("state")
        submitted_event_id = request.form.get("event_id")
        email_consent = request.form.get("email_consent")
        selected_interests = request.form.getlist("interests")
        age_range = request.form.get("age_range")
        income_range = request.form.get("income_range")
        marital_status = request.form.get("marital_status")
        has_401k = request.form.get("has_401k")
        financial_interest = request.form.get("financial_interest")

    # To determine the consent status based on the email_consent value
        if email_consent == "Yes":
            consent_status = "Yes"
        else:
            consent_status = "No"

    # To independently verify the three required contact fields  
        if not first_name or not first_name.strip():
            return "First name is required.", 400

        if not last_name or not last_name.strip():
            return "Last name is required.", 400

        if not email or not email.strip():
            return "Email address is required.", 400

    # To call the normalize_phone function to validate the phone number
        normalized_phone = normalize_phone(phone_number)

    # return an error if phone number is invalid and reload form with previously entered data
        if phone_number and phone_number.strip() and not normalized_phone:
            return render_template(
                "intake_form.html",
                event=event,
                phone_error="Please enter a valid 10-digit phone number.",
                form_data=request.form
            ), 400

    # To validate and keep everything if an error occurs in the qualification fields 
        if (
            "Travel" in selected_interests
            or "Financial Education" in selected_interests
        ):
            if age_range not in VALID_AGE_RANGES:
                return render_template(
                    "intake_form.html",
                    event=event,
                    qualification_error="Please select a valid age range.",
                    form_data=request.form
                ), 400

            if income_range not in VALID_INCOME_RANGES:
                return render_template(
                    "intake_form.html",
                    event=event,
                    qualification_error="Please select a valid income range.",
                    form_data=request.form
                ), 400

            if marital_status not in VALID_MARITAL_STATUSES:
                return render_template(
                    "intake_form.html",
                    event=event,
                    qualification_error="Please select a valid marital status.",
                    form_data=request.form
                ), 400

            if "Financial Education" in selected_interests:
                if has_401k not in ["Yes", "No"]:
                    return render_template(
                        "intake_form.html",
                        event=event,
                        qualification_error="Please select Yes or No for the 401(k) question.",
                        form_data=request.form
                    ), 400

    # To connect to the database and perform operations
        conn = get_db_connection()

        try: 

        # to validate the event during POST 
            sumbitted_event = conn.execute(
                """
                SELECT event_id, event_name
                FROM events
                WHERE event_id = ?
                """,
                (submitted_event_id,)
            ).fetchone()

            if not sumbitted_event:
                conn.close()
                return "Invalid or missing source event.", 400 

        # To check if the contact already exists in the database based on the email address
            contact = conn.execute(
                """
                SELECT contact_id, first_name, last_name, email_address
                FROM contacts
                WHERE LOWER(email_address) = ?
                """,
                (email.strip().lower(),)
            ).fetchone()

        # If the contact exists, retrieve the contact_id; otherwise, create a new contact and retrieve the new contact_id
            if contact:
                contact_id = contact[0]

                print(contact)
                print("Contact ID:", contact_id)

            else:
                print("No existing contact found:")

                cursor = conn.execute(
                    """
                    INSERT INTO contacts (
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
                        first_name.strip(),
                        last_name.strip(),
                        email.strip().lower(),
                        normalized_phone,
                        state.strip(),
                        "Web Intake"
                    )   
                )
                
                contact_id = cursor.lastrowid

                print("Contact ID:", contact_id)

            print("Contact ready for intake:", contact_id)

        # To record the event interaction, email consent, and interests in the database
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
                        submitted_event_id,
                        "Web Intake"
                    )
                )

            except sqlite3.IntegrityError:
                print("Contact is already associated with this event.")

        # To record the email consent and update the contact's email permission status in the database
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
                    submitted_event_id,
                    consent_status,
                    "Web Intake"
                )
            )

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

        # To record the selected interests in the database, ensuring that duplicate interests for the same contact and event are not inserted
            for interest in selected_interests:
                try:
                    conn.execute(
                        """
                        INSERT INTO interests(
                            contact_id,
                            event_id,
                            interest_type,
                            interest_status
                        )
                        VALUES (?,?,?,?)
                        """,
                        (
                            contact_id,
                            submitted_event_id,
                            interest,
                            "Interested"
                        )
                    )

                except sqlite3.IntegrityError:
                    print(
                        f"{interest} already exists"
                        "for this contact at this event."
                    )

        # To record the qualification information in the database, ensuring that duplicate entries for the same contact and event are not inserted
            if(
                "Travel" in selected_interests 
                or "Financial Education" in selected_interests
            ):
                if "Financial Education" not in selected_interests:
                    has_401k = None
                    financial_interest = None

            # To insert or update the qualification information in the database using an UPSERT operation
                conn.execute(
                    """
                    INSERT INTO lead_qualifications(
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
                        UPDATED_AT = CURRENT_TIMESTAMP
                    """,
                    (
                        contact_id,
                        submitted_event_id,
                        age_range,
                        income_range,
                        marital_status,
                        has_401k,
                        financial_interest
                    )
                )

            conn.commit()

        except Exception as error:
            conn.rollback()
            print("Database transaction failed:", error) 

            return render_template(
                "intake_form.html",
                event=event,
                database_error="Something went wrong while saving your information. Please try again.",
                form_data=request.form
            ), 500

    # Runs whether the try succeeds or the except runs. 
        finally:
            conn.close() 

        return render_template("success.html")

        # To display the event intake form for a valid GET request
    return render_template("intake_form.html", event=event)

# To verify that the admin username and password match the protected credentials
def check_auth(username, password):
    return (
        username == os.environ.get("ADMIN_USERNAME")
        and password == os.environ.get("ADMIN_PASSWORD")
    )

# To request admin login credentials when authentication is missing or incorrect
def authenticate():
    return Response(
        "Authentication required.",
        401,
        {"WWW-Authenticate": 'Basic realm="Admin Area"'}
    )

# To protect admin pages by requiring valid authentication before access
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization

        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

        return f(*args, **kwargs)

    return decorated    

# To display the protected event-specific admin lead dashboard
@app.route("/admin/leads")
@requires_auth
def admin_leads():
    conn = get_db_connection()

    # To identify which event's leads and statistics should be displayed
    event_id = request.args.get("event_id")

    # To retrieve the contact, event, interest, consent, and qualification details for each event lead
    leads = conn.execute(
        """
        SELECT
            c.first_name,
            c.last_name,
            c.email_address,
            c.phone_number,
            e.event_name,
            es.signup_date,
            (
                SELECT GROUP_CONCAT(i.interest_type, ', ')
                FROM interests i
                WHERE i.contact_id = c.contact_id
                  AND i.event_id = es.event_id
            ) AS interests,
            (
                SELECT ec.consent_status
                FROM email_consents ec
                WHERE ec.contact_id = c.contact_id
                  AND ec.event_id = es.event_id
                ORDER BY ec.consent_id DESC
                LIMIT 1
            ) AS email_consent,
            (
                SELECT lq.age_range
                FROM lead_qualifications lq
                WHERE lq.contact_id = c.contact_id
                  AND lq.event_id = es.event_id
                ORDER BY lq.qualification_id DESC
                LIMIT 1
            ) AS age_range,
            (
                SELECT lq.income_range
                FROM lead_qualifications lq
                WHERE lq.contact_id = c.contact_id
                  AND lq.event_id = es.event_id
                ORDER BY lq.qualification_id DESC
                LIMIT 1
            ) AS income_range,
            (
                SELECT lq.marital_status
                FROM lead_qualifications lq
                WHERE lq.contact_id = c.contact_id
                  AND lq.event_id = es.event_id
                ORDER BY lq.qualification_id DESC
                LIMIT 1
            ) AS marital_status,
            (
                SELECT lq.has_401k
                FROM lead_qualifications lq
                WHERE lq.contact_id = c.contact_id
                  AND lq.event_id = es.event_id
                ORDER BY lq.qualification_id DESC
                LIMIT 1
            ) AS has_401k,
            (
                SELECT lq.financial_interest
                FROM lead_qualifications lq
                WHERE lq.contact_id = c.contact_id
                  AND lq.event_id = es.event_id
                ORDER BY lq.qualification_id DESC
                LIMIT 1
            ) AS financial_interest

        FROM contacts c
        JOIN event_signups es
            ON c.contact_id = es.contact_id
        JOIN events e
            ON es.event_id = e.event_id
        WHERE es.event_id = ?
        ORDER BY es.signup_date DESC
        """,
        (event_id,)
    ).fetchall()

    # To count the total number of signups for the selected events
    total_signups = conn.execute(
        """
        SELECT COUNT(*)
        FROM event_signups
        WHERE event_id = ?
        """,
        (event_id,)
    ).fetchone()[0]

    # To count contacts whose most recent email consent for the selected event is Yes
    email_opt_ins = conn.execute(
    """
    SELECT COUNT(*)
    FROM email_consents ec
    WHERE ec.event_id = ?
      AND ec.consent_status = 'Yes'
      AND ec.consent_id = (
          SELECT MAX(ec2.consent_id)
          FROM email_consents ec2
          WHERE ec2.contact_id = ec.contact_id
            AND ec2.event_id = ec.event_id
      )
    """,
    (event_id,)
).fetchone()[0]

    # To count leads interested in Entertainment 
    entertainment_count = conn.execute(
        """
        SELECT COUNT(DISTINCT contact_id)
        FROM interests
        WHERE interest_type = 'Entertainment'
          AND event_id = ?
        """,
        (event_id,)
    ).fetchone()[0]

    # To count leads interested in Travel
    travel_count = conn.execute(
        """
        SELECT COUNT(DISTINCT contact_id)
        FROM interests
        WHERE interest_type = 'Travel'
          AND event_id = ?
        """,
        (event_id,)
    ).fetchone()[0]

    # To count leads interested in Financial Education
    financial_count = conn.execute(
        """
        SELECT COUNT(DISTINCT contact_id)
        FROM interests
        WHERE interest_type = 'Financial Education'
          AND event_id = ?
        """,
        (event_id,)
    ).fetchone()[0]

    # To close the database connection after retrieving the dashboard data
    conn.close()

    # To send the event lead data and summary statistics to the admin dashboard
    return render_template(
        "admin_leads.html",
        leads=leads,
        total_signups=total_signups,
        email_opt_ins=email_opt_ins,
        entertainment_count=entertainment_count,
        travel_count=travel_count,
        financial_count=financial_count
    )

    


if __name__ == "__main__":
    app.run(debug=True)
