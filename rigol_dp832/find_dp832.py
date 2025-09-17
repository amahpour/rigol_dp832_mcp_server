#!/usr/bin/env python3
"""
Simple DP832 Network Discovery

This script will automatically find your Rigol DP832 on the network.
"""

import sys
import os
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add current directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pyvisa
    from rigol_dp832.rigol_dp import DP832
    VISA_AVAILABLE = True
except ImportError:
    VISA_AVAILABLE = False
    print("Error: PyVISA not available. Please install: pip install pyvisa")
    sys.exit(1)

def get_local_network():
    """Get the local network range"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return ".".join(local_ip.split(".")[:-1])
    except:
        return "192.168.1"  # Default fallback

def ping_ip(ip):
    """Ping a single IP address"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False

def test_dp832_connection(ip):
    """Test if IP has a DP832"""
    try:
        resource_string = f"TCPIP0::{ip}::5555::SOCKET"
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_string, read_termination="\n", timeout=2000)
        
        # Try to get device ID
        id_response = inst.query("*IDN?")
        inst.close()
        rm.close()
        
        # Check if it's a Rigol DP832
        if "RIGOL" in id_response.upper() and "DP832" in id_response.upper():
            return id_response.strip()
        return False
    except:
        return False

def find_dp832():
    """Find DP832 on the network"""
    print("🔍 Searching for Rigol DP832 on the network...")
    print("This may take a minute...")
    
    # Get local network
    network_base = get_local_network()
    print(f"Scanning network: {network_base}.x")
    
    # First, find responsive hosts
    print("\nStep 1: Finding responsive hosts...")
    responsive_ips = []
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {}
        for i in range(1, 255):
            ip = f"{network_base}.{i}"
            futures[executor.submit(ping_ip, ip)] = ip
        
        for future in as_completed(futures):
            ip = futures[future]
            if future.result():
                responsive_ips.append(ip)
                print(f"  ✓ {ip}")
    
    if not responsive_ips:
        print("❌ No responsive hosts found. Check your network connection.")
        return None
    
    print(f"\nFound {len(responsive_ips)} responsive hosts")
    
    # Second, test each for DP832
    print("\nStep 2: Testing for DP832 devices...")
    
    for ip in responsive_ips:
        print(f"  Testing {ip}...", end=" ")
        device_id = test_dp832_connection(ip)
        if device_id:
            print(f"🎉 FOUND DP832!")
            print(f"\nDevice Information:")
            print(f"  IP Address: {ip}")
            print(f"  Device ID: {device_id}")
            print(f"  VISA Resource: TCPIP0::{ip}::5555::SOCKET")
            return ip, device_id
        else:
            print("✗")
    
    print("\n❌ No DP832 found on the network.")
    return None

def main():
    """Main function"""
    print("Rigol DP832 Network Discovery")
    print("=" * 40)
    
    result = find_dp832()
    
    if result:
        ip, device_id = result
        print(f"\n✅ SUCCESS! Your DP832 is at: {ip}")
        print(f"\nTo use it in your code:")
        print(f"ps = DP832(")
        print(f"    conn_type='VISA',")
        print(f"    visa_resource_string='TCPIP0::{ip}::5555::SOCKET'")
        print(f")")
    else:
        print(f"\n❌ DP832 not found.")
        print(f"\nTroubleshooting:")
        print(f"1. Make sure your DP832 is connected to the network")
        print(f"2. Check that SCPI over Ethernet is enabled on the DP832")
        print(f"3. Verify the device has a valid IP address")
        print(f"4. Try running: ping {get_local_network()}.1")

if __name__ == "__main__":
    main()
