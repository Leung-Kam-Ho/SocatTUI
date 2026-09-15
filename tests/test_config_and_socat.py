"""Tests for SocatTUI configuration and device target resolution."""

import unittest
from unittest.mock import patch, MagicMock
from socattui.config import Bridge, Config
from socattui.detector import USBDevice
from socattui.socat import start_bridge, _build_socat_cmd


class TestBridgeTargetType(unittest.TestCase):
    def test_bridge_defaults(self):
        b = Bridge(name="Test", device="/dev/ttyUSB0", port=7777)
        self.assertEqual(b.target_type, "hwid")

    def test_bridge_to_from_dict(self):
        d = {
            "name": "ExtensionPort",
            "device": "/dev/ttyUSB1",
            "port": 7778,
            "baudrate": 115200,
            "hwid": "USB VID:PID=0403:6011",
            "target_type": "device",
        }
        b = Bridge.from_dict(d)
        self.assertEqual(b.target_type, "device")
        self.assertEqual(b.to_dict()["target_type"], "device")

    def test_from_dict_backward_compatibility(self):
        d = {
            "name": "Legacy",
            "device": "/dev/ttyUSB0",
            "port": 7777,
        }
        b = Bridge.from_dict(d)
        self.assertEqual(b.target_type, "hwid")

    @patch("socattui.socat.detect_devices")
    @patch("subprocess.Popen")
    def test_start_bridge_hwid_target(self, mock_popen, mock_detect):
        mock_detect.return_value = [
            USBDevice(path="/dev/ttyUSB5", hwid="MATCH_HWID"),
        ]
        b = Bridge(
            name="HWIDTarget",
            device="/dev/ttyUSB0",
            port=7777,
            hwid="MATCH_HWID",
            target_type="hwid",
        )
        success = start_bridge(b, detached=True)
        self.assertTrue(success)
        # Should resolve device to /dev/ttyUSB5
        self.assertEqual(b.device, "/dev/ttyUSB5")

    @patch("socattui.socat.detect_devices")
    @patch("subprocess.Popen")
    def test_start_bridge_device_target(self, mock_popen, mock_detect):
        # Even if detect_devices has a matching HWID on another port
        mock_detect.return_value = [
            USBDevice(path="/dev/ttyUSB5", hwid="SAME_HWID"),
        ]
        b = Bridge(
            name="DeviceTarget",
            device="/dev/ttyUSB1",
            port=7778,
            hwid="SAME_HWID",
            target_type="device",
        )
        success = start_bridge(b, detached=True)
        self.assertTrue(success)
        # Should NOT change device to /dev/ttyUSB5 because target_type is "device"
        self.assertEqual(b.device, "/dev/ttyUSB1")
        mock_detect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
