#include <zmq.hpp>
#include <iostream>
#include <string>
#include <nlohmann/json.hpp>
#include <chrono>
#include <vector>
#include <numeric>  // For std::accumulate

using json = nlohmann::json;

// Limit the number of stored data points for efficient calculations
constexpr size_t MAX_DATA_POINTS = 50;

// Storage for rolling calculations
std::vector<double> bid_ask_spreads, bid_ask_imbalances, order_flows;

int main() {
    zmq::context_t context(1);
    zmq::socket_t receiver(context, ZMQ_SUB);
    zmq::socket_t sender(context, ZMQ_PUB);

    receiver.connect("tcp://127.0.0.1:5555");
    receiver.setsockopt(ZMQ_SUBSCRIBE, "", 0);
    sender.bind("tcp://127.0.0.1:5556");

    // Reserve space to avoid repeated allocations
    bid_ask_spreads.reserve(MAX_DATA_POINTS);
    bid_ask_imbalances.reserve(MAX_DATA_POINTS);
    order_flows.reserve(MAX_DATA_POINTS);

    std::cout << "✅ C++ Stream Processor Started. Waiting for incoming live data...\n";

    while (true) {
        auto start_time = std::chrono::high_resolution_clock::now();

        zmq::message_t request;
        if (!receiver.recv(request, zmq::recv_flags::dontwait)) {
            continue;  // Skip loop iteration if no message is available
        }

        std::string received_data(static_cast<char*>(request.data()), request.size());

        try {
            // Fast JSON parsing
            json market_data = json::parse(received_data, nullptr, false);

            // Print received raw data
            std::cout << "📥 Received Data: " << received_data << std::endl;

            // Extract fields efficiently
            const double bid_price = market_data.value("bid_price", 0.0);
            const double ask_price = market_data.value("ask_price", 0.0);
            const double bid_size = market_data.value("bid_size", 0.0);
            const double ask_size = market_data.value("ask_size", 0.0);
            const double tot_buy_qty = market_data.value("tot_buy_qty", 0.0);
            const double tot_sell_qty = market_data.value("tot_sell_qty", 0.0);

            // Compute bid-ask spread, imbalance, and order flow
            const double bid_ask_spread = ask_price - bid_price;
            const double bid_ask_imbalance = bid_size - ask_size;
            const double order_flow = tot_buy_qty - tot_sell_qty;

            // Store values in limited-size vectors
            if (bid_ask_spreads.size() >= MAX_DATA_POINTS) bid_ask_spreads.erase(bid_ask_spreads.begin());
            if (bid_ask_imbalances.size() >= MAX_DATA_POINTS) bid_ask_imbalances.erase(bid_ask_imbalances.begin());
            if (order_flows.size() >= MAX_DATA_POINTS) order_flows.erase(order_flows.begin());

            bid_ask_spreads.push_back(bid_ask_spread);
            bid_ask_imbalances.push_back(bid_ask_imbalance);
            order_flows.push_back(order_flow);

            // Compute mean values using std::accumulate (faster than loop)
            const double mean_spread = std::accumulate(bid_ask_spreads.begin(), bid_ask_spreads.end(), 0.0) / bid_ask_spreads.size();
            const double mean_imbalance = std::accumulate(bid_ask_imbalances.begin(), bid_ask_imbalances.end(), 0.0) / bid_ask_imbalances.size();
            const double mean_order_flow = std::accumulate(order_flows.begin(), order_flows.end(), 0.0) / order_flows.size();

            // Determine predictions with reduced branching overhead
            std::string order_book_prediction = "Neutral 📊";
            std::string order_flow_prediction = "Neutral 📊";
            std::string signal = "⚡ No Strong Signal";

            if (bid_ask_spread > mean_spread * 1.5 && bid_ask_imbalance > mean_imbalance * 1.5) {
                order_book_prediction = "Bullish Breakout 🚀";
                order_flow_prediction = "Bullish 📈";
                signal = "✅ Buy Signal";
            } else if (bid_ask_spread < mean_spread * 0.5 && bid_ask_imbalance < mean_imbalance * 0.5) {
                order_book_prediction = "Bearish Breakdown 📉";
                order_flow_prediction = "Bearish 📉";
                signal = "❌ Sell Signal";
            }

            auto end_time = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double, std::milli> elapsed = end_time - start_time;

            // Construct processed JSON object
            json processed_data = {
                {"symbol", market_data.value("symbol", "N/A")},
                {"bid_price", bid_price},
                {"ask_price", ask_price},
                {"bid_size", bid_size},
                {"ask_size", ask_size},
                {"tot_buy_qty", tot_buy_qty},
                {"tot_sell_qty", tot_sell_qty},
                {"order_book_prediction", order_book_prediction},
                {"order_flow_prediction", order_flow_prediction},
                {"signal", signal},
                {"processing_time_ms", elapsed.count()}
            };

            // Convert JSON to string for sending
            std::string processed_json_str = processed_data.dump();
            zmq::message_t processed_message(processed_json_str.begin(), processed_json_str.end());
            sender.send(processed_message, zmq::send_flags::dontwait);

            // Print processed data
            std::cout << "📤 Processed Data Sent: " << processed_json_str << std::endl;
            std::cout << "⏱️ Processing Time: " << elapsed.count() << " ms\n";

        } catch (const std::exception &e) {
            std::cerr << "❌ Error processing data: " << e.what() << std::endl;
        }
    }

    return 0;
}
