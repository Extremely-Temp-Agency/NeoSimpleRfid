from gpiozero import Button, RotaryEncoder
from rpi_lcd import LCD
import signal
import time

class LCDMenu:
    def __init__(self, select_pin, back_pin, encoder_pin1, encoder_pin2, line1_text, string_length, use_numbers):
        self.lcd = LCD()
        self.line1_text = line1_text
        self.string_length = string_length
        self.use_numbers = use_numbers
        self.current_char = '0' if use_numbers else 'A'
        #variable where text is held at end
        self.selected_text = ""
        self.input_complete = False

        self.select_button = Button(select_pin)
        self.back_button = Button(back_pin)
        self.encoder = RotaryEncoder(encoder_pin1, encoder_pin2, wrap=False)
        self.encoder.when_rotated = self.rotary_encoder

        # Setup signal handler for cleanup
        signal.signal(signal.SIGINT, self.cleanup)

    def print_lcd(self, line1, line2=""):
        self.lcd.clear()
        print(f"LCD Line 1: {line1}")  # Debug print for line 1
        print(f"LCD Line 2: {line2}")  # Debug print for line 2
        self.lcd.text(line1, 1)
        self.lcd.text(line2, 2)

    def rotary_encoder(self):
        if self.encoder.steps > 0:
            self.increment_char()
        elif self.encoder.steps < 0:
            self.decrement_char()
        self.encoder.steps = 0  # Reset the steps after handling

    def increment_char(self):
        if self.use_numbers:
            if self.current_char < '9':
                self.current_char = chr(ord(self.current_char) + 1)
            else:
                self.current_char = '0'
        else:
            if self.current_char < 'Z':
                self.current_char = chr(ord(self.current_char) + 1)
            else:
                self.current_char = 'A'
        self.update_display()

    def decrement_char(self):
        if self.use_numbers:
            if self.current_char > '0':
                self.current_char = chr(ord(self.current_char) - 1)
            else:
                self.current_char = '9'
        else:
            if self.current_char > 'A':
                self.current_char = chr(ord(self.current_char) - 1)
            else:
                self.current_char = 'Z'
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
        self.select_button.close()
        self.back_button.close()
        self.encoder.close()
        print("Cleanup done.")
        exit(0)

    def run(self,line1_text=None, string_length=None, use_numbers=None):
        #Make sure that any updated parameters don't break the menu, and update them
        if line1_text is not None:
            self.line1_text = line1_text
        if string_length is not None:
            self.string_length = string_length
        if use_numbers is not None:
            self.use_numbers = use_numbers
            self.current_char = '0' if use_numbers else 'A'
        self.selected_text = ""
        self.input_complete = False

        self.update_display()
        #Actually handle the user input while we havent completed
        while not self.input_complete:
            if self.select_button.is_pressed:
                self.select_char()
            if self.back_button.is_pressed:
                self.selected_text = self.selected_text[:-1]  # Remove last character
                self.update_display()
            time.sleep(0.1)
        self.print_lcd("Submitted", "")
        time.sleep(.25)
        return self.selected_text

