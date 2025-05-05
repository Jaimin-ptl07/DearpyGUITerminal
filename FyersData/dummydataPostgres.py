import asyncio
import asyncpg
import random
import time

# PostgreSQL Connection Settings
DB_CONFIG = {
    "user": "postgres",
    "password": "jaimin07",
    "database": "NewsDatabase",
    "host": "localhost",
    "port": 5432
}

async def create_table():
    """Creates the market_data table if it does not exist."""
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                bid_price DECIMAL NOT NULL,
                ask_price DECIMAL NOT NULL,
                bid_size INT NOT NULL,
                ask_size INT NOT NULL,
                timestamp DOUBLE PRECISION DEFAULT EXTRACT(EPOCH FROM NOW())
            );
        """)
        print("✅ Table `market_data` is ready!")
    except Exception as e:
        print("❌ Error creating table:", e)
    finally:
        await conn.close()

async def insert_dummy_data():
    """Continuously inserts simulated market data into PostgreSQL in real-time."""
    conn = await asyncpg.connect(**DB_CONFIG)
    print("✅ Connected to PostgreSQL - Inserting Live Data...")

    while True:
        try:
            symbol = "NSE:SBIN-EQ"
            bid_price = round(random.uniform(680, 700), 2)
            ask_price = round(random.uniform(680, 700), 2)
            bid_size = random.randint(100, 500)
            ask_size = random.randint(100, 500)
            timestamp = time.time()

            query = """
                INSERT INTO market_data (symbol, bid_price, ask_price, bid_size, ask_size, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6);
            """
            await conn.execute(query, symbol, bid_price, ask_price, bid_size, ask_size, timestamp)

            print(f"📩 Inserted: {symbol} | Bid: {bid_price} | Ask: {ask_price} | Time: {timestamp}")

        except Exception as e:
            print("❌ Error inserting data:", e)

        await asyncio.sleep(1)  # Simulate real-time updates every second

async def main():
    await create_table()  # Ensure table exists before inserting data
    await insert_dummy_data()

if __name__ == "__main__":
    asyncio.run(main())
