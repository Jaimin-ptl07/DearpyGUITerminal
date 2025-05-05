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
access_token = "REPLACE_WITH_ACCESS_TOKEN"
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
