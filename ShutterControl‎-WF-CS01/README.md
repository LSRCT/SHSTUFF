## ShutterControl WF-CS01
This guide explains how to flash tasmota on to WF-CS01 shutter controls.
Guides like this have been done before, but I found all of them to be incomplete or unneccessary damaging to the device.

### Hardware
The first step is to open up the device. This does not require removing any screws, simple remove the glass cover.
The device looks similar to this:


Next we need to remove the top PCB. It can simply be pulled out.

Next we are going to solder on the wires for flashing. On the front side the required pins are GND, Vcc, Rx, Tx and GPIO0.
As usually, the GPIO0 pin need to be pulled to ground to put the device into flashing mode.

Next we solder another wire onto Pin1, the reset pin, of the IC on the back side. Pulling this pin to GND prevents the IC from trying to talk to the ESP and therby using the rx/tx pins. Other tutorial () simply cut the trace to the rx pin, however i find this to be a drastic measure.

Next we flash the thing as seen in.