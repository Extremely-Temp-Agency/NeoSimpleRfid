from mfrc522 import MFRC522
import socket
import time
import signal
from threading import Thread, Event
from signal import pause
from rpi_lcd import LCD
from lcd_menu import LCDMenu

# UDP settings
UDP_IP = "192.168.50.51"
UDP_PORT = 5005

# Create an object for the LCD display
lcd = LCD()

# Sector to be Read, Is updated by menu on startup
sector = 4

# Events to control thread termination and starting a new scan
scan_complete_event = Event()
start_scan_event = Event()

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    print_lcd("Ctrl+C captured", "Ending read.")
    lcd.clear()
    print("Cleanup done.")
    exit(0)

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# This is the default key for authentication
key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

def print_lcd(line1, line2=""):
    # Handle wrapping of line1 into line2 if line1 is too long
    if len(line1) > 16:
        overflow = line1[16:]
        line1 = line1[:16]
        if len(line2) > 0:
            line2 = overflow + " " + line2
        else:
            line2 = overflow
    # Ensure line2 does not exceed 16 characters
    line2 = line2[:16]
    # Update LCD display
    lcd.clear()
    lcd.text(line1, 1)
    lcd.text(line2, 2)

def authenticate_sector(mfrc, sector, key, uid):
    trailer_block = sector * 4 + 3  # Trailer block for the sector
    status = mfrc.MFRC522_Auth(mfrc.PICC_AUTHENT1A, trailer_block, key, uid)
    return status == mfrc.MI_OK

def read_data(mfrc, block):
    # Read the data from the block
    return mfrc.MFRC522_Read(block)

def send_udp_message(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

def rfid_scan(sector):
    global last_uid
    # Reinitialize the MFRC522 reader
    MIFAREReader = MFRC522()
    while not scan_complete_event.is_set():
        # Scan for cards
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:
                uid_str = f"{uid[0]:02X}{uid[1]:02X}{uid[2]:02X}{uid[3]:02X}"

                last_uid = uid_str

                # Select the scanned tag
                MIFAREReader.MFRC522_SelectTag(uid)

                # Attempt to authenticate and read the selected sector
                if authenticate_sector(MIFAREReader, sector, key, uid):
                    data = read_data(MIFAREReader, sector * 4)  # Read from the first block of the selected sector
                    value = data[0]  # Assuming the value is stored in the first byte

                    # Send UDP message
                    message = f"UID: {uid_str}, Sector {sector} Value: {value}"
                    send_udp_message(message)

                    # Display on LCD
                    print_lcd(f"UID: {uid_str}", f"Value: {value}")

                # Indicate scan completion
                scan_complete_event.set()

            # Wait a bit to avoid immediate re-scanning of the same card
            time.sleep(1)
        else:
            # Brief sleep to avoid busy looping
            time.sleep(0.1)

def start_new_scan(sector):
    global scan_complete_event
    while True:
        scan_complete_event.clear()
        print_lcd("Press any button", "to start scan")
        start_scan_event.wait()  # Wait for any button to be pressed
        start_scan_event.clear()
        rfid_thread = Thread(target=rfid_scan, args=(sector,))
        rfid_thread.start()
        rfid_thread.join()  # Wait for the thread to complete

def button_callback():
    global start_scan_event
    start_scan_event.set()  # Signal that the start button has been pressed

if __name__ == "__main__":
    # Run the menu to select sector number
    lcd_menu = LCDMenu(increment_pin=17, decrement_pin=27, select_pin=22, line1_text="Sector Number:", string_length=2, use_numbers=True)
    sector_number_str = lcd_menu.run()
    sector_number = int(sector_number_str)

    # Display the selected sector number
    print_lcd("Sector Selected:", sector_number_str)
    time.sleep(2)

    # Assign button callback to start scan
    start_button = Button(23)  # Example pin for starting the scan
    start_button.when_pressed = button_callback

    # Start the RFID scan manager in a separate thread
    scan_manager_thread = Thread(target=start_new_scan, args=(sector_number,))
    scan_manager_thread.daemon = True
    scan_manager_thread.start()

    print("Waiting for button presses...")
