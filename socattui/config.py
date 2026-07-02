"""YAML configuration manager for SocatTUI."""

import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

import yaml


CONFIG_DIR = Path.home() / ".config" / "socattui"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


@dataclass
class Bridge:
    """A single socat bridge configuration."""
    name: str
    device: str
    port: int
    baudrate: int = 9600
    pid: Optional[int] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("pid", None)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Bridge":
        return cls(
            name=data["name"],
            device=data["device"],
            port=data["port"],
            baudrate=data.get("baudrate", 9600),
        )


@dataclass
class Config:
    """Application configuration."""
    bridges: list[Bridge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"bridges": [b.to_dict() for b in self.bridges]}

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        bridges = [Bridge.from_dict(b) for b in data.get("bridges", [])]
        return cls(bridges=bridges)


def load_config() -> Config:
    """Load config from YAML file, or return empty config."""
    if not CONFIG_FILE.exists():
        return Config()
    with open(CONFIG_FILE, "r") as f:
        data = yaml.safe_load(f) or {}
    return Config.from_dict(data)


def save_config(config: Config) -> None:
    """Save config to YAML file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)


def add_bridge(bridge: Bridge) -> Config:
    """Add a bridge to config and save."""
    config = load_config()
    config.bridges.append(bridge)
    save_config(config)
    return config


def update_bridge(index: int, bridge: Bridge) -> Config:
    """Update a bridge at index and save."""
    config = load_config()
    if 0 <= index < len(config.bridges):
        config.bridges[index] = bridge
        save_config(config)
    return config


def remove_bridge(index: int) -> Config:
    """Remove a bridge at index and save."""
    config = load_config()
    if 0 <= index < len(config.bridges):
        config.bridges.pop(index)
        save_config(config)
    return config
