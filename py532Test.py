from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from pymongo import MongoClient
from datetime import datetime


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
        
        # Find the Term in mongodb
        section_value = "4-5"
        section = section_collection.find_one({"section": section_value})
        
        # Find the term in mongodb
        term_value = "2023-2024"
        term = term_collection.find_one({"term": term_value})
        
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
                "term": term,  # Replace with actual term
                "section": section,  # Replace with actual section
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