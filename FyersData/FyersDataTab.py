import dearpygui.dearpygui as dpg
from fyers_apiv3 import fyersModel
from Utils.ModalNotification import ModalNotification
import time
import random

class FyersDataTab:
    def __init__(self):
        self.client_id = "FYERS_CLIENT_ID"
        self.modal = ModalNotification()  # Initialize modal notification

    def read_access_token(self):
        """Reads access token from access_token.log file."""
        try:
            with open("C:/Users/JAIMIN/Desktop/dearpyguiTerminal/access_token.log", "r") as f:
                token_line = f.readline().strip()
                if token_line.startswith("Access Token:"):
                    return token_line.split("Access Token:")[1].strip()
            return None  # If format is incorrect
        except FileNotFoundError:
            return None  # If file doesn't exist

    def fetch_historic_data(self, symbol="NSE:SBIN-EQ", resolution="60", range_from="1690895316", range_to="1691068173"):
        """Fetch historic data from Fyers API using the latest access token."""
        self.access_token = self.read_access_token()  # Fetch the latest token when fetching data
        if not self.access_token:
            self.modal.show("Access token not found. Please generate the Fyers access token from the settings.")
            return None  # Stop execution if no access token is found

        self.fyers = fyersModel.FyersModel(client_id=self.client_id, is_async=False, token=self.access_token, log_path="")

        data = {
            "symbol": symbol,
            "resolution": resolution,
            "date_format": "0",
            "range_from": range_from,
            "range_to": range_to,
            "cont_flag": "1"
        }

        response = self.fyers.history(data=data)
        return response

    def display_fyers_data(self):
        """Fetch and display Fyers data in a DearPyGui table and update graph."""
        response = self.fetch_historic_data()
        if response is None:
            return  # Stop execution if no access token or response

        # Validate response
        if response.get("s") != "ok":
            dpg.set_value("fyers_status", f"Error: {response.get('message', 'Failed to fetch data')}")
            return

        dpg.set_value("fyers_status", "Data Fetched Successfully")

        # Clear only rows, keeping the table intact
        rows = dpg.get_item_children("fyers_table", 1)  # Get table rows
        if rows:
            for row in rows:
                dpg.delete_item(row)  # Remove only the rows

        timestamps, open_prices, high_prices, low_prices, close_prices, volumes = [], [], [], [], [], []

        # Populate table with new data
        for candle in response["candles"]:
            timestamp, open_price, high, low, close, volume = candle
            timestamps.append(timestamp)
            open_prices.append(open_price)
            high_prices.append(high)
            low_prices.append(low)
            close_prices.append(close)
            volumes.append(volume)

            with dpg.table_row(parent="fyers_table"):
                dpg.add_text(str(timestamp))
                dpg.add_text(str(open_price))
                dpg.add_text(str(high))
                dpg.add_text(str(low))
                dpg.add_text(str(close))
                dpg.add_text(str(volume))

        # Update Graphs
        self.update_fyers_graph(timestamps, open_prices, high_prices, low_prices, close_prices)

    def update_fyers_graph(self, timestamps, open_prices, high_prices, low_prices, close_prices):
        """Update the DearPyGui plot with new data."""
        dpg.configure_item("open_series", x=timestamps, y=open_prices)
        dpg.configure_item("high_series", x=timestamps, y=high_prices)
        dpg.configure_item("low_series", x=timestamps, y=low_prices)
        dpg.configure_item("close_series", x=timestamps, y=close_prices)
        dpg.configure_item("ohlc_series", dates=timestamps, opens=open_prices, closes=close_prices, lows=low_prices, highs=high_prices)

    def FyersTab(self):
        """Create the Fyers Data tab in DearPyGui."""
        with dpg.tab(label="Fyers Data"):
            dpg.add_text("📈 Fyers Historical Market Data", color=(0, 255, 255))
            dpg.add_button(label="Fetch Data", callback=self.display_fyers_data)
            dpg.add_separator()
            dpg.add_text("", tag="fyers_status")  # Status message

            # Table for historical data
            with dpg.table(header_row=True, tag="fyers_table", row_background=True, hideable=True, resizable=True):
                dpg.add_table_column(label="Timestamp", width_stretch=True)
                dpg.add_table_column(label="Open", width_stretch=True)
                dpg.add_table_column(label="High", width_stretch=True)
                dpg.add_table_column(label="Low", width_stretch=True)
                dpg.add_table_column(label="Close", width_stretch=True)
                dpg.add_table_column(label="Volume", width_stretch=True)

            dpg.add_separator()
            dpg.add_text("📊 Price Chart", color=(0, 255, 255))

            # Create plots for Open, High, Low, Close data
            with dpg.collapsing_header(label="Line Chart"):

                with dpg.plot(label="Stock Prices", height=300, width=-1):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Timestamp")
                    with dpg.plot_axis(dpg.mvYAxis, label="Price"):
                        dpg.add_line_series([], [], label="Open", tag="open_series")
                        dpg.add_line_series([], [], label="High", tag="high_series")
                        dpg.add_line_series([], [], label="Low", tag="low_series")
                        dpg.add_line_series([], [], label="Close", tag="close_series")

            # Create a candlestick (OHLC) chart
            with dpg.collapsing_header(label="Candlestick Chart"):

                with dpg.plot(label="OHLC Chart", height=400, width=-1):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Timestamp")
                    with dpg.plot_axis(dpg.mvYAxis, label="OHLC Price"):
                        dpg.add_candle_series([], [], [], [], [], label="OHLC", tag="ohlc_series")
