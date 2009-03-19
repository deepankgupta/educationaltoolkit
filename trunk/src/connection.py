#!/usr/bin/env python
#
#	Connection.py
#		OLPC Project : Educational Toolkit

"""UI class implementation for connectivity and data synchronization"""

from hashlib import sha1
import logging
import os
import dbus
import gobject
import telepathy
from tempfile import TemporaryFile
from uuid import UUID, uuid4

from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject
from dbus.mainloop.glib import DBusGMainLoop
from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection

# File informations
__author__="David Goulet"
__date__="March 25, 2008"
__version__="0.1"

# Tests/Exams repository (XML Files)
# @TODO --> Change to good path
XML_LIBRARY_PATH = "."

# DBus Namespace and Object path
DBUS_SERVICE = "org.laptop.Activity.Educational_toolkit"
DBUS_IFACE = "org.laptop.Activity.Educational_toolkit" 
DBUS_PATH = "/org/laptop/Activity/Educational_toolkit"

log = logging.getLogger('educational-toolkit')

class Interface(ExportedGObject):
    """
    Protocol that nodes communicate with.
    
    :CVariables:
        TRANSFER_BUFFER_LENGTH : int
            Number of bytes to transfer from sender at a time
    :IVariables:
        tube
            The DBus tube that's being used to communicate
        transfers : dict
            The current transfers that are being sent
        receive_types : frozenset
            File types to accept from the network
    """
    
    TRANSFER_BUFFER_LENGTH = 4096    
    
    def __init__(self, tube, receive_types=None):
        super(Interface, self).__init__(tube, PATH)
        self.tube = tube
        self.transfers = {}
        if receive_types:
            self.receive_types = frozenset(receive_types)
        else:
            self.receive_types = frozenset()
        self._add_handlers()
    
    def _add_handlers():
        self.tube.add_signal_receiver(self.start_transfer_callback,
                                      'StartTransfer',
                                      DBUS_IFACE, path=DBUS_PATH,
                                      sender_keyword='sender')
        self.tube.add_signal_receiver(self.transfer_callback,
                                      'Transfer',
                                      DBUS_IFACE, path=DBUS_PATH,
                                      sender_keyword='sender')
    
    def broadcast(self, data, data_type):
        """
        Broadcasts a file across the network.
        
        :Parameters:
            data : file-like object
                Data to send
            data_type : string
                Internal identifier for data (test or answers)
        """
        # Get file info
        data_checksum = sha1()
        while True:
            new_data = data.read(data_checksum.block_size)
            if new_data:
                data_checksum.update(new_data)
            else:
                break
        data_length = data.tell()
        data.seek(0)
        data_id = uuid4().hex
        # Send over network
        self.StartTransfer(data_id, data_type, data_length,
                           data_checksum.hexdigest())
        while True:
            new_data = data.read(self.TRANSFER_BUFFER_LENGTH)
            if new_data:
                self.Transfer(data_id, new_data)
            else:
                break
    
    @signal(dbus_interface=DBUS_IFACE, in_signature='ssus', out_signature='')
    def StartTransfer(self, file_id, file_type, file_length, file_checksum):
        pass
    
    @signal(dbus_interface=DBUS_IFACE, in_signature='s', out_signature='')
    def Transfer(self, file_id, chunk):
        pass
    
    def start_transfer_callback(self, file_id, file_type, file_length,
                                file_checksum, sender=None):
        if file_type not in self.receive_types:
            return
        self.transfers[file_id] = {'file': TemporaryFile(),
                                   'type': file_type,
                                   'length': file_length,
                                   'sha1': file_checksum,
                                   'current_sha1': sha1(),
                                   'done': False,}
    
    def transfer_callback(self, file_id, chunk, sender=None):
        try:
            transfer = self.transfers[file_id]
        except KeyError:
            return
        else:
            transfer['file'].write(chunk)
            transfer['current_sha1'].update(chunk)
            if transfer['current_sha1'].hexdigest() == transfer['sha1']:
                transfer['done'] = True
