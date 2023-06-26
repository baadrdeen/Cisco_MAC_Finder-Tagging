[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/baadrdeen/Cisco_MAC_Finder-Tagging)
# MAC Lookup and VLAN Tagging Script

This Python script is designed to perform MAC address lookup in a network infrastructure and optionally tag the corresponding switch ports with a VLAN ID. It utilizes the Netmiko library for SSH connectivity to network devices and supports Cisco-formatted, Linux-formatted, and Windows-formatted MAC addresses.

## Prerequisites

- Python 3.x
- `netmiko` library (`pip install netmiko`)
- `PyYAML` library (`pip install pyyaml`)

## Usage

To run the script, execute the following command:

```
python3 Cisco_MAC_Finder&Tagging.py
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

## Example Usage

Here is an example of how to use the script:

1. Edit a file named `MAC_file.txt` in the same directory and add the MAC addresses to be looked up, each on a new line.

2. Edit a YAML file named `switches.yml` containing the switch information. The format should be as follows:

   ```yaml
   switch_site:
     - name: switch_name
       mgmt_ip: switch_ip
       port: ssh_port
   ```

   Replace `switch_site` with a meaningful name for your switch site, `switch_name` with the switch's hostname, `switch_ip` with the management IP address, and `ssh_port` with the SSH port number.

3. Run the script using the command:

   ```
   python3 Cisco_MAC_Finder&Tagging.py
   ```

4. Enter your username, password, and VLAN ID (if desired) when prompted.

5. The script will perform the MAC address lookup and display the results on the terminal.

6. If you provided a VLAN ID, the script will also configure the switch ports where the MAC address is found with the specified VLAN ID.

Note: Make sure to modify the script and YAML file according to your network environment and requirements.

Certainly! Here's the formatted use case that you can insert into your README file on GitHub:

## Use Case Scenario
A network administrator wants to streamline the process of locating MAC addresses in the network and assigning them to specific VLANs. They have a list of MAC addresses stored in a file (MAC_file.txt), and they want to automate the process of searching for these MAC addresses across multiple switches and configuring the associated switch ports with a specific VLAN.

The administrator runs the script and is prompted to enter their login credentials (username and password) and the VLAN ID they want to assign to the switch ports. The script then reads the MAC addresses from the file, one by one, and performs the following steps for each MAC address:

1. Analyzes the MAC address format to determine if it is in Cisco, Linux, or Windows format.
2. Converts the MAC address to Cisco format if necessary.
3. Searches for the MAC address in the MAC address table of each switch defined in the switches.yml file.
4. If the MAC address is found on a switch, the script records the switch name, VLAN, and port where the MAC address is located.
5. If a VLAN ID is provided, the script configures the switch port with the specified VLAN using SSH commands.
6. After processing all MAC addresses, the script displays the number of switches where each MAC address was found and provides a summary of the switch names, ports, and VLANs associated with each MAC address.

By using this script, the network administrator can save time and effort by automating the process of MAC address lookup and VLAN configuration, making network management more efficient and less error-prone.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please create an issue or submit a pull request.

## Author

[Badr-eddine](https://www.linkedin.com/in/badreddine-aharchi)

## License

This project is licensed under the [MIT License](LICENSE).
