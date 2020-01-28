import urllib3
import re
import smtplib
import os
import pickle
import time
password = "fnotify123"
login = "flatnotifier42069@gmail.com"
sender = login
receiver = "alex.netsch97@gmail.com"
port = 465
smtp_server = "smtp.gmail.com"


def getResults(data):
    lstings = []
    data = data.split("<ul id=\"resultListItems\" class=\"is24-res-list is24-res-gallery result-list border-top\">")[1]
    data = data.split("<ul class=\"is24-res-list is24-res-gallery result-list recommendation-list\">")[0]
    data = data.replace("\n", "")
    data = data.split("class=\"result-list__listing \"")[1:]
    for listing in data:
        lstings.append(dict())
        id = re.findall(r"(?<=data-id=\")(.\d*)", listing)[0]
        rent = re.findall(r"\d*(?= €<)", listing)[0]
        lstings[-1]["id"] = id
        lstings[-1]["rent"] = rent
        lstings[-1]["link"] = "https://www.immobilienscout24.de/expose/" + str(id)
    return lstings


def checkNew(lstings, lstings_new):
    for id in lstings_new:
        for listing in lstings:
            if listing["id"] == id["id"]:
                break
        else:
            notifyAN(id)
    return lstings_new


def notifyAN(flat):
    message = f"""\
Subject: Hello There
To: {receiver}
From: {sender} 

New flat found, rent: {flat["rent"]}
{flat["link"]}

General Kenobi"""
    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender, receiver, message)



def run():
    http = urllib3.PoolManager()
    if os.path.isfile("pastListings.p"):
        lstings = pickle.load(open("pastListings.p", "rb"))
        print("Read listings from file, found " + str(len(lstings)) + " listings")
    else:
        print("No listing file found")
        lstings = []
    print("Starting 60 sec loop...")
    while 1:
        r = http.request('GET',
                         "https://www.immobilienscout24.de/Suche/de/baden-wuerttemberg/freiburg-im-breisgau/wohnung-mieten?price=-550.0&sorting=2")
        res = getResults(r.data.decode())
        lstings = checkNew(lstings, res)
        pickle.dump(lstings, open("pastListings.p", "wb"))
        time.sleep(60)


if __name__ == "__main__":
    run()
