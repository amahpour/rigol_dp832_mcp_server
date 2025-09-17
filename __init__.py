"""
Rigol DP832 Ethernet Control Library

A simple, lightweight Python library for controlling Rigol DP832 power supplies
over Ethernet using VISA TCP/IP connections.
"""

from .rigol_dp832 import DP832
from .discovery import find_dp832_devices, find_first_dp832, test_ip

__version__ = "1.0.0"
__author__ = "Ari Mahpour"
__email__ = ""

__all__ = [
    "DP832",
    "find_dp832_devices", 
    "find_first_dp832",
    "test_ip"
]
