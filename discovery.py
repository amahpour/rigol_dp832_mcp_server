"""
Network Discovery Tools for Rigol DP832

This module provides functions to automatically discover DP832 devices on the network.
"""

import socket
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple


def get_local_network() -> str:
    """Get the local network range"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return ".".join(local_ip.split(".")[:-1])
    except:
        return "192.168.1"  # Default fallback


def ping_ip(ip: str) -> bool:
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


def test_dp832_connection(ip: str, port: int = 5555) -> Optional[str]:
    """Test if IP has a DP832 and return device ID if found"""
    try:
        import pyvisa
        resource_string = f"TCPIP0::{ip}::{port}::SOCKET"
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_string, read_termination="\n", timeout=2000)
        
        # Try to get device ID
        id_response = inst.query("*IDN?")
        inst.close()
        rm.close()
        
        # Check if it's a Rigol DP832
        if "RIGOL" in id_response.upper() and "DP832" in id_response.upper():
            return id_response.strip()
        return None
    except:
        return None


def find_dp832_devices(network_base: Optional[str] = None, port: int = 5555) -> List[Tuple[str, str]]:
    """
    Find all DP832 devices on the network
    
    Args:
        network_base: Network base (e.g., "192.168.1"). If None, auto-detect.
        port: SCPI port to test (default: 5555)
    
    Returns:
        List of tuples (ip_address, device_id) for found DP832 devices
    """
    if network_base is None:
        network_base = get_local_network()
    
    print(f"Scanning network {network_base}.x for DP832 devices...")
    
    # First, find responsive hosts
    print("Step 1: Finding responsive hosts...")
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
        print("No responsive hosts found.")
        return []
    
    print(f"\nFound {len(responsive_ips)} responsive hosts")
    
    # Second, test each for DP832
    print(f"\nStep 2: Testing for DP832 devices on port {port}...")
    dp832_devices = []
    
    for ip in responsive_ips:
        print(f"  Testing {ip}...", end=" ")
        device_id = test_dp832_connection(ip, port)
        if device_id:
            print(f"🎉 FOUND DP832!")
            dp832_devices.append((ip, device_id))
        else:
            print("✗")
    
    return dp832_devices


def find_first_dp832(network_base: Optional[str] = None, port: int = 5555) -> Optional[Tuple[str, str]]:
    """
    Find the first DP832 device on the network
    
    Args:
        network_base: Network base (e.g., "192.168.1"). If None, auto-detect.
        port: SCPI port to test (default: 5555)
    
    Returns:
        Tuple (ip_address, device_id) for the first found DP832, or None if none found
    """
    devices = find_dp832_devices(network_base, port)
    return devices[0] if devices else None


def test_ip(ip_address: str, port: int = 5555) -> Optional[str]:
    """
    Test a specific IP address for a DP832
    
    Args:
        ip_address: IP address to test
        port: SCPI port to test (default: 5555)
    
    Returns:
        Device ID if DP832 found, None otherwise
    """
    return test_dp832_connection(ip_address, port)
