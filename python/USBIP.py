import socket
import struct
from abc import ABC, abstractmethod


USBIP_DIR_OUT = 0
USBIP_DIR_IN = 1


class BaseStructure(ABC):
    def __init__(self, **kwargs):
        self.init_from_dict(**kwargs)
        for field in self._fields_:
            if len(field) > 2:
                if not hasattr(self, field[0]):
                    setattr(self, field[0], field[2])

    def init_from_dict(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def size(self):
        return struct.calcsize(self.format())

    def format(self):
        pack_format = self._byte_order_
        for field in self._fields_:
            if isinstance(field[1], BaseStructure):
                pack_format += str(field[1].size()) + 's'
            else:
                pack_format += field[1]
        return pack_format

    def pack(self):
        values = []
        for field in self._fields_:
            if isinstance(field[1], BaseStructure):
                values.append(getattr(self, field[0], 0).pack())
            else:
                values.append(getattr(self, field[0], 0))
        return struct.pack(self.format(), *values)

    def unpack(self, buf):
        values = struct.unpack(self.format(), buf)
        keys_vals = {}
        for i, val in enumerate(values):
            keys_vals[self._fields_[i][0]] = val

        self.init_from_dict(**keys_vals)

    @property
    @abstractmethod
    def _byte_order_(self): pass

    @property
    @abstractmethod
    def _fields_(self): pass


class USBIPHeader(BaseStructure):
    _byte_order_ = '>'  # USBIP uses big-endian
    _fields_ = [
        ('version', 'H', 0x0111),  # USB/IP version 1.1.1
        ('command', 'H'),
        ('status', 'I')
    ]


class USBInterface(BaseStructure):
    _byte_order_ = '>'
    _fields_ = [
        ('bInterfaceClass', 'B'),
        ('bInterfaceSubClass', 'B'),
        ('bInterfaceProtocol', 'B'),
        ('align', 'B', 0)
    ]


class OP_REP_DevList(BaseStructure):
    _byte_order_ = '>'
    _fields_ = [
        ('base', USBIPHeader()),
        ('nExportedDevice', 'I'),
        ('usbPath', '256s'),
        ('busID', '32s'),
        ('busnum', 'I'),
        ('devnum', 'I'),
        ('speed', 'I'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bConfigurationValue', 'B'),
        ('bNumConfigurations', 'B'),
        ('bNumInterfaces', 'B'),
        ('interfaces', USBInterface())
    ]


class OP_REP_Import(BaseStructure):
    _byte_order_ = '>'
    _fields_ = [
        ('base', USBIPHeader()),
        ('usbPath', '256s'),
        ('busID', '32s'),
        ('busnum', 'I'),
        ('devnum', 'I'),
        ('speed', 'I'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bConfigurationValue', 'B'),
        ('bNumConfigurations', 'B'),
        ('bNumInterfaces', 'B')
    ]


class USBIP_RET_Submit(BaseStructure):
    _byte_order_ = '>'
    _fields_ = [
        ('command', 'I'),
        ('seqnum', 'I'),
        ('devid', 'I', 0),
        ('direction', 'I', 0),
        ('ep', 'I', 0),
        ('status', 'I'),
        ('actual_length', 'I'),
        ('start_frame', 'I', 0),
        ('number_of_packets', 'I', 0xffffffff),
        ('error_count', 'I'),
        ('padding', 'Q', 0)
    ]

    def pack(self):
        packed_data = BaseStructure.pack(self)
        packed_data += self.data
        return packed_data


class USBIP_CMD_Submit(BaseStructure):
    _byte_order_ = '>'
    _fields_ = [
        ('command', 'I'),
        ('seqnum', 'I'),
        ('devid', 'I'),
        ('direction', 'I'),
        ('ep', 'I'),  # endpoint
        ('transfer_flags', 'I'),
        ('transfer_buffer_length', 'I'),
        ('start_frame', 'I'),
        ('number_of_packets', 'I'),
        ('interval', 'I'),
        ('setup', '8s')
    ]


class StandardDeviceRequest(BaseStructure):
    _byte_order_ = '<'  # USB uses little-endian
    _fields_ = [
        ('bmRequestType', 'B'),
        ('bRequest', 'B'),
        ('wValue', 'H'),
        ('wIndex', 'H'),
        ('wLength', 'H')
    ]


class DeviceDescriptor(BaseStructure):
    _byte_order_ = '<'
    _fields_ = [
        ('bLength', 'B', 18),
        ('bDescriptorType', 'B', 1),
        ('bcdUSB', 'H', 0x0110),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bMaxPacketSize0', 'B'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('iManufacturer', 'B', 0),
        ('iProduct', 'B', 0),
        ('iSerialNumber', 'B', 0),
        ('bNumConfigurations', 'B')
    ]


class DeviceConfiguration(BaseStructure):
    _byte_order_ = '<'
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 2),
        ('wTotalLength', 'H'),
        ('bNumInterfaces', 'B'),
        ('bConfigurationValue', 'B', 1),
        ('iConfiguration', 'B', 0),
        ('bmAttributes', 'B', 0x80),
        ('bMaxPower', 'B')
    ]


class BOSDescriptor(BaseStructure):
    _byte_order_ = '<'
    _fields_ = [
        ('bLength', 'B', 0x05),
        ('bDescriptorType', 'B', 0x0F),  # Binary Device Object Store (BOS) Descriptor
        ('wTotalLength', 'H'),
        ('bNumDeviceCaps', 'B'),
    ]


class DeviceQualifierDescriptor(BaseStructure):
    _byte_order_ = '<'
    _fields_ = [
        ('bLength', 'B', 0x0a),
        ('bDescriptorType', 'B', 0x06),  # Device Qualifier Descriptor
        ('bcdUSB', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bMaxPacketSize0', 'B'),
        ('bNumConfigurations', 'B'),
        ('bReserved', 'B', 0),
    ]


class InterfaceDescriptor(BaseStructure):
    _byte_order_ = '<'
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 4),
        ('bInterfaceNumber', 'B', 0),
        ('bAlternateSetting', 'B', 0),
        ('bNumEndpoints', 'B', 1),
        ('bInterfaceClass', 'B'),
        ('bInterfaceSubClass', 'B'),
        ('bInterfaceProtocol', 'B'),
        ('iInterface', 'B', 0)
    ]


class EndpointDescriptor(BaseStructure):
    _byte_order_ = '<'
    _fields_ = [
        ('bLength', 'B', 7),
        ('bDescriptorType', 'B', 0x5),
        ('bEndpointAddress', 'B'),
        ('bmAttributes', 'B'),
        ('wMaxPacketSize', 'H'),
        ('bInterval', 'B')
    ]


class USBRequest():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class USBDevice(ABC):
    '''
    Abstract Base Class
    '''

    @property
    @abstractmethod
    def configurations(self): pass

    @property
    @abstractmethod
    def device_descriptor(self): pass

    def __init__(self):
        self.generate_raw_configuration()

    def generate_raw_configuration(self):
        all_configurations = bytearray()
        for configuration in self.configurations:
            all_configurations.extend(configuration.pack())
            for interface in configuration.interfaces:
                for interface_alternative in interface:
                    all_configurations.extend(interface_alternative.pack())
                    if hasattr(interface_alternative, 'class_descriptor'):
                        all_configurations.extend(interface_alternative.class_descriptor.pack())
                    for endpoint in interface_alternative.endpoints:
                        all_configurations.extend(endpoint.pack())
                        if hasattr(endpoint, 'class_descriptor'):
                            all_configurations.extend(endpoint.class_descriptor.pack())
        self.all_configurations = all_configurations

    def send_usb_ret(self, usb_req, usb_res, usb_len, status=0):
        print(f'Sending {bytes_to_string(usb_res)}')
        self.connection.sendall(USBIP_RET_Submit(command=0x3,
                                                 seqnum=usb_req.seqnum,
                                                 status=status,
                                                 actual_length=usb_len,
                                                 data=usb_res).pack())

    def handle_get_descriptor(self, control_req, usb_req):
        handled = False
        descriptor_type, descriptor_index = control_req.wValue.to_bytes(length=2, byteorder='big')
        print(f"handle_get_descriptor {descriptor_type:n} {descriptor_index:n}")
        if descriptor_type == 0x01:  # Device Descriptor
            handled = True
            ret = self.device_descriptor.pack()
            self.send_usb_ret(usb_req, ret, len(ret))
        elif descriptor_type == 0x02:  # Configuration Descriptor
            handled = True
            ret = self.all_configurations[:control_req.wLength]
            self.send_usb_ret(usb_req, ret, len(ret))

        return handled

    def handle_set_configuration(self, control_req, usb_req):
        # Only supports 1 configuration
        print(f"handle_set_configuration {control_req.wValue:n}")
        self.send_usb_ret(usb_req, b'', 0)
        return True

    def handle_usb_control(self, usb_req):
        control_req = StandardDeviceRequest()
        control_req.unpack(usb_req.setup)
        handled = False
        print(f"  UC Request Type {control_req.bmRequestType}")
        print(f"  UC Request {control_req.bRequest}")
        print(f"  UC Value  {control_req.wValue}")
        print(f"  UC Index  {control_req.wIndex}")
        print(f"  UC Length {control_req.wLength}")
        if control_req.bmRequestType == 0x80:  # Data flows IN, from Device to Host
            if control_req.bRequest == 0x00:  # GET_STATUS
                attributes = self.configurations[0].bmAttributes
                is_self_powered = attributes & (1 << 6)
                is_remote_wakeup = attributes & (1 << 5)
                ret = 0x0000 | (is_remote_wakeup << 1) | (is_self_powered)
                self.send_usb_ret(usb_req, ret, 2)
                handled = True

            elif control_req.bRequest == 0x06:  # GET_DESCRIPTOR
                handled = self.handle_get_descriptor(control_req, usb_req)

        elif control_req.bmRequestType == 0x00:  # Data flows OUT, from Host to Device
            if control_req.bRequest == 0x09:  # Set Configuration
                handled = self.handle_set_configuration(control_req, usb_req)

        if not handled:
            self.handle_device_specific_control(control_req, usb_req)

    def handle_usb_request(self, usb_req):
        if usb_req.ep == 0:  # Endpoint 0 is always the control endpoint
            self.handle_usb_control(usb_req)
        else:
            self.handle_data(usb_req)

    @abstractmethod
    def handle_data(self, usb_req):
        pass

    @abstractmethod
    def handle_device_specific_control(self, usb_req):
        pass


def bytes_to_string(bytes):
    if bytes:
        return ''.join(["\\x{0:02x}".format(val) for val in bytes])
    return None


class USBContainer:
    usb_devices = []

    def add_usb_device(self, usb_device):
        self.usb_devices.append(usb_device)

    def handle_attach(self):
        usb_dev = self.usb_devices[0]
        device_descriptor = usb_dev.device_descriptor
        return OP_REP_Import(base=USBIPHeader(command=3, status=0),
                             usbPath='/sys/devices/pci0000:00/0000:00:01.2/usb1/1-1'.encode('ascii'),
                             busID='1-1'.encode('ascii'),
                             busnum=1,
                             devnum=2,
                             speed=2,
                             idVendor=device_descriptor.idVendor,
                             idProduct=device_descriptor.idProduct,
                             bcdDevice=device_descriptor.bcdDevice,
                             bDeviceClass=device_descriptor.bDeviceClass,
                             bDeviceSubClass=device_descriptor.bDeviceSubClass,
                             bDeviceProtocol=device_descriptor.bDeviceProtocol,
                             bConfigurationValue=usb_dev.configurations[0].bConfigurationValue,
                             bNumConfigurations=device_descriptor.bNumConfigurations,
                             bNumInterfaces=usb_dev.configurations[0].bNumInterfaces)

    def handle_device_list(self):
        usb_dev = self.usb_devices[0]
        device_descriptor = usb_dev.device_descriptor
        return OP_REP_DevList(base=USBIPHeader(command=5, status=0),
                              nExportedDevice=1,
                              usbPath='/sys/devices/pci0000:00/0000:00:01.2/usb1/1-1'.encode('ascii'),
                              busID='1-1'.encode('ascii'),
                              busnum=1,
                              devnum=2,
                              speed=2,
                              idVendor=device_descriptor.idVendor,
                              idProduct=device_descriptor.idProduct,
                              bcdDevice=device_descriptor.bcdDevice,
                              bDeviceClass=device_descriptor.bDeviceClass,
                              bDeviceSubClass=device_descriptor.bDeviceSubClass,
                              bDeviceProtocol=device_descriptor.bDeviceProtocol,
                              bConfigurationValue=usb_dev.configurations[0].bConfigurationValue,
                              bNumConfigurations=device_descriptor.bNumConfigurations,
                              bNumInterfaces=usb_dev.configurations[0].bNumInterfaces,
                              interfaces=USBInterface(bInterfaceClass=usb_dev.configurations[0].interfaces[0][0].bInterfaceClass,
                                                      bInterfaceSubClass=usb_dev.configurations[0].interfaces[0][0].bInterfaceSubClass,
                                                      bInterfaceProtocol=usb_dev.configurations[0].interfaces[0][0].bInterfaceProtocol))

    def run(self, ip='0.0.0.0', port=3240):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, port))
        s.listen()
        attached = False
        req = USBIPHeader()
        while 1:
            conn, addr = s.accept()
            print('Connection address:', addr)
            while 1:
                if not attached:
                    data = conn.recv(8)
                    if not data:
                        break
                    req.unpack(data)
                    print('Header Packet')
                    print('command:', hex(req.command))
                    if req.command == 0x8005:  # OP_REQ_DEVLIST
                        print('list of devices')
                        conn.sendall(self.handle_device_list().pack())
                    elif req.command == 0x8003:  # OP_REQ_IMPORT
                        print('attach device')
                        conn.recv(32)  # receive bus id
                        conn.sendall(self.handle_attach().pack())
                        attached = True
                else:
                    print('----------------')
                    print('handles requests')
                    cmd = USBIP_CMD_Submit()
                    cmd_header_data = conn.recv(cmd.size())
                    cmd.unpack(cmd_header_data)
                    transfer_buffer = conn.recv(cmd.transfer_buffer_length) if cmd.direction == USBIP_DIR_OUT else None
                    print(f"usbip cmd {cmd.command:x}")
                    print(f"usbip seqnum {cmd.seqnum:x}")
                    print(f"usbip devid {cmd.devid:x}")
                    print(f"usbip direction {cmd.direction:x}")
                    print(f"usbip ep {cmd.ep:x}")
                    print(f"usbip flags {cmd.transfer_flags:x}")
                    print(f"usbip transfer buffer length {cmd.transfer_buffer_length:x}")
                    print(f"usbip start {cmd.start_frame:x}")
                    print(f"usbip number of packets {cmd.number_of_packets:x}")
                    print(f"usbip interval {cmd.interval:x}")
                    print(f"usbip setup {bytes_to_string(cmd.setup)}")
                    print(f"usbip transfer buffer {bytes_to_string(transfer_buffer)}")
                    usb_req = USBRequest(seqnum=cmd.seqnum,
                                         devid=cmd.devid,
                                         direction=cmd.direction,
                                         ep=cmd.ep,
                                         flags=cmd.transfer_flags,
                                         numberOfPackets=cmd.number_of_packets,
                                         interval=cmd.interval,
                                         setup=cmd.setup,
                                         transfer_buffer=transfer_buffer)
                    self.usb_devices[0].connection = conn
                    self.usb_devices[0].handle_usb_request(usb_req)
            print('Close connection\n')
            conn.close()
