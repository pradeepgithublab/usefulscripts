import requests
import pandas as pd
import ipaddress

# Constants
API_TOKEN = 'xh9oBdbYQllXCmCh5Ad63h3Y3enrewPWrDD37XpYA5f1ealYTPJQEb2FMkmo0DBi9vFIiLJpNlHd6fM95Zog8e0NldKTnOol'
ORG_ID = '15e7597e-9b06-4381-8443-16aba95c5e0d'
BASE_URL = 'https://api.eu.mist.com/api/v1'
CIDR_RANGES = [
    '10.192.8.0/22', '10.192.4.1/22'
]

# Custom MAC and IP to search
CUSTOM_MAC = 'e8c829e304ae'
CUSTOM_IP = '192.168.7.146'

# Headers for authentication
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_site_id_from_csv(cidr_ranges):
    """Fetch the matching SiteID from the CSV file based on CIDR ranges."""
    try:
        csv_url = 'https://printerbucket001.s3.us-east-1.amazonaws.com/site_id_subnet.csv'
        df = pd.read_csv(csv_url)

        for cidr in cidr_ranges:
            for _, row in df.iterrows():
                subnet = row['CIDR']
                site_id = row['SiteID']
                if ipaddress.IPv4Network(cidr).overlaps(ipaddress.IPv4Network(subnet)):
                    return site_id

        return None  # No match found
    except Exception as e:
        print(f"Error fetching SiteID from CSV: {e}")
        return None

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

def find_ap_for_custom_mac_ip(clients):
    """Find the Access Point name for the given custom MAC and IP."""
    for client in clients:
        if client.get('mac') == CUSTOM_MAC and client.get('ip') == CUSTOM_IP:
            return client.get('ap_name', 'Unknown')
    return None

def main():
    print("Fetching SiteID from the CSV file based on CIDR ranges...")

    # Fetch the SiteID dynamically based on CIDR range
    site_id = fetch_site_id_from_csv(CIDR_RANGES)

    if not site_id:
        print("No matching SiteID found for the CIDR ranges.")
        return

    print(f"Using SiteID: {site_id} for the API calls...")

    # Fetch data
    clients = fetch_connected_clients(site_id)
    access_points = fetch_access_points(site_id)

    if not clients:
        print("No clients found.")
        return

    if not access_points:
        print("No access points found.")
        return

    # Map AP names to clients
    clients_with_ap_names = map_ap_names_to_clients(clients, access_points)

    # Find the Access Point name for the custom MAC and IP
    ap_name = find_ap_for_custom_mac_ip(clients_with_ap_names)

    if ap_name:
        print(f"Access Point Name for MAC '{CUSTOM_MAC}' and IP '{CUSTOM_IP}': {ap_name}")
    else:
        print(f"No Access Point found for MAC '{CUSTOM_MAC}' and IP '{CUSTOM_IP}'.")

if __name__ == "__main__":
    main()

