# On the Raspberry Pi with built-in UART:
import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3000)

import adafruit_thermal_printer
ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)

printer = ThermalPrinter(uart)
print("Rodando papel!")

printer.feed(2)

print("Papel rodado!")
