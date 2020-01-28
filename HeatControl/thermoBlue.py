#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
"""
-AN
TODO async stuff can be handled by a wrapper
"""
import struct
import sys

from bleak import BleakClient
from bleak.exc import BleakError


class ThermoBlue:

    def __init__(self, address):
        """
        Sensor tag class init
        :param address: Mac address of the thing
        """
        self.__name__ = "tBlue"
        self.address = address
        self.bClient = BleakClient(address)
        self.UUIDS = dict()
        self.init_info_dicts()
        self.verbose = 1

    def error_wrapper(func):
        """
        Decorator for error wrapping to keep the error output simple. TODO needs expansion
        :return: the function return if no error occurs.
        """
        def wrapper(*args):
            try:
                ret = func(*args)
                return ret
            except BleakError as err:
                if "Device with address" in str(err):
                    print("Connection to " + str(err).split()[3]+" failed, is the device turned on and the mac address correct?")
                    sys.exit(1)
                if "Characteristic" in str(err):
                    print("Data send/recieve failed. Initiate the device correctly and check the UUIDs.")
                    sys.exit(2)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
        return wrapper

    def _TI_UUID(self, val):
        """
        Simple method to format hex numbers correctly for UUIDs
        :param val: Hex val
        :return: Full UUID
        """
        return ("%08X-0000-1000-8000-00805f9b34fb" % (0x00000000 + val)).lower()


    def init_info_dicts(self):
        """
        Inits a dict with UUIDs for reading the different sensors
        """
        self.UUIDS = {"Battery": "47e9ee2c-47e9-11e4-8939-164230d1df67",
                      "DeviceName": "00002a00-0000-1000-8000-00805f9b34fb",
                      "Auth": "47e9ee30-47e9-11e4-8939-164230d1df67",
                      "Temperature": "47e9ee2b-47e9-11e4-8939-164230d1df67"
                      }

        self.evals = {"Battery": lambda a: int(a[0]),
                      "DeviceName": lambda a: "".join(map(chr, a)),
                      "Temperature": self.calcTemp,
                      "Auth": lambda a: a
                      }



    #@error_wrapper
    def init_bt(self, timeout=15):
        """
        inits the bluetooth connection and the sensors.
        :param timeout: Bluetooth search timeout
        """
        if self.verbose:
            print("Connecting to BLE device")
        self.bClient.loop.run_until_complete(self.connect_bt_async(timeout=timeout))
        self.bClient.loop.run_until_complete(self.init_sensors())
        if self.verbose:
            print("Connected")


    async def connect_bt_async(self, timeout):
        """
        asynchronus connect. Not to be called directly
        :param timeout:  Bluetooth search timeout
        """
        await self.bClient.connect(timeout=timeout)
        await self.bClient.is_connected()
        a = await self.bClient.get_services()
        print([[self.bClient.services.get_descriptor(desc).characteristic_uuid, self.bClient.services.get_descriptor(desc).handle] for desc in self.bClient.services.descriptors])
        print([[desc] for desc in self.bClient.services.characteristics])

    async def init_sensors(self, ):
        """
        asynchronus init for sensors. Not to be called directly
        """
        if self.verbose:
            print("Initiation sensors")
        await self.bClient.write_gatt_char("47e9ee30-47e9-11e4-8939-164230d1df67", bytearray([0x00, 0x00, 0x00, 0x00]), response=True)
        if self.verbose:
            print("Sensors initiated")

    @error_wrapper
    def getData(self, name):
        """
        Gets data from the specified sensor. Name corresponds to a key in the UUID dict.
        :param name: name of the sensor
        """
        data = self.bClient.loop.run_until_complete(self.getData_async(self.UUIDS[name]))
        evalDat = self.evals[name](data)
        return evalDat

    async def getData_async(self, UUID):
        """
        asynchronus init for sensors. Not to be called directly
        :param UUID: UUID for the bluetooth read
        """
        data = await self.bClient.read_gatt_char(UUID)  # read temp
        return data

    @error_wrapper
    def writeData(self, name, data):
        self.bClient.loop.run_until_complete(self.writeData_async(self.UUIDS[name], data))
        return 1

    async def writeData_async(self, UUID, data, response=True):
        await self.bClient.write_gatt_char(UUID, data, response=response)
        return 1

    def setTempTarget(self, temp):
        self.writeData("Temperature", bytearray([0x80, temp*2, 0x80, 0x80, 0x80, 0x80, 0x80]))
        return 1

    def calcHum(self, hum0):
        """
        Eval function for humidity
        :param hum0: recieved data
        :return: humidity
        """
        (rawT, rawH) = struct.unpack('<HH', hum0)
        temp = -40.0 + 165.0 * (rawT / 65536.0)
        RH = 100.0 * (rawH / 65536.0)
        return RH

    def calcMov(self, mov0):
        """
        Eval function for movement TODO
        :param mov0: recieved data
        :return: movement data
        """
        (gyroZ, gyroY, gyroX) = struct.unpack('<hhh', mov0[:6])
        (accZ, accY, accX) = struct.unpack('<hhh', mov0[6:12])
        [accZ, accY, accX, gyroZ, gyroY, gyroX] = [(x*8) / 32768.0 for x in [accZ, accY, accX, gyroZ, gyroY, gyroX]]
        return [accX, accY, accZ, gyroX, gyroY, gyroZ]

    def calcTemp(self, temp0):
        """
        Eval function for temperature
        :param temp0: recieved data
        :return: temeprature in deg C
        """
        rawTobj = struct.unpack('<BBBBBBB', temp0)
        tAmb = [x/2 for x in rawTobj]
        tAmb[-1] = rawTobj[-1]
        tAmb[-2] = rawTobj[-2]
        return tAmb

    def calcLight(self, light0):
        """
        Eval function for light sensor
        :param light0: recieved data
        :return: light sensor value
        """
        raw = struct.unpack('<h', light0)[0]
        m = raw & 0xFFF
        e = (raw & 0xF000) >> 12
        return 0.01 * (m << e)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Syntax dude")
        sys.exit(-1)
    targetTemp = int(sys.argv[1])
    print(targetTemp)
    tag = ThermoBlue("88:5F:78:7B:F4:FC")
    tag.init_bt()
    print("Temperature: ", tag.getData("Temperature"))
    print("Battery: ", tag.getData("Battery"))
    print("DeviceName: ", tag.getData("DeviceName"))
    tag.setTempTarget(targetTemp)
    print("Temperature: ", tag.getData("Temperature"))
    #tag.start_continuous_stream(out_data_handles=["MovementSensor"])
