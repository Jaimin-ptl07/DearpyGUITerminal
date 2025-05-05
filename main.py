import dearpygui.dearpygui as dpg
import asyncio
import feedparser
from FyersAuthentication.FyersAuthWindow import open_fyers_auth_window
from FyersData.FyersDataTab import FyersDataTab
from PostgresData.PostgresDataTab import PostgresDataViewer
from FyersData.RealTimeInsight import LiveDataTab
from NewsSentiment.NewsTab import NewsTab
from FyersData.RealTimeMarket import LiveDataTab
import datetime
# Set a custom User-Agent to prevent RSS feeds from blocking requests
feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# List of RSS feeds to fetch news from (cycled every 10 sec)
RSS_FEEDS = [
    "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "https://www.business-standard.com/rss/latest.rss",
    "https://www.business-standard.com/rss/markets-106.rss",
]

    # Define Bloomberg colors
BLOOMBERG_ORANGE = [255, 165, 0]
BLOOMBERG_DARK = [25, 25, 25]
BLOOMBERG_BLACK = [0, 0, 0]
BLOOMBERG_WHITE = [255, 255, 255]
BLOOMBERG_RED = [255, 0, 0]
BLOOMBERG_GREEN = [0, 200, 0]
BLOOMBERG_YELLOW = [255, 255, 0]
BLOOMBERG_BLUE = [100, 150, 250]
BLOOMBERG_GRAY = [120, 120, 120]

async def fetch_news(feed_url):
    """Fetch and parse news articles from a single RSS feed asynchronously."""
    try:
        parsed_feed = await asyncio.to_thread(feedparser.parse, feed_url)
        news_items = []
        for entry in parsed_feed.entries:
            title = entry.get("title", "No Title").strip()
            desc = (entry.get("description") or entry.get("summary") or "").strip()
            news_items.append((title, desc))

        return news_items[:5]  # Limit to 5 news items

    except Exception as e:
        print(f"⚠️ Error fetching news from {feed_url}: {e}")
        return [("Error fetching news", str(e))]

async def update_news(feed_url):
    """Fetch news from a specific feed and update the UI dynamically."""
    news_data = await fetch_news(feed_url)

    # Clear old news rows
    children = dpg.get_item_children("news_table", 1)  # Get rows
    if children:
        for child in children:
            dpg.delete_item(child)  # Remove old rows

    # Add new news rows dynamically
    for title, description in news_data:
        with dpg.table_row(parent="news_table"):
            dpg.add_text(title)
            dpg.add_text(description, wrap=600)  # Adjust wrapping for better readability

async def update_news_periodically():
    """Cycle through RSS feeds every 10 seconds, updating news dynamically."""
    feed_index = 0
    while dpg.is_dearpygui_running():
        await update_news(RSS_FEEDS[feed_index])  # Fetch news from the current RSS feed
        feed_index = (feed_index + 1) % len(RSS_FEEDS)  # Move to the next feed in sequence
        await asyncio.sleep(10)  # Wait 10 seconds before fetching from the next feed

# Create DearPyGui context
dpg.create_context()

# Create a maximized viewport
dpg.create_viewport(
    title="Financial Dashboard",
    decorated=True,
    resizable=True,
    clear_color=(0.1, 0.1, 0.1, 1)  # Dark theme
)
dpg.maximize_viewport()

# Setup GUI
dpg.setup_dearpygui()
dpg.show_viewport()

# Get updated viewport dimensions
width = dpg.get_viewport_width()
height = dpg.get_viewport_height()
fyers_tab = FyersDataTab()
postgres_viewer = PostgresDataViewer()
realinsight = LiveDataTab()
news_tab = NewsTab()
real_market = LiveDataTab()
# News Section UI
with dpg.window(label="News Dashboard", width=width, height=height, tag="primary", no_title_bar=True, no_resize=True,
                no_move=True):
    with dpg.group(horizontal=True):
        dpg.add_text("FINCEPT", color=BLOOMBERG_ORANGE)
        dpg.add_text("PROFESSIONAL", color=BLOOMBERG_WHITE)
        dpg.add_text(" | ", color=BLOOMBERG_GRAY)
        dpg.add_input_text(label="", default_value="Enter Command", width=300)
        dpg.add_button(label="Search", width=80)
        dpg.add_text(" | ", color=BLOOMBERG_GRAY)
        dpg.add_text(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", tag="time_display")

    dpg.add_separator()
    # Menu Bar
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="New")
            dpg.add_menu_item(label="Open")
            dpg.add_menu_item(label="Save")
            dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

        with dpg.menu(label="View"):
            dpg.add_menu_item(label="Dashboard")
            dpg.add_menu_item(label="Market Data")
            dpg.add_menu_item(label="Portfolio")

        with dpg.menu(label="Settings"):
            dpg.add_menu_item(label="FyersAuth", callback=open_fyers_auth_window)  # Open FyersAuth window
            dpg.add_menu_item(label="Theme")

        with dpg.menu(label="Help"):
            dpg.add_menu_item(label="About")
            dpg.add_menu_item(label="Documentation")

    with dpg.child_window(autosize_x=True, height=height - 200):
        with dpg.group(horizontal=True, width=0):
            # Left Column - Navigation
            with dpg.child_window(width=200, autosize_y=True):
                with dpg.tree_node(label="Stock Screener"):
                    dpg.add_button(label="Market Trends")
                with dpg.tree_node(label="Economic Indicators"):
                    dpg.add_button(label="GDP Data")
                with dpg.tree_node(label="Technical Analysis"):
                    dpg.add_button(label="Moving Averages")

            # Center Column - Main Data Window
            with dpg.child_window(width=width - 200, autosize_y=True):
                with dpg.tab_bar():
                    fyers_tab.FyersTab()
                    #realinsight.LiveDataTabUI()
                    real_market.LiveDataTabUI()
                    news_tab.create_news_tab()
                    postgres_viewer.create_postgres_tab() # Add PostgreSQL Tab

            # Right Column - Small Quick Actions
            with dpg.child_window(width=200, autosize_y=True):
                dpg.add_button(label="Trade", width=75, height=40)
                dpg.add_button(label="Watchlist", width=75, height=40)
                dpg.add_button(label="Alerts", width=75, height=40)

    with dpg.child_window(height=150):
        dpg.add_text("Latest News (Updates Every 10s)", color=(255, 200, 0))  # News Header

        with dpg.table(header_row=True, borders_outerH=True, scrollX=True, borders_outerV=True, borders_innerH=True,
                       borders_innerV=True, resizable=True, tag="news_table"):
            # Define table columns
            dpg.add_table_column(label="Title", width_stretch=True)
            dpg.add_table_column(label="Description", width_stretch=True)

# Run Async Tasks
async def main_loop():
    """Start DearPyGui and continuously update the news in the background."""
    await update_news(RSS_FEEDS[0])  # Fetch initial news from first feed
    asyncio.create_task(update_news_periodically())  # Start background updates
    dpg.set_primary_window("primary", True)
    # dpg.start_dearpygui()
    # dpg.destroy_context()
    # Keep DearPyGui running while updating frames
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        await asyncio.sleep(0.01)  # Yield control to the event loop

# Start event loop
asyncio.run(main_loop())
dpg.destroy_context()