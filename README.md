# usbip-python3

USBIP and Python3 for Windows 10/11. These servers should be running v1.1.1 or 0x273

### Install Python3

https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe

### Install USBIPD

https://github.com/dorssel/usbipd-win/releases/download/v3.2.0/usbipd-win_3.2.0.msi

### Admin CMD

`bcdedit /set testsigning on`
`reboot`

### Install USBip

https://github.com/vadimgrn/usbip-win2/releases/download/v.0.9.5.6/USBip-0.9.5.6-Release.exe
(Full Install)


## Windows USBIP-D Server

https://github.com/dorssel/usbipd-win

Windows software for sharing locally connected USB devices to other machines, including Hyper-V guests and WSL 2.
(reference Cezanne - https://github.com/dorssel/usbipd-win/issues/79 ) 


## USB/IP Client for Windows

* Fully compatible with USB/IP protocol
* Works with Linux USB/IP server at least for kernels 4.19 - 6.2
* The driver is not signed, Windows Test Signing Mode must be enabled
* Windows 10 x64 Version 1809 (OS build 17763) and later
* Server must support USB/IP protocol v.1.1.1

Note: Is not ready for production use, can cause BSOD (whateva)

https://github.com/vadimgrn/usbip-win2


## Classic Stuff from USBIP Community

### v1.1.1 Windows USBIP Client

*deprecated*

This project aims to support both a USB/IP server and a client on Windows platform.

https://github.com/cezanne/usbip-win
