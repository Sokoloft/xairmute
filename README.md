# xairmute
Toggle a Channel or Mute Group with OSC on Behringer X-Air Series Mixers via CLI

### Why?
I needed the ability to mute microphone channels and groups via a keybind.
This script in conjunction with KDE's shortcuts system setting does just that.

This should work on Windows/macOS, but I have yet to test it.

"Vibe coded" with ChatGPT.

## Usage
```
usage: xairmute [-h] [-v] [-c # | -g # | -q # | --fx # | --aux | --main | --port [PORT] | --ip [192.168.X.XXX]]

Toggle a Channel or Mute Group with OSC on Behringer X-Air Series Mixers via CLI

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c, --channel #       toggle channel # (1-16)
  -g, --group #         toggle mute group # (1-4)
  -q, --query #         query channel mute status
  --fx #                toggle FX # (1-4)
  --aux                 toggle Aux mute
  --main                toggle Main L/R mute
  --port [PORT]         change mixer's port in config
  --ip [192.168.X.XXX]  change mixer's ip in config
```

## Installation

It's as simple as `pip install xairmute`

### Docs used

[X-Air / M-Air OSC Commands](https://web.archive.org/web/20260607074026/https://behringer.world/wiki/doku.php?id=x-air_osc)

[X AIR Mixer Series Remote Control Protocol](https://archive.org/details/x-air-remote-control-protocol)
