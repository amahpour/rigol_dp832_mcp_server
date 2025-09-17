# Rigol DP832 Ethernet Control Library

A simple, lightweight Python library for controlling Rigol DP832 power supplies over Ethernet using VISA TCP/IP connections.

## Features

- ✅ **Ethernet-only**: Focused on Ethernet connectivity (no USB dependencies)
- ✅ **Simple API**: Easy-to-use interface for all DP832 functions
- ✅ **Auto-discovery**: Find your DP832 on the network automatically
- ✅ **Context manager**: Safe connection handling with `with` statements
- ✅ **Comprehensive**: All major DP832 functions supported
- ✅ **Lightweight**: Minimal dependencies (just PyVISA)

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Find Your Device

```bash
# Auto-discover your DP832
python find_dp832.py

# Or test a specific IP
python find_dp832.py 192.168.1.100

# Or search a specific network (useful for WSL, VPN, etc.)
python find_dp832.py --network 192.168.68
python find_dp832.py -n 192.168.68  # Short form
```

### 3. Use the Library

```python
from rigol_dp832 import DP832

# Connect to your DP832
with DP832("192.168.1.100") as ps:
    # Get device info
    device_id = ps.id()
    print(f"Connected to: {device_id['model']}")
    
    # Set channel 1 to 5V, 1A
    ps.set_channel_settings(1, 5.0, 1.0)
    ps.set_output_state(1, True)
    
    # Measure the output
    voltage = ps.measure_voltage(1)
    current = ps.measure_current(1)
    print(f"Output: {voltage:.3f}V, {current:.3f}A")
```

## API Reference

### Connection

```python
# Basic connection
ps = DP832("192.168.1.100")

# With custom port and timeout
ps = DP832("192.168.1.100", port=5555, timeout=5000)

# Using context manager (recommended)
with DP832("192.168.1.100") as ps:
    # Your code here
    pass
```

### Device Information

```python
device_id = ps.id()
# Returns: {"manufacturer": "RIGOL TECHNOLOGIES", "model": "DP832A", ...}
```

### Channel Control

```python
# Set voltage and current
ps.set_channel_settings(channel=1, voltage=5.0, current=1.0)

# Turn output on/off
ps.set_output_state(channel=1, state=True)

# Get current settings
settings = ps.get_channel_settings(1)
# Returns: {"voltage": 5.0, "current": 1.0}
```

### Measurements

```python
# Individual measurements
voltage = ps.measure_voltage(1)
current = ps.measure_current(1)
power = ps.measure_power(1)

# All measurements at once
measurements = ps.measure_all(1)
# Returns: {"voltage": 5.009, "current": 0.001, "power": 0.002}
```

### Protection Settings

```python
# Over Current Protection (OCP)
ps.set_ocp_enabled(1, True)
ps.set_ocp_value(1, 3.3)  # 3.3A limit
ocp_enabled = ps.get_ocp_enabled(1)
ocp_value = ps.get_ocp_value(1)

# Over Voltage Protection (OVP)
ps.set_ovp_enabled(1, True)
ps.set_ovp_value(1, 33.0)  # 33V limit
ovp_enabled = ps.get_ovp_enabled(1)
ovp_value = ps.get_ovp_value(1)

# Check for alarms
if ps.get_ocp_alarm(1):
    ps.clear_ocp_alarm(1)
if ps.get_ovp_alarm(1):
    ps.clear_ovp_alarm(1)
```

### Bulk Operations

```python
# Get all output states
states = ps.get_all_output_states()
# Returns: {1: False, 2: False, 3: False}

# Get all channel settings
settings = ps.get_all_settings()
# Returns: {1: {"voltage": 0.0, "current": 3.0}, ...}

# Get all measurements
measurements = ps.get_all_measurements()
# Returns: {1: {"voltage": 0.0, "current": 0.0, "power": 0.0}, ...}
```

## Network Discovery

The library includes tools to automatically find your DP832 on the network:

### Command Line Discovery

```bash
# Auto-discover on local network
python find_dp832.py

# Test specific IP address
python find_dp832.py 192.168.1.100

# Search specific network (useful for WSL, VPN, etc.)
python find_dp832.py --network 192.168.68
python find_dp832.py -n 192.168.68  # Short form

# Get help
python find_dp832.py --help
```

### Python API Discovery

```python
from discovery import find_dp832_devices, find_first_dp832

# Find all DP832 devices on local network
devices = find_dp832_devices()
for ip, device_id in devices:
    print(f"Found DP832 at {ip}: {device_id}")

# Find all DP832 devices on specific network
devices = find_dp832_devices("192.168.68")
for ip, device_id in devices:
    print(f"Found DP832 at {ip}: {device_id}")

# Find the first DP832
result = find_first_dp832()
if result:
    ip, device_id = result
    print(f"First DP832 at {ip}")
```

## Setup Requirements

1. **Network Connection**: Connect your DP832 to your network via Ethernet
2. **IP Configuration**: Configure the IP address on your DP832
3. **SCPI Interface**: Enable SCPI over Ethernet on the DP832 (usually port 5555)
4. **Dependencies**: Install PyVISA (`pip install pyvisa`)

## Troubleshooting

### Connection Issues

1. **Check IP Address**: Verify the IP address is correct
2. **Network Connectivity**: Ping the device: `ping 192.168.1.100`
3. **SCPI Interface**: Ensure SCPI over Ethernet is enabled
4. **Firewall**: Check that port 5555 is not blocked
5. **PyVISA**: Ensure PyVISA is installed and working

### Common Error Messages

- `could not connect: -1073807339`: Device not reachable at the IP address
- `No VISA devices found`: PyVISA can't find the device
- `Channel must be 1, 2, or 3`: Invalid channel number provided

## Examples

See `example.py` for a complete working example.

## License

This library is provided as-is for controlling Rigol DP832 power supplies over Ethernet.