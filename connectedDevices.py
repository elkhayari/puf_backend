import pyudev
import time

def monitor_devices():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='tty')

    for device in iter(monitor.poll, None):
        if device.action == 'add':
            print(f"Device connected: {device.device_node}")
            # Call a function to handle the connected device
            handle_device_connection(device)
        elif device.action == 'remove':
            print(f"Device disconnected: {device.device_node}")
            # Call a function to handle the disconnected device
            handle_device_disconnection(device)

def handle_device_connection(device):
    # Implement your logic for handling the connected device
    # For example, you can create a dynamic instance in Redis or perform any other necessary actions
    pass

def handle_device_disconnection(device):
    # Implement your logic for handling the disconnected device
    # For example, you can update the status of the device in Redis or perform any other necessary actions
    pass

# Start monitoring devices
while True:
    try:
        monitor_devices()
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        time.sleep(1)

