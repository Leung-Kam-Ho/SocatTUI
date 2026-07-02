"""USB device detection for macOS and Linux."""

import os
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class USBDevice:
    """Detected USB serial device."""
    path: str
    description: str = ""
    manufacturer: str = ""

    @property
    def short_name(self) -> str:
        return os.path.basename(self.path)


def detect_macos_devices() -> list[USBDevice]:
    """Detect USB serial devices on macOS using system_profiler."""
    devices = []
    try:
        result = subprocess.run(
            ["system_profiler", "SPUSBDataType", "-json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            # Look for serial devices in USB tree
            for item in data.get("SPUSBDataType", []):
                _extract_devices(item, devices)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass

    # Also check for known serial device paths
    for dev_path in ["/dev/cu.usbserial-*", "/dev/cu.SLAB_USBtoUART", "/dev/cu.usbmodem*"]:
        import glob
        for path in glob.glob(dev_path):
            if not any(d.path == path for d in devices):
                devices.append(USBDevice(path=path, description="USB Serial"))

    return devices


def _extract_devices(item: dict, devices: list[USBDevice]) -> None:
    """Recursively extract USB devices from system_profiler output."""
    if isinstance(item, dict):
        # Check if this is a serial device
        name = item.get("_name", "")
        if "serial" in name.lower() or "uart" in name.lower() or "usb" in name.lower():
            # Look for serial port info
            for key, value in item.items():
                if isinstance(value, str) and value.startswith("/dev/"):
                    devices.append(USBDevice(
                        path=value,
                        description=name,
                        manufacturer=item.get("spd", {}).get("_name", "")
                    ))
        # Recurse into children
        for key, value in item.items():
            if isinstance(value, list):
                for subitem in value:
                    _extract_devices(subitem, devices)
            elif isinstance(value, dict):
                _extract_devices(value, devices)


def detect_linux_devices() -> list[USBDevice]:
    """Detect USB serial devices on Linux using /sys and /dev."""
    devices = []

    # Check /dev/ttyACM* and /dev/ttyUSB*
    import glob
    for pattern in ["/dev/ttyACM*", "/dev/ttyUSB*"]:
        for path in sorted(glob.glob(pattern)):
            description = ""
            # Try to get device info from sysfs
            dev_name = os.path.basename(path)
            sys_path = f"/sys/class/tty/{dev_name}/device"
            if os.path.exists(sys_path):
                try:
                    # Get product name
                    product_path = os.path.join(os.path.dirname(sys_path), "product")
                    if os.path.exists(product_path):
                        with open(product_path, "r") as f:
                            description = f.read().strip()
                except (IOError, OSError):
                    pass

            devices.append(USBDevice(path=path, description=description))

    return devices


def detect_devices() -> list[USBDevice]:
    """Detect USB serial devices based on current platform."""
    if sys.platform == "darwin":
        return detect_macos_devices()
    elif sys.platform == "linux":
        return detect_linux_devices()
    else:
        return []


def get_platform() -> str:
    """Get current platform identifier."""
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform == "linux":
        return "linux"
    else:
        return "unknown"
