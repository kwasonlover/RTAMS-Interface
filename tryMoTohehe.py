from pymongo import MongoClient
from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from pprint import pprint
from datetime import datetime
from gpiozero import Button

import time

# Initialize GPIO Buttons
upButton = Button(17, pull_up=False)
downButton = Button(18, pull_up=False)
leftButton = Button(27, pull_up=False)
rightButton = Button(22, pull_up=False)

# Initialize pn532 components
pn532 = Pn532_i2c()
pn532.SAMconfigure()

# Initialize MongoClient
client = MongoClient("mongodb+srv://ClintCalumpad:StrongPassword121@attendancemonitoringsys.uigzk5u.mongodb.net/?retryWrites=true&w=majority")
db = client["rtams-dev"]
students_collection = db["students"]
attendances_collection = db["attendances"]
courses_collection = db["courses"]
terms_collection = db["term"]
sections_collection = db["sections"]

# Fetch data from MongoDB and build a dictionary with lists
data_dict = {}

# Fetch courses and convert the cursor to a list
courses = list(courses_collection.find())
data_dict["courses"] = courses

# Fetch terms and convert the cursor to a list
terms = list(terms_collection.find())
data_dict["term"] = terms

# Fetch sections and convert the cursor to a list
sections = list(sections_collection.find())
data_dict["sections"] = sections

# Define the simplified payload object with empty strings
payload = {
    "courses": data_dict["courses"][0],
    "term": data_dict["term"][0],
    "sections": data_dict["sections"][0],
}

# Variable to track the selected row
selected_row = True  # Set to True to initially cycle through data_dict keys
# selected_key = list(data_dict.keys())[0]  # Set the initial selected key
# selected_value = list(data_dict[selected_key])[0]  # Set the initial selected value

selected_key = list(payload.keys())[0]  # Set the initial selected key
selected_value = payload[selected_key]  # Set the initial selected value

print("initialized selected key: ", selected_key)
print("initialized selected value: ", selected_value)

# Function to update payload based on the selected key
def update_payload(selected_key, selected_value):
    global payload
    print("key from update",payload[selected_key])
    index_in_data_dict = list(data_dict[selected_key]).index(selected_value)

    # Update payload[selected_key] using the obtained index
    payload[selected_key] = data_dict[selected_key][index_in_data_dict]


def handle_button_press(button):
    global selected_row, selected_key, selected_value
    if button == upButton or button == downButton:
        selected_row = not selected_row #selectedRow = !selectedRow
        # print("\n")
        # checkSelectedRow()
    elif button == leftButton:
        if not selected_row:
            # If selected_row is false, set the payload[selected_key] value to the previous index of data_dict[selected_key] value
            current_index = list(data_dict[selected_key]).index(selected_value)


            # Check if the current index is greater than 0 before decrementing
            if current_index > 0:
                new_index = current_index - 1
                selected_value = list(data_dict[selected_key])[new_index]
                update_payload(selected_key, selected_value)
        else:
            current_index = list(data_dict).index(selected_key)
            if current_index > 0:
                selected_key = list(payload.keys())[current_index - 1]
                selected_value = payload[selected_key]
        
    elif button == rightButton:
        if not selected_row:
            current_index = list(data_dict[selected_key]).index(selected_value)
            max_index = len(data_dict[selected_key]) - 1

            if current_index < max_index:
                new_index = current_index + 1
                selected_value = list(data_dict[selected_key])[new_index]
                update_payload(selected_key, selected_value)
        else:
            current_index = list(data_dict).index(selected_key)
            max_index = len(list(data_dict)) - 1
            if current_index < max_index:
                selected_key = list(payload.keys())[current_index + 1]
                selected_value = payload[selected_key]
    # print(payload)
    checkSelectedRow()
    time.sleep(0.75)

def checkSelectedRow(): #display to lcd
    print("\n\n")
    if selected_row:
        print(">", selected_key)
        print(selected_value)
    else:
        print(selected_key)
        print(">", selected_value)
    print("current payload:", payload)


# NFC-Related code/modules


# Read NFC UID and check if student exists 
def read_nfc():
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
        section = sections_collection.find_one({"section": section_value})
        print(section)
        
        # Find the term in mongodb
        term_value = "2023-2024"
        term = terms_collection.find_one({"term": term_value})
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

# pprint(data_dict)
# Main loop
try:
    while True:
        upButton.when_pressed = lambda: handle_button_press(upButton)
        downButton.when_pressed = lambda: handle_button_press(downButton)
        leftButton.when_pressed = lambda: handle_button_press(leftButton)
        rightButton.when_pressed = lambda: handle_button_press(rightButton)
except KeyboardInterrupt:
    print("Program terminated.")
finally:
    if client:
        client.close()