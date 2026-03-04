# xairmute
Toggle a Channel or Mute Group with OSC on Behringer X-Air Series Mixers via CLI

### Why?
I needed the ability to mute microphone channels and groups via a keybind.
This script in conjunction with KDE's shortcuts system setting does just that.

This should work on Windows/macOS, but I have yet to test it.

"Vibe coded" with ChatGPT.

## Usage
```
usage: xairmute [-h] [-v] [-c # | -g # | --port [PORT] | --ip [192.168.X.XXX]]

Toggle a Channel or Mute Group with OSC on Behringer X-Air Series Mixers via CLI

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c, --channel #       toggle channel # (1-18)
  -g, --group #         toggle mute group # (1-4)
  --port [PORT]         change mixer's port in config
  --ip [192.168.X.XXX]  change mixer's ip in config
```

## Installation

It's as simple as `pip install xairmute`

### Docs used

[X-Air / M-Air OSC Commands](https://behringer.world/wiki/doku.php?id=x-air_osc)

[X AIR Mixer Series Remote Control Protocol](https://cdn.mediavalet.com/aunsw/musictribe/hmivS7F05kKSJlWDYPGLpA/agTKkSIWS0y1bJl97YZEjg/Original/X%20AIR%20Remote%20Control%20Protocol.pdf)