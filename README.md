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
1. Update all Raspberry Pis to the version of Raspian.
2. On the Raspberry Pi 3 run `pip3 install spur`.
