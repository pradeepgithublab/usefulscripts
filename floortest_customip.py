import requests

# Constants
MIST_API_TOKEN = 'xh9oBdbYQllXCmCh5Ad63h3Y3enrewPWrDD37XpYA5f1ealYTPJQEb2FMkmo0DBi9vFIiLJpNlHd6fM95Zog8e0NldKTnOol'
ORG_ID = '15e7597e-9b06-4381-8443-16aba95c5e0d'
BASE_URL = 'https://api.eu.mist.com/api/v1'

# Custom IP address
custom_ip = "10.130.27.74"
print(f"Custom IP Address: {custom_ip}")

# Set headers for the API request
headers = {
    "Authorization": f"Token {MIST_API_TOKEN}",
    "Content-Type": "application/json"
}

# Step 1: Get the list of all sites
try:
    sites_url = f"{BASE_URL}/orgs/{ORG_ID}/sites"
    sites_response = requests.get(sites_url, headers=headers)
    sites_response.raise_for_status()
    sites_data = sites_response.json()

    # Step 2: Loop through each site to check connected clients
    connected_ap = None  # Variable to store the connected AP name

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

            # Search for the client with the matching custom IP address
            for client in clients_data:
                if client.get('ip') == custom_ip:  # Match with the custom IP
                    connected_ap = client.get('connected_ap_name')  # Store the AP hostname
                    print(f"Connected Access Point at site '{site_name}': {connected_ap}")
                    break

            # If a connected AP was found, stop further site checks
            if connected_ap:
                break

        except requests.exceptions.RequestException as e:
            print(f"Error retrieving clients for site {site_name}: {e}")

    # If no connected AP was found after all sites were checked
    if not connected_ap:
        print("\nNo matching access point found for the custom IP address.")

except requests.exceptions.RequestException as e:
    print(f"Error retrieving site list: {e}")
