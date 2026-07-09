# SocatTUI

TUI tool for configuring socat USB serial relay/bridging. Easily bridge USB serial devices to TCP ports without editing shell scripts.

**Features:**
- Automatic Hardware ID (HWID) tracking: Bridges reliably reconnect to your USB devices even if the OS assigns them a different device path (e.g. changing from `/dev/ttyUSB0` to `/dev/ttyUSB1`).
- Intuitive TUI for managing multiple bridges.
- CLI for quick start/stop operations.

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
    hwid: 'USB VID:PID=2341:0043 SER=557363138333512022D2 LOCATION=2-1'
    port: 7777
    baudrate: 9600
  - name: Raspberry Pi
    device: /dev/ttyACM0
    hwid: 'USB VID:PID=2E8A:0005 SER=E66058388325B229 LOCATION=1-1'
    port: 7778
    baudrate: 9600
```

## Platform Support

- **macOS**: `/dev/cu.usbserial-*`, `/dev/cu.usbmodem*`
- **Linux**: `/dev/ttyACM*`, `/dev/ttyUSB*`

## Requirements

- Python 3.12+
- socat installed (`brew install socat` or `apt install socat`)

## Roadmap

SocatTUI currently works perfectly fine for USB serial to TCP bridging. However, the ultimate future goal is to support **all** functions and address types available in the `socat` utility, providing a complete and intuitive TUI for any complex `socat` configuration.

- [x] USB Serial to TCP bridging
- [ ] UDP support
- [ ] UNIX domain sockets
- [ ] File/Pipe streaming
- [ ] SSL/TLS wrapping
- [ ] Advanced `socat` options support

## Contributing

Contributions are always welcome! If you'd like to help achieve the roadmap goals, fix bugs, or improve the TUI:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Feel free to open an issue for bug reports, suggestions, or feature requests.
