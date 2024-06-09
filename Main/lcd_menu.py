from gpiozero import Button
from rpi_lcd import LCD
import signal
import time

class LCDMenu:
    def __init__(self, increment_pin, decrement_pin, select_pin, line1_text, string_length, use_numbers):
        self.lcd = LCD()
        self.line1_text = line1_text
        self.string_length = string_length
        self.use_numbers = use_numbers
        self.current_char = '0' if use_numbers else 'A'
        self.selected_text = ""
        self.input_complete = False

        self.buttons = [
            Button(increment_pin),
            Button(decrement_pin),
            Button(select_pin, hold_time=2)
        ]

        self.buttons[0].when_pressed = self.increment_char
        self.buttons[1].when_pressed = self.decrement_char
        self.buttons[2].when_pressed = self.select_char
        self.buttons[2].when_held = self.complete_input

        # Setup signal handler for cleanup
        signal.signal(signal.SIGINT, self.cleanup)

    def print_lcd(self, line1, line2=""):
        self.lcd.clear()
        print(f"LCD Line 1: {line1}")  # Debug print for line 1
        print(f"LCD Line 2: {line2}")  # Debug print for line 2
        self.lcd.text(line1, 1)
        self.lcd.text(line2, 2)

    def increment_char(self):
        if self.use_numbers:
            self.current_char = chr((ord(self.current_char) - 48 + 1) % 10 + 48)  # Rotate within 0-9
        else:
            self.current_char = chr((ord(self.current_char) - 65 + 1) % 26 + 65)  # Rotate within A-Z
        self.update_display()

    def decrement_char(self):
        if self.use_numbers:
            self.current_char = chr((ord(self.current_char) - 48 - 1) % 10 + 48)  # Rotate within 0-9
        else:
            self.current_char = chr((ord(self.current_char) - 65 - 1) % 26 + 65)  # Rotate within A-Z
        self.update_display()

    def select_char(self):
        if len(self.selected_text) < self.string_length:
            self.selected_text += self.current_char
            if len(self.selected_text) >= self.string_length:
                self.complete_input()
        self.update_display()

    def complete_input(self):
        self.input_complete = True

    def update_display(self):
        # Show the full selected text with the current character at the end
        display_text = self.selected_text
        if not self.input_complete and len(display_text) < self.string_length:
            display_text += self.current_char
        if len(display_text) > 16:
            self.print_lcd(self.line1_text[:16], display_text[-16:])
        else:
            self.print_lcd(self.line1_text[:16], display_text)

    def cleanup(self, signal_received=None, frame=None):
        self.lcd.clear()
        for button in self.buttons:
            button.close()
        print("Cleanup done.")
        exit(0)

    def run(self):
        self.update_display()
        print("Waiting for button presses...")
        while not self.input_complete:
            time.sleep(0.1)
        self.print_lcd("Submitted", "")
        time.sleep(2)  # Display "Submitted" for 2 seconds
        return self.selected_text
