import requests
import csv

# Constants
MIST_API_TOKEN = 'xh9oBdbYQllXCmCh5Ad63h3Y3enrewPWrDD37XpYA5f1ealYTPJQEb2FMkmo0DBi9vFIiLJpNlHd6fM95Zog8e0NldKTnOol'
ORG_ID = '15e7597e-9b06-4381-8443-16aba95c5e0d'
BASE_URL = 'https://api.eu.mist.com/api/v1'

# Output CSV file
OUTPUT_FILE = "sites_list.csv"

# Set headers for the API request
headers = {
    "Authorization": f"Token {MIST_API_TOKEN}",
    "Content-Type": "application/json"
}

# Fetch site names and their IDs, and export to a CSV file
try:
    # API endpoint for retrieving sites
    sites_url = f"{BASE_URL}/orgs/{ORG_ID}/sites"

    # Make the GET request
    response = requests.get(sites_url, headers=headers)
    response.raise_for_status()  # Raise an error for HTTP issues

    # Parse the JSON response
    sites_data = response.json()

    # Prepare data for CSV
    formatted_data = []
    for site in sites_data:
        site_name = site.get('name', 'Unknown')
        site_id = site.get('id', 'Unknown')
        formatted_data.append({"Site Name": site_name, "SiteID": site_id})

    # Write data to a CSV file
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Site Name", "SiteID"])
        writer.writeheader()  # Write the header row
        writer.writerows(formatted_data)  # Write the site data rows

    print(f"Site data successfully exported to {OUTPUT_FILE}")

except requests.exceptions.RequestException as e:
    print(f"Error fetching sites: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
