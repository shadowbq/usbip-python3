# usbip-python3

USBIP and Python3 for Windows 10/11. These servers should be running v1.1.1 or 0x273

### Install Python3

https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe

### Admin CMD

`bcdedit /set testsigning on`
`reboot`

### Install USBip

https://github.com/vadimgrn/usbip-win2/releases/download/v.0.9.5.6/USBip-0.9.5.6-Release.exe
(Full Install)

### USB/IP Client for Windows

* Fully compatible with USB/IP protocol
* Works with Linux USB/IP server at least for kernels 4.19 - 6.2
* The driver is not signed, Windows Test Signing Mode must be enabled
* Windows 10 x64 Version 1809 (OS build 17763) and later
* Server must support USB/IP protocol v.1.1.1

Note: Is not ready for production use, can cause BSOD (whateva)

* https://github.com/vadimgrn/usbip-win2

## Run

You may want to change the `hid-mouse.py` run command to use port 50000

```python
usb_container.run(ip="0.0.0.0", port="50000")
```


```
C:\Program Files\USBip>usbip.exe -t 50000 list -r 127.0.0.1
Exportable USB devices
======================
    1-1    : unknown vendor : unknown product (2706:0000)
           : /sys/devices/pci0000:00/0000:00:01.2/usb1/1-1
           : (Defined at Interface level) (00/00/00)
           :  0 - Human Interface Device/Boot Interface Subclass/Mouse (03/01/02)
```

`.\usbip.exe -t 50000 attach -r 127.0.0.1 -b 1-1`


## Others

USB D Server is when you want to share an actual USB Device. When you use the python `hid-mouse.py`, the `USBIP.py` acts a USB-IP Server instead. 



### Install USBIPD

https://github.com/dorssel/usbipd-win/releases/download/v3.2.0/usbipd-win_3.2.0.msi

### Windows USBIP-D Server

https://github.com/dorssel/usbipd-win

Windows software for sharing locally connected USB devices to other machines, including Hyper-V guests and WSL 2.
(reference Cezanne - https://github.com/dorssel/usbipd-win/issues/79 ) 



## Classic Stuff from USBIP Community

### v1.1.1 Windows USBIP Client

*deprecated*

This project aims to support both a USB/IP server and a client on Windows platform.

https://github.com/cezanne/usbip-win
