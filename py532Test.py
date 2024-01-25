from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from pymongo import MongoClient
from datetime import datetime
from gpiozero import Button

import time


# # Set up GPIO
# upButton = Button(17)
# downButton = Button(18)
# leftButton = Button(22)
# rightButton = Button(27)


# # Define categories and payloads
# categories = ["Course", "Term", "Section"]
# course_payloads = ["Calculus 1", "Chemistry for Engineers", "Computer Engineering as a Discipline", "Computer Engineering Technology 1"]
# term_payloads = ["2023-2024", "2024-2025", "2025-2026", "2026-2027", "2027-2028"]
# section_payloads = ["4-1", "4-2", "4-3", "4-4", "4-5"]

print("Ready. Tap the NFC Tag to create/update an attendance.")

# Initialize MongoClient
client = MongoClient("mongodb+srv://ClintCalumpad:StrongPassword121@attendancemonitoringsys.uigzk5u.mongodb.net/?retryWrites=true&w=majority")
db = client["rtams-dev"]
students_collection = db["students"]
courses_collection = db["courses"]
attendances_collection = db["attendances"]
term_collection = db["term"]
section_collection = db["sections"]

# Initialize pn532 components
pn532 = Pn532_i2c()
pn532.SAMconfigure()

# # Initial state and category index
# current_category_index = 0

# def getSelectedPayload():
#      if categories[current_category_index] == "Course":
#         return course_payloads[0]  # Replace with actual logic to get the selected course
#      elif categories[current_category_index] == "Term":
#         return term_payloads[0]  # Replace with actual logic to get the selected term
#      elif categories[current_category_index] == "Section":
#         return section_payloads[0]  # Replace with actual logic to get the selected section

# def handleButtonPress(button):
#     global current_category_index
    
#     if button == upButton:
#         current_category_index = (current_category_index - 1) % len(categories)
#     elif button == downButton:
#         current_category_index = (current_category_index + 1) % len(categories) 
#     elif button == leftButton:
#         payload = getSelectedPayload()
    
#     print((categories[current_category_index], payload))
        

try:
    card_data = pn532.read_mifare().get_data()
    card_data_formatted = ' '.join(format(x, '02X') for x in card_data)
    nfc_uid = ' '.join(card_data_formatted.split()[7:])
    
    # Find the student based on the NFC UID
    student = students_collection.find_one({"nfcUID": nfc_uid})
    if not student:
        print("Student not found for the given NFC UID.")
    else:
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
    
    print("Press Ctrl+C to exit.")
    # while True:
    #     # Check button presses and handle them
    #     if upButton.is_pressed:
    #         print("Up button is pressed.")
    #         handleButtonPress(upButton)
    #     elif downButton.is_pressed:
    #         print("Down button is pressed.")
    #         handleButtonPress(downButton)
    #     elif leftButton.is_pressed:
    #         print("Left button is pressed.")
    #         handleButtonPress(leftButton)
    #     elif rightButton.is_pressed:
    #         print("Right button is pressed.")
    #         handleButtonPress(rightButton)

    #     time.sleep(0.1)
            
except Exception as e:
    print(f"Error generating attendance report: {e}")
finally:
    # Close the MongoDB connection
    if client:
        client.close()