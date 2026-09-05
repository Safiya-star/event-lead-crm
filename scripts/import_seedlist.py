"""
Import an existing contact seed list into the Event Lead CRM database.

This utility script:
1. Loads contact data from a local Excel file.
2. Performs basic validation of the source data
3. Renames source columns to match the CRM database schema.
4. Add CRM-specific fields that are not present in the source file.
5. Inserts new contacts into the SQLite contacts table.
6. Skips contacts that violate an existing database uniqueness constraint.

The source Excel file and SQLite database are stored locally and excluded 
from version control to prevent contact data from being commited to GitHub.
"""


import pandas as pd    
from pathlib import Path
import sqlite3

# Identify the root Directory of the Event Lead CRM project.
project_root = Path(__file__).parent.parent

# Define local data and database locations.
# These files contain contact information and are excludedd from Git.
excel_file = project_root/"data"/"seed_contacts.xlsx"
database_file = project_root/"database"/"event_leads.db"

# Load the existing contact seed list from Excel.
df = pd.read_excel(excel_file) 

# Preview the imported data before processing.
print(df.head())

print("\n---SEED LIST VALIDATION---")

print("Total records:", len(df))

print("\nColumn names:")
print(df.columns.tolist())

# Identify missing values in each source column
print("\nMissing values:")
print(df.isnull().sum())

# Identify duplicate email addresses before database insertion.
print("\nDuplicate email addresses:")
print(df["Email address"].duplicated().sum())

# Rename source columns to match the contacts table schema.
df = df.rename(columns={
    "First Name": "first_name",
    "Last Name": "last_name",
    "Email status": "email_status",
    "Email permission status": "email_permission_status",
    "Email address": "email_address"
})
print("\n---TRANSFORMED COLUMNS---")
print(df.columns.tolist())

# Connect to the local development CRM database.
conn = sqlite3.connect(database_file)
print("\nConnected to event_leads.db successfully!")

# Add fields required by the CRM that were not included in the original list
df["phone_number"] = None
df["state"] = None
df["source"] = "Seed List"

# Track the result of the import process.
inserted = 0
skipped = 0

# Process each source record and insert it into the contacts table.
for _, row in df.iterrows():
    try:
        conn.execute(
            """
            INSERT INTO contacts (
                first_name,
                last_name,
                email_address,
                phone_number,
                state,
                email_status,
                email_permission_status,
                source
            )
        
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                row["first_name"],
                row["last_name"],
                row["email_address"],
                row["phone_number"],
                row["state"],
                row["email_status"],
                row["email_permission_status"],
                row["source"]
            )
        )
                    
        inserted += 1

    # Skip records that violate an existing database integrity constraint.
    except sqlite3.IntegrityError:
        skipped += 1

# Save all successful inserts and close the database connection.
conn.commit()

# Display a summary of the completed import.
conn.close()
print(f"\nNew contacts inserted: {inserted}")
print(f"Existing contacts skipped: {skipped}")
