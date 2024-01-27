from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
from gpiozero import Button

# Initialize MongoClient
client = MongoClient("mongodb+srv://<USERNAME>:<PASSWORD>@<YOUR_CLUSTER_URL>/?retryWrites=true&w=majority")
db = client["your_database_name"]
courses_collection = db["courses"]
terms_collection = db["terms"]
sections_collection = db["sections"]

# Fetch data from MongoDB and build a dictionary with lists
data_dict = {}

# Fetch courses and convert the cursor to a list
courses = list(courses_collection.find())
data_dict["courses"] = courses

# Fetch terms and convert the cursor to a list
terms = list(terms_collection.find())
data_dict["terms"] = terms

# Fetch sections and convert the cursor to a list
sections = list(sections_collection.find())
data_dict["sections"] = sections

# Define the simplified payload object with empty strings
payload = {
    "course": "",
    "section": "",
    "term": "",
}

# GPIO Buttons
up_button = Button(17, pull_up=False)
down_button = Button(18, pull_up=False)
left_button = Button(27, pull_up=False)
right_button = Button(22, pull_up=False)

# Variable to track the selected row
selected_row = True  # Set to True to initially cycle through data_dict keys

# Function to update payload based on the selected key
def update_payload(selected_key, selected_value):
    global payload
    if selected_row:
        payload[selected_key] = selected_value
    else:
        payload[selected_key] = data_dict[selected_key][selected_value]

# Main loop
try:
    while True:
        # Handle GPIO button events
        if up_button.is_pressed:
            if selected_row:
                # Cycle through data_dict keys
                selected_key_index = list(data_dict.keys()).index(selected_key)
                selected_key = list(data_dict.keys())[(selected_key_index - 1) % len(data_dict)]
            else:
                # Cycle through values of the selected key
                selected_value_index = list(data_dict[selected_key]).index(selected_value)
                selected_value = list(data_dict[selected_key])[(selected_value_index - 1) % len(data_dict[selected_key])]

            update_payload(selected_key, selected_value)

        elif down_button.is_pressed:
            if selected_row:
                # Cycle through data_dict keys
                selected_key_index = list(data_dict.keys()).index(selected_key)
                selected_key = list(data_dict.keys())[(selected_key_index + 1) % len(data_dict)]
            else:
                # Cycle through values of the selected key
                selected_value_index = list(data_dict[selected_key]).index(selected_value)
                selected_value = list(data_dict[selected_key])[(selected_value_index + 1) % len(data_dict[selected_key])]

            update_payload(selected_key, selected_value)

        elif left_button.is_pressed:
            selected_row = True

        elif right_button.is_pressed:
            selected_row = False
            selected_key = list(data_dict.keys())[0]  # Set the initial selected key
            selected_value = list(data_dict[selected_key])[0]  # Set the initial selected value

        # Print the updated payload
        print("Updated Payload:")
        pprint(payload)

except KeyboardInterrupt:
    print("Program terminated.")
finally:
    # Close the MongoDB connection
    if client:
        client.close()
