from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from pymongo import MongoClient
from datetime import datetime
from gpiozero import Button

import time

print("Ready. Tap the NFC Tag to create/update an attendance.")
print("Press Ctrl+C to exit.")

# Initialize MongoClient
client = MongoClient("mongodb+srv://ClintCalumpad:StrongPassword121@attendancemonitoringsys.uigzk5u.mongodb.net/?retryWrites=true&w=majority")
db = client["rtams-dev"]
students_collection = db["students"]

courses_collection = db["courses"]
courses_list = list(courses_collection.find({}, {"courseName": 1, "_id": 1}))

attendances_collection = db["attendances"]

term_collection = db["term"]
term_list = list(term_collection.find({}, {"term": 1, "_id": 0}))

section_collection = db["sections"]
sections_list = list(section_collection.find({}, {"section": 1, "_id": 0}))

# Initialize the GPIO buttons
upButton = Button(17, pull_up=False)
downButton = Button(18, pull_up=False)
leftButton = Button(27, pull_up=False)
rightButton = Button(22, pull_up=False)

# Initialize pn532 components
pn532 = Pn532_i2c()
pn532.SAMconfigure()

# Initial state

data_dict = {}

collections = [courses_collection, term_collection, section_collection]

isFirstRow = True  #  for collections, 1 for payloads
current_index = 0
current_collection_index = 0
current_payload_index = 0

payload = {
    "courses": data_dict["courses"][0],
    "term": data_dict["term"][0],
    "sections": data_dict["sections"][0],
}

selected_key = list(payload.keys())[0]

def switch_collection(direction):
    global current_collection_index, current_payload_index
    
    if isFirstRow == True:
        if direction == "left":
            current_collection_index = (current_collection_index - 1) % len(collections)
        elif direction == "right":
            current_collection_index = (current_collection_index + 1) % len(collections)
        current_payload_index = 0

def switch_payload(button):
    global current_collection_index, current_payload_index
    
    current_collection = collections[current_collection_index]
    
    if isFirstRow == True:
    
        if current_collection.name == "courses" and current_collection: 

            if button == leftButton:
                current_payload_index = (current_payload_index - 1) % len(courses_list)
            elif button == rightButton:
                current_payload_index = (current_payload_index + 1) % len(courses_list)
        
        elif current_collection.name == "term" and current_collection:
            
            if button == leftButton:
                current_payload_index = (current_payload_index - 1) % len(term_list)
            elif button == rightButton:
                current_payload_index = (current_payload_index + 1) % len(term_list)
        
        elif current_collection.name == "term" and current_collection:
            
            if button == leftButton:
                current_payload_index = (current_payload_index - 1) % len(sections_list)
            elif button == rightButton:
                current_payload_index = (current_payload_index + 1) % len(sections_list)

# Read NFC UID and check if student exists 
def read_nfc_and_handle_attendance():
    try:
        # Read NFC UID and format it to readable HEX
        card_data = pn532.read_mifare().get_data()
        card_data_formatted = ' '.join(format(x, '02X') for x in card_data)
        nfc_uid = ' '.join(card_data_formatted.split()[7:])

        # Find the student based on the NFC UID
        student = students_collection.find_one({"nfcUID": nfc_uid})
        if not student:
            print("Student not found for the given NFC UID.")
        else:
            # Handle attendance logic 
            handle_attendance_logic(student)

    except Exception as e:
        print(f"Error generating attendance report: {e}")
    
    
def display_current_state():
    if isFirstRow == True:
        isFirstRow = "Collections"
    elif isFirstRow == False:
        isFirstRow = "Payloads"
    current_collection = collections[current_collection_index]
    current_payload = payload[current_collection_index]
    print(f"Selected row: {isFirstRow}")
    print(f"Selected Collection: {current_collection.name}")
    print(f"Selected Payload: {current_payload}")
    
def switch_row(direction):
    global isFirstRow, current_index
    if direction == "up" or direction == "down":
        isFirstRow = not isFirstRow

def handle_button_press(button):
    if button == upButton or button == downButton:
        switch_row("up" if button == upButton else "down")
        display_current_state()
    elif button == leftButton or button == rightButton:
        switch_collection("left" if button == leftButton else "right")
        display_current_state()

# Checks if attendance exists and create/update it depending on the return
def handle_attendance_logic(student):
    try:
        # Get the current date and format it
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get the current time
        current_time = datetime.now().strftime("%H:%M")
        
        # Find the course based on the course code
        courseCode = "MATH 20043"
        course = courses_collection.find_one({"courseCode": courseCode})
        print(course)
        
        # Find the Term in mongodb
        section_value = "4-5"
        section = section_collection.find_one({"section": section_value})
        print(section)
        
        # Find the term in mongodb
        term_value = "2023-2024"
        term = term_collection.find_one({"term": term_value})
        print(term)
        
        # Check if there is an existing attendance for the same student, course, and date
        existing_attendance = attendances_collection.find_one({
            "student": student["_id"],
            "course": course["_id"],
            "date": current_date,
        })
        
        if existing_attendance:
            # If there is an existing entry, update the timeOut if it's not already set
            if existing_attendance["timeIn"] and not existing_attendance["timeOut"]:
                existing_attendance["timeOut"] = current_time
                attendances_collection.update_one(
                    {"_id": existing_attendance["_id"]},
                    {"$set": {"timeOut": existing_attendance["timeOut"]}}
                )
                print("Updated attendance report.")
            else:
                print("Attendance already recorded for this course on the same day.")
        
        else:
            # If no existing attendance, create a new one
            new_attendance = {
                "student": student["_id"],
                "nfcUID": student["nfcUID"],
                "studentName": student["name"],
                "course": course["_id"],
                "date": current_date,
                "term": term["term"],  # Replace with actual term
                "section": section["section"],  # Replace with actual section
                "timeIn": current_time,
                "timeOut": None,
            }
            saved_report = attendances_collection.insert_one(new_attendance)
            print(f"New attendance report created with ID: {saved_report.inserted_id}")
        time.sleep(5)
    except Exception as e:
        print(f"Error generating attendance report: {e}")

try:
    while True:
        read_nfc_and_handle_attendance()
        upButton.when_pressed = lambda: handle_button_press(upButton)
        downButton.when_pressed = lambda: handle_button_press(downButton)
        leftButton.when_pressed = lambda: handle_button_press(leftButton)
        rightButton.when_pressed = lambda: handle_button_press(rightButton)

except KeyboardInterrupt:
    print("Program terminated.")
    if client:
        client.close()