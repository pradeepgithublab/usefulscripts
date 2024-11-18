import socket
from io import StringIO
import pandas as pd
import requests

# Constants
SUBNET_TO_SITE_URL = 'https://printerbucket001.s3.us-east-1.amazonaws.com/subnet2site.csv'
SITE_TO_PRINTER_URL = 'https://printerbucket001.s3.us-east-1.amazonaws.com/site2printers.csv'

# Get the system hostname and IP address
hostname = socket.gethostname()
print(f"User's Hostname: {hostname}")

ip_address = socket.gethostbyname(hostname)
print(f"User's IP Address: {ip_address}")

# Function to determine subnet mask from IP address
def get_subnet(ip):
    subnet = ".".join(ip.split(".")[:3]) + ".0/24"
    return subnet

# Fetch CSV files from URLs
def fetch_csv(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        # Normalize column names by stripping spaces
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        print(f"Fetched CSV from {url}. Columns: {df.columns.tolist()}")
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSV from {url}: {e}")
        return None

# Main script
try:
    # Determine the user's subnet
    user_subnet = get_subnet(ip_address)
    print(f"User's Subnet: {user_subnet}")

    # Fetch the subnet-to-site mapping CSV
    subnet_to_site_df = fetch_csv(SUBNET_TO_SITE_URL)
    if subnet_to_site_df is None:
        raise Exception("Failed to fetch subnet-to-site mapping.")

    # Ensure the 'Subnet' column exists
    if 'Subnet' not in subnet_to_site_df.columns:
        raise KeyError(f"'Subnet' column not found in subnet-to-site mapping CSV. Columns: {subnet_to_site_df.columns.tolist()}")

    # Find the site for the user's subnet
    site_info = subnet_to_site_df[subnet_to_site_df['Subnet'] == user_subnet]
    if site_info.empty:
        print("No site information found for the user's subnet.")
        exit()

    site_name = site_info['Site'].iloc[0]
    print(f"User's Site: {site_name}")

    # Fetch the site-to-printer mapping CSV
    site_to_printer_df = fetch_csv(SITE_TO_PRINTER_URL)
    if site_to_printer_df is None:
        raise Exception("Failed to fetch site-to-printer mapping.")

    # Ensure the 'Site' column exists
    if 'Site' not in site_to_printer_df.columns:
        raise KeyError(f"'Site' column not found in site-to-printer mapping CSV. Columns: {site_to_printer_df.columns.tolist()}")

    # Find the printers for the user's site
    printer_info = site_to_printer_df[site_to_printer_df['Site'] == site_name]
    if printer_info.empty:
        print(f"No printers found for the site '{site_name}'.")
        exit()

    # Display printer information
    print(f"Printers at site '{site_name}':")
    for _, row in printer_info.iterrows():
        printer_name = row.get('Printer', 'Unknown')  # Default to 'Unknown' if 'Printer' column is missing
        location = row.get('Location', 'Unknown')  # Default to 'Unknown' if 'Location' column is missing
        print(f"Printer Name: {printer_name}, Location: {location}")
except Exception as e:
    print(f"An error occurred: {e}")
