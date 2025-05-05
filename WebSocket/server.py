import asyncio
import websockets
import json
import random

# Set to store connected clients
connected_clients = set()

# Function to generate dummy stock data
def generate_stock_data():
    stock_data = {
        'symbol': 'AAPL',
        'price': round(random.uniform(150, 200), 2),
        'volume': random.randint(1000, 10000)
    }
    return stock_data

# Handler for each client connection
async def client_handler(websocket, path):
    # Register client
    connected_clients.add(websocket)
    try:
        # Keep the connection open
        await websocket.wait_closed()
    finally:
        # Unregister client
        connected_clients.remove(websocket)

# Function to broadcast messages to all connected clients
async def broadcast():
    while True:
        if connected_clients:  # Check if there are connected clients
            stock_data = generate_stock_data()
            message = json.dumps(stock_data)
            # Create a list of tasks for sending messages
            send_tasks = [asyncio.create_task(client.send(message)) for client in connected_clients]
            # Wait for all send tasks to complete
            await asyncio.gather(*send_tasks)
        await asyncio.sleep(1)  # Broadcast every second

async def main():
    async with websockets.serve(client_handler, "localhost", 8765):
        await broadcast()  # Start broadcasting stock data

if __name__ == "__main__":
    asyncio.run(main())
