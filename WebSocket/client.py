import asyncio
import websockets

async def connect():
    uri = "ws://localhost:8765"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("Connected to server")
                while True:
                    message = await websocket.recv()
                    print(f"Received: {message}")
        except websockets.ConnectionClosedOK:
            print("Connection closed with code 1001 (going away). Reconnecting...")
            await asyncio.sleep(5)  # Wait before reconnecting
        except Exception as e:
            print(f"An error occurred: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect())
