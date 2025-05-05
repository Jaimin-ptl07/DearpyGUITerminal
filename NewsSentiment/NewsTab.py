import requests
import feedparser
import dearpygui.dearpygui as dpg
from gnews import GNews

# RSS Feed URLs categorized
RSS_FEEDS = {
    "Latest News": ["https://www.business-standard.com/rss/latest.rss"],
    "Markets": ["https://www.business-standard.com/rss/markets-106.rss"],
    "Economics": ["https://www.business-standard.com/rss/economy-102.rss"],
    "Companies": ["https://www.business-standard.com/rss/companies-101.rss"],
    "Industries": ["https://www.business-standard.com/rss/industry-217.rss"],
    "Technology": ["https://www.business-standard.com/rss/technology-108.rss"],
    "Politics": ["https://www.business-standard.com/rss/politics-155.rss"],
}

feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


class NewsTab:
    def __init__(self):
        self.news_data = []
        self.categories = ["All"] + list(RSS_FEEDS.keys())
        self.current_category = "All"
        self.tab_id = "news_tab"  # Unique identifier for this tab

    def fetch_rss_news(self, category, limit=10):
        """Fetch and parse news articles based on selected category."""
        try:
            temp_news_data = []
            categories_to_fetch = [category] if category != "All" else list(RSS_FEEDS.keys())

            for cat in categories_to_fetch:
                for feed_url in RSS_FEEDS.get(cat, []):
                    parsed_feed = feedparser.parse(feed_url)
                    if not parsed_feed.entries:
                        print(f"⚠️ No news found for category: {cat}")
                    for entry in parsed_feed.entries[:limit]:
                        title = entry.get("title", "No Title").strip()
                        summary = (entry.get("description") or entry.get("summary") or "").strip()
                        published = entry.get("published", "No Date Available").strip()
                        temp_news_data.append((title, summary, published, cat))

            self.news_data = temp_news_data
            print(f"✅ Debug: Fetched {len(self.news_data)} articles for category: {category}")
        except Exception as e:
            print(f"❌ Error fetching RSS news: {e}")

    def display_news_data(self, category):
        """Fetch and display news data in a DearPyGui table."""
        self.current_category = category
        dpg.set_value(f"{self.tab_id}_status", f"Fetching {category} News...")
        self.fetch_rss_news(category)

        # Clear only rows, keeping the table intact
        rows = dpg.get_item_children(f"{self.tab_id}_table", 1)
        if rows:
            for row in rows:
                dpg.delete_item(row)

        # Populate table with new data
        news_found = False
        for title, summary, published, cat in self.news_data:
            if self.current_category == "All" or cat == self.current_category:
                news_found = True
                with dpg.table_row(parent=f"{self.tab_id}_table"):
                    dpg.add_text(title)
                    dpg.add_text(summary)
                    dpg.add_text(published)

        if not news_found:
            dpg.set_value(f"{self.tab_id}_status", f"No news available for {self.current_category}.")
        else:
            dpg.set_value(f"{self.tab_id}_status", "News Data Fetched Successfully")

    def create_news_tab(self):
        """Create the News Data tab in DearPyGui."""
        with dpg.tab(label="Financial News"):
            dpg.add_text("📰 Latest Financial News", color=(0, 255, 255))
            dpg.add_button(label="Fetch News", callback=lambda: self.display_news_data("All"))
            dpg.add_separator()
            dpg.add_text("", tag=f"{self.tab_id}_status")  # Unique Status message

            # Explicit buttons for each category
            with dpg.group(horizontal=True):
                dpg.add_button(label="All", callback=lambda: self.display_news_data("All"))
                dpg.add_button(label="Latest News", callback=lambda: self.display_news_data("Latest News"))
                dpg.add_button(label="Markets", callback=lambda: self.display_news_data("Markets"))
                dpg.add_button(label="Economics", callback=lambda: self.display_news_data("Economics"))
                dpg.add_button(label="Companies", callback=lambda: self.display_news_data("Companies"))
                dpg.add_button(label="Industries", callback=lambda: self.display_news_data("Industries"))
                dpg.add_button(label="Technology", callback=lambda: self.display_news_data("Technology"))
                dpg.add_button(label="Politics", callback=lambda: self.display_news_data("Politics"))

            dpg.add_separator()

            # Table for news data
            with dpg.table(header_row=True, tag=f"{self.tab_id}_table", row_background=True, hideable=True,
                           resizable=True):
                dpg.add_table_column(label="Headline", width_stretch=True)
                dpg.add_table_column(label="Summary", width_stretch=True)
                dpg.add_table_column(label="Published Date", width_stretch=True)


if __name__ == "__main__":
    news_tab = NewsTab()
    dpg.create_context()
    dpg.create_viewport(title='Financial News', width=900, height=600)
    with dpg.window(label="Main Dashboard"):
        news_tab.create_news_tab()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
