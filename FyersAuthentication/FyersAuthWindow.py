import dearpygui.dearpygui as dpg
from FyersAuthentication.fyersauth import get_token, get_profile  # Import methods from fyersauth.py

def authenticate_and_fetch():
    """Fetch Fyers authentication details, generate access token, and display profile dynamically."""
    # Retrieve user inputs from the UI
    totp_key = dpg.get_value("totp_key")
    username = dpg.get_value("username")
    pin = dpg.get_value("pin")
    client_id = dpg.get_value("client_id")
    secret_key = dpg.get_value("secret_key")
    redirect_uri = dpg.get_value("redirect_uri")

    # Validate user input
    if not all([totp_key, username, pin, client_id, secret_key, redirect_uri]):
        dpg.set_value("auth_status", "Please fill all fields!")
        return

    try:
        dpg.set_value("auth_status", "Authenticating...")

        # Get access token dynamically using user input
        token = get_token(totp_key, username, pin, client_id, secret_key, redirect_uri)

        # Handle authentication failure
        if not token in token:
            dpg.set_value("auth_status", f"Authentication Failed! {token}")
            return

        # Fetch user profile using access token
        user_data = get_profile(token, client_id)

        # Handle profile retrieval failure
        if not user_data or user_data.get("s", "").lower() == "error":
            dpg.set_value("auth_status", "Failed to fetch user profile!")
            return

        # Display the user profile in the table
        display_user_data(user_data)
        dpg.set_value("auth_status", "Authentication Successful!")

    except Exception as e:
        dpg.set_value("auth_status", f"Error: {str(e)}")


def display_user_data(user_data):
    """Displays authenticated user data in the DearPyGui table."""
    if not user_data or "data" not in user_data:
        dpg.set_value("auth_status", "Invalid user data received.")
        return

    #dpg.delete_item("user_table", children_only=True)  # Clear old data

    user_info = user_data["data"]

    # Populate table with user profile dynamically
    for key, value in user_info.items():
        if value is None:  # Convert None values to "N/A"
            value = "N/A"

        with dpg.table_row(parent="user_table"):
            dpg.add_text(str(key))  # Field Name
            dpg.add_text(str(value))  # Field Value


def open_fyers_auth_window():
    """Opens the Fyers Authentication window with user input fields."""
    if dpg.does_item_exist("fyers_auth_window"):
        dpg.configure_item("fyers_auth_window", show=True)
        return

    with dpg.window(label="Fyers Authentication", modal=True, tag="fyers_auth_window", width=500, height=500):
        dpg.add_text("Enter Fyers Authentication Details", color=(255, 255, 0))
        dpg.add_separator()
        dpg.add_input_text(label="TOTP Key", tag="totp_key")
        dpg.add_input_text(label="Username", tag="username")
        dpg.add_input_text(label="PIN", password=True, tag="pin")
        dpg.add_input_text(label="Client ID", tag="client_id")
        dpg.add_input_text(label="Secret Key", password=True, tag="secret_key")
        dpg.add_input_text(label="Redirect URI", tag="redirect_uri")

        dpg.add_separator()
        dpg.add_button(label="Authenticate", callback=authenticate_and_fetch)
        dpg.add_same_line()
        dpg.add_button(label="Close", callback=lambda: dpg.configure_item("fyers_auth_window", show=False))

        dpg.add_separator()
        dpg.add_text("Status:", color=(0, 255, 0))
        dpg.add_text("", tag="auth_status")

        dpg.add_separator()
        dpg.add_text("User Profile Information", color=(0, 255, 255))

        with dpg.table(header_row=True, tag="user_table"):
            dpg.add_table_column(label="Field", width_stretch=True)
            dpg.add_table_column(label="Value", width_stretch=True)
