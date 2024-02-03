#!/usr/bin/env python3

import json
import csv
import time
import os
from tkinter import *
import easygui
import requests
import shutil


tmcurl = "https://www.tuftsmedicine.org/sites/default/files/2024-01/043400617_tuftsmedicalcenter_standardcharges.csv"
mwhurl = "https://www.tuftsmedicine.org/sites/default/files/2024-01/042767880_melrosewakefieldhospital_standardcharges.csv"
lghurl = "https://www.tuftsmedicine.org/sites/default/files/2024-01/042103590_lowellgeneralhospital_standardcharges.csv"

title = "Healthcare Cost Transparency Tool"


class Hospital:
    def __init__(self, location, url, initials):
        self.location = location
        self.url = url
        self.initials = initials


# Add new hospitals here
tmc = Hospital("Tufts Medical Center", tmcurl, "tmc")
mwh = Hospital("Melrose Wakefield Hospital", mwhurl, "mwh")
lgh = Hospital("Lowell General Hospital", lghurl, "lgh") 


def vars(x):
    global csv_from_hospital_path
    global json_file_path
    global csv_file_path
    csv_from_hospital_path = f"{x}-original.csv"
    csv_file_path = f"{x}-fixed.csv"
    json_file_path = f"{x}.json"


def pullfile(url):
    # Pull file down from hosptial website
    there = os.path.exists(json_file_path)
    if there:
        old = time.time() - os.path.getmtime(json_file_path) > (3 * 30 * 24 * 60 * 60)
    if there == False or old:
        print(f"{csv_from_hospital_path} is missing or older than 24hrs, downloading a fresh copy")
        try:
            r = requests.get(url, verify=False,stream=True)
            r.raw.decode_content = True
            with open(csv_from_hospital_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)            
            found = 0
            headerrow = "Code"
            with open(csv_from_hospital_path, "r") as input:
                with open(csv_file_path, "w") as output: 
                    for line in input:
                        if line.startswith(headerrow):
                            found = 1
                        if found == 0:
                            pass
                        else:
                            output.write(line)
            remove_file(csv_from_hospital_path)
            load_json_from_csv_file_with_headers(csv_file_path, json_file_path)
        except:
            if there:
                print("unable to download a fresh copy at this time, using local copy")
                jsonify()
            else:
                exit(1)
    else:
        print(f"{csv_from_hospital_path} is newer than 24hrs, skipping download")
        jsonify()


def start():
    global data
    global records
    global facility
    message = "Choose a facility"
    choices = [lgh.location, mwh.location, tmc.location, "Exit"]
    facility = easygui.buttonbox(message, title, choices)
    if facility == lgh.location:
        vars("lgh")
        url = lgh.url
        pullfile(url)
    elif facility == mwh.location:
        vars("mhw")       
        url = mwh.url
        pullfile(url)
    elif facility == tmc.location:
        vars("tmc")
        url = tmc.url
        pullfile(url)
    else:
        exit(0)
        

def load_json_from_csv_file_with_headers(csv_file_path, json_file_path):
    with open(csv_file_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)   
        data = []
        for row in reader:
            data.append(dict(zip(headers, row)))
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file)
    remove_file(csv_file_path)
    jsonify()      
    
    
def jsonify():
    global records
    global data
    f = open(json_file_path)
    data = json.load(f)
    f.close()
    records = len(data)  
    asktype()              

 
def asktype():
    message = "What are you looking to do?"
    choices = ["Search by CPT", "Search by Description", "Exit"]
    output = easygui.buttonbox(message, title, choices)
    try:
        if output == "Search by CPT":
            options = menulevel("Code")
            cpt = easygui.choicebox("Pick the item you want cost for:", "CPT Lookup", options)
            happy = bool(cpt)
            if happy == True:
                pass
            else:
                exit(0)
            k = level2("Code", cpt)
        elif output == "Search by Description":
            options = menulevel("Description")
            description = easygui.choicebox("Pick the item you want cost for", "Description Lookup", options)
            happy = bool(description)
            if happy == True:
                pass
            else:
                exit(0)            
            k = level2("Description", description)
        else:
            exit(0)
    except:
        exit(0)
    # k is a list of the column headers  
    k = list(k)

    # Remove the first three columns headers ("Cost", "Description", and "Type") so they aren't in the next menu
    # In some cases 'Package/Line_Level' is there, if so it is also removed
    if 'Package/Line_Level' in k:
        del k[0:4:1]
    else:
        del k[0:3:1]
    message = "Which charge would you like to see?"
    choice = easygui.choicebox(message, title, k)
    happy = bool(choice)
    if happy == True:
        pass
    else:
        exit(0)  
            
    try:
        # If price is a float make sure it contains 2 decimal points and add "$" prefix
        flt = float(data[record][choice])
        cash = f"{flt:.2f}"
        money = str(f"\n\n\n\n{data[record]['Description']}\n\n\n\nCPT Code: {data[record]['Code']}\n\n\n\n{choice}: ${cash}")
    except:
        money = data[record][choice]
        
    choices = ["Do another", "Quit"]
    p = easygui.buttonbox(money, facility, choices)
    if p == "Do another":
        start()  


def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        
        
def level2(k, v):
    global record
    for record in range(records):
        if data[record][k] == v:
            return data[record].keys()


def menulevel(c):
    # Return a list of items in the c column
    values = []
    for record in range(records):
        x = data[record][c]
        values.append(x) 
    return values


start()