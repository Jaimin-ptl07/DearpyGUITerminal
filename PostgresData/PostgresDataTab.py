import dearpygui.dearpygui as dpg
import psycopg2


class PostgresDataViewer:
    def __init__(self):
        """
        Initialize an empty database configuration.
        """
        self.db_config = {
            "dbname": "",
            "user": "",
            "password": "",
            "host": "localhost",
            "port": "5432",
            "table": ""
        }
        self.connection = None
        self.tables = []

    def connect_db(self):
        """
        Establish a connection to the PostgreSQL database.
        """
        try:
            self.connection = psycopg2.connect(
                dbname=self.db_config["dbname"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                host=self.db_config["host"],
                port=self.db_config["port"]
            )
            return True
        except Exception as e:
            dpg.set_value("postgres_status", f"❌ Database Connection Error: {e}")
            return False

    def fetch_tables(self):
        """
        Fetch all table names from the PostgreSQL database and update the dropdown.
        """
        if not self.connect_db():
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            self.tables = [row[0] for row in cursor.fetchall()]
            cursor.close()

            # ✅ Update the Combo Box with Fetched Table Names
            dpg.configure_item("table_selector", items=self.tables)

            dpg.set_value("postgres_status", f"✅ Tables Loaded Successfully")
        except Exception as e:
            dpg.set_value("postgres_status", f"❌ Error Fetching Tables: {e}")
            self.tables = []

    def fetch_table_data(self):
        """
        Fetch the selected table's data dynamically.
        """
        if not self.db_config["table"]:
            dpg.set_value("postgres_status", "⚠️ No table selected!")
            return None, None

        if not self.connect_db():
            return None, None

        query = f"SELECT * FROM {self.db_config['table']} LIMIT 50;"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]  # Get column names
            data = cursor.fetchall()
            cursor.close()

            return column_names, data  # ✅ Keep the connection open until done
        except Exception as e:
            dpg.set_value("postgres_status", f"❌ Query Error: {e}")
            return None, None

    def display_table_data(self):
        """
        Display the selected PostgreSQL table in a DearPyGui table.
        """
        column_names, data = self.fetch_table_data()
        if not data:
            return

        dpg.set_value("postgres_status", f"✅ Loaded {self.db_config['table']} Successfully")

        # Clear existing columns and rows before inserting new data
        existing_columns = dpg.get_item_children("postgres_table", 0)
        if existing_columns:
            for col in existing_columns:
                dpg.delete_item(col)

        existing_rows = dpg.get_item_children("postgres_table", 1)
        if existing_rows:
            for row in existing_rows:
                dpg.delete_item(row)

        # Dynamically create table columns
        for col_name in column_names:
            dpg.add_table_column(label=col_name, parent="postgres_table")

        # Populate table with data
        for row in data:
            with dpg.table_row(parent="postgres_table"):
                for cell in row:
                    dpg.add_text(str(cell))

    def update_db_config(self, sender, app_data, key):
        """
        Update database configuration based on user input.
        """
        self.db_config[key] = app_data

    def update_table_selection(self, sender, app_data):
        """
        Update the selected table from the combo box.
        """
        self.db_config["table"] = app_data
        self.display_table_data()

    def create_postgres_tab(self):
        """
        Create the PostgreSQL Data tab in DearPyGui with user input fields.
        """
        with dpg.tab(label="PostgreSQL Viewer"):
            dpg.add_text("🔍 Enter PostgreSQL Credentials", color=(255, 255, 0))

            # User Input Fields for Database Connection
            dpg.add_input_text(label="Database Name", callback=lambda s, a: self.update_db_config(s, a, "dbname"))
            dpg.add_input_text(label="User", callback=lambda s, a: self.update_db_config(s, a, "user"))
            dpg.add_input_text(label="Password", password=True,
                               callback=lambda s, a: self.update_db_config(s, a, "password"))
            dpg.add_input_text(label="Host", default_value="localhost",
                               callback=lambda s, a: self.update_db_config(s, a, "host"))
            dpg.add_input_text(label="Port", default_value="5432",
                               callback=lambda s, a: self.update_db_config(s, a, "port"))

            # Load Tables Button
            dpg.add_button(label="Fetch Tables", callback=self.fetch_tables)
            dpg.add_separator()

            # Dropdown to Select Table
            dpg.add_combo(label="Select Table", tag="table_selector", items=self.tables,
                          callback=self.update_table_selection)

            # Status Text
            dpg.add_text("", tag="postgres_status")

            # Create Table for Data Display
            with dpg.child_window(horizontal_scrollbar=True):
                with dpg.table(header_row=True, hideable=True, policy=dpg.mvTable_SizingFixedFit, tag="postgres_table", resizable=True, scrollX=True, row_background=True, scrollY=True):
                    pass  # Columns will be dynamically added
