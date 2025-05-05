#include <iostream>
#include <pqxx/pqxx>
#include <thread>
#include <chrono>

// PostgreSQL Connection String
const std::string DB_CONN = "dbname=DATABASENAME user=USERNAME password=YOUR_PWD host=localhost port=5432";

// Function to create table if it doesn't exist
void create_table_if_not_exists() {
    try {
        pqxx::connection conn(DB_CONN);
        pqxx::work txn(conn);

        txn.exec(R"(
            CREATE TABLE IF NOT EXISTS market_data (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                bid_price DECIMAL NOT NULL,
                ask_price DECIMAL NOT NULL,
                bid_size INT NOT NULL,
                ask_size INT NOT NULL,
                timestamp DOUBLE PRECISION DEFAULT EXTRACT(EPOCH FROM NOW())
            );
        )");

        txn.commit();
        std::cout << "✅ Table `market_data` is ready!\n";
    } catch (const std::exception &e) {
        std::cerr << "❌ Error creating table: " << e.what() << std::endl;
    }
}

// Function to fetch latest market data from PostgreSQL
void fetch_latest_market_data() {
    try {
        pqxx::connection conn(DB_CONN);
        pqxx::work txn(conn);

        pqxx::result result = txn.exec(
            "SELECT symbol, bid_price, ask_price, bid_size, ask_size, timestamp "
            "FROM market_data ORDER BY timestamp DESC LIMIT 1;"
        );

        if (!result.empty()) {
            std::cout << "\n📩 Latest Market Data:\n";
            std::cout << "---------------------------------\n";
            std::cout << "Symbol:       " << result[0]["symbol"].as<std::string>() << "\n";
            std::cout << "Bid Price:    " << result[0]["bid_price"].as<double>() << "\n";
            std::cout << "Ask Price:    " << result[0]["ask_price"].as<double>() << "\n";
            std::cout << "Bid Size:     " << result[0]["bid_size"].as<int>() << "\n";
            std::cout << "Ask Size:     " << result[0]["ask_size"].as<int>() << "\n";
            std::cout << "Timestamp:    " << result[0]["timestamp"].as<double>() << "\n";
            std::cout << "---------------------------------\n";
        } else {
            std::cout << "⚠️ No market data available in the database.\n";
        }
    } catch (const std::exception &e) {
        std::cerr << "❌ PostgreSQL Fetch Error: " << e.what() << std::endl;
    }
}

int main() {
    std::cout << "✅ Starting C++ Stream Processor...\n";

    // Ensure the table exists before fetching data
    create_table_if_not_exists();

    while (true) {
        fetch_latest_market_data();
        std::this_thread::sleep_for(std::chrono::seconds(1));  // Fetch new data every second
    }

    return 0;
}
