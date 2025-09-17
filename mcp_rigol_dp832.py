"""
Rigol DP832 MCP Server

A Model Context Protocol (MCP) server that enables AI agents to interact with Rigol DP832
programmable power supplies via Ethernet connection. Provides tools for device discovery,
channel control, measurements, and protection settings.

This server acts as a bridge between AI agents and Rigol DP832 power supplies, allowing
automated power supply control workflows through the MCP protocol.
"""

from fastmcp import FastMCP
import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
from rigol_dp832.rigol_dp import DP832, DP821, DP712
from rigol_dp832.find_dp832 import find_dp832
from rigol_dp832.test_ip import test_ip

# Initialize the MCP server with a descriptive name
mcp = FastMCP(name="RigolDP832MCP")

# Global variable to store the current power supply connection
current_ps: Optional[Any] = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_IP = os.environ.get("RIGOL_DP832_IP")
DEFAULT_PORT = int(os.environ.get("RIGOL_DP832_PORT", "5555"))


def get_connection_string(ip: Optional[str] = None, port: Optional[int] = None) -> str:
    """
    Get the VISA connection string for the power supply.
    
    Args:
        ip: IP address (uses configured IP if not provided)
        port: Port number (uses configured port if not provided)
    
    Returns:
        VISA connection string
    """
    if ip is None:
        ip = DEFAULT_IP
    if port is None:
        port = DEFAULT_PORT
    
    if ip is None:
        raise ValueError("No IP address configured. Set RIGOL_DP832_IP environment variable or provide IP parameter.")
    
    return f"TCPIP0::{ip}::{port}::SOCKET"


def auto_discover_device() -> Optional[str]:
    """
    Auto-discover a DP832 device on the network.
    
    Returns:
        IP address of discovered device, or None if not found
    """
    try:
        result = find_dp832()
        if result:
            ip, _ = result
            return ip
        return None
    except Exception as e:
        logger.error(f"Auto-discovery failed: {e}")
        return None


@mcp.tool()
def ping() -> str:
    """
    Simple health check to verify the MCP server is running.

    Returns:
        str: Always returns "pong" to confirm server is responsive

    This is useful for testing connectivity and server status.
    """
    return "pong"


@mcp.tool()
def discover_devices() -> List[Dict[str, Any]]:
    """
    Discover Rigol DP832/DP821/DP712 devices on the network.

    Scans the network for available Rigol power supplies and returns
    information about each discovered device including IP address,
    connection string, and device details.

    Returns:
        List[Dict[str, Any]]: List of discovered devices with connection information.
            Each dict contains: 'ip', 'connection_string', 'device_info'

    Example:
        Returns devices like:
        [
            {
                "ip": "192.168.1.100",
                "connection_string": "TCPIP0::192.168.1.100::5555::SOCKET",
                "device_info": {"manufacturer": "RIGOL TECHNOLOGIES", "model": "DP832", ...}
            }
        ]
    """
    try:
        # The find_dp832 function returns (ip, device_id) or None
        result = find_dp832()
        
        if result is None:
            return [{"error": "No DP832 devices found on the network"}]
        
        ip, device_id = result
        connection_string = f"TCPIP0::{ip}::{DEFAULT_PORT}::SOCKET"
        
        try:
            # Test connection and get device info
            ps = DP832(conn_type="VISA", visa_resource_string=connection_string)
            device_info = ps.id()
            ps.close()
            
            return [{
                "ip": ip,
                "connection_string": connection_string,
                "device_info": device_info
            }]
        except Exception as e:
            logger.warning(f"Could not get device info for {ip}: {e}")
            return [{
                "ip": ip,
                "connection_string": connection_string,
                "device_info": None,
                "error": str(e)
            }]
        
    except Exception as e:
        logger.error(f"Device discovery failed: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def test_connection(ip_address: str = None) -> Dict[str, Any]:
    """
    Test connection to a Rigol power supply.

    Tests connection to the configured IP address or a specific IP address.
    If no IP is provided and none is configured, attempts auto-discovery.

    Args:
        ip_address (str, optional): IP address to test. Uses configured IP if not provided.

    Returns:
        Dict[str, Any]: Connection test results including status, device info, and connection string

    Example:
        test_connection() -> {
            "status": "success",
            "ip": "192.168.1.100",
            "connection_string": "TCPIP0::192.168.1.100::5555::SOCKET",
            "device_info": {"manufacturer": "RIGOL TECHNOLOGIES", "model": "DP832", ...}
        }
    """
    try:
        # Determine which IP to use
        if ip_address is None:
            if DEFAULT_IP is None:
                # Try auto-discovery
                ip_address = auto_discover_device()
                if ip_address is None:
                    return {
                        "status": "failed",
                        "error": "No IP address configured and auto-discovery failed. Set RIGOL_DP832_IP environment variable."
                    }
            else:
                ip_address = DEFAULT_IP
        
        connection_string = f"TCPIP0::{ip_address}::{DEFAULT_PORT}::SOCKET"
        
        # Test the connection - test_ip returns device_id string or None
        device_id = test_ip(ip_address)
        
        if device_id:
            # Get device information
            ps = DP832(conn_type="VISA", visa_resource_string=connection_string)
            device_info = ps.id()
            ps.close()
            
            return {
                "status": "success",
                "ip": ip_address,
                "connection_string": connection_string,
                "device_info": device_info
            }
        else:
            return {
                "status": "failed",
                "ip": ip_address,
                "error": "No DP832 device found at this IP address"
            }
    except Exception as e:
        return {
            "status": "failed",
            "ip": ip_address or "unknown",
            "error": str(e)
        }


@mcp.tool()
def connect(ip_address: str = None, port: int = None) -> Dict[str, Any]:
    """
    Connect to a Rigol power supply.

    Establishes a connection to the power supply using the configured IP address
    or a specific IP address. If no IP is provided and none is configured,
    attempts auto-discovery.

    Args:
        ip_address (str, optional): IP address to connect to. Uses configured IP if not provided.
        port (int, optional): Port number. Uses configured port if not provided.

    Returns:
        Dict[str, Any]: Connection status and device information

    Example:
        connect() -> {
            "status": "connected",
            "ip": "192.168.1.100",
            "connection_string": "TCPIP0::192.168.1.100::5555::SOCKET",
            "device_info": {"manufacturer": "RIGOL TECHNOLOGIES", "model": "DP832", ...}
        }
    """
    global current_ps
    
    try:
        # Close existing connection if any
        if current_ps:
            current_ps.close()
        
        # Determine which IP to use
        if ip_address is None:
            if DEFAULT_IP is None:
                # Try auto-discovery
                ip_address = auto_discover_device()
                if ip_address is None:
                    return {
                        "status": "failed",
                        "error": "No IP address configured and auto-discovery failed. Set RIGOL_DP832_IP environment variable."
                    }
            else:
                ip_address = DEFAULT_IP
        
        # Get connection string
        connection_string = get_connection_string(ip_address, port)
        
        # Create new connection
        current_ps = DP832(conn_type="VISA", visa_resource_string=connection_string)
        
        # Get device information
        device_info = current_ps.id()
        
        return {
            "status": "connected",
            "ip": ip_address,
            "connection_string": connection_string,
            "device_info": device_info
        }
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@mcp.tool()
def disconnect() -> str:
    """
    Disconnect from the currently connected power supply.

    Closes the active connection and releases resources.

    Returns:
        str: Disconnection status message
    """
    global current_ps
    
    if current_ps:
        try:
            current_ps.close()
            current_ps = None
            return "Disconnected successfully"
        except Exception as e:
            return f"Error during disconnect: {e}"
    else:
        return "No active connection to disconnect"


@mcp.tool()
def get_device_info() -> Dict[str, Any]:
    """
    Get information about the currently connected device.

    Returns:
        Dict[str, Any]: Device information including manufacturer, model, serial number, and version

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    return current_ps.id()


@mcp.tool()
def set_channel_settings(channel: int, voltage: float, current: float) -> Dict[str, Any]:
    """
    Set voltage and current settings for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)
        voltage (float): Voltage setting in volts
        current (float): Current setting in amperes

    Returns:
        Dict[str, Any]: Confirmation of the settings applied

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current_ps.set_channel_settings(channel, voltage, current)
        return {
            "status": "success",
            "channel": channel,
            "voltage": voltage,
            "current": current
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_channel_settings(channel: int) -> Dict[str, Any]:
    """
    Get current voltage and current settings for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Current channel settings

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        settings = current_ps.get_channel_settings(channel)
        return {
            "status": "success",
            "channel": channel,
            "settings": settings
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def set_output_state(channel: int, state: bool) -> Dict[str, Any]:
    """
    Enable or disable the output of a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)
        state (bool): True to enable output, False to disable

    Returns:
        Dict[str, Any]: Confirmation of the output state change

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current_ps.set_output_state(channel, state)
        return {
            "status": "success",
            "channel": channel,
            "output_enabled": state
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_output_state(channel: int) -> Dict[str, Any]:
    """
    Get the current output state of a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Current output state

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        state = current_ps.get_output_state(channel)
        return {
            "status": "success",
            "channel": channel,
            "output_enabled": state
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def measure_voltage(channel: int) -> Dict[str, Any]:
    """
    Measure the voltage of a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Voltage measurement in volts

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        voltage = current_ps.measure_voltage(channel)
        return {
            "status": "success",
            "channel": channel,
            "voltage": voltage,
            "unit": "V"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def measure_current(channel: int) -> Dict[str, Any]:
    """
    Measure the current of a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Current measurement in amperes

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current = current_ps.measure_current(channel)
        return {
            "status": "success",
            "channel": channel,
            "current": current,
            "unit": "A"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def measure_all(channel: int) -> Dict[str, Any]:
    """
    Measure voltage, current, and power of a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: All measurements including voltage, current, and power

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        measurements = current_ps.measure_all(channel)
        return {
            "status": "success",
            "channel": channel,
            "measurements": measurements,
            "units": {"voltage": "V", "current": "A", "power": "W"}
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def set_ocp_enabled(channel: int, state: bool) -> Dict[str, Any]:
    """
    Enable or disable overcurrent protection (OCP) for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)
        state (bool): True to enable OCP, False to disable

    Returns:
        Dict[str, Any]: Confirmation of the OCP state change

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current_ps.set_ocp_enabled(channel, state)
        return {
            "status": "success",
            "channel": channel,
            "ocp_enabled": state
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_ocp_enabled(channel: int) -> Dict[str, Any]:
    """
    Get the current overcurrent protection (OCP) state for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Current OCP state

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        ocp_enabled = current_ps.get_ocp_enabled(channel)
        return {
            "status": "success",
            "channel": channel,
            "ocp_enabled": ocp_enabled
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def set_ocp_value(channel: int, current_limit: float) -> Dict[str, Any]:
    """
    Set the overcurrent protection (OCP) value for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)
        current_limit (float): OCP current limit in amperes

    Returns:
        Dict[str, Any]: Confirmation of the OCP value setting

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current_ps.set_ocp_value(channel, current_limit)
        return {
            "status": "success",
            "channel": channel,
            "ocp_current_limit": current_limit,
            "unit": "A"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_ocp_value(channel: int) -> Dict[str, Any]:
    """
    Get the current overcurrent protection (OCP) value for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Current OCP value

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        ocp_value = current_ps.get_ocp_value(channel)
        return {
            "status": "success",
            "channel": channel,
            "ocp_current_limit": ocp_value,
            "unit": "A"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def set_ovp_enabled(channel: int, state: bool) -> Dict[str, Any]:
    """
    Enable or disable overvoltage protection (OVP) for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)
        state (bool): True to enable OVP, False to disable

    Returns:
        Dict[str, Any]: Confirmation of the OVP state change

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current_ps.set_ovp_enabled(channel, state)
        return {
            "status": "success",
            "channel": channel,
            "ovp_enabled": state
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_ovp_enabled(channel: int) -> Dict[str, Any]:
    """
    Get the current overvoltage protection (OVP) state for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Current OVP state

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        ovp_enabled = current_ps.get_ovp_enabled(channel)
        return {
            "status": "success",
            "channel": channel,
            "ovp_enabled": ovp_enabled
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def set_ovp_value(channel: int, voltage_limit: float) -> Dict[str, Any]:
    """
    Set the overvoltage protection (OVP) value for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)
        voltage_limit (float): OVP voltage limit in volts

    Returns:
        Dict[str, Any]: Confirmation of the OVP value setting

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current_ps.set_ovp_value(channel, voltage_limit)
        return {
            "status": "success",
            "channel": channel,
            "ovp_voltage_limit": voltage_limit,
            "unit": "V"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_ovp_value(channel: int) -> Dict[str, Any]:
    """
    Get the current overvoltage protection (OVP) value for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Current OVP value

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        ovp_value = current_ps.get_ovp_value(channel)
        return {
            "status": "success",
            "channel": channel,
            "ovp_voltage_limit": ovp_value,
            "unit": "V"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_output_mode(channel: int) -> Dict[str, Any]:
    """
    Get the current output mode of a specific channel.

    Returns CV (constant voltage), CC (constant current), or UR (unregulated) mode.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Current output mode

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        mode = current_ps.get_output_mode(channel)
        return {
            "status": "success",
            "channel": channel,
            "output_mode": mode
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def clear_ocp_alarm(channel: int) -> Dict[str, Any]:
    """
    Clear the overcurrent protection (OCP) alarm for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Confirmation of alarm clearing

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current_ps.clear_ocp_alarm(channel)
        return {
            "status": "success",
            "channel": channel,
            "message": "OCP alarm cleared"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def clear_ovp_alarm(channel: int) -> Dict[str, Any]:
    """
    Clear the overvoltage protection (OVP) alarm for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: Confirmation of alarm clearing

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        current_ps.clear_ovp_alarm(channel)
        return {
            "status": "success",
            "channel": channel,
            "message": "OVP alarm cleared"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_ocp_alarm(channel: int) -> Dict[str, Any]:
    """
    Check if overcurrent protection (OCP) alarm is active for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: OCP alarm state

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        alarm_active = current_ps.get_ocp_alarm(channel)
        return {
            "status": "success",
            "channel": channel,
            "ocp_alarm_active": alarm_active
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_ovp_alarm(channel: int) -> Dict[str, Any]:
    """
    Check if overvoltage protection (OVP) alarm is active for a specific channel.

    Args:
        channel (int): Channel number (1, 2, or 3 for DP832; 1, 2 for DP821; 1 for DP712)

    Returns:
        Dict[str, Any]: OVP alarm state

    Raises:
        RuntimeError: If no device is currently connected
    """
    if not current_ps:
        raise RuntimeError("No device connected. Use connect() first.")
    
    try:
        alarm_active = current_ps.get_ovp_alarm(channel)
        return {
            "status": "success",
            "channel": channel,
            "ovp_alarm_active": alarm_active
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Start the MCP server when run directly
    mcp.run()
