#!/usr/bin/env python3
__author__ = "AHARCHI_Badr-eddine"

import re
import signal
import sys
import yaml
from getpass import getpass
from netmiko import ConnectHandler

# Signal handler function to exit gracefully on SIGINT
def signal_handler(frame, signal):
    sys.exit()

# Function to get user input for MAC address from the terminal
def get_input(Macfiled):
    user_input = Macfiled

    # Analyze Mac address
    if len(user_input) >= 14 and len(user_input) <= 17:
        MAC, mac_format = analyze_mac(user_input)
    else:
        print('\033[91m', end="")
        print("[❌] wrong MAC address")
        print('\033[0m', end="")
        exit()

    return MAC, mac_format

# Function to get user login credentials from the terminal
def get_login():
    username = input("[+] Username: ")
    password = getpass("[+] Password: ")
    vlanid = input("[+] New VLAN ID or hit enter: ")

    # Analyze inputs
    if (len(vlanid) >= 1 and len(vlanid) <= 4 and vlanid.strip().isdigit()) or vlanid == '':
        pass
    else:
        print('\033[91m', end="")
        print("[❌] wrong input")
        print('\033[0m', end="")
        exit()

    return username, password, vlanid

# Function to analyze the MAC address format
def analyze_mac(mac):
    cisco_pattern = re.compile(r"([0-9a-fA-F]{4}(?:.[0-9a-fA-F]{4}){2})")
    linux_pattern = re.compile(r"([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})")
    windows_pattern = re.compile(r"([0-9a-fA-F]{2}(?:-[0-9a-fA-F]{2}){5})")

    Cisco_MAC = re.findall(cisco_pattern, mac)
    Linux_MAC = re.findall(linux_pattern, mac)
    Windows_MAC = re.findall(windows_pattern, mac)

    mac_format = ""

    print('\033[1m', end="")
    print('\033[92m', end="")

    if Cisco_MAC:
        MAC = Cisco_MAC[0]
        print(f"[+] Cisco formatted MAC detected")
        mac_format = "cisco"
    elif Linux_MAC:
        MAC = Linux_MAC[0]
        print(f"[+] Linux formatted MAC detected")
        mac_format = "linux"
    elif Windows_MAC:
        MAC = Windows_MAC[0]
        print(f"[+] Windows formatted MAC detected")
        mac_format = "windows"
    else:
        print('\033[91m', end="")
        print(f"[❌] Invalid MAC address: {mac}")
        exit()

    print('\033[0m', end="")

    return MAC, mac_format

# Function to convert Cisco formatted MAC address to Linux format
def convert_cisco_mac_to_linux(mac):
    char_count = 1
    total_chars = 0
    mac_addr = []

    for char in mac.replace(".", ""):
        if char_count == 2 and total_chars != 11:
            mac_addr.append(char + ":")
            char_count = 1
        else:
            mac_addr.append(char)
            char_count += 1

        total_chars += 1

    mac = "".join(x for x in mac_addr)

    return mac

# Function to convert Linux formatted MAC address to Cisco format
def convert_linux_mac_to_cisco(mac):
    char_count = 1
    total_chars = 0
    mac_addr = []

    for char in mac.replace(":", ""):
        if char_count == 4 and total_chars != 11:
            mac_addr.append(char + ".")
            char_count = 1
        else:
            mac_addr.append(char)
            char_count += 1

        total_chars += 1

    mac = "".join(x for x in mac_addr)

    return mac

# Function to convert Windows formatted MAC address to Cisco format
def convert_windows_mac_to_cisco(mac):
    char_count = 1
    total_chars = 0
    mac_addr = []

    for char in mac.replace("-", ""):
        if char_count == 4 and total_chars != 11:
            mac_addr.append(char + ".")
            char_count = 1
        else:
            mac_addr.append(char)
            char_count += 1

        total_chars += 1

    mac = "".join(x for x in mac_addr)

    return mac

# Function to open and read a YAML file
def open_yaml_file(yamlfile):
    with open(yamlfile, "r") as swfile:
        switches = yaml.safe_load(swfile)
    return switches

# Function to look up MAC address in the provided MAC table
def lookup_mac(username, password, mac, yamlfile, vlanid):
    counter = 0
    switches = open_yaml_file(yamlfile)
    sites = switches.keys()
    switch_list = []
    seen_in_site = False
    seen_in_sw = False

    print('\033[1m', end="")
    print('\033[92m', end="")
    print(f"[+] Searching for: ", end="")
    print('\033[94m', end="")
    print(f"{mac}")
    print('\033[92m', end="")

    for site in sites:
        if seen_in_site:
            break

        site_items = len(site)
        print(f"[+] Looking up {site} site on {site_items} devices.")
        print("-" * 50)
      
        for sw in switches[site]:
            if seen_in_sw:
                break

            swname = sw['name']
            swip = sw['mgmt_ip']
            sshport = sw['port']
            swname, mac_table = SSH_to_SW(username, password,
                                          swip, sshport,
                                          swname)

            if not mac_table:
                print('\033[93m', end="")
                print("[-] MAC table fetch was not successful")
                print('\033[0m', end="")
                continue

            for line in mac_table.splitlines():
                if (mac in line) and (('Gi' in line) or ('Fa' in line)):
                    counter += 1
                    switch_list.append(swname)
                    vlan = line.split()[0]
                    port = line.split()[3]
                    seen_in_site = True
                    seen_in_sw = True
                    if vlanid:
                        Tag_port(username, password, swip, sshport, swname, port, vlanid)

    print(f"[+] MAC was seen on {counter} switch(es)")

    for sw in switch_list:
        print(f"\t{sw} on port {port} and VLAN {vlan}", flush=True)

    print('\033[0m')

# Function to establish an SSH connection to a switch and retrieve the MAC address table
def SSH_to_SW(username, password, swip, sshport, swname):
    get_mac_command = "show mac address-table"
    sshport = str(sshport)

    device = {
        'device_type': 'cisco_ios',
        'ip': swip,
        'port': sshport,
        'username': username,
        'password': password,
        'fast_cli': False,
    }

    print('\033[1;36m', end="")
    print(f"[*] Connecting to {swname} using {swip}")
    print('\033[0m', end="")

    try:
        net_connect = ConnectHandler(**device)
        mac_table = net_connect.send_command(get_mac_command, delay_factor=10)
        net_connect.send_command("\n", delay_factor=10)
        net_connect.disconnect()
        return swname, mac_table
    except Exception as e:
        print('\033[91m', end="")
        print(f"[-] Could not connect to {swname} using {swip}")
        print(e)
        print('\033[0m', end="")
        pass

# Function to configure a switch port with a specific VLAN
def Tag_port(username, password, swip, sshport, swname, port, vlanid):
    tagging_command = ['interface '+ port,
                       'shutdown',
                       'switchport voice vlan ' + vlanid,
                       'no shutdown',
                       'end']
    sshport = str(sshport)

    device = {
        'device_type': 'cisco_ios',
        'ip': swip,
        'port': sshport,
        'username': username,
        'password': password,
        'fast_cli': False,
    }

    print('\033[1;36m', end="")
    print(f"|---> [*] Configuring interface {port} with VLAN {vlanid}")
    print('\033[0m', end="")

    try:
        net_connect = ConnectHandler(**device)
        mac_table = net_connect.send_config_set(tagging_command, delay_factor=10)
        net_connect.send_command("\n", delay_factor=10)
        print(f"|---> [*] Interface {port} Configured with VLAN {vlanid}")
        net_connect.disconnect()
        pass
    except Exception as e:
        print('\033[91m', end="")
        print(f"[-] Could not connect to configure {swname} using {swip}")
        print(e)
        print('\033[0m', end="")
        pass

# Main function
def main():
    signal.signal(signal.SIGINT, signal_handler)
    mac_list = open('MAC_file.txt')
    username, password, vlanid = get_login()
    
    for mac in mac_list:
        mac = mac.strip()
        mac, platform = get_input(mac)
        if platform == "linux":
            mac = convert_linux_mac_to_cisco(mac)
        elif platform == "windows":
            mac = convert_windows_mac_to_cisco(mac)
        
        lookup_mac(username, password, mac, "switches.yml", vlanid)

if __name__ == "__main__":
    main()
