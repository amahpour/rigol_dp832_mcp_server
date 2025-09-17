#!/usr/bin/env python3
"""
Example usage of Rigol DP832 Ethernet Control

This example demonstrates how to use the DP832 library with your device.
Update the IP_ADDRESS variable with your device's IP address.
"""

from rigol_dp832 import DP832

# Configuration - UPDATE THIS WITH YOUR DP832's IP ADDRESS
IP_ADDRESS = "192.168.68.140"  # Replace with your DP832's IP address


def main():
    """Example usage of the DP832 library"""
    
    print("Rigol DP832 Ethernet Control Example")
    print("=" * 40)
    
    try:
        # Connect to the DP832
        print(f"Connecting to DP832 at {IP_ADDRESS}...")
        with DP832(IP_ADDRESS) as ps:
            print("✅ Connected successfully!")
            
            # Get device information
            device_id = ps.id()
            print(f"\nDevice Information:")
            print(f"  Manufacturer: {device_id['manufacturer']}")
            print(f"  Model: {device_id['model']}")
            print(f"  Serial: {device_id['serial_number']}")
            print(f"  Version: {device_id['version']}")
            
            # Check current states
            print(f"\nCurrent Output States:")
            for channel in [1, 2, 3]:
                state = ps.get_output_state(channel)
                print(f"  Channel {channel}: {'ON' if state else 'OFF'}")
            
            # Check current settings
            print(f"\nCurrent Channel Settings:")
            for channel in [1, 2, 3]:
                settings = ps.get_channel_settings(channel)
                print(f"  Channel {channel}: {settings['voltage']:.2f}V, {settings['current']:.3f}A")
            
            # Example: Set channel 1 to 5V, 1A and turn it on
            print(f"\nSetting Channel 1 to 5V, 1A...")
            ps.set_channel_settings(1, 5.0, 1.0)
            ps.set_output_state(1, True)
            
            # Wait a moment for stabilization
            import time
            time.sleep(1)
            
            # Measure the output
            print(f"\nMeasurements after setting Channel 1:")
            voltage = ps.measure_voltage(1)
            current = ps.measure_current(1)
            power = ps.measure_power(1)
            print(f"  Voltage: {voltage:.3f}V")
            print(f"  Current: {current:.3f}A")
            print(f"  Power: {power:.3f}W")
            
            # Check protection settings
            print(f"\nProtection Settings for Channel 1:")
            ocp_enabled = ps.get_ocp_enabled(1)
            ocp_value = ps.get_ocp_value(1)
            ovp_enabled = ps.get_ovp_enabled(1)
            ovp_value = ps.get_ovp_value(1)
            print(f"  OCP: {'Enabled' if ocp_enabled else 'Disabled'} ({ocp_value:.3f}A)")
            print(f"  OVP: {'Enabled' if ovp_enabled else 'Disabled'} ({ovp_value:.2f}V)")
            
            # Turn off the output
            print(f"\nTurning off Channel 1...")
            ps.set_output_state(1, False)
            
            print(f"\n✅ Example completed successfully!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Check that the IP address is correct: {IP_ADDRESS}")
        print(f"2. Make sure the DP832 is connected to the network")
        print(f"3. Verify SCPI over Ethernet is enabled")
        print(f"4. Try running: python find_dp832.py")


if __name__ == "__main__":
    main()
