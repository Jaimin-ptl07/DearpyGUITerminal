import json
import zmq
from fyers_apiv3.FyersWebsocket import data_ws

# Initialize ZeroMQ context and PUB socket
context = zmq.Context()
socket = context.socket(zmq.PUB)  # PUB socket to allow multiple subscribers
socket.bind("tcp://127.0.0.1:5555")  # Publishing data on localhost


def onmessage(message):
    """
    Callback function to handle incoming WebSocket messages.
    Sends the processed message to the C++ stream processing framework.
    """
    try:
        print("📩 Received Market Data:", message)

        # Convert message to JSON format
        json_data = json.dumps(message)

        # Send JSON formatted data to C++ application
        socket.send_string(json_data)

        print("✅ Sent Data to C++:", json_data)

    except Exception as e:
        print(f"❌ Error processing message: {e}")


def onerror(message):
    """Handle WebSocket errors."""
    print("⚠️ WebSocket Error:", message)


def onclose(message):
    """Handle WebSocket disconnections."""
    print("🔴 WebSocket Disconnected:", message)


def onopen():
    """Subscribe to stock symbols when WebSocket connection is opened."""
    print("🔗 Connected to Fyers WebSocket. Subscribing to symbols...")

    data_type = "SymbolUpdate"
    symbols = ['NSE:SBIN-EQ']  # Add your stock symbols here

    fyers.subscribe(symbols=symbols, data_type=data_type)
    fyers.keep_running()


# Fyers WebSocket Authentication (Replace with actual access token)
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE3NDE4NDI3MjIsImV4cCI6MTc0MTkxMjIwMiwibmJmIjoxNzQxODQyNzIyLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCbjBta2lycHFBb0RVdGZvX2hXVm42eW15RVpDNG9uWFJrcUd0bFFzdWY2QXNzR2JGQ2NiYkZHZEhTNGxLcTk5OUQ1aGFOckxESDZ2OVFHVXlHOG9ERDMwUng2RW4wZU9hMzNWcHBvRnZ3UURJUzRQMD0iLCJkaXNwbGF5X25hbWUiOiJCSUpBTCBOSUtVTCBQQVRFTCIsIm9tcyI6IksxIiwiaHNtX2tleSI6IjQ2YmZiODhmYjhlYjQxMjU0NDNjNWJmZjJmMDg4Y2MyYzY0ZDMwZjU2NTU4NWQzOGQ0ZDVlYzc1IiwiaXNEZHBpRW5hYmxlZCI6bnVsbCwiaXNNdGZFbmFibGVkIjpudWxsLCJmeV9pZCI6IlhCMDI1MDciLCJhcHBUeXBlIjoxMDAsInBvYV9mbGFnIjoiTiJ9.Zn05vg5RDSn5A6BXlVyRz4i78kAudBGyDrxCAwSk7yA"
# Initialize Fyers WebSocket Client
fyers = data_ws.FyersDataSocket(
    access_token=access_token,
    log_path="",
    litemode=False,
    write_to_file=False,
    reconnect=True,
    on_connect=onopen,
    on_close=onclose,
    on_error=onerror,
    on_message=onmessage
)

# Connect to Fyers WebSocket
if __name__ == "__main__":
    print("🚀 Starting Fyers Live Data Stream...")
    fyers.connect()
