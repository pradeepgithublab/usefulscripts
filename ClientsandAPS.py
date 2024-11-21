import requests
import pandas as pd
from prettytable import PrettyTable

# Constants
API_TOKEN = 'xh9oBdbYQllXCmCh5Ad63h3Y3enrewPWrDD37XpYA5f1ealYTPJQEb2FMkmo0DBi9vFIiLJpNlHd6fM95Zog8e0NldKTnOol'
ORG_ID = '15e7597e-9b06-4381-8443-16aba95c5e0d'
SITE_ID = '7ddd12b8-7ecf-451f-9f52-88b3b7ae30c3'
BASE_URL = 'https://api.eu.mist.com/api/v1'

# Headers for authentication
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_connected_clients(site_id):
    """Fetch the list of connected clients."""
    try:
        url = f"{BASE_URL}/sites/{site_id}/stats/clients"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching connected clients: {e}")
        return []

def fetch_access_points(site_id):
    """Fetch the list of access points for a site."""
    try:
        url = f"{BASE_URL}/sites/{site_id}/devices"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access points: {e}")
        return []

def map_ap_names_to_clients(clients, access_points):
    """Map the access point names to connected clients."""
    ap_mapping = {ap['mac']: ap['name'] for ap in access_points}
    for client in clients:
        ap_mac = client.get('ap_mac')
        client['ap_name'] = ap_mapping.get(ap_mac, 'Unknown')
    return clients

def display_clients_in_table(clients):
    """Display connected clients in a tabular format."""
    table = PrettyTable()
    table.field_names = ["MAC Address", "IP Address", "AP Hostname"]

    for client in clients:
        table.add_row([
            client.get('mac', 'N/A'),
            client.get('ip', 'N/A'),
            client.get('ap_name', 'Unknown')
        ])

    print(table)

def main():
    print("Fetching connected clients and access points...")

    # Fetch data
    clients = fetch_connected_clients(SITE_ID)
    access_points = fetch_access_points(SITE_ID)

    if not clients:
        print("No clients found.")
        return

    if not access_points:
        print("No access points found.")
        return

    # Map AP names to clients
    clients_with_ap_names = map_ap_names_to_clients(clients, access_points)

    # Display in tabular format
    print("Connected Users:")
    display_clients_in_table(clients_with_ap_names)

if __name__ == "__main__":
    main()
