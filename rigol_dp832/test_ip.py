#!/usr/bin/env python3
"""
Test a specific IP address for Rigol DP832 connectivity.

Usage:
    python test_ip.py 192.168.1.100
"""

import sys
import os

# Add current directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pyvisa
    VISA_AVAILABLE = True
except ImportError:
    VISA_AVAILABLE = False


def test_ip(ip: str, port: int = 5555) -> str | None:
    """
    Test if a Rigol DP832/DP821/DP712 is at the specified IP address.
    
    Args:
        ip: IP address to test
        port: Port number (default: 5555)
    
    Returns:
        Device ID string if found, None otherwise
    """
    if not VISA_AVAILABLE:
        raise ImportError("PyVISA not available. Please install: pip install pyvisa")
    
    try:
        resource_string = f"TCPIP0::{ip}::{port}::SOCKET"
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_string, read_termination="\n", timeout=2000)
        
        # Try to get device ID
        id_response = inst.query("*IDN?")
        inst.close()
        rm.close()
        
        # Check if it's a Rigol DP series power supply
        id_upper = id_response.upper()
        if "RIGOL" in id_upper and any(model in id_upper for model in ["DP832", "DP821", "DP712"]):
            return id_response.strip()
        return None
    except Exception:
        return None


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python test_ip.py <ip_address> [port]")
        print("Example: python test_ip.py 192.168.1.100")
        print("Example: python test_ip.py 192.168.1.100 5555")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    
    print(f"Testing {ip}:{port} for Rigol power supply...")
    
    device_id = test_ip(ip, port)
    
    if device_id:
        print(f"✅ Found device: {device_id}")
        print(f"   VISA Resource: TCPIP0::{ip}::{port}::SOCKET")
    else:
        print(f"❌ No Rigol power supply found at {ip}:{port}")
        print("\nTroubleshooting:")
        print("1. Verify the IP address is correct")
        print("2. Check that SCPI over Ethernet is enabled on the device")
        print("3. Ensure no firewall is blocking port", port)


if __name__ == "__main__":
    main()

