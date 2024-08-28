import usb.core
import usb.util
import bluetooth

class LovenseAPI:
    def __init__(self, usb_vendor_id=0x1915, usb_product_id=0x520C):
        self.device = usb.core.find(idVendor=usb_vendor_id, idProduct=usb_product_id)
        if self.device is None:
            raise ValueError("Lovense device not found.")
        
        if self.device.is_kernel_driver_active(0):
            self.device.detach_kernel_driver(0)

        usb.util.claim_interface(self.device, 0)

    def send_command(self, command):
        """Send a command to the Lovense device over USB."""
        endpoint_out = self.device[0][(0, 0)][0]
        self.device.write(endpoint_out.bEndpointAddress, command)

    def start_vibration(self, intensity):
        """Start the vibration with a given intensity level (1-10)."""
        command = f'\x01Vibrate:{intensity}\r\n'.encode()
        self.send_command(command)

    def stop_vibration(self):
        """Stop the vibration."""
        command = b'\x01Vibrate:0\r\n'
        self.send_command(command)

    def change_thrusting_speed(self, speed):
        """Change the thrusting speed (1-10)."""
        command = f'\x01ChangeSpeed:{speed}\r\n'.encode()
        self.send_command(command)

    def connect_to_app(self, device_address):
        """Establish a Bluetooth connection with the Lovense app."""
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((device_address, 1))
        return socket

    def control_with_app(self, device_address):
        """Control the Lovense device via the Lovense app over Bluetooth."""
        socket = self.connect_to_app(device_address)
        
        # Send commands to the device via the app
        socket.send(b'Vibrate:1\r\n')
        socket.send(b'Vibrate:5\r\n')
        socket.send(b'Vibrate:0\r\n')
        socket.send(b'ChangeSpeed:2\r\n')
        
        socket.close()

# Example usage:
if __name__ == "__main__":
    lovense = LovenseAPI()

    # Control the Lovense device directly
    lovense.start_vibration(5)
    lovense.change_thrusting_speed(2)
    lovense.stop_vibration()

    # Control the Lovense device through the app
    lovense.control_with_app('00:00:00:00:00:00')  # Replace with the actual Bluetooth address
