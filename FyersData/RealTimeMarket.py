import asyncio
import zmq
import zmq.asyncio
import dearpygui.dearpygui as dpg
import json
import threading
import queue
import time
from fyers_apiv3.FyersWebsocket import data_ws

# Initialize ZeroMQ context and PUB socket
context = zmq.Context()
socket = context.socket(zmq.PUB)  # PUB socket to allow multiple subscribers
socket.bind("tcp://127.0.0.1:5555")  # Publishing data on localhost

# Fyers WebSocket Authentication (Replace with actual access token)
access_token = "REPLACE_YOUR_ACCESS_TOKEN"

# Global variable to store user input symbol
user_symbol = "NSE:SBIN-EQ"


def onmessage(message):
    """
    Callback function to handle incoming WebSocket messages.
    Sends the processed message to the C++ stream processing framework.
    """
    try:
        #print("📩 Received Market Data:", message)
        json_data = json.dumps(message)
        socket.send_string(json_data)
        #print("✅ Sent Data to C++:", json_data)
    except Exception as e:
        print(f"❌ Error processing message: {e}")


def onerror(message):
    print("⚠️ WebSocket Error:", message)


def onclose(message):
    print("🔴 WebSocket Disconnected:", message)


def onopen():
    """Subscribe to stock symbols when WebSocket connection is opened."""
    print("🔗 Connected to Fyers WebSocket. Subscribing to symbols...")
    data_type = "SymbolUpdate"
    fyers.subscribe(symbols=[user_symbol], data_type=data_type)
    fyers.keep_running()


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


class LiveDataTab:
    def __init__(self):
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5556")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.data_queue = queue.Queue()
        self.max_rows = 10
        self.table_rows = []
        threading.Thread(target=self.start_websocket_listener, daemon=True).start()

    async def receive_data(self):
        while True:
            try:
                message = await self.socket.recv_string()
                processed_data = json.loads(message)
                self.data_queue.put(processed_data)
            except Exception as e:
                print("Error receiving data:", e)
            await asyncio.sleep(0.1)

    def start_websocket_listener(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.receive_data())

    def update_table(self):
        while not self.data_queue.empty():
            processed_data = self.data_queue.get()
            print(processed_data)  # Debugging

            row = [
                processed_data.get("symbol", "N/A"),
                str(processed_data.get("bid_price", "N/A")),
                str(processed_data.get("ask_price", "N/A")),
                str(processed_data.get("bid_size", "N/A")),
                str(processed_data.get("ask_size", "N/A")),
                str(processed_data.get("order_book_prediction", "N/A")),
                str(processed_data.get("order_flow_prediction", "N/A")),
                str(processed_data.get("signal", "N/A")),
                f"{processed_data.get('processing_time_ms', 0):.2f} ms",
            ]

            # Ensure table exists before modifying
            if dpg.does_item_exist("live_data_table"):
                # Get current children (rows) of the table
                current_rows = dpg.get_item_children("live_data_table", 1)

                # If there are 10 or more rows, delete the oldest (first) one
                if len(current_rows) >= 20:
                    dpg.delete_item(current_rows[0])

                # Add new row
                with dpg.table_row(parent="live_data_table"):
                    for value in row:
                        dpg.add_text(value)

    def LiveDataTabUI(self):
        global user_symbol

        with dpg.tab(label="Live Market Data"):
            dpg.add_text("📊 Real-Time Market Data", color=(0, 255, 255))
            dpg.add_separator()

            # Input Field and Button to Update Symbol
            def update_symbol():
                global user_symbol

                new_symbol = dpg.get_value("symbol_input")

                # Unsubscribe from the previous symbol
                print(f"🔄 Unsubscribing from {user_symbol}")
                fyers.unsubscribe(symbols=[user_symbol], data_type="SymbolUpdate")

                # Update to new symbol
                user_symbol = new_symbol
                print(f"✅ Subscribing to {user_symbol}")

                # Subscribe to the new symbol
                fyers.subscribe(symbols=[user_symbol], data_type="SymbolUpdate")

                # Restart WebSocket connection to apply changes
                fyers.connect()

            dpg.add_input_text(label="Enter Symbol", tag="symbol_input", default_value=user_symbol)
            dpg.add_button(label="Fetch Data", callback=update_symbol)
            dpg.add_separator()

            with dpg.table(header_row=True, tag="live_data_table", row_background=True, hideable=True, resizable=True,
                           scrollY=True):
                dpg.add_table_column(label="Symbol", width_stretch=True)
                dpg.add_table_column(label="Bid Price", width_stretch=True)
                dpg.add_table_column(label="Ask Price", width_stretch=True)
                dpg.add_table_column(label="Bid Size", width_stretch=True)
                dpg.add_table_column(label="Ask Size", width_stretch=True)
                dpg.add_table_column(label="Order Book Prediction", width_stretch=True)
                dpg.add_table_column(label="Order Flow Prediction", width_stretch=True)
                dpg.add_table_column(label="Signal", width_stretch=True)
                dpg.add_table_column(label="Processing Time", width_stretch=True)

            dpg.add_separator()
            dpg.add_text("📈 Market Trends", color=(0, 255, 255))

            with dpg.collapsing_header(label="Live Trend Charts"):
                with dpg.plot(label="Price Trends", height=300, width=-1):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Timestamp")
                    with dpg.plot_axis(dpg.mvYAxis, label="Price"):
                        dpg.add_line_series([], [], label="Bid Price", tag="bid_series")
                        dpg.add_line_series([], [], label="Ask Price", tag="ask_series")

        threading.Thread(target=self.auto_update_table, daemon=True).start()

    def auto_update_table(self):
        while True:
            self.update_table()
            time.sleep(0.1)


if __name__ == "__main__":
    print("🚀 Starting Fyers Live Data Stream...")
    fyers.connect()
    dpg.create_context()
    live_data_tab = LiveDataTab()
    live_data_tab.LiveDataTabUI()
    dpg.create_viewport(title="Live Market Data", width=1000, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
