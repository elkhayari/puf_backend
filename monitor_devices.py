import pyudev
import websockets
import threading

# WebSocket server URL
SERVER_URL = "ws://localhost:8000/ws"


def send_message(message):
    ws = websockets.serve()
    ws.send(message)
    ws.close()


def monitor_device():
    # Create a monitor object to listen for device events
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='tty')

    # Start monitoring devices
    for device in iter(monitor.poll, None):
        # Replace this code with your actual device monitoring logic
        # For example, read the device status or sensor data
        device_status = f"Device {device.action}: {device.device_node}"

        # Send the device status as a WebSocket message
        send_message(device_status)


# Start monitoring the device in a separate thread
monitor_thread = threading.Thread(target=monitor_device)
monitor_thread.daemon = True
monitor_thread.start()

# Start monitoring devices
while True:
    try:
        monitor_device()
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"An error occurred: {str(e)}")
