#!/usr/bin/env python3
"""
Simple DP832 Network Discovery CLI

Usage:
    python find_dp832.py                           # Auto-discover
    python find_dp832.py 192.168.1.100            # Test specific IP
    python find_dp832.py --network 192.168.68     # Search specific network
    python find_dp832.py -n 192.168.68            # Short form
"""

import sys
import argparse
from discovery import find_first_dp832, test_ip, find_dp832_devices


def main():
    parser = argparse.ArgumentParser(
        description="Find Rigol DP832 devices on the network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python find_dp832.py                           # Auto-discover on local network
  python find_dp832.py 192.168.1.100            # Test specific IP address
  python find_dp832.py --network 192.168.68     # Search 192.168.68.x network
  python find_dp832.py -n 192.168.68            # Short form for network search
  python find_dp832.py --network 10.0.0         # Search 10.0.0.x network (WSL, etc.)
        """
    )
    
    parser.add_argument(
        'ip_address', 
        nargs='?', 
        help='Specific IP address to test'
    )
    parser.add_argument(
        '--network', '-n',
        help='Network base to search (e.g., 192.168.68 for 192.168.68.x)'
    )
    
    args = parser.parse_args()
    
    if args.ip_address:
        # Test specific IP
        print(f"Testing {args.ip_address} for DP832...")
        
        device_id = test_ip(args.ip_address)
        if device_id:
            print(f"✅ DP832 found!")
            print(f"Device: {device_id}")
            print(f"\nTo use it in your code:")
            print(f"from rigol_dp832 import DP832")
            print(f"ps = DP832('{args.ip_address}')")
        else:
            print(f"❌ No DP832 found at {args.ip_address}")
    
    elif args.network:
        # Search specific network
        print(f"🔍 Searching for Rigol DP832 on network {args.network}.x...")
        devices = find_dp832_devices(args.network)
        
        if devices:
            print(f"\n✅ Found {len(devices)} DP832 device(s):")
            for ip, device_id in devices:
                print(f"  {ip}: {device_id}")
                print(f"\nTo use it in your code:")
                print(f"from rigol_dp832 import DP832")
                print(f"ps = DP832('{ip}')")
        else:
            print(f"\n❌ No DP832 found on network {args.network}.x")
            print("\nTroubleshooting:")
            print("1. Make sure your DP832 is connected to the network")
            print("2. Check that SCPI over Ethernet is enabled")
            print("3. Verify the device has a valid IP address")
            print("4. Try a different network base (e.g., 192.168.1, 10.0.0)")
    
    else:
        # Auto-discovery
        print("🔍 Searching for Rigol DP832 on the network...")
        result = find_first_dp832()
        
        if result:
            ip, device_id = result
            print(f"\n✅ SUCCESS! Your DP832 is at: {ip}")
            print(f"Device: {device_id}")
            print(f"\nTo use it in your code:")
            print(f"from rigol_dp832 import DP832")
            print(f"ps = DP832('{ip}')")
        else:
            print("\n❌ No DP832 found on the network.")
            print("\nTroubleshooting:")
            print("1. Make sure your DP832 is connected to the network")
            print("2. Check that SCPI over Ethernet is enabled")
            print("3. Verify the device has a valid IP address")
            print("4. Try specifying a network base: python find_dp832.py --network 192.168.68")


if __name__ == "__main__":
    main()
