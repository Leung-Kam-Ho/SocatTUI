# SocatTUI

TUI tool for configuring socat USB serial relay/bridging. Easily bridge USB serial devices to TCP ports without editing shell scripts.

## Install

### Homebrew (macOS)

```bash
brew tap Leung-Kam-Ho/socattui
brew trust Leung-Kam-Ho/socattui
brew install socattui
```

To upgrade:

```bash
brew upgrade socattui
```

To uninstall:

```bash
brew uninstall socattui
brew untap Leung-Kam-Ho/socattui
```

### From source

```bash
# Clone the repo
git clone https://github.com/Leung-Kam-Ho/SocatTUI.git
cd SocatTUI

# Install globally as a CLI tool
uv tool install .
```

After installation, `socattui` is available globally.

**Important**: If `socattui` is not found when a venv is activated, add `~/.local/bin` to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

To upgrade:

```bash
uv tool upgrade socattui
```

To uninstall:

```bash
uv tool uninstall socattui
```

## Usage

### Launch TUI

```bash
socattui tui
```

### TUI Keybindings

| Key | Action |
|-----|--------|
| `a` | Add bridge |
| `e` | Edit selected bridge |
| `d` | Delete bridge |
| `s` | Start selected bridge |
| `x` | Stop selected bridge |
| `S` | Start all bridges |
| `X` | Stop all bridges |
| `r` | Refresh devices/status |
| `q` | Quit |

### CLI Commands

```bash
# Detect USB devices
socattui detect

# Start all configured bridges (background)
socattui up

# Stop all bridges
socattui down

# List bridges and status
socattui list
```

## Config

Saved to `~/.config/socattui/config.yaml`:

```yaml
bridges:
  - name: Arduino Uno
    device: /dev/cu.usbserial-220
    port: 7777
    baudrate: 9600
  - name: Raspberry Pi
    device: /dev/ttyACM0
    port: 7778
    baudrate: 9600
```

## Platform Support

- **macOS**: `/dev/cu.usbserial-*`, `/dev/cu.usbmodem*`
- **Linux**: `/dev/ttyACM*`, `/dev/ttyUSB*`

## Requirements

- Python 3.12+
- socat installed (`brew install socat` or `apt install socat`)
