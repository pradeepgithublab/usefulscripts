import socket
import ipaddress
import subprocess
import threading

# Define printer-specific ports to check
PRINTER_PORTS = [9100, 515, 631]

# Function to get host IP and subnet mask
def get_ip_and_subnet():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    # Assuming a common subnet mask; update if needed
    subnet_mask = "255.255.255.0"
    return ip_address, subnet_mask

# Convert subnet mask to CIDR prefix
def subnet_to_cidr(subnet_mask):
    return sum([bin(int(x)).count('1') for x in subnet_mask.split('.')])

# Ping an IP to check if it's alive
def ping_ip(ip):
    try:
        # Cross-platform ping (-c for Linux/Mac, -n for Windows)
        command = ["ping", "-c", "1", ip] if socket.gethostname().find('.') != -1 else ["ping", "-n", "1", ip]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

# Scan a specific IP for printer ports
def scan_printer(ip, results):
    for port in PRINTER_PORTS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((ip, port)) == 0:
                    results.append(ip)
                    break  # No need to check further ports
        except Exception:
            pass

# Discover printers on the network
def discover_printers(ip_address, subnet_mask):
    print(f"Scanning network for printers based on IP: {ip_address} and Subnet Mask: {subnet_mask}")

    # Generate subnet range
    cidr_prefix = subnet_to_cidr(subnet_mask)
    network = ipaddress.IPv4Network(f"{ip_address}/{cidr_prefix}", strict=False)

    # Step 1: Ping sweep to find active hosts
    print("Performing ping sweep to find active hosts...")
    active_hosts = []
    threads = []
    for ip in network.hosts():
        t = threading.Thread(target=lambda ip=ip: active_hosts.append(str(ip)) if ping_ip(str(ip)) else None)
        threads.append(t)
        t.start()

        # Limit the number of threads
        if len(threads) > 50:
            for t in threads:
                t.join()
            threads = []

    # Wait for all ping threads to finish
    for t in threads:
        t.join()

    print(f"Active hosts found: {len(active_hosts)}")

    # Step 2: Scan active hosts for printer ports
    print("Scanning active hosts for printers...")
    printer_results = []
    threads = []
    for ip in active_hosts:
        t = threading.Thread(target=scan_printer, args=(ip, printer_results))
        threads.append(t)
        t.start()

        # Limit the number of threads
        if len(threads) > 50:
            for t in threads:
                t.join()
            threads = []

    # Wait for all port scan threads to finish
    for t in threads:
        t.join()

    return printer_results

# Main script
if __name__ == "__main__":
    try:
        # Get the machine's IP address and subnet mask
        ip_address, subnet_mask = get_ip_and_subnet()

        # Discover printers on the network
        printers = discover_printers(ip_address, subnet_mask)

        if printers:
            print("\nAvailable Printers on the Network:")
            for printer_ip in printers:
                print(f"Printer IP: {printer_ip}")
        else:
            print("\nNo printers found on the network.")

    except Exception as e:
        print(f"An error occurred: {e}")
