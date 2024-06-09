from LCDMenu import LCDMenu


        #Define GPIO Pin out for Raspi
select_pin = 17
back_pin = 27
encoder_pin1 = 12
encoder_pin2 = 16

line1_text = ""
string_length = 8
use_numbers = False
menu = LCDMenu(select_pin, back_pin, encoder_pin1, encoder_pin2, line1_text="Sector:", string_length = 2, use_numbers=True)



if __name__ == "__main__":
    menu.line1_text = "Sector:"
    menu.string_length = 2
    menu.use_numbers = True
    selected_sector= menu.run("Sector:",2,True)

    menu.line1_text = "Block"
    menu.string_length = 2
    menu.use_numbers = True
    selected_block = menu.run("Block",2,True)

    menu.line1_text = "Auth:"
    menu.string_length = 3
    menu.use_numbers = True
    selected_auth = menu.run("Auth",3,True)
    print(selected_sector)
    print(selected_auth)
    print(selected_block)    
