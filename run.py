from pymongo import MongoClient
from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from pprint import pprint
from datetime import datetime, timedelta
from bson import ObjectId
from gpiozero import Button
from rpi_lcd import LCD

import threading
import time

lcd = LCD(bus=0, width=16, rows=2)

data_lock = threading.Lock()

upButton = Button(17, pull_up=False)
downButton = Button(23, pull_up=False)
leftButton = Button(27, pull_up=False)
rightButton = Button(22, pull_up=False)

pn532 = Pn532_i2c()
pn532.SAMconfigure()

client = MongoClient("mongodb+srv://ClintCalumpad:StrongPassword121@attendancemonitoringsys.uigzk5u.mongodb.net/?retryWrites=true&w=majority")
db = client["rtams-dev"]
students_collection = db["students"]
attendances_collection = db["attendances"]
classlistsCollection = db["classlists"]
terms_collection = db["terms"]
sections_collection = db["sections"]
sessions_collection = db["sessions"]

data_dict = {}

classlists = list(classlistsCollection.find({}, {'sectionCode' : 1, 'subjectCode': 1, 'term': 1, 'students' : 1})) #sectionCode, subjectCode, term, students
# courses copy initialization
courses = classlists.copy()
data_dict["courses"] = courses 

terms = list(terms_collection.find({}, {'term': 1}))
data_dict["term"] = terms

sections = list(sections_collection.find({}, {'section': 1}))
data_dict["sections"] = sections

print("sections from api", sections)

payload = {
    "courses": data_dict["courses"][0],
    "term": data_dict["term"][0],
    "sections": data_dict["sections"][0],
}

selected_row = True   

selected_key = list(payload.keys())[0]  # Set the initial selected key
selected_value = payload[selected_key]  # Set the initial selected value

print("initialized selected key: ", selected_key, type(selected_key))
print("initialized selected value: ", selected_value)
print("")
print("Classlist", classlists)
print("payload", payload)
print("")


print(str(payload["sections"]["_id"]))
print(payload["courses"]["sectionCode"])
print(str(payload["term"]["_id"]))
print(payload["courses"]["term"])

def update_payload(selected_key, selected_value):
    global payload
    global courses
    print("key from update", payload[selected_key])
    index_in_data_dict = list(data_dict[selected_key]).index(selected_value)
    payload[selected_key] = data_dict[selected_key][index_in_data_dict]
    
    if selected_key != "courses":
        filtered_courses = []
        plSection = str(payload["sections"]["_id"])
        plTerm = str(payload["term"]["_id"])
        
        print("")
        print("payload section", plSection, type(plSection))
        print("payload term", plTerm, type(plTerm))
        print("")
        for course in classlists:
            clSection = str(course["sectionCode"])
            clTerm = str(course["term"])
            if clSection == plSection and clTerm == plTerm:
                filtered_courses.append(course)

        courses = filtered_courses.copy() if filtered_courses else classlists.copy()
        payload["courses"] = courses[0]
        print("")
        print("filtered courses",filtered_courses)
        print("original classlist from api", classlists)
        print("Courses copy:", courses)
        data_dict["courses"] = courses

    # index_in_data_dict = list(data_dict[selected_key]).index(selected_value)
    # payload[selected_key] = data_dict[selected_key][index_in_data_dict]
 
def handle_button_press(button):
    global selected_row, selected_key, selected_value, data_lock
    with data_lock:
        if button == upButton or button == downButton:
            selected_row = not selected_row 
        elif button == leftButton:
            if not selected_row:
                current_index = list(data_dict[selected_key]).index(selected_value)


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
        checkSelectedRow()
        display_lcd()
        time.sleep(0.25)
        print("\n\nat button press courses copy:", courses)
        print("\n\npayload:", payload)

def checkSelectedRow(): 
    print("\n\n")
    if selected_row:
        print(">", selected_key)
        print(selected_value)
    else:
        print(selected_key)
        print(">", selected_value)
    print("current payload:", payload)

def scroll_text(text, row):
    if len(text) > 16:
        for i in range(len(text) - 15):
            lcd.text(text[i:i+16], row)
            time.sleep(0.2)
    else:
        lcd.text(text, row)


def display_lcd():
    if selected_row:
        lcd.text("> " + selected_key, 1)
        if selected_key == 'courses':
            scroll_text(selected_value['subjectCode'], 2)
        elif selected_key == 'term':
            scroll_text(selected_value['term'], 2)
        elif selected_key == 'sections':
            scroll_text(selected_value['section'], 2)
    else:
        lcd.text(selected_key, 1)
        if selected_key == 'courses':
            scroll_text("> " + selected_value['subjectCode'], 2)
        elif selected_key == 'term':
            scroll_text("> " + selected_value['term'], 2)
        elif selected_key == 'sections':
            scroll_text("> " + selected_value['section'], 2)


# NFC-Related code/modules


def read_nfc():
    try:
        lcd.text('RTAMS', 1)
        sleep(1)
        scroll_text('Real-Time Attendance Monitoring System', 2)
        sleep(1)
        display_lcd()
        while True: 
            card_data = pn532.read_mifare().get_data()
            card_data_formatted = ' '.join(format(x, '02X') for x in card_data)
            nfc_uid = ' '.join(card_data_formatted.split()[7:])

            student = students_collection.find_one({"nfcUID": nfc_uid})
            if not student:
                print("Student not found. Contact an administrator.")
                lcd.clear()
                scroll_text("Student not found.", 1)
                scroll_text("Contact an administrator.", 2)
                sleep(1)
                lcd.clear()
                display_lcd()
            else:
                handle_attendance_logic(student)

    except Exception as e:
        print(f"Error generating attendance report: {e}")
        scroll_text(f"Error generating attendance report: {e}")
        sleep(1)
        lcd.clear()
        display_lcd()
        
def calculate_hours_rendered(time_in_str, time_out_str):
    time_format = "%H:%M"
    time_in = datetime.strptime(time_in_str, time_format)
    time_out = datetime.strptime(time_out_str, time_format)
    time_difference = time_out - time_in
    hours_rendered = time_difference.seconds // 3600  # Convert time difference to hours
    minutes_rendered = (time_difference.seconds % 3600) // 60  # Convert remaining seconds to minutes
    return minutes_rendered


def handle_attendance_logic(student):
    global payload
    try:

	#check if student is in payload.courses.students[]
        current_date = datetime.now().strftime("%Y:%m:%d")
        current_time = datetime.now().strftime("%H:%M")

        # Check if there is an existing session for the current course where checked is False
        existing_session = sessions_collection.find_one({
            "classlist": payload["courses"]["_id"],
            "checked": False
        })
        
        # If no such session exists, create a new session
        if not existing_session:
            new_session = {
                "classlist": payload["courses"]["_id"],
                "date": current_date,
                "checked": False
            }
            saved_session = sessions_collection.insert_one(new_session)
            print(f"New session created with ID: {saved_session.inserted_id}")
        
        existing_attendance = attendances_collection.find_one({
            "student": student["_id"],
            "course": payload["courses"]["_id"], #course nalang
            "date": current_date,
        })

	
        
        if existing_attendance:
            if existing_attendance["timeIn"] and not existing_attendance["timeOut"]:
                existing_attendance["timeOut"] = current_time
                minutes_rendered = calculate_hours_rendered(existing_attendance["timeIn"], current_time)

		#get the difference of minutes between time in and out
		#existing_attendance["hoursRendered"]= the difference in minutes, even though it says hours rendered


                attendances_collection.update_one(
                    {"_id": existing_attendance["_id"]},
                    {"$set": {"timeOut": existing_attendance["timeOut"], "hoursRendered": minutes_rendered}} 
                    #also set the hoursRendered
                )
                print("Updated attendance record.")
                lcd.clear()
                scroll_text("Updated", 1)
                scroll_text("attendance.", 2)
                sleep(1)
                lcd.clear()
                display_lcd()
            else:
                print("Attendance already exists for this course today.")
                lcd.clear()
                scroll_text("Attendance already exists", 1)
                scroll_text("for this course today.", 2)
                sleep(1)
                lcd.clear()
                display_lcd()
                
        else:
            new_attendance = {
                "student": student["_id"],
                "nfcUID": student["nfcUID"],
                "studentName": student["name"],
                "course": payload["courses"]["_id"],
                "date": current_date,
                "timeIn": current_time,
                "timeOut": None,
		        "hoursRendered": 0
            }
            saved_report = attendances_collection.insert_one(new_attendance)
            print(new_attendance)
            print(f"New attendance report created with ID: {saved_report.inserted_id}")
            lcd.clear()
            lcd.text("Attendance", 1)
            lcd.text("recorded.", 2)
            sleep(1)
            lcd.clear()
            display_lcd()
        time.sleep(2)
    except Exception as e:
        print(f"Error generating attendance report: {e}")
        scroll_text(f"Error generating attendance report: {e}", 1)



nfc_thread = threading.Thread(target=read_nfc)
nfc_thread.daemon = False  # Set the thread as a daemon to exit when the main program exits
nfc_thread.start()

try:
    while True:
        upButton.when_pressed = lambda: handle_button_press(upButton)
        downButton.when_pressed = lambda: handle_button_press(downButton)
        leftButton.when_pressed = lambda: handle_button_press(leftButton)
        rightButton.when_pressed = lambda: handle_button_press(rightButton)

        time.sleep(0.2)
except KeyboardInterrupt:
    print("Program terminated.")
    lcd.clear()
finally:
    if client:
        client.close()