"""USB device detection for macOS and Linux."""

import os
import sys
from dataclasses import dataclass
import serial.tools.list_ports


@dataclass
class USBDevice:
    """Detected USB serial device."""
    path: str
    description: str = ""
    manufacturer: str = ""
    hwid: str = ""

    @property
    def short_name(self) -> str:
        return os.path.basename(self.path)


def detect_devices() -> list[USBDevice]:
    """Detect USB serial devices based on current platform using pyserial."""
    devices = []
    
    # Get all available COM ports
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        # Ignore non-USB serial devices (optional, but usually good for a "USB Serial Bridge")
        # if not port.vid and not port.pid:
        #     continue
            
        devices.append(USBDevice(
            path=port.device,
            description=port.description or "",
            manufacturer=port.manufacturer or "",
            hwid=port.hwid or ""
        ))
        
    return devices


def get_platform() -> str:
    """Get current platform identifier."""
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform == "linux":
        return "linux"
    else:
        return "unknown"
