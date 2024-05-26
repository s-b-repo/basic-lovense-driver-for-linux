import usb.core
import usb.util
import bluetooth

# Find the Lovense device
dev = usb.core.find(idVendor=0x1915, idProduct=0x520C)

if dev is None:
    raise ValueError("Lovense device not found.")

# Detach and claim the device interface
if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

usb.util.claim_interface(dev, 0)

# Send commands to the Lovense device
def send_command(command):
    endpoint_out = dev[0][(0, 0)][0]
    dev.write(endpoint_out.bEndpointAddress, command)

# Establish Bluetooth connection with Lovense app
def connect_to_app(device_address):
    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.connect((device_address, 1))
    return socket

# Example: Start vibration with intensity level 5
def start_vibration(intensity):
    command = f'\x01Vibrate:{intensity}\r\n'.encode()
    send_command(command)

# Example: Stop vibration
def stop_vibration():
    command = b'\x01Vibrate:0\r\n'
    send_command(command)

# Example: Change thrusting speed
def change_thrusting_speed(speed):
    command = f'\x01ChangeSpeed:{speed}\r\n'.encode()
    send_command(command)

# Example: Connect to Lovense app and control the device
def control_with_app(device_address):
    socket = connect_to_app(device_address)
    # Send commands to control the device through the app
    # Example: Start vibration
    socket.send(b'Vibrate:1\r\n')
    # Example: Change vibration intensity
    socket.send(b'Vibrate:5\r\n')
    # Example: Stop vibration
    socket.send(b'Vibrate:0\r\n')
    # Example: Change thrusting speed
    socket.send(b'ChangeSpeed:2\r\n')
    # Close the Bluetooth connection
    socket.close()

# Example: Control the Lovense device directly
start_vibration(5)
change_thrusting_speed(2)
stop_vibration()

# Example: Control the Lovense device through the app
control_with_app('00:00:00:00:00:00')  # Replace with the actual device address
