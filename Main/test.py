from LCDMenu import LCDMenu
import Rfid_Scanner
import time
import threading
# Initialize MFRC522
scanner = Rfid_Scanner.Rfid_Scanner()

# Define GPIO Pin out for Raspi LCD/Buttons
select_pin = 17
back_pin = 27
encoder_pin1 = 12
encoder_pin2 = 16
scan_results = {"uid": None, "value":None}

# Initialize the LCDMenu
menu = LCDMenu(select_pin, back_pin, encoder_pin1, encoder_pin2, line1_text="Sector:", string_length=2, use_numbers=True)

# Shared data structure to store scan results
scan_results = {"uid": None, "value": None}
stop_thread = threading.Event()

def continuous_scan_thread(sector, block, results, stop_event):
    for uid, value in scanner.continuous_scan(sector, block):
        results["uid"] = uid
        results["value"] = value
        stop_event.set()  # Signal that the scan is complete
        break
    
if __name__ == "__main__":
    # Set menu parameters and run for sector input
    ##selected_sector = menu.run("Sector:", 2, True)
    selected_sector=1

    # Set menu parameters and run for block input
    ##selected_block = menu.run("Block:", 2, True)
    selected_block =1
    # Set menu parameters and run for auth input
    ##selected_auth = menu.run("Auth:", 3, True)
    selected_auth =255

    # Print selected inputs
    print(f"Selected Sector: {selected_sector}")
    print(f"Selected Block: {selected_block}")
    print(f"Selected Auth: {selected_auth}")

    # Continuous scanning and printing results
while True:
                print("This is the main loop")
                stop_thread.clear()
                scan_thread = threading.Thread(target=continuous_scan_thread, args=(selected_sector, selected_block, scan_results, stop_thread))
                scan_thread.start()
                scan_thread.join()  # Wait for the scanning thread to complete

        # Use the scan results
                if scan_results["uid"] is not None and scan_results["value"] is not None:
                        print(f"UID: {scan_results['uid']} / Value: {scan_results['value']}")

                time.sleep(1)  # Sleep before starting the next scan
