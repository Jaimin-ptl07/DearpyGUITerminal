import asyncio
import zmq
import zmq.asyncio
import dearpygui.dearpygui as dpg
import json
import threading
import time
import queue

# Set the event loop policy for Windows compatibility
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Initialize ZeroMQ subscriber
context = zmq.asyncio.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:5556")  # Connect to C++ processed data
socket.setsockopt_string(zmq.SUBSCRIBE, "")

# Thread-safe queue to store received messages
data_queue = queue.Queue()

# Max number of rows in the table before clearing old data
max_rows = 10
table_rows = []

async def receive_data():
    """Asynchronous function to receive processed data from C++ and store it in a queue."""
    while True:
        try:
            message = await socket.recv_string()
            processed_data = json.loads(message)
            data_queue.put(processed_data)  # Store in thread-safe queue
        except Exception as e:
            print("Error receiving data:", e)
        await asyncio.sleep(0.1)  # Adjust the sleep interval as needed

def update_table():
    """Fetches processed data from the queue and updates the Dear PyGui table safely in the main thread."""
    global table_rows

    while not data_queue.empty():
        processed_data = data_queue.get()

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
        table_rows.append(row)
        if len(table_rows) > max_rows:
            table_rows.pop(0)  # Remove the oldest row

        # Safe UI update
        if dpg.does_item_exist("table"):
            dpg.delete_item("table", children_only=True)
            # Recreate table columns
            dpg.add_table_column(label="Symbol", parent="table")
            dpg.add_table_column(label="Bid Price", parent="table")
            dpg.add_table_column(label="Ask Price", parent="table")
            dpg.add_table_column(label="Bid Size", parent="table")
            dpg.add_table_column(label="Ask Size", parent="table")
            dpg.add_table_column(label="Order Book Prediction", parent="table")
            dpg.add_table_column(label="Order Flow Prediction", parent="table")
            dpg.add_table_column(label="Signal", parent="table")
            dpg.add_table_column(label="Processing Time", parent="table")
            # Add rows
            for row_data in table_rows:
                with dpg.table_row(parent="table"):
                    for value in row_data:
                        dpg.add_text(value)
        else:
            print("Table item does not exist.")

def gui():
    """Creates the GUI using DearPyGui."""
    dpg.create_context()

    with dpg.window(label="Live Market Data Table", width=1000, height=400):
        dpg.add_text("📊 Live Market Data Feed", color=(255, 255, 0), bullet=True)
        dpg.add_separator()

        # Create Table
        with dpg.table(header_row=True, resizable=True, borders_innerH=True, borders_innerV=True, tag="table"):
            dpg.add_table_column(label="Symbol")
            dpg.add_table_column(label="Bid Price")
            dpg.add_table_column(label="Ask Price")
            dpg.add_table_column(label="Bid Size")
            dpg.add_table_column(label="Ask Size")
            dpg.add_table_column(label="Order Book Prediction")
            dpg.add_table_column(label="Order Flow Prediction")
            dpg.add_table_column(label="Signal")
            dpg.add_table_column(label="Processing Time")

    dpg.create_viewport(title="Live Market Data Table", width=1000, height=400)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        update_table()  # Fetch & update table with new data
        dpg.render_dearpygui_frame()
        time.sleep(0.1)  # Refresh every 100ms

    dpg.destroy_context()

# Start the asynchronous data receiver
async def main():
    # Run the GUI in a separate thread
    gui_thread = threading.Thread(target=gui, daemon=True)
    gui_thread.start()

    # Start receiving data
    await receive_data()

if __name__ == "__main__":
    asyncio.run(main())
