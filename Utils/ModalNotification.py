import dearpygui.dearpygui as dpg

class ModalNotification:
    def __init__(self):
        self.modal_id = "modal_notification"

        with dpg.window(label="Notification", modal=True, show=False, tag=self.modal_id, no_title_bar=True):
            self.message_text = dpg.add_text("")
            dpg.add_separator()
            dpg.add_button(label="OK", width=75, callback=self.hide)

    def show(self, message):
        """Display the modal notification with the given message."""
        dpg.set_value(self.message_text, message)
        dpg.configure_item(self.modal_id, show=True)

    def hide(self):
        """Hide the modal notification."""
        dpg.configure_item(self.modal_id, show=False)
