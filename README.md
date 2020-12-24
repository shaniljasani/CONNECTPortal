# Project: Camp CONNECT Portal
testing something
## Development

### System Requirements
* Linux, MacOS, or Windows
* Python 3.3 or greater

### Step 1: Clone and Change Directory

```
git clone https://github.com/shaniljasani/CONNECTPortal.git
```

```
cd CONNECTPortal
```
### Step 2: Add a `config.py` File
Use the `config_EXAMPLE.py` file template to create a `config.py` file. Add your `AIRTABLE_API_KEY` to the file. *This is an important step to ensure data is properly collected from AirTable*

### Step 3: Set up a Python Virtual Environment in Directory

Run the following command to create a python virtual environment.
```
python3 -m venv venv
```
This will create a folder called `venv` in the current directory which should be the root of this project's directory. `venv` stores all the virtual environment binary files.

### Step 4: Run the Virtual Environment

The following command will start up the virtual environment
```
source venv/bin/activate
```

### Step 5: Download Dependencies
```
pip install -r requirements.txt
```

### Step 6: Start the Server
```
python app.py
```

## Scripts
The `/scripts` folder provides Python scripts that may be useful to perform Airtable data population in situations where data from other tables is manipulated and needs to be synced across the Airtable data tables.

* `populate_auth_table.py`: takes data from Facilitators and Participants tables and creates authentication for users that don't already have one

## Context/Current situation

CONNECT, a virtual camp that was brought directly to the homes of 1,075 participants during a 10-day period this July, was an effort to bring the global youth together through creativity and exploration. 

Due to the success of the July camp, GE will be hosting another virtual camp in December (26th - 30th). 

In the run-up to the July camp, the technology team built a portal to service the needs of the virtual camp model.

The Camp CONNECT Portal is a central resource for participants, facilitators, and staff to access resources, support, and personalized schedules. 

## Scope:

In July, the portal allowed participants and facilitators to use their camp ID to login to the portal and access the above information. 


Upon login, participants and facilitators had access to a PDF-generated schedule. 


For the December camp, we are looking to integrate their personalised schedule directly into their schedule webpage (once they login). This will allow for an integrated + smoother experience. 


This will also be extended to staff members.

## Milestones:
* Single Sign-On using Camp ID and Password
* Custom Participant & Facilitator Schedule Page
   * (data exists in Google Sheets & Airtable)

## Preferred skillsets:
* HTML/CSS/Bootstrap
* Python with Flask, or similar Web Development Framework
* SQL 

## Time Duration:
Assuming a team of three (with varying levels of experience), we estimate this to take a maximum of 15 hours

## Deadline:
5th December 2020

## Previous Portal Screenshots and Previous Schedule:
https://campconnect.co/moodle/pluginfile.php/82/mod_resource/content/3/Portal%20Quick%20Start.pdf

https://drive.google.com/file/d/1zvYYK8m-xPbFTCb9Z3B9Vq4scgjlkXru/view?usp=sharing

https://campconnect.co/schedules/pdf-data/3/2055-3.pdf
