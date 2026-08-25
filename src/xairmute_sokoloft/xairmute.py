"""
xairmute_sokoloft - CLI for Behringer X-Air Mixers
Copyright (C) 2026 Sokoloft Kado

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, version 3 of the License.
"""

# Depends:
# pip install python-osc

import sys
from json import dump, load, JSONDecodeError
from ipaddress import IPv4Address, ip_address
from socket import socket, AF_INET, SOCK_DGRAM, timeout, SOL_SOCKET, SO_REUSEADDR
from argparse import ArgumentParser
from pathlib import Path
from time import sleep

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_packet import OscPacket

App = "xairmute"
Version = "1.0.3"

CONFIG_DIR = Path.home() / ".config" / App
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "mixer_ip": "",
    "mixer_port": 10024,
    "timeout_seconds": 0.1
}


# ---------- Config Helpers ----------

def read_config():
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as config_file:
            return load(config_file)
    except JSONDecodeError:
        print(f"\nInvalid config file: {CONFIG_FILE}")
        sys.exit(1)


def write_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as config_file:
        dump(config, config_file, indent=4)


def prompt_value(prompt_text, validator, error_message):
    while True:
        value = input(f"\n{prompt_text}: ").strip()
        try:
            return validator(value)
        except ValueError:
            print(f"\n{error_message}")


def validate_ip(value):
    IPv4Address(value)
    return value


def ip_prompt():
    return prompt_value(
        "Enter your Mixer's IP address",
        validate_ip,
        "Invalid IP address. Please enter a valid IPv4 address."
    )


def validate_port(value):
    port = int(value)
    if not 1024 <= port <= 65535:
        raise ValueError
    return port


def port_prompt():
    prompt = input("\nUse default port 10024? (Y/n): ").strip().lower()

    if prompt in ("", "y", "yes"):
        return 10024

    return prompt_value(
        "Enter your Mixer's OSC port (1024–65535)",
        validate_port,
        "Port must be a number between 1024 and 65535."
    )


def ensure_config():
    config = read_config()

    if not config.get("mixer_ip"):
        print("First run detected — configuration required.")
        ip = ip_prompt()
        port = port_prompt()

        config["mixer_ip"] = ip
        config["mixer_port"] = port

        write_config(config)
        print(f"\nCreated {CONFIG_FILE} successfully.\n")
        sys.exit(0)

    return config


# ---------- OSC Helpers ----------

def send_query(sock, address, mixer_ip, mixer_port):
    builder = OscMessageBuilder(address=address)
    msg = builder.build()
    sock.sendto(msg.dgram, (mixer_ip, mixer_port))


def send_value(sock, address, value, mixer_ip, mixer_port):
    builder = OscMessageBuilder(address=address)
    builder.add_arg(value)
    msg = builder.build()
    sock.sendto(msg.dgram, (mixer_ip, mixer_port))


def wait_for_reply(sock, address):
    try:
        while True:
            data, _ = sock.recvfrom(4096)
            packet = OscPacket(data)
            for timed in packet.messages:
                msg = timed.message
                if msg.address == address:
                    return msg.params[0]
    except timeout:
        print("\nError: No response from the mixer (timeout).")
        sys.exit(1)


# ---------- Main ----------

def main():
    parser = ArgumentParser(
        prog=f"{App}",
        description="Toggle a Channel or Mute Group with OSC on Behringer X-Air Series Mixers via CLI"
    )

    parser.add_argument("-v", "--version", action="version", version=f"{App} {Version}")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--channel", type=int, metavar="#", help="toggle channel # (1-16)")
    group.add_argument("-g", "--group", type=int, metavar="#", help="toggle mute group # (1-4)")
    group.add_argument("-q", "--query", type=int, metavar="#", help="query channel mute status")
    group.add_argument("--fx", type=int, metavar="#", help="toggle FX # (1-4)")
    group.add_argument("--aux", action="store_true", help="toggle Aux mute")
    group.add_argument("--main", action="store_true", help="toggle Main L/R mute")
    group.add_argument(
        "--port",
        nargs="?",
        const=True,
        metavar="PORT",
        type=int,
        help="change mixer's port in config"
    )
    group.add_argument(
        "--ip",
        nargs="?",
        const=True,
        metavar="192.168.X.XXX",
        help="change mixer's ip in config"
    )

    args = parser.parse_args()

    # ----- IP -----
    if args.ip is not None:

        config = read_config()

        # Interactive mode
        if args.ip is True:
            new_ip = ip_prompt()
        else:
            try:
                IPv4Address(args.ip)
                new_ip = args.ip
            except ValueError:
                parser.error("Invalid IP address format.")

        config["mixer_ip"] = new_ip
        write_config(config)

        print(f"\nMixer IP set to {new_ip}\n")
        sys.exit(0)


    # ----- Port -----
    if args.port is not None:

        config = read_config()

        if args.port is True:
            new_port = port_prompt()
        else:
            new_port = args.port
            if not 1024 <= new_port <= 65535:
                parser.error("Port must be between 1024 and 65535")

        config["mixer_port"] = new_port
        write_config(config)

        print(f"\nMixer port set to {new_port}\n")
        sys.exit(0)


    # ----- Load config for normal operation -----
    config = ensure_config()

    mixer_ip = str(config["mixer_ip"])
    mixer_port = int(config["mixer_port"])
    timeout_seconds = float(config["timeout_seconds"])

    try:
        ip_address(mixer_ip)
    except ValueError:
        print(f"\nInvalid IP in {CONFIG_FILE}. Use --ip to fix it.\n")
        sys.exit(1)


    # ----- Determine target -----
    if args.channel is not None:
        if not 1 <= args.channel <= 16:
            parser.error("Channel number must be between 1 and 16")
        address = f"/ch/{args.channel:02d}/mix/on"

    elif args.group is not None:
        if not 1 <= args.group <= 4:
            parser.error("Mute group number must be between 1 and 4")
        address = f"/config/mute/{args.group}"

    elif args.query is not None:
        if not 1 <= args.query <= 16:
            parser.error("Query number must be between 1 and 16")
        address = f"/ch/{args.query:02d}/mix/on"

    elif args.fx is not None:
        if not 1 <= args.fx <= 4:
            parser.error("FX number must be between 1 and 4")
        address = f"/rtn/{args.fx}/mix/on"

    elif args.aux:
        address = f"/rtn/aux/mix/on"

    elif args.main:
        address = f"/lr/mix/on"

    else:
        parser.error("You must specify a valid command. Run with -h to see commands.")

    query_mode = args.query is not None


    # ----- Toggle Logic -----
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.settimeout(timeout_seconds)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(("", 0))

        send_query(sock, address, mixer_ip, mixer_port)
        current = wait_for_reply(sock, address)

        if not query_mode:
            new_value = 0 if current == 1 else 1
            send_value(sock, address, new_value, mixer_ip, mixer_port)

            sleep(0.01)

            send_query(sock, address, mixer_ip, mixer_port)
            confirmed = wait_for_reply(sock, address)
        else:
            confirmed = current

    if confirmed not in (0, 1):
        print("Warning: Unexpected response from mixer.")
        sys.exit(1)

    state = "MUTED" if confirmed == 0 else "UNMUTED"
    print(state)


def main_cli():
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)

if __name__ == "__main__":
    main_cli()
