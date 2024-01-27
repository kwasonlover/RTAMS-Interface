from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from pymongo import MongoClient
from datetime import datetime
from gpiozero import Button

print("Ready. Tap the NFC Tag to create/update an attendance.")
print("Press Ctrl+C to exit.")

# Initialize MongoClient
client = MongoClient("mongodb+srv://ClintCalumpad:StrongPassword121@attendancemonitoringsys.uigzk5u.mongodb.net/?retryWrites=true&w=majority")
db = client["rtams-dev"]
students_collection = db["students"]
courses_collection = db["courses"]
attendances_collection = db["attendances"]
term_collection = db["term"]
section_collection = db["sections"]

# Initialize the GPIO buttons
upButton = Button(17, pull_up=False)
downButton = Button(18, pull_up=False)
leftButton = Button(27, pull_up=False)
rightButton = Button(22, pull_up=False)

# Initialize pn532 components
pn532 = Pn532_i2c()
pn532.SAMconfigure()

# Initial state
collections = [courses_collection, term_collection, section_collection]
payloads = [[], [], []]
current_column_index = 0  # 0 for collections, 1 for payloads
current_index = 0
current_collection_index = 0
current_payload_index = 0


def switch_collection(direction):
    global current_collection_index, current_payload_index
    if direction == "left":
        current_collection_index = (current_collection_index - 1) % len(collections)
    elif direction == "right":
        current_collection_index = (current_collection_index + 1) % len(collections)
    current_payload_index = 0

# def switch_payload(button):
#     global current collection index, current_payload_index
    
#     if current_list:  # Check if the list is not empty
#         if button == leftButton:
#             current_payload_index = (current_payload_index - 1) % len(current_list)
#         elif button == rightButton:
#             current_payload_index = (current_payload_index + 1) % len(current_list)

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
    finally:
        # Close the MongoDB connection
        if client:
            client.close()

def get_display_name(collection, index):
    # Add collection-specific logic to get the display name
    if collection == courses_collection:
        return collection[index]["courseName"]
    elif collection == term_collection:
        return collection[index]["term"]
    elif collection == section_collection:
        return collection[index]["section"]

def display_current_state():
    if current_column_index == 0:
        current_column = "Collections"
    elif current_column_index == 1:
        current_column = "Payloads"
    current_collection = collections[current_collection_index]
    current_payload = payloads[current_collection_index]
    print(f"Selected Column: {current_column}")
    print(f"Selected Collection: {current_collection.name}")
    print(f"Selected Payload: {current_payload}")



def switch_column(direction):
    global current_column_index, current_index
    if direction == "up" or direction == "down":
        current_column_index = (current_column_index + 1) % 2
    current_index = 0



def handle_button_press(button):
    if button == upButton or button == downButton:
        switch_column("up" if button == upButton else "down")
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
    except Exception as e:
        print(f"Error generating attendance report: {e}")
    finally:
        # Close the MongoDB connection
        if client:
            client.close()
    
    
        

try:
    while True:
        upButton.when_pressed = lambda: handle_button_press(upButton)
        downButton.when_pressed = lambda: handle_button_press(downButton)
        leftButton.when_pressed = lambda: handle_button_press(leftButton)
        rightButton.when_pressed = lambda: handle_button_press(rightButton)

except KeyboardInterrupt:
    print("Program terminated.")