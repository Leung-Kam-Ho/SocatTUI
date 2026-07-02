"""Textual TUI application for SocatTUI."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import (
    Header, Footer, Static, Button, DataTable, Input, Select, Label
)
from textual.binding import Binding
from textual import on

from .config import (
    Config, Bridge, load_config, save_config, add_bridge, update_bridge, remove_bridge
)
from .detector import detect_devices, USBDevice, get_platform
from .socat import start_bridge, stop_bridge, start_all, stop_all, get_status


class AddBridgeScreen(ModalScreen[bool]):
    """Modal screen to add or edit a bridge."""

    CSS = """
    #add-dialog {
        width: 80;
        height: 28;
        border: tall $primary;
        background: $surface;
        layout: vertical;
        padding: 1 0;
    }

    #dialog-content {
        height: 1fr;
        padding: 1 3;
    }

    .form-row {
        height: 3;
        padding: 0 1;
        margin: 1 0;
    }

    .form-label {
        width: 14;
        height: 3;
        content-align: left middle;
    }

    .form-input {
        width: 1fr;
        height: 3;
    }

    #button-row {
        height: 5;
        padding: 1 3;
        align: center middle;
    }

    Button {
        margin: 0 2;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, bridge: Bridge | None = None, devices: list[USBDevice] | None = None):
        super().__init__()
        self.bridge = bridge
        self.devices = devices or []
        self.is_edit = bridge is not None

    def compose(self) -> ComposeResult:
        with Container(id="add-dialog"):
            with Container(id="dialog-content"):
                yield Static(
                    "Edit Bridge" if self.is_edit else "Add New Bridge",
                    id="dialog-title"
                )

                with Horizontal(classes="form-row"):
                    yield Label("Name:", classes="form-label")
                    yield Input(
                        value=self.bridge.name if self.bridge else "",
                        placeholder="Bridge name",
                        id="name-input",
                        classes="form-input"
                    )

                with Horizontal(classes="form-row"):
                    yield Label("Device:", classes="form-label")
                    # Build device options for Select
                    device_options = [(d.path, d.path) for d in self.devices]
                    if self.bridge:
                        # Add current device to options if not in detected list
                        if not any(d.path == self.bridge.device for d in self.devices):
                            device_options.insert(0, (self.bridge.device, self.bridge.device))
                    # Ensure at least one option
                    if not device_options:
                        device_options = [("/dev/ttyUSB0", "No devices detected")]
                    yield Select(
                        device_options,
                        allow_blank=True,
                        id="device-select",
                        classes="form-input",
                        prompt="Select device..."
                    )

                with Horizontal(classes="form-row"):
                    yield Label("Port:", classes="form-label")
                    yield Input(
                        value=str(self.bridge.port) if self.bridge else "7777",
                        placeholder="TCP port",
                        id="port-input",
                        classes="form-input"
                    )

                with Horizontal(classes="form-row"):
                    yield Label("Baudrate:", classes="form-label")
                    yield Input(
                        value=str(self.bridge.baudrate) if self.bridge else "9600",
                        placeholder="Baud rate",
                        id="baudrate-input",
                        classes="form-input"
                    )

            with Horizontal(id="button-row"):
                yield Button("Save", variant="primary", id="save-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    @on(Button.Pressed, "#save-btn")
    def save_pressed(self) -> None:
        name = self.query_one("#name-input", Input).value.strip()
        device = self.query_one("#device-select", Select).value
        port_str = self.query_one("#port-input", Input).value.strip()
        baudrate_str = self.query_one("#baudrate-input", Input).value.strip()

        if not name or not port_str:
            self.notify("Please fill all required fields", severity="error")
            return

        # Check device selection
        if device is Select.BLANK or not device:
            self.notify("Please select a device", severity="error")
            return

        # Ensure device path starts with /dev/
        if not device.startswith("/dev/"):
            device = f"/dev/{device}"

        try:
            port = int(port_str)
            baudrate = int(baudrate_str) if baudrate_str else 9600
        except ValueError:
            self.notify("Port and baudrate must be numbers", severity="error")
            return

        new_bridge = Bridge(name=name, device=device, port=port, baudrate=baudrate)

        if self.is_edit and self.bridge:
            # Update existing
            config = load_config()
            for i, b in enumerate(config.bridges):
                if b.name == self.bridge.name and b.device == self.bridge.device:
                    update_bridge(i, new_bridge)
                    break
        else:
            add_bridge(new_bridge)

        self.dismiss(True)

    @on(Button.Pressed, "#cancel-btn")
    def cancel_pressed(self) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


class SocatTUI(App):
    """Main TUI application for SocatTUI."""

    TITLE = "SocatTUI"
    SUB_TITLE = "USB Serial Bridge Manager"

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-content {
        height: 1fr;
    }

    #devices-panel {
        height: auto;
        max-height: 40%;
        border: solid $primary;
        margin: 1 0;
    }

    #bridges-panel {
        height: 1fr;
        border: solid $primary;
        margin: 1 0;
    }

    .panel-title {
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    DataTable {
        height: 1fr;
    }

    #status-bar {
        height: 3;
        dock: bottom;
    }

    .status-item {
        width: 1fr;
        content-align: left middle;
        padding: 0 1;
    }

    .button-bar {
        height: 3;
        padding: 0 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "add_bridge", "Add Bridge"),
        Binding("e", "edit_bridge", "Edit"),
        Binding("d", "delete_bridge", "Delete"),
        Binding("s", "start_selected", "Start"),
        Binding("x", "stop_selected", "Stop"),
        Binding("S", "start_all", "Start All"),
        Binding("X", "stop_all", "Stop All"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.devices: list[USBDevice] = []
        self.selected_index: int | None = None

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="main-content"):
            with ScrollableContainer(id="devices-panel"):
                yield Static("Detected USB Devices", classes="panel-title")
                yield DataTable(id="devices-table")

            with Container(id="bridges-panel"):
                yield Static("Configured Bridges", classes="panel-title")
                yield DataTable(id="bridges-table")
                with Horizontal(classes="button-bar"):
                    yield Button("Add", variant="primary", id="add-btn")
                    yield Button("Edit", variant="default", id="edit-btn")
                    yield Button("Delete", variant="error", id="delete-btn")
                    yield Button("Start", variant="success", id="start-btn")
                    yield Button("Stop", variant="warning", id="stop-btn")
                    yield Button("Start All", variant="primary", id="start-all-btn")
                    yield Button("Stop All", variant="error", id="stop-all-btn")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize tables and detect devices on app start."""
        self._refresh_devices()
        self._refresh_bridges()

    def _refresh_devices(self) -> None:
        """Detect and display USB devices."""
        self.devices = detect_devices()
        table = self.query_one("#devices-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Device", "Description")
        for dev in self.devices:
            table.add_row(dev.path, dev.description or dev.short_name)

    def _refresh_bridges(self) -> None:
        """Reload and display configured bridges."""
        self.config = load_config()
        status = get_status(self.config)

        table = self.query_one("#bridges-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Name", "Device", "Port", "Baud", "Status")

        for bridge in self.config.bridges:
            bridge_status = status.get(bridge.name, {})
            running = bridge_status.get("running", False)
            pid = bridge_status.get("pid")
            status_text = f"Running (PID: {pid})" if running else "Stopped"
            table.add_row(
                bridge.name,
                bridge.device,
                str(bridge.port),
                str(bridge.baudrate),
                status_text,
            )

    @on(Button.Pressed, "#add-btn")
    def action_add_bridge(self) -> None:
        """Open add bridge dialog."""
        self.push_screen(AddBridgeScreen(devices=self.devices), self._on_dialog_close)

    @on(Button.Pressed, "#edit-btn")
    def action_edit_bridge(self) -> None:
        """Edit selected bridge."""
        table = self.query_one("#bridges-table", DataTable)
        if table.cursor_row is None or table.cursor_row >= len(self.config.bridges):
            self.notify("No bridge selected", severity="warning")
            return
        bridge = self.config.bridges[table.cursor_row]
        self.push_screen(
            AddBridgeScreen(bridge=bridge, devices=self.devices),
            self._on_dialog_close
        )

    @on(Button.Pressed, "#delete-btn")
    def action_delete_bridge(self) -> None:
        """Delete selected bridge."""
        table = self.query_one("#bridges-table", DataTable)
        if table.cursor_row is None or table.cursor_row >= len(self.config.bridges):
            self.notify("No bridge selected", severity="warning")
            return
        bridge = self.config.bridges[table.cursor_row]
        # Stop if running
        stop_bridge(bridge)
        remove_bridge(table.cursor_row)
        self._refresh_bridges()

    @on(Button.Pressed, "#start-btn")
    def action_start_selected(self) -> None:
        """Start selected bridge."""
        table = self.query_one("#bridges-table", DataTable)
        if table.cursor_row is None or table.cursor_row >= len(self.config.bridges):
            self.notify("No bridge selected", severity="warning")
            return
        bridge = self.config.bridges[table.cursor_row]
        if start_bridge(bridge):
            self.notify(f"Started {bridge.name}")
        else:
            self.notify(f"Failed to start {bridge.name}", severity="error")
        self._refresh_bridges()

    @on(Button.Pressed, "#stop-btn")
    def action_stop_selected(self) -> None:
        """Stop selected bridge."""
        table = self.query_one("#bridges-table", DataTable)
        if table.cursor_row is None or table.cursor_row >= len(self.config.bridges):
            self.notify("No bridge selected", severity="warning")
            return
        bridge = self.config.bridges[table.cursor_row]
        stop_bridge(bridge)
        self.notify(f"Stopped {bridge.name}")
        self._refresh_bridges()

    @on(Button.Pressed, "#start-all-btn")
    def action_start_all(self) -> None:
        """Start all bridges."""
        results = start_all(self.config)
        started = sum(1 for v in results.values() if v)
        self.notify(f"Started {started}/{len(results)} bridges")
        self._refresh_bridges()

    @on(Button.Pressed, "#stop-all-btn")
    def action_stop_all(self) -> None:
        """Stop all bridges."""
        results = stop_all(self.config)
        stopped = sum(1 for v in results.values() if v)
        self.notify(f"Stopped {stopped}/{len(results)} bridges")
        self._refresh_bridges()

    def action_refresh(self) -> None:
        """Refresh devices and bridges."""
        self._refresh_devices()
        self._refresh_bridges()
        self.notify("Refreshed")

    def _on_dialog_close(self, result: bool) -> None:
        """Handle dialog close."""
        if result:
            self._refresh_bridges()


def run_tui():
    """Run the TUI application."""
    app = SocatTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
