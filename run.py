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
courses_collection = db["courses"]
terms_collection = db["term"]
sections_collection = db["sections"]

data_dict = {}

courses = list(courses_collection.find({}, {'courseName': 1}))
data_dict["courses"] = courses

terms = list(terms_collection.find({}, {'term': 1}))
data_dict["term"] = terms

sections = list(sections_collection.find({}, {'section': 1}))
data_dict["sections"] = sections

payload = {
    "courses": data_dict["courses"][0],
    "term": data_dict["term"][0],
    "sections": data_dict["sections"][0],
}

selected_row = True  

selected_key = list(payload.keys())[0]  # Set the initial selected key
selected_value = payload[selected_key]  # Set the initial selected value

print("initialized selected key: ", selected_key)
print("initialized selected value: ", selected_value)


def update_payload(selected_key, selected_value):
    global payload
    print("key from update",payload[selected_key])
    index_in_data_dict = list(data_dict[selected_key]).index(selected_value)

    payload[selected_key] = data_dict[selected_key][index_in_data_dict]


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
        time.sleep(0.75)

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
            scroll_text(selected_value['courseName'], 2)
        elif selected_key == 'term':
            scroll_text(selected_value['term'], 2)
        elif selected_key == 'sections':
            scroll_text(selected_value['section'], 2)
    else:
        lcd.text(selected_key, 1)
        if selected_key == 'courses':
            scroll_text("> " + selected_value['courseName'], 2)
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

def handle_attendance_logic(student):
    global payload
    try:
        current_date = datetime.now().strftime("%Y:%m:%d")
        current_time = datetime.now().strftime("%H:%M")
        existing_attendance = attendances_collection.find_one({
            "student": student["_id"],
            "courseCode": payload["courses"]["_id"],
            "date": current_date,
        })
        
        if existing_attendance:
            if existing_attendance["timeIn"] and not existing_attendance["timeOut"]:
                existing_attendance["timeOut"] = current_time
                attendances_collection.update_one(
                    {"_id": existing_attendance["_id"]},
                    {"$set": {"timeOut": existing_attendance["timeOut"]}}
                )
                print("Updated attendance record.")
                lcd.clear()
                scroll_text("Updated attendance", 1)
                scroll_text("record.", 2)
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
                "courseCode": payload["courses"]["_id"],
                "date": current_date,
                "term": payload["term"]["term"],  
                "section": payload["sections"]["section"],
                "timeIn": current_time,
                "timeOut": None,
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