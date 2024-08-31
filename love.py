import usb.core
import usb.util
import bluetooth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LovenseAPI:
    def __init__(self, usb_vendor_id=0x1915, usb_product_id=0x520C):
        self.device = None
        self._usb_vendor_id = usb_vendor_id
        self._usb_product_id = usb_product_id
        self._connect_usb()

    def _connect_usb(self):
        """Connect to the Lovense device via USB."""
        try:
            self.device = usb.core.find(idVendor=self._usb_vendor_id, idProduct=self._usb_product_id)
            if self.device is None:
                raise ValueError("Lovense device not found via USB.")
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
            usb.util.claim_interface(self.device, 0)
            logging.info("Successfully connected to the Lovense device via USB.")
        except Exception as e:
            logging.error(f"Failed to connect to USB device: {e}")
            raise

    def _release_usb(self):
        """Release the USB interface and device."""
        try:
            usb.util.release_interface(self.device, 0)
            usb.util.dispose_resources(self.device)
            logging.info("Released USB device resources.")
        except Exception as e:
            logging.error(f"Failed to release USB device: {e}")

    def send_command(self, command):
        """Send a command to the Lovense device over USB."""
        try:
            endpoint_out = self.device[0][(0, 0)][0]
            self.device.write(endpoint_out.bEndpointAddress, command)
            logging.info(f"Command sent: {command}")
        except Exception as e:
            logging.error(f"Failed to send command: {e}")

    def start_vibration(self, intensity):
        """Start the vibration with a given intensity level (1-10)."""
        if not (1 <= intensity <= 10):
            logging.error("Intensity must be between 1 and 10.")
            return
        command = f'\x01Vibrate:{intensity}\r\n'.encode()
        self.send_command(command)

    def stop_vibration(self):
        """Stop the vibration."""
        command = b'\x01Vibrate:0\r\n'
        self.send_command(command)

    def change_thrusting_speed(self, speed):
        """Change the thrusting speed (1-10)."""
        if not (1 <= speed <= 10):
            logging.error("Speed must be between 1 and 10.")
            return
        command = f'\x01ChangeSpeed:{speed}\r\n'.encode()
        self.send_command(command)

    def connect_to_app(self, device_address, timeout=10):
        """Establish a Bluetooth connection with the Lovense app."""
        try:
            socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            socket.settimeout(timeout)
            socket.connect((device_address, 1))
            logging.info(f"Connected to Lovense app via Bluetooth at {device_address}.")
            return socket
        except bluetooth.BluetoothError as e:
            logging.error(f"Bluetooth connection failed: {e}")
            raise

    def control_with_app(self, device_address):
        """Control the Lovense device via the Lovense app over Bluetooth."""
        try:
            with self.connect_to_app(device_address) as socket:
                socket.send(b'Vibrate:1\r\n')
                logging.info("Sent Vibrate:1 command via Bluetooth.")
                socket.send(b'Vibrate:5\r\n')
                logging.info("Sent Vibrate:5 command via Bluetooth.")
                socket.send(b'Vibrate:0\r\n')
                logging.info("Sent Vibrate:0 command via Bluetooth.")
                socket.send(b'ChangeSpeed:2\r\n')
                logging.info("Sent ChangeSpeed:2 command via Bluetooth.")
        except Exception as e:
            logging.error(f"Failed to control device via app: {e}")

    def close(self):
        """Release resources and close connections."""
        self._release_usb()
        logging.info("Closed LovenseAPI instance.")

# Example usage:
if __name__ == "__main__":
    try:
        lovense = LovenseAPI()

        # Control the Lovense device directly
        lovense.start_vibration(5)
        lovense.change_thrusting_speed(2)
        lovense.stop_vibration()

        # Control the Lovense device through the app
        lovense.control_with_app('00:00:00:00:00:00')  # Replace with the actual Bluetooth address

    except Exception as e:
        logging.error(f"Error during Lovense API operations: {e}")
    finally:
        if lovense:
            lovense.close()
