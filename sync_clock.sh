#!/bin/bash

# Function to check network connectivity
check_network() {
    while ! ping -q -c 1 google.com &> /dev/null; do
        echo "Network not available. Retrying..."
        sleep 2  # Adjust the sleep interval (in seconds) as needed
    done
}

# Call the function to check network connectivity
check_network

# Network is now available, synchronize the clock
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"
echo "Clock synchronized successfully."
