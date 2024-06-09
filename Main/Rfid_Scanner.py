# Rfid_Scanner.py

from mfrc522 import MFRC522
import time

class Rfid_Scanner:
    def __init__(self, sector, key):
        self.sector = sector
        self.key = key
        self.MIFAREReader = MFRC522()

    def authenticate_sector(self, uid):
        trailer_block = self.sector * 4 + 3
        status = self.MIFAREReader.MFRC522_Auth(self.MIFAREReader.PICC_AUTHENT1A, trailer_block, self.key, uid)
        return status == self.MIFAREReader.MI_OK

    def read_data(self, block):
        return self.MIFAREReader.MFRC522_Read(block)

    def scan_tag(self):
        status, _ = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)
        if status == self.MIFAREReader.MI_OK:
            status, uid = self.MIFAREReader.MFRC522_Anticoll()
            if status == self.MIFAREReader.MI_OK:
                uid_str = f"{uid[0]:02X}{uid[1]:02X}{uid[2]:02X}{uid[3]:02X}"
                self.MIFAREReader.MFRC522_SelectTag(uid)
                if self.authenticate_sector(uid):
                    data = self.read_data(self.sector * 4)
                    value = data[0]  # Assuming the value is stored in the first byte
                    return uid_str, value
        return None, None

    def continuous_scan(self):
        while True:
            uid, value = self.scan_tag()
            if uid is not None:
                yield uid, value
            time.sleep(0.1)  # Brief sleep to avoid busy looping

if __name__ == "__main__":
    # Example usage
    sector = 4
    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    scanner = Rfid_Scanner(sector, key)
    for uid, value in scanner.continuous_scan():
        print(f"UID: {uid}, Value: {value}")
