# photoPi
A system of networked Raspberry Pi Cameras which captures pictures simultaneously in quick\* succession for later use in a photogrammetry application.

## Requirements
This repository is based on a specific set of budget-friendly requirements but every effort has been made to keep it scalable and flexible.
### Hardware
- 1 Raspberry Pi 3 Model B+
- 1 USB WiFi Adapter ([example](https://www.amazon.com/gp/product/B003MTTJOY/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&psc=1))
- Many Raspberry Pi Zero W
- Many Raspberry Pi Camera Modules
  - Camera V2
  - NoIR Camera V2
### Software
This project would not be possible without these amazing repositories:
- [RaspAP](https://github.com/billz/raspap-webgui) by Bill Zimmerman
- [Spur](https://github.com/mwilliamson/spur.py) by Michael Williamson
- [PiCamera](https://github.com/waveform80/picamera) by Dave Jones

## Getting Started
1. Update all Raspberry Pis to the latest version of Raspian.  Ensure each Pi has a unique hostname and the same username and password.
2. On the Raspberry Pi 3 run `pip3 install spur` to install the Spur repository.  This will allow the Pi Server to initiate a SSH connection to the Pi Zero W's.
3. Plug in the USB WiFi Adapter and follow the RaspAP [quick installation instructions](https://github.com/billz/raspap-webgui#prerequisites) to set up an access point on the Pi 3.
4. Connect the Pi Zero W's to the newly set up Pi 3 access point.
5. Copy `captureServer.py` and `clientIP.txt`, `path.txt`, and `ssh.txt` from configSamples onto the Pi 3.
6. RaspAP will have set up an apache server at `\var\www\html`.  Create a new folder inside that directory (`\var\www\html\[newFolder]`) and copy `captureClient.py` into that new directory.
7. Update `clientIP.txt`, `path.txt`, and `ssh.txt`.

## Operation
1. Run `python3 captureServer.py` on the Pi 3.
2. The Pi 3 will open a socket for each client Pi Zero W and issue an SSH command to each client which downloads and runs `captureClient.py`.
3. Enter file name, image format, and sequence length when prompted.
4. The Pi 3 will generate 5 Exposure Profiles and publish them on the local server for the user to inspect.  Choose one when prompted.
5. The Pi 3 will trigger synchronized captures on all clients for the duration of the user set sequence length.

## Troubleshooting
 -  `clientReboot.py` will force all clients and finally the server to reboot which in effect closes unsused or dead sockets.
 - `captureServer.py` will error if establishing a SSH connection to a client for the first time.  Running `ssh [user]@client.IP.Address` and accepting the subsequent unknown HASH prompt for each client will remedy this.
