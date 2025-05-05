import asyncio
import zmq
import zmq.asyncio
import dearpygui.dearpygui as dpg
import json
import threading
import queue
import time

class LiveDataTab:
    """Class to handle real-time market data via ZeroMQ and display in DearPyGui."""

    def __init__(self):
        """Initialize WebSocket connection and UI components."""
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5556")  # Connect to C++ processed data
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

        # Thread-safe queue to store received messages
        self.data_queue = queue.Queue()

        # Max number of rows in the table before clearing old data
        self.max_rows = 10
        self.table_rows = []

        # Start WebSocket data listener in a background thread
        threading.Thread(target=self.start_websocket_listener, daemon=True).start()

    async def receive_data(self):
        """Asynchronous function to receive processed data from C++ and store it in a queue."""
        while True:
            try:
                message = await self.socket.recv_string()
                processed_data = json.loads(message)
                self.data_queue.put(processed_data)  # Store in thread-safe queue
            except Exception as e:
                print("Error receiving data:", e)
            await asyncio.sleep(0.1)  # Adjust the sleep interval as needed

    def start_websocket_listener(self):
        """Runs the WebSocket listener in an asyncio event loop inside a background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.receive_data())

    def update_table(self):
        """Fetches processed data from the queue and updates the Dear PyGui table safely in the main thread."""
        while not self.data_queue.empty():
            processed_data = self.data_queue.get()

            # Format row data
            row = [
                processed_data.get("symbol", "N/A"),
                str(processed_data.get("bid_price", "N/A")),
                str(processed_data.get("ask_price", "N/A")),
                str(processed_data.get("bid_size", "N/A")),
                str(processed_data.get("ask_size", "N/A")),
                processed_data.get("order_book_prediction", "N/A"),
                processed_data.get("order_flow_prediction", "N/A"),
                processed_data.get("signal", "N/A"),
                f"{processed_data.get('processing_time_ms', 0):.2f} ms",
            ]

            # Append to table, limit rows
            self.table_rows.append(row)
            if len(self.table_rows) > self.max_rows:
                self.table_rows.pop(0)  # Remove the oldest row

            # Safe UI update
            if dpg.does_item_exist("live_data_table"):
                #dpg.delete_item("live_data_table", children_only=True)

                # Add rows
                for row_data in self.table_rows:
                    with dpg.table_row(parent="live_data_table"):
                        for value in row_data:
                            dpg.add_text(value)

    def LiveDataTabUI(self):
        """Creates the Live Data tab in DearPyGui, callable from dashboard."""
        with dpg.tab(label="Live Market Data"):
            dpg.add_text("📊 Real-Time Market Data", color=(0, 255, 255))
            dpg.add_separator()

            # Table for live data
            with dpg.table(header_row=True, tag="live_data_table", row_background=True, hideable=True, resizable=True, scrollY=True):
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

            # Create plots for real-time market trends
            with dpg.collapsing_header(label="Live Trend Charts"):

                with dpg.plot(label="Price Trends", height=300, width=-1):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Timestamp")
                    with dpg.plot_axis(dpg.mvYAxis, label="Price"):
                        dpg.add_line_series([], [], label="Bid Price", tag="bid_series")
                        dpg.add_line_series([], [], label="Ask Price", tag="ask_series")

        # Start auto-updating table in background thread
        threading.Thread(target=self.auto_update_table, daemon=True).start()

    def auto_update_table(self):
        """Continuously updates the table every 100ms in the main UI thread."""
        while True:
            self.update_table()
            time.sleep(0.1)  # Refresh every 100ms
