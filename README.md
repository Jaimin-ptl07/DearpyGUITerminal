# DearpyGUITerminal

**DearpyGUITerminal** is a terminal-based application built using [Dear PyGui](https://github.com/hoffstadt/DearPyGui). It integrates various modules such as Fyers API authentication, data retrieval, news sentiment analysis, and more to provide a comprehensive terminal interface for financial data analysis.

## Features

- **Fyers Authentication**: Securely authenticate with the Fyers API.
- **Data Retrieval**: Fetch real-time and historical data from Fyers.
- **News Sentiment Analysis**: Analyze news articles to gauge market sentiment.
- **WebSocket Integration**: Real-time data streaming using WebSockets.
- **Plotly Charts**: Visualize data using interactive Plotly charts.
- **PostgreSQL Integration**: Store and retrieve data from a PostgreSQL database.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Jaimin-ptl07/DearpyGUITerminal.git
   cd DearpyGUITerminal
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:

```bash
python main.py
```

This will launch the terminal interface, allowing you to interact with various features such as data retrieval, chart visualization, and more.

## Project Structure

- `FyersAuthentication/`: Handles authentication with the Fyers API.
- `FyersData/`: Modules for fetching data from Fyers.
- `NewsSentiment/`: Tools for analyzing news sentiment.
- `PostgresData/`: Interfaces for PostgreSQL data storage and retrieval.
- `Utils/`: Utility functions and helpers.
- `WebSocket/`: Modules for real-time data streaming.
- `main.py`: Entry point of the application.
- `demo.py`: Demonstration script showcasing various features.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Dear PyGui](https://github.com/hoffstadt/DearPyGui) for the GUI framework.
- [Fyers API](https://myapi.fyers.in/docs/) for financial data access.
- [Plotly](https://plotly.com/python/) for interactive charting.
