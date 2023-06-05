# MAC Lookup and VLAN Tagging Script

This Python script is designed to perform MAC address lookup in a network infrastructure and optionally tag the corresponding switch ports with a VLAN ID. It utilizes the Netmiko library for SSH connectivity to network devices and supports Cisco-formatted, Linux-formatted, and Windows-formatted MAC addresses.

## Prerequisites

- Python 3.x
- `netmiko` library (`pip install netmiko`)
- `PyYAML` library (`pip install pyyaml`)

## Usage

To run the script, execute the following command:

```
python mac_lookup.py
```

### Input

The script requires a file named `MAC_file.txt` in the same directory. This file should contain a list of MAC addresses, with each MAC address on a new line.

### Output

The script will output the following information:

- Whether the MAC address is Cisco-formatted, Linux-formatted, or Windows-formatted
- The number of switches where the MAC address is found
- For each switch:
  - The switch name
  - The switch port where the MAC address is found
  - The VLAN ID of the port (if provided)

### Username and Password

The script will prompt you to enter your username and password for authentication. Please provide the appropriate credentials to connect to the network devices.

### VLAN ID

You have the option to provide a VLAN ID. If you choose to do so, the script will configure the switch ports where the MAC address is found with the specified VLAN ID. If you don't provide a VLAN ID, the script will only perform the MAC address lookup.

## Script Structure

The script consists of the following functions:

### signal_handler(frame, signal)

This function is a signal handler for graceful exit on SIGINT (e.g., pressing Ctrl+C).

### get_input(Macfiled)

This function receives user input from the terminal and checks the length of the MAC address. If the length is correct, it passes the MAC address to `analyze_mac()` for further analysis.

### get_login()

This function receives user input from the terminal for the username, password, and VLAN ID (optional). It checks the input for validity and returns the entered values.

### analyze_mac(mac)

This function checks whether the MAC address is Cisco-formatted, Linux-formatted, or Windows-formatted based on predefined patterns. It extracts the MAC address and returns it along with the detected format.

### convert_cisco_mac_to_linux(mac)

This function converts a Cisco-formatted MAC address to Linux format.

### convert_linux_mac_to_cisco(mac)

This function converts a Linux-formatted MAC address to Cisco format.

### convert_windows_mac_to_cisco(mac)

This function converts a Windows-formatted MAC address to Cisco format.

### open_yaml_file(yamlfile)

This function opens a YAML file containing switch information and returns its content.

### lookup_mac(username, password, mac, yamlfile, vlanid)

This function performs the MAC address lookup by iterating through the switch information obtained from the YAML file. It connects to each switch, retrieves the MAC address table, and checks if the MAC address is present. If found, it increments a counter, stores the switch name, VLAN ID, and port information, and optionally configures the port with the provided VLAN ID.

### SSH_to_SW(username, password, swip, sshport, swname)

This function establishes an SSH connection to a switch and retrieves the MAC address table using the Netmiko library. It returns the switch name and MAC address table.

### Tag_port(username, password, swip, sshport, swname, port, vlanid)

This function configures the switch port with the provided VLAN ID using SSH and the Netmiko library.

### main()

This is the main

 function that orchestrates the execution of the script. It handles the signal handler registration, reads the MAC addresses from the file, prompts for login credentials, and performs the MAC address lookup and optional VLAN tagging.

## Example Usage

Here is an example of how to use the script:

1. Create a file named `MAC_file.txt` in the same directory and add the MAC addresses to be looked up, each on a new line.

2. Create a YAML file named `switches.yml` containing the switch information. The format should be as follows:

   ```yaml
   switch_site:
     - name: switch_name
       mgmt_ip: switch_ip
       port: ssh_port
   ```

   Replace `switch_site` with a meaningful name for your switch site, `switch_name` with the switch's hostname, `switch_ip` with the management IP address, and `ssh_port` with the SSH port number.

3. Run the script using the command:

   ```
   python mac_lookup.py
   ```

4. Enter your username, password, and VLAN ID (if desired) when prompted.

5. The script will perform the MAC address lookup and display the results on the terminal.

6. If you provided a VLAN ID, the script will also configure the switch ports where the MAC address is found with the specified VLAN ID.

Note: Make sure to modify the script and YAML file according to your network environment and requirements.

Enjoy using the MAC lookup and VLAN tagging script!

## Author

[Badr-eddine](https://www.linkedin.com/in/badreddine-aharchi)
