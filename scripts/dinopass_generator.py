# File:         dinopass_generator.py
# Author:       @shaniljasani
# Description:  This file generates a user-defined quantity of strong passwords using the dinopass API

import requests

def verify_strong(pw):
    validity = False
    # ensure between 8 and 12 chars
    if len(pw) >= 8 and len(pw) <= 12:
        # ensure has a lower and capital char
        if pw.lower() != pw and pw.upper() != pw:
            # ensure has a special char
            if pw.isalnum() != pw:
                validity = True
    return validity

num_pw = int(input("How many strong passwords would you like? "))

while num_pw > 0:
    pw = str(requests.get("https://www.dinopass.com/password/strong").text)
    if verify_strong(pw):
        print(pw)
        num_pw -= 1