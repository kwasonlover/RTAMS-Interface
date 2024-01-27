from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
import keyboard
import time

# Initialize MongoClient
client = MongoClient("mongodb+srv://ClintCalumpad:StrongPassword121@attendancemonitoringsys.uigzk5u.mongodb.net/?retryWrites=true&w=majority")
db = client["rtams-dev"]
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


def checkSelectedRow(): #display to lcd
    if selected_row:
        print(">", selected_key)
        print(selected_value)
    else:
        print(selected_key)
        print(">", selected_value)

# pprint(data_dict)
# Main loop
try:
    while True:

        # Display current payload
        print("\n\nCurrent Payload:")
        pprint(payload)

        # Display options
        print("Options:")
        print("[W] or [D] To select if you want to change category or the category key")
        print("[A] or [S] To Change for the category or value")

        checkSelectedRow()

        # Simulate keyboard events using input()
        key_press = input("Press Enter to simulate button press:") #kahit wala na

        if key_press.lower() == 'w' or key_press.lower() == 's':
            #make selected_row = !selected_row (forgive me but this is the idea in javascript, i'm not too familiar with python)
            selected_row = not selected_row #selectedRow = !selectedRow
            print("\n")
            checkSelectedRow()

        elif key_press.lower() == 'a':
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


        elif key_press.lower() == 'd':
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

except KeyboardInterrupt:
    print("Program terminated.")
finally:
    if client:
        client.close()