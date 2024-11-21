import requests
import pandas as pd
import ipaddress
from charset_normalizer import detect

# Constants
API_TOKEN = 'xh9oBdbYQllXCmCh5Ad63h3Y3enrewPWrDD37XpYA5f1ealYTPJQEb2FMkmo0DBi9vFIiLJpNlHd6fM95Zog8e0NldKTnOol'
ORG_ID = '15e7597e-9b06-4381-8443-16aba95c5e0d'
BASE_URL = 'https://api.eu.mist.com/api/v1'
CIDR_RANGES = [
    '10.192.8.0/22', '10.192.4.1/22'
]
# Custom MAC and IP to search
CUSTOM_IP = '192.168.7.230'
CUSTOM_MAC = 'bc03581fae1e'

# Headers for authentication
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

PRINTER_CSV_URL = "https://printerbucket001.s3.us-east-1.amazonaws.com/phasevprinters.csv"

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

def fetch_printer_location_mapping():
    """Fetch the printer and location mapping from the CSV file."""
    try:
        # Download the file and detect encoding
        response = requests.get(PRINTER_CSV_URL)
        response.raise_for_status()
        raw_data = response.content
        detected_encoding = detect(raw_data)['encoding']
       # print(f"Detected file encoding: {detected_encoding}")

        # Decode content manually and handle errors
        decoded_content = raw_data.decode(detected_encoding, errors='replace')

        # Read the CSV from the decoded string
        from io import StringIO
        df = pd.read_csv(StringIO(decoded_content))
        return df
    except Exception as e:
        print(f"Error fetching printer location mapping: {e}")
        return pd.DataFrame()

def find_printer_and_location(ap_name, printer_data):
    """Find the Printer and Location for the given Access Point name."""
    for _, row in printer_data.iterrows():
        floor = row.get("Floor")  # Safely fetch the floor value
        if floor and isinstance(floor, str):  # Ensure it's not None and is a string
            if floor in ap_name:  # Check if the floor exists in the AP name
                return row.get("Printer", "Unknown Printer"), row.get("Location", "Unknown Location")
    return "Unknown Printer", "Unknown Location"

def find_ap_for_custom_mac_ip(clients):
    """Find the Access Point name for the given custom MAC and IP."""
    for client in clients:
        if client.get('mac') == CUSTOM_MAC and client.get('ip') == CUSTOM_IP:
            return client.get('ap_name', 'Unknown')
    return None

def main():
    # Fetch the SiteID dynamically based on CIDR range
    site_id = fetch_site_id_from_csv(CIDR_RANGES)

    if not site_id:
        print("No matching SiteID found for the CIDR ranges.")
        return

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

    # Fetch Printer and Location mapping
    printer_data = fetch_printer_location_mapping()

    # Find the Access Point name for the custom MAC and IP
    ap_name = find_ap_for_custom_mac_ip(clients_with_ap_names)

    if ap_name:
        printer, location = find_printer_and_location(ap_name, printer_data)
        print(f"Access Point Name: {ap_name}")
        print(f"Printer: {printer}")
        print(f"Location: {location}")
    else:
        print(f"No Access Point found for MAC '{CUSTOM_MAC}' and IP '{CUSTOM_IP}'.")

if __name__ == "__main__":
    main()
