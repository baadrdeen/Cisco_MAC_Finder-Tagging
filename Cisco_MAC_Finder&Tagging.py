#!/usr/bin/python
__author__ = "AHARCHI_Badr-eddine"
import re
import signal
import sys
import yaml

from getpass import getpass
from netmiko import ConnectHandler


def signal_handler(frame, signal):
    '''
    Exit gracefully on SIGINT
    '''

    sys.exit()


def get_input(Macfiled):
    '''
    Receive user input from terminal
    check length, if correct, pass to
    AnalyzeMac()
    '''
    #user_input = sys.argv[1].strip()
    # get the mac @ from the file
    user_input = Macfiled

    # Analyze Mac @
    if len(user_input) >= 14 and len(user_input) <= 17:
        MAC, mac_format = analyze_mac(user_input)
    else:
        print('\033[91m', end="")
        print("[❌] wrong MAC address")
        print('\033[0m', end="")
        exit()

    return MAC, mac_format

def get_login():
    '''
    Receive user input from terminal

    '''
    username = input("[+] Username: ")
    password = getpass("[+] Password: ")
    vlanid = input("[+] New VLAN ID or hit enter: ")

    return username, password, vlanid

def analyze_mac(mac):
    '''
    Check whether the MAC is a Cisco
    formatted MAC or a normal MAC.
    '''
    # Check based on patterns
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


def convert_cisco_mac_to_linux(mac):
    '''
    Gets a MAC and converts it to
    Linux format
    '''
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


def convert_linux_mac_to_cisco(mac):
    '''
    Gets a MAC and converts it to
    Cisco format
    '''
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


def convert_windows_mac_to_cisco(mac):
    '''
    Gets a MAC and converts it to
    Cisco format
    '''
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


def open_yaml_file(yamlfile):
    '''
    opens a YAML file and returns
    its content to lookup_mac()
    '''
    with open(yamlfile, "r") as swfile:
        switches = yaml.safe_load(swfile)
    return switches


def lookup_mac(username, password, mac, yamlfile, vlanid):
    '''
    receives MAC table and looks for
    intended mac
    '''
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

        # Break the loop if the mac is seen in a site
        if seen_in_site:
            break

        site_items = len(site)
        print(f"[+] Looking up {site} site on {site_items} devices.")
        print("-" * 50)

        for sw in switches[site]:

            if seen_in_sw:
                if 'Fa' in port:
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
                if mac in line:
                    counter += 1
                    switch_list.append(swname)
                    vlan = line.split()[0]
                    mactype = line.split()[2]
                    port = line.split()[3]
                    seen_in_site = True
                    seen_in_sw = True
                    if vlanid:
                        Tag_port(username, password, swip, sshport, swname, port, vlanid)


    print(f"[+] MAC was seen on {counter} switch(es)")

    for sw in switch_list:
        print(f"\t{sw} on port {port} and VLAN {vlan}", flush=True)

    print('\033[0m')


def SSH_to_SW(username, password, swip, sshport, swname):
    '''
    SSH to switches and look
    for MAC address
    '''
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
        mac_table = net_connect.send_command(get_mac_command, delay_factor=5)
        net_connect.send_command("\n", delay_factor=5)
        net_connect.disconnect()
        return swname, mac_table
    except Exception as e:
        print('\033[91m', end="")
        print(f"[-] Could not connect to {swname} using {swip}")
        print(e)
        print('\033[0m', end="")
        pass

def Tag_port(username, password, swip, sshport, swname, port, vlanid):
    '''
    SSH to switches and configure the port
    '''
    #get_mac_command = "show mac address-table"
    tagging_command = ['interface '+ port,
                       'shutdown',
                       'switchport voice vlan ' + vlanid,
                       'no shutdown',
                       'end'
                       'write']
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
        mac_table = net_connect.send_config_set(tagging_command, delay_factor=5)
        net_connect.send_command("\n", delay_factor=5)
        print(f"|---> [*] Interface {port} Configured with VLAN {vlanid}")
        net_connect.disconnect()
        pass
    except Exception as e:
        print('\033[91m', end="")
        print(f"[-] Could not connect to configure {swname} using {swip}")
        print(e)
        print('\033[0m', end="")
        pass


def main():
    
    signal.signal(signal.SIGINT, signal_handler)
    mac_list = open ('MAC_file.txt')
    username, password, vlanid = get_login()
    
    for mac in mac_list:
        mac=mac.strip()
        mac, platform = get_input(mac)
        if platform == "linux":
            mac = convert_linux_mac_to_cisco(mac)
        elif platform == "windows":
            mac = convert_windows_mac_to_cisco(mac)
        
        lookup_mac(username, password, mac, "switches.yml", vlanid)


if __name__ == "__main__":
    main()
