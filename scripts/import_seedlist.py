import pandas as pd    
from pathlib import Path
import sqlite3

project_root = Path(__file__).parent.parent
excel_file = project_root/"data"/"seed_contacts.xlsx"
database_file = project_root/"database"/"event_leads.db"

df = pd.read_excel(excel_file)    
print(df.head())

print("\n---SEED LIST VALIDATION---")

print("Total records:", len(df))

print("\nColumn names:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate email addresses:")
print(df["Email address"].duplicated().sum())

df = df.rename(columns={
    "First Name": "first_name",
    "Last Name": "last_name",
    "Email status": "email_status",
    "Email permission status": "email_permission_status",
    "Email address": "email_address"
})
print("\n---TRANSFORMED COLUMNS---")
print(df.columns.tolist())

conn = sqlite3.connect(database_file)
print("\nConnected to event_leads.db successfully!")

df["phone_number"] = None
df["state"] = None
df["source"] = "Tommy Seed List"

inserted = 0
skipped = 0

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

    except sqlite3.IntegrityError:
        skipped += 1

conn.commit()

conn.close()
print(f"\nNew contacts inserted: {inserted}")
print(f"Existing contacts skipped: {skipped}")
