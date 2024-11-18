import socket
import requests

# Constants
MIST_API_TOKEN = 'xh9oBdbYQllXCmCh5Ad63h3Y3enrewPWrDD37XpYA5f1ealYTPJQEb2FMkmo0DBi9vFIiLJpNlHd6fM95Zog8e0NldKTnOol'
ORG_ID = '15e7597e-9b06-4381-8443-16aba95c5e0d'
BASE_URL = 'https://api.eu.mist.com/api/v1'

# Get the system hostname
hostname = socket.gethostname()
print(f"User's Hostname: {hostname}")

# Get the system's IP address
ip_address = socket.gethostbyname(hostname)
print(f"User's IP Address: {ip_address}")

# Set headers for the API request
headers = {
    "Authorization": f"Token {MIST_API_TOKEN}",
    "Content-Type": "application/json"
}

# Floor message dictionary
floor_messages = {
    "2f": "Printer is located on the 2nd floor.",
    "3f": "Printer is located on the 3rd floor.",
    "4f": "Printer is located on the 4th floor.",
    "5f": "Printer is located on the 5th floor.",
    "6f": "Printer is located on the 6th floor.",
    "7f": "Printer is located on the 7th floor.",
    "8f": "Printer is located on the 8th floor.",
    "9f": "Printer is located on the 9th floor.",
    "10f": "Printer is located on the 10th floor."
}

# Step 1: Get list of all sites
try:
    sites_url = f"{BASE_URL}/orgs/{ORG_ID}/sites"
    sites_response = requests.get(sites_url, headers=headers)
    sites_response.raise_for_status()
    sites_data = sites_response.json()
    
    # Initialize a variable to track if a matching AP is found
    connected_ap = None

    # Step 2: Loop through each site to check connected clients
    for site in sites_data:
        site_id = site.get('id')
        site_name = site.get('name')

        print(f"\nChecking site: {site_name}")

        # API endpoint for retrieving connected clients in the site
        clients_url = f"{BASE_URL}/sites/{site_id}/stats/clients"

        try:
            clients_response = requests.get(clients_url, headers=headers)
            clients_response.raise_for_status()
            clients_data = clients_response.json()

            # Search for the client with the matching IP address
            for client in clients_data:
                if client.get('ip') == ip_address:  # Match with user's IP
                    connected_ap = client.get('connected_ap_name')  # Store the AP hostname

                    # Check the floor based on AP hostname
                    floor_message = "Printer location could not be determined."
                    for floor_key, message in floor_messages.items():
                        if floor_key in connected_ap:
                            floor_message = message
                            break
                    
                    print(f"Connected Access Point at site '{site_name}': {connected_ap}")
                    print(floor_message)
                    break

            # If a connected AP was found, stop further site checks
            if connected_ap:
                break

        except requests.exceptions.RequestException as e:
            print(f"Error retrieving clients for site {site_name}: {e}")

    # If no connected AP was found after all sites were checked
    if not connected_ap:
        print("\nNo matching access point found for the user's IP address.")

except requests.exceptions.RequestException as e:
    print(f"Error retrieving site list: {e}")
