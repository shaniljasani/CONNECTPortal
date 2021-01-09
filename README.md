# CONNECT Portal

The CONNECT Portal is a central resource platform for the CONNECT Program hosted by [Global Encounters](https://the.ismaili/global-encounters). Participants and Facilitators can:

* See their schedules 
* View Resources
* Get Support

[View the Portal Guide](https://link.campconnect.co/portalguide)

## Milestones:
* Single Sign-On using Camp ID and Passcode
* Custom Participant & Facilitator Schedule Page
   * (data from Airtable)
* Dynamic Resources Page
* Support Helpdesk Integration with Freshdesk

## System Requirements
* Linux, MacOS, or Windows
* Python 3.3 or greater

## Installation & Usage

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

## Attributions
Special thanks to [@AtaGowani](https://github.com/AtaGowani) and [@SGhulamani](https://github.com/sghulamani) for their contributions to this project.  
Theme: [SB Admin 2](https://startbootstrap.com/theme/sb-admin-2)

## License
[MIT](https://choosealicense.com/licenses/mit/)