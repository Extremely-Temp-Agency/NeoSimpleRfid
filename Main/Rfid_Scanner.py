from mfrc522 import MFRC522
import time

class Rfid_Scanner:
    def __init__(self, key=None):
        # Set default key to [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF] if not provided
        if key is None:
            self.key = [0xFF] * 6
        else:
            self.key = [key] * 6
        
        self.MIFAREReader = MFRC522()

    def authenticate_sector(self, uid, sector):
        # Locate correct trailer block on any normal sector
        if sector < 32:
            trailer_block = sector * 4 + 3
        # Locate correct trailer block on mifare4k large sectors
        else:
            trailer_block = ((sector - 32) * 16) + 128 + 15
        status = self.MIFAREReader.MFRC522_Auth(self.MIFAREReader.PICC_AUTHENT1A, trailer_block, self.key, uid)
        return status == self.MIFAREReader.MI_OK

    def read_data(self, block):
        return self.MIFAREReader.MFRC522_Read(block)
    
    def write_data(self, block, value):
        self.MIFAREReader.MFRC522_Write(block, value)

    # Takes a sector and block int and finds the correct total block number
    def sectorblock_to_block(self, sector, block):
        if sector < 32:
            val = (sector * 4) + block
        else:
            val = ((sector - 32) * 16) + 128 + block
        return val    

    def scan_tag(self, sector, block, valuetowrite=None, byte=0, write=False):
        print("scanning")
        value=0
        totalblock = self.sectorblock_to_block(sector, block)
        status, _ = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)
        print(status)
        if status == self.MIFAREReader.MI_OK:
            print("card detected")
            status, uid = self.MIFAREReader.MFRC522_Anticoll()
            if status == self.MIFAREReader.MI_OK:
                uid_str = f"{uid[0]:02X}{uid[1]:02X}{uid[2]:02X}{uid[3]:02X}"
                self.MIFAREReader.MFRC522_SelectTag(uid)
                print("got UID attempting auth")
                if self.authenticate_sector(uid, sector):
                    print("auth good!")
                    data = self.read_data(totalblock)
                    print("read good!")
                    print(data)
                    if data:
                        value = data[byte]
                        if write:
                            print("write Good!")
                            self.write_data(totalblock, valuetowrite)
                            print("Rfid Library vals")
                            print(uid)
                            print(value)
                        return uid_str, value
            self.MIFAREReader.MFRC522_StopCrypto1()
        return None, None

    def continuous_scan(self, sector, block, valuetowrite=None, byte=0, write=False):
        while True:
            uid, value = self.scan_tag(sector, block, valuetowrite, byte, write)
            if uid is not None:
                print("Rfid Library vals")
                print(uid)
                print(value)
                return uid, value
            time.sleep(.1)  # Brief sleep to avoid busy looping
