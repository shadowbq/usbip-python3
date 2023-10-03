import time
import random
import datetime
from USBIP import BaseStructure, USBDevice, InterfaceDescriptor, DeviceDescriptor, DeviceConfiguration, EndpointDescriptor, USBContainer


# data event counter
count = 0

# Emulating USB mouse

# HID Configuration


class HIDDescriptor(BaseStructure):
    _byte_order_ = '<'
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 0x21),  # HID
        ('bcdHID', 'H'),
        ('bCountryCode', 'B'),
        ('bNumDescriptors', 'B'),
        ('bDescriptorType1', 'B'),
        ('wDescriptionLength', 'H'),
    ]


hid_descriptor = HIDDescriptor(bcdHID=0x0001,  # Mouse
                     bCountryCode=0x0,
                     bNumDescriptors=0x1,
                     bDescriptorType1=0x22,  # Report
                     wDescriptionLength=0x0034)


interface_d = InterfaceDescriptor(bAlternateSetting=0,
                                  bNumEndpoints=1,
                                  bInterfaceClass=3,  # class HID
                                  bInterfaceSubClass=1,
                                  bInterfaceProtocol=2,
                                  iInterface=0)

end_point = EndpointDescriptor(bEndpointAddress=0x81,
                     bmAttributes=0x3,
                     wMaxPacketSize=0x0008, 
                     bInterval=0xFF)  # interval to report

mouse_device_descriptor = DeviceDescriptor(bDeviceClass=0x0,
                                           bDeviceSubClass=0x0,
                                           bDeviceProtocol=0x0,
                                           bMaxPacketSize0=0x8,
                                           idVendor=0x2706,
                                           idProduct=0x0,
                                           bcdDevice=0x0,
                                           bNumConfigurations=1)

configuration = DeviceConfiguration(wTotalLength=0x0022,
                                    bNumInterfaces=0x1,
                                    bConfigurationValue=1,
                                    iConfiguration=0x0,  # No string
                                    bmAttributes=0x80,  # valid self powered
                                    bMaxPower=50)  # 100 mA current

interface_d.class_descriptor = hid_descriptor
interface_d.endpoints = [end_point]  # Supports only one endpoint
interface = [interface_d] # List of interface alternatives
configuration.interfaces = [interface]   # Supports only one interface


class USBHID(USBDevice):
    configurations = [configuration]  # Supports only one configuration
    device_descriptor = mouse_device_descriptor

    def __init__(self):
        USBDevice.__init__(self)
        self.start_time = datetime.datetime.now()

    def generate_mouse_report(self):

        arr = [0x05, 0x01,		# Usage Page (Generic Desktop)
               0x09, 0x02,		# Usage (Mouse)
               0xa1, 0x01,		# Collection (Application)
               0x09, 0x01,  # Usage (Pointer)
               0xa1, 0x00,  # Collection (Physical)
               0x05, 0x09,  # Usage Page (Button)
               0x19, 0x01,  # Usage Minimum (1)
               0x29, 0x03,  # Usage Maximum (3)
               0x15, 0x00,  # Logical Minimum (0)
               0x25, 0x01,  # Logical Maximum (1)
               0x95, 0x03,  # Report Count (3)
               0x75, 0x01,  # Report Size (1)
               0x81, 0x02,  # Input (Data, Variable, Absolute)
               0x95, 0x01,  # Report Count (1)
               0x75, 0x05,  # Report Size (5)
               0x81, 0x01,  # Input (Constant)
               0x05, 0x01,  # Usage Page (Generic Desktop)
               0x09, 0x30,  # Usage (X)
               0x09, 0x31,  # Usage (Y)
               0x09, 0x38,  # Usage (Wheel)
               0x15, 0x81,  # Logical Minimum (-0x7f)
               0x25, 0x7f,  # Logical Maximum (0x7f)
               0x75, 0x08,  # Report Size (8)
               0x95, 0x03,  # Report Count (3)
               0x81, 0x06,  # Input (Data, Variable, Relative)
               0xc0,  # End Collection
               0xc0]		# End Collection
        return bytearray(arr)

    def comp(self, val):
        if val >= 0:
            return val
        else:
            return 256 + val

    def handle_data(self, usb_req):
        # Sending random mouse data
        # Send data only for 5 seconds
        # if (datetime.datetime.now() - self.start_time).seconds < 10:
        global count
        if count < 100:
            mouse_data = [0x0, self.comp(random.randint(-5, 5)), self.comp(random.randint(-5, 5)), 0]
            ret = bytearray(mouse_data)
            self.send_usb_ret(usb_req, ret, len(ret))
            time.sleep(0.05)
        count = count + 1

    def handle_device_specific_control(self, control_req, usb_req):
        if control_req.bmRequestType == 0x81:
            if control_req.bRequest == 0x6:  # Get Descriptor
                descriptor_type, descriptor_index = control_req.wValue.to_bytes(length=2, byteorder='big')
                if descriptor_type == 0x22:  # send initial report
                    print('send initial report')
                    ret = self.generate_mouse_report()
                    self.send_usb_ret(usb_req, ret, len(ret))

        if control_req.bmRequestType == 0x21:  # Host Request
            if control_req.bRequest == 0x0a:  # set idle
                print('Idle')
                # Idle
                # self.send_ok(usb_req)
                self.send_usb_ret(usb_req, b'', 0, 0)
                pass


usb_dev = USBHID()
usb_container = USBContainer()
usb_container.add_usb_device(usb_dev)  # Supports only one device!
usb_container.run()

# Run in cmd: usbip.exe -a 127.0.0.1 "1-1"
