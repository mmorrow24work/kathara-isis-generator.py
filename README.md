# kathara-isis-generator

Creating the startup files for a complex kathara network would be very difficult and very time consuming if done manually,
so best practice is to create them using a programmatic method in the same way we create startup scripts for routers and switches.

A common method is to use a spreadsheet which contains all the logic and access to the lab.conf data; another is to create a 
program which will use the lab.conf as an input and output all the startup files. 

Both methods have their pros and cons, but we have chosen to use Python3 scripts because it allowed us to use AI to create 
the code based on prompts that describe the requirement.

This code was created using AI (https://claude.ai/) based on the following prompt:

Create a Python3 script that reads a kathara lab.conf file as input and will output all the kathara startup files.

Use ISIS routing and assign IPs to all interfaces and check that they are online and use the most appropriate subnet masks - 
e.g. use /30 networks for point-to-point connections and /29 networks elsewhere if possible, otherwise use /28 or /27 etc. 

Include debug code and comments to help with troubleshooting.

Ensure snmp_manager which will run Zabbix server has the IP 192.168.1.7 because the Zabbix agents will be configured to respond to the Zabbix agents.

Mick Morrow  | Solutions Architect
Email: Mick.Morrow@telent.com
Mobile: 07974398922
Web: www.telent.com
