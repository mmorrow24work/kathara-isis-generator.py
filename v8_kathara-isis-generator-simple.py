#!/usr/bin/env python3

"""
Kathara ISIS Configuration Generator - Back to Basics
Based on your working v3.2 with minimal first-run improvements
"""

import os
import sys
import re
import argparse
import hashlib
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Default configuration values
DEFAULT_CONFIG = {
    'ISIS_AREA': '0001',
    'ISIS_PROCESS': 'MAIN',
    'MGMT_SUBNET': '192.168.10',
    'PTP_SUBNET': '10.0',
    'MULTI_SUBNET': '10',
    'DNS_SERVER': '1.1.1.1',
    'ROUTER_PATTERNS': 'frr|FRR|quagga|vyos|router',
    'PC_PATTERNS': 'alpine|ubuntu|debian|pc|client|workstation',
    'MANAGER_PATTERNS': 'zabbix|snmp|manager|monitor|nms'
}

# Color codes for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_info(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}", file=sys.stderr)

def print_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}", file=sys.stderr)

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}", file=sys.stderr)

def print_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}", file=sys.stderr)

class SimpleISISGenerator:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.devices = []
        self.device_networks = {}
        self.device_images = {}
        self.device_types = {}
        
    def load_config_file(self, config_file: str):
        """Load configuration from file"""
        if config_file and os.path.isfile(config_file):
            print_info(f"Loading configuration from {config_file}")
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip().strip('\'"')
            except Exception as e:
                print_error(f"Error loading config file: {e}")
                sys.exit(1)
    
    def detect_device_type(self, image: str) -> str:
        """Detect device type from image name"""
        router_patterns = self.config['ROUTER_PATTERNS']
        pc_patterns = self.config['PC_PATTERNS']
        manager_patterns = self.config['MANAGER_PATTERNS']
        
        if re.search(router_patterns, image, re.IGNORECASE):
            return "router"
        elif re.search(manager_patterns, image, re.IGNORECASE):
            return "manager"
        elif re.search(pc_patterns, image, re.IGNORECASE):
            return "pc"
        else:
            return "generic"
    
    def parse_lab_conf(self, lab_conf: str):
        """Parse lab.conf and extract device information"""
        if not os.path.isfile(lab_conf):
            print_error("lab.conf file not found!")
            sys.exit(1)
        
        print_info("Parsing lab.conf...")
        
        try:
            with open(lab_conf, 'r') as f:
                content = f.read()
        except Exception as e:
            print_error(f"Error reading lab.conf: {e}")
            sys.exit(1)
        
        devices = set()
        
        # Parse device configurations
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('LAB_'):
                continue
            
            if '=' in line:
                left, right = line.split('=', 1)
                right = right.strip().strip('"\'')
                
                pattern = r'^([^[]+)\[([^]]+)\]$'
                device_match = re.match(pattern, left)
                if device_match:
                    device, property_name = device_match.groups()
                    devices.add(device)
                    
                    if property_name == 'image':
                        self.device_images[device] = right
                        self.device_types[device] = self.detect_device_type(right)
                    elif property_name.isdigit():
                        if device not in self.device_networks:
                            self.device_networks[device] = []
                        self.device_networks[device].append(f"{property_name}:{right}")
        
        self.devices = sorted(list(devices))
        
        for device in self.devices:
            if device not in self.device_networks:
                self.device_networks[device] = []
            if device not in self.device_images:
                self.device_images[device] = "unknown"
                self.device_types[device] = "generic"
    
    def identify_frr_routers(self) -> List[str]:
        """Identify which devices need ISIS configuration"""
        frr_routers = []
        
        print_info("Identifying routers...")
        
        for device in self.devices:
            device_type = self.device_types[device]
            
            if device_type == "router":
                frr_routers.append(device)
                print_success(f"Found router: {device} (image: {self.device_images[device]})")
        
        if not frr_routers:
            print_warning("No routers found in lab.conf")
            sys.exit(0)
        
        return frr_routers
    
    def is_management_network(self, network_name: str) -> bool:
        """Check if network is management network"""
        has_manager = False
        has_router = False
        
        for device in self.devices:
            networks = self.device_networks[device]
            if any(network_name in net for net in networks):
                device_type = self.device_types[device]
                if device_type == "manager":
                    has_manager = True
                elif device_type == "router":
                    has_router = True
        
        return has_manager and has_router
    
    def generate_ip_for_network(self, network_name: str, device_index: int, total_devices: int) -> str:
        """Generate IP addresses for interfaces"""
        if self.is_management_network(network_name):
            return f"{self.config['MGMT_SUBNET']}.{10 + device_index}/24"
        else:
            # Use the network name directly if it's numeric, otherwise hash it
            try:
                # If network_name is a number, use it directly to avoid conflicts
                subnet_num = int(network_name)
                # Ensure it's in valid range
                subnet_num = (subnet_num % 250) + 1
            except ValueError:
                # If not numeric, use hash but with better collision avoidance
                hash_obj = hashlib.md5(network_name.encode())
                hash_hex = hash_obj.hexdigest()
                # Use more bits to reduce collisions
                subnet_num = (int(hash_hex[:4], 16) % 250) + 1
            
            if total_devices == 2:
                # For /30 networks: .1 and .2 are the only usable IPs
                # device_index starts at 1, so we use device_index directly (1,2)
                return f"{self.config['PTP_SUBNET']}.{subnet_num}.{device_index}/30"
            else:
                return f"{self.config['MULTI_SUBNET']}.{subnet_num}.0.{device_index + 1}/24"
    
    def is_external_network(self, network_name: str, frr_routers: List[str]) -> bool:
        """Check if a network connects to external devices"""
        for device in self.devices:
            networks = self.device_networks[device]
            if any(network_name in net for net in networks):
                if device not in frr_routers:
                    return True
        return False
    
    def find_router_on_network(self, network_name: str, frr_routers: List[str]) -> Optional[str]:
        """Find the router connected to a specific network"""
        for router in frr_routers:
            if any(network_name in net for net in self.device_networks[router]):
                return router
        return None
    
    def get_router_ip_on_network(self, router: str, network_name: str, frr_routers: List[str]) -> Optional[str]:
        """Get the IP address of a router on a specific network"""
        router_position = 0
        device_count = 0
        
        # Count devices on this network and find router position
        for device in self.devices:
            if any(network_name in net for net in self.device_networks[device]):
                device_count += 1
                if device == router:
                    router_position = device_count
        
        if router_position > 0:
            router_ip = self.generate_ip_for_network(network_name, router_position, device_count)
            return router_ip.split('/')[0]
        
        return None
    
    def safe_write_file(self, filename: str, content: str, executable: bool = False):
        """Safely write content to file with error handling"""
        try:
            with open(filename, 'w') as f:
                f.write(content)
            
            if executable:
                os.chmod(filename, 0o755)
            
            print_success(f"Generated {filename}")
            
        except Exception as e:
            print_error(f"Failed to write {filename}: {e}")
            sys.exit(1)
    
    def generate_isis_config(self, router_name: str, router_index: int, frr_routers: List[str]):
        """Generate simple, working ISIS configuration"""
        print_info(f"Generating ISIS configuration for {router_name}...")
        
        networks = self.device_networks[router_name]
        startup_file = f"{router_name}.startup"
        
        content = f"""#!/bin/bash

# Startup configuration for {router_name}
# Generated by Kathara ISIS Generator - Simple & Working Version
# Device image: {self.device_images[router_name]}

echo "Starting configuration for {router_name}..."

# Wait for interfaces to be ready
sleep 5

"""
        
        # Configure interfaces
        external_interface = ""
        
        for network_info in networks:
            if not network_info:
                continue
            
            try:
                if_num, network_name = network_info.split(':', 1)
            except ValueError:
                continue
            
            # Count devices on this network
            device_count = 0
            device_position = 0
            for device in self.devices:
                if any(network_name in net for net in self.device_networks[device]):
                    device_count += 1
                    if device == router_name:
                        device_position = device_count
            
            # Generate IP address
            ip_addr = self.generate_ip_for_network(network_name, device_position, device_count)
            
            # Check if this is an external network
            is_external = self.is_external_network(network_name, frr_routers)
            
            if is_external and not external_interface:
                external_interface = f"eth{if_num}"
            
            content += f"""# Configure interface eth{if_num}
echo "Configuring eth{if_num} with IP {ip_addr} on network {network_name}"
ip addr add {ip_addr} dev eth{if_num}
ip link set eth{if_num} up

"""
        
        # Enable IP forwarding
        content += """# Enable IP forwarding
echo "Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1

"""
        
        # Add NAT if there's an external interface
        if external_interface:
            content += f"""# Configure NAT for external connectivity
echo "Configuring NAT on {external_interface}..."
iptables -t nat -A POSTROUTING -o {external_interface} -j MASQUERADE

"""
        
        # Simple FRR configuration
        content += """# Enable ISIS daemon in FRR
echo "Enabling ISIS daemon..."
sed -i 's/isisd=no/isisd=yes/' /etc/frr/daemons

# Start FRR daemons
echo "Starting FRR daemons..."
/usr/lib/frr/frrinit.sh start

# Wait for FRR to start
sleep 8

# Restart FRR to ensure isisd is loaded
echo "Restarting FRR with ISIS enabled..."
/usr/lib/frr/frrinit.sh restart

# Wait for restart
sleep 5

# Check if isisd is running, start manually if needed
if ! pgrep isisd > /dev/null; then
    echo "Starting isisd manually..."
    /usr/lib/frr/isisd -d
    sleep 3
fi

# Configure FRR ISIS via vtysh
echo "Configuring ISIS routing..."
vtysh << 'FRRCMD'
configure terminal
"""
        
        # Generate proper NET address
        system_id = f"{0:04d}.{0:04d}.{router_index + 1:04d}"
        net_address = f"49.{self.config['ISIS_AREA']}.{system_id}.00"
        
        content += f"""router isis {self.config['ISIS_PROCESS']}
 net {net_address}
 is-type level-2-only
 log-adjacency-changes
 redistribute connected level-2
exit
"""
        
        # Add ALL interfaces to ISIS
        for network_info in networks:
            if not network_info:
                continue
            
            try:
                if_num, network_name = network_info.split(':', 1)
            except ValueError:
                continue
            
            content += f"""interface eth{if_num}
 ip router isis {self.config['ISIS_PROCESS']}
exit
"""
        
        content += f"""write
exit
FRRCMD

# Set DNS resolver
echo "nameserver {self.config['DNS_SERVER']}" > /etc/resolv.conf

echo "Configuration completed for {router_name}"
echo "Device {router_name} is ready!"

# Keep container running
tail -f /dev/null
"""
        
        self.safe_write_file(startup_file, content, executable=True)
    
    def generate_basic_config(self, device_name: str, frr_routers: List[str]):
        """Generate simple configuration for non-router devices"""
        startup_file = f"{device_name}.startup"
        if os.path.isfile(startup_file):
            print_info(f"Startup file already exists for {device_name}, skipping...")
            return
        
        networks = self.device_networks[device_name]
        device_type = self.device_types[device_name]
        
        print_info(f"Generating configuration for {device_name} (type: {device_type})...")
        
        content = f"""#!/bin/bash

# Startup configuration for {device_name}
# Generated by Kathara ISIS Generator - Simple Version
# Device type: {device_type}
# Device image: {self.device_images[device_name]}

echo "Starting configuration for {device_name}..."

# Wait for interfaces to be ready
sleep 3

"""
        
        # Configure interfaces and find the best gateway
        gateways = []
        
        for network_info in networks:
            if not network_info:
                continue
            
            try:
                if_num, network_name = network_info.split(':', 1)
            except ValueError:
                continue
            
            device_count = 0
            device_position = 0
            for device in self.devices:
                if any(network_name in net for net in self.device_networks[device]):
                    device_count += 1
                    if device == device_name:
                        device_position = device_count
            
            ip_addr = self.generate_ip_for_network(network_name, device_position, device_count)
            
            content += f"""# Configure interface eth{if_num}
echo "Configuring eth{if_num} with IP {ip_addr}"
ip addr add {ip_addr} dev eth{if_num}
ip link set eth{if_num} up

"""
            
            # Find router on this network for gateway
            router = self.find_router_on_network(network_name, frr_routers)
            if router:
                router_ip = self.get_router_ip_on_network(router, network_name, frr_routers)
                if router_ip:
                    gateways.append(router_ip)
        
        # Add default route using the first available gateway with proper priority
        if gateways:
            gateway = gateways[0]  # Use the first available gateway
            content += f"""# Remove any existing default routes
ip route del default || true

# Add default route with higher priority than Docker's default
echo "Adding default route via {gateway}"
ip route add default via {gateway} metric 100

# Ensure this route persists and has priority
sleep 2
ip route del default dev eth1 || true  # Remove Docker's default route if present

"""
        
        content += f"""# Set DNS resolver
echo "nameserver {self.config['DNS_SERVER']}" > /etc/resolv.conf

echo "Configuration completed for {device_name}"

# Keep container running
tail -f /dev/null
"""
        
        self.safe_write_file(startup_file, content, executable=True)
    
    def run(self, args):
        """Main execution function"""
        print_info("Kathara ISIS Configuration Generator - Simple & Working Version")
        print_info("=" * 65)
        
        # Load configuration file if specified
        self.load_config_file(args.config)
        
        # Override with command line arguments
        if args.isis_area:
            self.config['ISIS_AREA'] = args.isis_area
        if args.isis_process:
            self.config['ISIS_PROCESS'] = args.isis_process
        if args.mgmt_subnet:
            self.config['MGMT_SUBNET'] = args.mgmt_subnet
        if args.ptp_subnet:
            self.config['PTP_SUBNET'] = args.ptp_subnet
        if args.multi_subnet:
            self.config['MULTI_SUBNET'] = args.multi_subnet
        if args.dns_server:
            self.config['DNS_SERVER'] = args.dns_server
        
        # Check if lab.conf exists
        if not os.path.isfile(args.lab_conf):
            print_error(f"lab.conf file not found: {args.lab_conf}")
            sys.exit(1)
        
        # Display current configuration
        print_info("Configuration:")
        for key, value in self.config.items():
            print_info(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Parse lab.conf
        self.parse_lab_conf(args.lab_conf)
        
        # Identify FRR routers
        frr_routers = self.identify_frr_routers()
        
        # Generate ISIS configuration for each router
        for router_index, router in enumerate(frr_routers):
            self.generate_isis_config(router, router_index, frr_routers)
        
        # Generate basic configuration for other devices
        for device in self.devices:
            if device not in frr_routers:
                self.generate_basic_config(device, frr_routers)
        
        print_success("Configuration generation complete!")
        print_info("Generated files:")
        
        for device in self.devices:
            startup_file = f"{device}.startup"
            if os.path.isfile(startup_file):
                print_info(f"  - {startup_file}")
        
        print_info("")
        print_info("Usage:")
        print_info("  kathara lstart                    # Start the lab")
        print_info("  python3 verify-simple.py          # Verify the lab")
        print_info("  kathara lclean                     # Stop the lab")

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="Kathara ISIS Configuration Generator - Simple & Working",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('lab_conf', help='Kathara lab.conf file')
    parser.add_argument('-c', '--config', help='Load configuration from file')
    parser.add_argument('--isis-area', help=f'ISIS area ID (default: {DEFAULT_CONFIG["ISIS_AREA"]})')
    parser.add_argument('--isis-process', help=f'ISIS process name (default: {DEFAULT_CONFIG["ISIS_PROCESS"]})')
    parser.add_argument('--mgmt-subnet', help=f'Management subnet prefix (default: {DEFAULT_CONFIG["MGMT_SUBNET"]})')
    parser.add_argument('--ptp-subnet', help=f'Point-to-point subnet prefix (default: {DEFAULT_CONFIG["PTP_SUBNET"]})')
    parser.add_argument('--multi-subnet', help=f'Multi-access subnet prefix (default: {DEFAULT_CONFIG["MULTI_SUBNET"]})')
    parser.add_argument('--dns-server', help=f'DNS server IP (default: {DEFAULT_CONFIG["DNS_SERVER"]})')
    
    return parser

def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    generator = SimpleISISGenerator()
    try:
        generator.run(args)
    except KeyboardInterrupt:
        print_error("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

