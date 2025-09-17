"""
Rigol DP832 Ethernet Control Library

A simplified library for controlling Rigol DP832 power supplies over Ethernet using VISA TCP/IP.
This library focuses only on Ethernet connectivity, making it lightweight and easy to use.

Example:
    from rigol_dp832 import DP832
    
    # Connect to your DP832
    ps = DP832("192.168.1.100")
    
    # Use the device
    ps.set_channel_settings(1, 5.0, 1.0)
    ps.set_output_state(1, True)
    voltage = ps.measure_voltage(1)
"""

import logging
import pyvisa
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DP832:
    """
    Rigol DP832 Programmable Power Supply - Ethernet Control
    
    This class provides a simple interface to control a Rigol DP832 power supply
    over Ethernet using VISA TCP/IP connections.
    """
    
    def __init__(self, ip_address: str, port: int = 5555, timeout: int = 5000):
        """
        Initialize connection to DP832
        
        Args:
            ip_address: IP address of the DP832
            port: SCPI port (default: 5555)
            timeout: Connection timeout in milliseconds (default: 5000)
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        
        # Create VISA resource string
        self.resource_string = f"TCPIP0::{ip_address}::{port}::SOCKET"
        
        # Initialize VISA connection
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(
            self.resource_string, 
            read_termination="\n", 
            timeout=timeout
        )
        
        logger.info(f"Connected to DP832 at {ip_address}:{port}")
    
    def close(self):
        """Close the connection to the device"""
        if hasattr(self, 'inst'):
            self.inst.close()
        if hasattr(self, 'rm'):
            self.rm.close()
        logger.info("Connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def _validate_channel(self, channel: int):
        """Validate channel number"""
        if channel not in [1, 2, 3]:
            raise ValueError(f"Channel must be 1, 2, or 3, got {channel}")
    
    def id(self) -> Dict[str, str]:
        """
        Get device identification information
        
        Returns:
            Dictionary with manufacturer, model, serial_number, and version
        """
        id_str = self.inst.query("*IDN?").strip().split(",")
        return {
            "manufacturer": id_str[0],
            "model": id_str[1],
            "serial_number": id_str[2],
            "version": id_str[3],
        }
    
    def get_output_state(self, channel: int) -> bool:
        """
        Get the output state of a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            True if output is ON, False if OFF
        """
        self._validate_channel(channel)
        state = self.inst.query(f":OUTP:STAT? CH{channel}").strip()
        return state == "ON"
    
    def set_output_state(self, channel: int, state: bool):
        """
        Set the output state of a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            state: True to turn ON, False to turn OFF
        """
        self._validate_channel(channel)
        state_str = "ON" if state else "OFF"
        self.inst.write(f":OUTP:STAT CH{channel},{state_str}")
        logger.info(f"Channel {channel} output set to {state_str}")
    
    def get_channel_settings(self, channel: int) -> Dict[str, float]:
        """
        Get voltage and current settings for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            Dictionary with 'voltage' and 'current' values
        """
        self._validate_channel(channel)
        settings = self.inst.query(f":APPL? CH{channel}").strip().split(",")
        return {
            "voltage": float(settings[-2]),
            "current": float(settings[-1])
        }
    
    def set_channel_settings(self, channel: int, voltage: float, current: float):
        """
        Set voltage and current for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            voltage: Voltage setting in volts
            current: Current setting in amps
        """
        self._validate_channel(channel)
        self.inst.write(f":APPL CH{channel},{voltage},{current}")
        logger.info(f"Channel {channel} set to {voltage}V, {current}A")
    
    def measure_voltage(self, channel: int) -> float:
        """
        Measure the actual output voltage of a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            Measured voltage in volts
        """
        self._validate_channel(channel)
        voltage = self.inst.query(f":MEAS? CH{channel}").strip()
        return float(voltage)
    
    def measure_current(self, channel: int) -> float:
        """
        Measure the actual output current of a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            Measured current in amps
        """
        self._validate_channel(channel)
        current = self.inst.query(f":MEAS:CURR? CH{channel}").strip()
        return float(current)
    
    def measure_power(self, channel: int) -> float:
        """
        Measure the actual output power of a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            Measured power in watts
        """
        self._validate_channel(channel)
        measurements = self.inst.query(f":MEAS:ALL? CH{channel}").strip().split(",")
        return float(measurements[2])  # Power is the third value
    
    def measure_all(self, channel: int) -> Dict[str, float]:
        """
        Get all measurements for a channel (voltage, current, power)
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            Dictionary with 'voltage', 'current', and 'power' values
        """
        self._validate_channel(channel)
        measurements = self.inst.query(f":MEAS:ALL? CH{channel}").strip().split(",")
        return {
            "voltage": float(measurements[0]),
            "current": float(measurements[1]),
            "power": float(measurements[2])
        }
    
    def get_output_mode(self, channel: int) -> str:
        """
        Get the output mode of a channel (CV, CC, or UR)
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            Output mode: 'CV' (Constant Voltage), 'CC' (Constant Current), or 'UR' (Unregulated)
        """
        self._validate_channel(channel)
        mode = self.inst.query(f":OUTP:MODE? CH{channel}").strip()
        return mode
    
    def get_ocp_enabled(self, channel: int) -> bool:
        """
        Check if Over Current Protection (OCP) is enabled for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            True if OCP is enabled, False if disabled
        """
        self._validate_channel(channel)
        state = self.inst.query(f":OUTP:OCP? CH{channel}").strip()
        return state == "ON"
    
    def set_ocp_enabled(self, channel: int, enabled: bool):
        """
        Enable or disable Over Current Protection (OCP) for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            enabled: True to enable, False to disable
        """
        self._validate_channel(channel)
        state = "ON" if enabled else "OFF"
        self.inst.write(f":OUTP:OCP CH{channel},{state}")
        logger.info(f"Channel {channel} OCP set to {state}")
    
    def get_ocp_value(self, channel: int) -> float:
        """
        Get the Over Current Protection (OCP) value for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            OCP current value in amps
        """
        self._validate_channel(channel)
        value = self.inst.query(f":OUTP:OCP:VAL? CH{channel}").strip()
        return float(value)
    
    def set_ocp_value(self, channel: int, current: float):
        """
        Set the Over Current Protection (OCP) value for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            current: OCP current value in amps
        """
        self._validate_channel(channel)
        self.inst.write(f":OUTP:OCP:VAL CH{channel},{current}")
        logger.info(f"Channel {channel} OCP value set to {current}A")
    
    def get_ovp_enabled(self, channel: int) -> bool:
        """
        Check if Over Voltage Protection (OVP) is enabled for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            True if OVP is enabled, False if disabled
        """
        self._validate_channel(channel)
        state = self.inst.query(f":OUTP:OVP? CH{channel}").strip()
        return state == "ON"
    
    def set_ovp_enabled(self, channel: int, enabled: bool):
        """
        Enable or disable Over Voltage Protection (OVP) for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            enabled: True to enable, False to disable
        """
        self._validate_channel(channel)
        state = "ON" if enabled else "OFF"
        self.inst.write(f":OUTP:OVP CH{channel},{state}")
        logger.info(f"Channel {channel} OVP set to {state}")
    
    def get_ovp_value(self, channel: int) -> float:
        """
        Get the Over Voltage Protection (OVP) value for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            OVP voltage value in volts
        """
        self._validate_channel(channel)
        value = self.inst.query(f":OUTP:OVP:VAL? CH{channel}").strip()
        return float(value)
    
    def set_ovp_value(self, channel: int, voltage: float):
        """
        Set the Over Voltage Protection (OVP) value for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            voltage: OVP voltage value in volts
        """
        self._validate_channel(channel)
        self.inst.write(f":OUTP:OVP:VAL CH{channel},{voltage}")
        logger.info(f"Channel {channel} OVP value set to {voltage}V")
    
    def get_ocp_alarm(self, channel: int) -> bool:
        """
        Check if Over Current Protection alarm is active for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            True if OCP alarm is active, False if not
        """
        self._validate_channel(channel)
        alarm = self.inst.query(f":OUTP:OCP:ALAR? CH{channel}").strip()
        return alarm == "YES"
    
    def clear_ocp_alarm(self, channel: int):
        """
        Clear the Over Current Protection alarm for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
        """
        self._validate_channel(channel)
        self.inst.write(f":OUTP:OCP:CLEAR CH{channel}")
        logger.info(f"Channel {channel} OCP alarm cleared")
    
    def get_ovp_alarm(self, channel: int) -> bool:
        """
        Check if Over Voltage Protection alarm is active for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
            
        Returns:
            True if OVP alarm is active, False if not
        """
        self._validate_channel(channel)
        alarm = self.inst.query(f":OUTP:OVP:ALAR? CH{channel}").strip()
        return alarm == "ON"
    
    def clear_ovp_alarm(self, channel: int):
        """
        Clear the Over Voltage Protection alarm for a channel
        
        Args:
            channel: Channel number (1, 2, or 3)
        """
        self._validate_channel(channel)
        self.inst.write(f":OUTP:OVP:CLEAR CH{channel}")
        logger.info(f"Channel {channel} OVP alarm cleared")
    
    def get_all_output_states(self) -> Dict[int, bool]:
        """
        Get output states for all channels
        
        Returns:
            Dictionary mapping channel numbers to their output states
        """
        return {
            channel: self.get_output_state(channel)
            for channel in [1, 2, 3]
        }
    
    def get_all_settings(self) -> Dict[int, Dict[str, float]]:
        """
        Get voltage and current settings for all channels
        
        Returns:
            Dictionary mapping channel numbers to their settings
        """
        return {
            channel: self.get_channel_settings(channel)
            for channel in [1, 2, 3]
        }
    
    def get_all_measurements(self) -> Dict[int, Dict[str, float]]:
        """
        Get all measurements for all channels
        
        Returns:
            Dictionary mapping channel numbers to their measurements
        """
        return {
            channel: self.measure_all(channel)
            for channel in [1, 2, 3]
        }
