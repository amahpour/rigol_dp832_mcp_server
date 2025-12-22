# Rigol DP832 MCP Server

A Python library and Model Context Protocol (MCP) server for controlling Rigol DP832 programmable power supplies via Ethernet connection using VISA TCP/IP.

## Features

- **Ethernet-only**: Focused on Ethernet connections, no USB/USBTMC dependencies
- **VISA TCP/IP**: Uses industry-standard VISA TCP/IP for reliable communication
- **Full DP832 Support**: Complete control of all DP832 channels and features
- **Network Discovery**: Automatic discovery tools to find your DP832 on the network
- **Easy to Use**: Simple Python API for power supply control
- **MCP Server**: Model Context Protocol server for AI agent integration
- **AI-Ready**: Direct integration with AI assistants and automation workflows

## Supported Models

- **DP832**: 3-channel programmable power supply (primary focus)
- **DP821**: 2-channel programmable power supply
- **DP712**: 1-channel programmable power supply

## Installation

### Option 1: Install via pip (Recommended)

Install directly from GitHub:

```bash
pip install git+https://github.com/amahpour/rigol_dp832_mcp_server.git
```

### Option 2: Clone and Install

1. Clone this repository:
```bash
git clone https://github.com/amahpour/rigol_dp832_mcp_server.git
cd rigol_dp832_mcp_server
```

2. Install the package:
```bash
pip install .
```

### Option 3: Development Install

For development with editable mode:

```bash
git clone https://github.com/amahpour/rigol_dp832_mcp_server.git
cd rigol_dp832_mcp_server
pip install -e .
```

## Quick Start

### 1. Connect Your DP832

Connect your DP832 to your network via Ethernet cable and configure its IP address.

### 2. Find Your Device

Use the automatic discovery tool to find your DP832:

```bash
python rigol_dp832/find_dp832.py
```

This will scan your network and provide the exact connection string to use.

### 3. Use the Library

```python
from rigol_dp832.rigol_dp import DP832

# Connect to your DP832
ps = DP832(
    conn_type="VISA",
    visa_resource_string="TCPIP0::192.168.1.100::5555::SOCKET"
)

# Get device information
device_id = ps.id()
print(f"Connected to: {device_id['model']}")

# Set channel 1 to 5V, 1A and turn it on
ps.set_channel_settings(channel=1, voltage=5.0, current=1.0)
ps.set_output_state(channel=1, state=True)

# Read measurements
voltage = ps.measure_voltage(1)
current = ps.measure_current(1)
print(f"Voltage: {voltage:.3f}V, Current: {current:.3f}A")

# Turn off the output
ps.set_output_state(channel=1, state=False)

# Close connection
ps.close()
```

## MCP Server Usage

This repository includes a Model Context Protocol (MCP) server that allows AI agents to directly control your Rigol power supply. The MCP server provides a comprehensive set of tools for device discovery, connection management, channel control, measurements, and protection settings.

### Starting the MCP Server

1. **Install dependencies** (if not already done):
```bash
pip install -r requirements.txt
```

2. **Start the MCP server**:
```bash
python mcp_rigol_dp832.py
```

### Using with Cursor IDE

The repository includes a `.cursor/mcp.json` configuration file that automatically configures the MCP server for use with Cursor IDE. **You need to update the IP address** in this file to match your power supply:

```json
{
  "mcpServers": {
    "rigol-dp832": {
      "command": "python3",
      "args": ["mcp_rigol_dp832.py"],
      "env": {
        "RIGOL_DP832_IP": "192.168.1.100",
        "RIGOL_DP832_PORT": "5555"
      }
    }
  }
}
```

**Configuration Options:**
- `RIGOL_DP832_IP`: IP address of your power supply (required)
- `RIGOL_DP832_PORT`: Port number (default: 5555)

**If you don't configure an IP address**, the server will attempt auto-discovery as a fallback.

### Configuration Approach

The MCP server uses a **configuration-first approach**:

1. **Primary**: Use the IP address configured in `.cursor/mcp.json` (recommended)
2. **Fallback**: Auto-discovery if no IP is configured
3. **Override**: Provide specific IP/port parameters to individual tools

This design ensures:
- **Reliability**: No need for discovery on every connection
- **Performance**: Faster connections using pre-configured IP
- **Flexibility**: Auto-discovery available when needed
- **Simplicity**: Most tools work without parameters

Once configured, you can interact with your power supply through natural language commands in Cursor, such as:
- "Connect to the power supply"
- "Set channel 1 to 5V and 1A"
- "Enable output on channel 1"
- "Measure the voltage and current on channel 1"
- "Discover available power supplies on the network" (for auto-discovery)

### Available MCP Tools

The MCP server provides the following tools:

#### Device Discovery & Connection
- `discover_devices()` - Find all Rigol power supplies on the network (auto-discovery)
- `test_connection(ip_address=None)` - Test connection to configured device or specific IP
- `connect(ip_address=None, port=None)` - Connect to configured device or specific IP/port
- `disconnect()` - Disconnect from current device
- `get_device_info()` - Get information about connected device

#### Channel Control
- `set_channel_settings(channel, voltage, current)` - Set voltage and current
- `get_channel_settings(channel)` - Get current settings
- `set_output_state(channel, state)` - Enable/disable output
- `get_output_state(channel)` - Get output state

#### Measurements
- `measure_voltage(channel)` - Measure voltage
- `measure_current(channel)` - Measure current
- `measure_all(channel)` - Measure voltage, current, and power

#### Protection Settings
- `set_ocp_enabled(channel, state)` - Enable/disable overcurrent protection
- `get_ocp_enabled(channel)` - Get OCP state
- `set_ocp_value(channel, current_limit)` - Set OCP current limit
- `get_ocp_value(channel)` - Get OCP current limit
- `set_ovp_enabled(channel, state)` - Enable/disable overvoltage protection
- `get_ovp_enabled(channel)` - Get OVP state
- `set_ovp_value(channel, voltage_limit)` - Set OVP voltage limit
- `get_ovp_value(channel)` - Get OVP voltage limit

#### Status & Diagnostics
- `get_output_mode(channel)` - Get output mode (CV/CC/UR)
- `get_ocp_alarm(channel)` - Check OCP alarm status
- `get_ovp_alarm(channel)` - Check OVP alarm status
- `clear_ocp_alarm(channel)` - Clear OCP alarm
- `clear_ovp_alarm(channel)` - Clear OVP alarm
- `ping()` - Health check

## Network Discovery Tools

### Automatic Discovery
```bash
python rigol_dp832/find_dp832.py
```
Scans your network and finds DP832 devices automatically.

### Test Specific IP
```bash
python rigol_dp832/test_ip.py 192.168.1.100
```
Tests a specific IP address for DP832 connectivity.

### Comprehensive Network Scan
```bash
python rigol_dp832/network_discovery.py
```
Performs a detailed network scan with multiple discovery methods.

## API Reference

### Connection

```python
from rigol_dp832.rigol_dp import DP832

ps = DP832(
    conn_type="VISA",
    visa_resource_string="TCPIP0::<IP_ADDRESS>::5555::SOCKET"
)
```

### Device Information

```python
device_id = ps.id()
# Returns: {'manufacturer': 'RIGOL TECHNOLOGIES', 'model': 'DP832', ...}
```

### Channel Control

```python
# Set voltage and current
ps.set_channel_settings(channel=1, voltage=5.0, current=1.0)

# Enable/disable output
ps.set_output_state(channel=1, state=True)

# Get current settings
settings = ps.get_channel_settings(channel=1)
# Returns: {'voltage': 5.0, 'current': 1.0}
```

### Measurements

```python
# Individual measurements
voltage = ps.measure_voltage(channel=1)
current = ps.measure_current(channel=1)

# All measurements at once
measurements = ps.measure_all(channel=1)
# Returns: {'voltage': 5.0, 'current': 0.5, 'power': 2.5}
```

### Protection Settings

```python
# Overcurrent Protection (OCP)
ps.set_ocp_enabled(channel=1, state=True)
ps.set_ocp_value(channel=1, setting=1.5)
ocp_enabled = ps.get_ocp_enabled(channel=1)
ocp_value = ps.get_ocp_value(channel=1)

# Overvoltage Protection (OVP)
ps.set_ovp_enabled(channel=1, state=True)
ps.set_ovp_value(channel=1, setting=6.0)
ovp_enabled = ps.get_ovp_enabled(channel=1)
ovp_value = ps.get_ovp_value(channel=1)
```

## Examples

See `rigol_dp832/ethernet_example.py` for a complete working example.

## Troubleshooting

### Connection Issues

1. **Check IP Address**: Verify the IP address is correct
2. **Network Connectivity**: Ping the device: `ping 192.168.1.100`
3. **SCPI Interface**: Ensure SCPI over Ethernet is enabled on the DP832
4. **Firewall**: Check that no firewall is blocking port 5555
5. **PyVISA**: Ensure PyVISA is installed and working

### Common Error Codes

- `-1073807339`: Connection timeout (device not found or not responding)
- `-1073807343`: Invalid resource string format
- `-1073807346`: Device busy or locked

## Requirements

- Python 3.6+
- PyVISA >= 1.11.0
- Network connection to DP832

## What's Excluded

This library focuses on Ethernet connections only. The following have been intentionally excluded:

- USB/USBTMC connections
- Custom socket implementations
- Web server functionality
- OpenAI integration

## License

This project is based on the original instrument-controllables library and maintains compatibility with the DP832 instrument control functionality.

## Contributing

Feel free to submit issues and enhancement requests!