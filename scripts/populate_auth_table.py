import os
import requests

from dotenv import load_dotenv
from airtable import Airtable

directory = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(directory, "../config.py")
load_dotenv(dotenv_path=CONFIG_PATH)

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("BASE_ID")

auth_table = Airtable(BASE_ID, "Authentication", API_KEY)
participant_table = Airtable(BASE_ID, "Participant", API_KEY)
facilitator_table = Airtable(BASE_ID, "Facilitator", API_KEY)

users = dict()

# GET DATA FROM FACILITATORS TABLE
print("Getting ids from facilitators table...")

facilitators_data = facilitator_table.get_all(fields="ID")
# Go through participant table data and store in participants with ID = airtable_id
for facilitator in facilitators_data:
  fields = facilitator["fields"]
  if fields:
    id = fields["ID"]
    if id:
      users[id] = facilitator["id"]

records_count = len(users)
print(str(records_count) + " records taken from facilitators table.\n")


# GET DATA FROM PARTICIPANTS TABLE
print("Getting ids from participant table...")

participants_data = participant_table.get_all(fields="ID")
# Go through participant table data and store in participants with ID = airtable_id
for participant in participants_data:
  fields = participant["fields"]
  if fields:
    id = fields["ID"]
    if id:
      users[id] = participant["id"]

records_count = len(users)
print(str(records_count) + " records taken from participant table.\n")


# GET DATA FROM AUTHENTICATION TABLE
print("Getting records from auth table...")

records_count = 0
authentication_data = auth_table.get_all(fields="ID")
# Go through authentication data and find duplicates with participant table
for participant in authentication_data:
  fields = participant["fields"]
  if fields:
    id = fields["ID"]
    if id:
      users[id] = None
      records_count += 1

print(str(records_count) + " of the records already exist in authentication table.\n")

# AGREGATE DATA FOR INSERTION
records = [[]]
batch = 0
record_iteration = 0
new_records = 0

# Create batch records
for user_id, reference_id in users.items():
  # If 10 records have already been added to a batch
  if record_iteration == 10:
    record_iteration = 0
    records.append([])
    batch += 1

  if reference_id:
    new_records += 1

    records[batch].append({
      "ID": int(user_id),
      "Password": requests.get(http://www.dinopass.com/password/simple).text
    })
    record_iteration += 1

print("Adding records to authentication table...")

# PUSH BATCH RECORDS TO THE AUTHENTICATION TABLE
for batch in records:
  auth_table.batch_insert(batch)

# print(records)

print(str(new_records) + " new records added to the authentication table.\n")