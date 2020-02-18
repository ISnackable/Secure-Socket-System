#Client socket in python
# Python 3.7 not using ANSI compatible console (The 2 lines of code below fixes this issue)
# importing stuff
import subprocess
subprocess.call('', shell=True)
import os
import json
from hashlib import pbkdf2_hmac
import getpass
from datetime import datetime
import socket
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import PKCS1_OAEP, PKCS1_v1_5, AES  
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15 
from Cryptodome.Hash import SHA256
import base64

# Function to get socket
def getnewsocket():
	return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientsocket = getnewsocket()
host = "localhost"
clientsocket.connect((host, 8089)) # Connect to server's socket

# Get today's day
today = datetime.today()
today_day = today.strftime('%A') # %A Formating returns Name of the day of the week
weekday = today.isoweekday()
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Variable Declaration
choice_of_action = " "
food_menus = {}
cart = {}
preorder = {}
total = 0.00
spam_menus = [
    f"Display Menu",
    "Search Menu",
    "Display Cart",
    "Edit Cart",
    "Check Out"
]

# Class of Customers as well as functions
class Customers:
    def __init__(self):
        self.membership = {}
        self.login = input(f"""{'=':=^45}
Welcome, please enter login/register.
1. Register (Get special discounts!)
2. Login
3. Login as Guest
{'=':=^45}
> """)  
        self.login_mode = False
        self.admin_mode = False
        self.discount_mode = False

    # Customer tracking system, append time, name, item ordered to excel Customers sheet
    def user_tracking(self):
        while True:
            while not self.login.isnumeric() or int(self.login) < 1 or int(self.login) > 3:
                if self.login == "not found":
                    print(f"\n\x1b[33m\u26A0  Warning: User '{self.customer_name}' is not found in the database.\u001b[0m", end="") # ⚠ \u26A0
                elif self.login == "break":
                    pass
                else:
                    print("\n\x1b[33m\u26A0  Warning: Please pick a valid input\u001b[0m", end="") # ⚠ \u26A0
                self.login = input(f"""
1. Register (Get special discounts!)
2. Login
3. Login as Guest
{'=':=^45}
> """)

            if self.login == "1":
                self.register_system()
            elif self.login == "2":
                self.login_system()
            elif self.login == "3":
                self.login_mode = True
                self.customer_name = "Guest"

            if self.login_mode: # If true, start program
                if self.login == "2":
                    clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"CHECKPREORDER {self.customer_name}")) # Send CHECKPREORDER to check if a user has any preorder
                    preorder_string = cryptothingy.decrypt_ciphertext(clientsocket.recv(8192)).decode()
                    if preorder_string != "NULL": # If user has preorder, cart will be reference from preorder dictionary
                        global cart
                        preorder = json.loads(preorder_string)
                        cart = preorder
                        print("\n\u001b[33m\u26A0  Warning: Added previously preordered item to cart!\u001b[0m")
                break
        print(f"Welcome {self.customer_name}, enjoy your meal.")
        sp_automated_menu() # Start SPAM

    # Register account and append to excel
    def register_system(self):
        self.customer_name = input("Login username: ")
        if len(self.customer_name) > 0:
            clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"CHECKUSER {self.customer_name}")) # Send CHECKUSER to check if user is in the system
            user_in_system = cryptothingy.decrypt_ciphertext(clientsocket.recv(4096)).decode()
        else:
            user_in_system = "FALSE"

        # Loops until input is not in membership dictionary
        while user_in_system == "TRUE" or self.customer_name == "":
            if self.customer_name == "":
                print(f"\n\u001b[33m\u26A0  Warning: Username cannot be empty!\u001b[0m") # ⚠ \u26A0
            else:
                print(f"\n\u001b[33m\u26A0  Warning: Username '{self.customer_name}' is already taken!\u001b[0m") # ⚠ \u26A0
            self.customer_name = input("Login username: ")
            if len(self.customer_name) > 0:
                clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"CHECKUSER {self.customer_name}")) # Send CHECKUSER to check if user is in the system
                user_in_system = cryptothingy.decrypt_ciphertext(clientsocket.recv(4096)).decode()
            else:
                user_in_system = "FALSE"

        self.passwd, self.passwd1 = getpass.getpass("New Password: "), getpass.getpass("Re-enter Password: ")

        # Loops until both passwd & passwd1 are indentical or it's blank
        while self.passwd != self.passwd1 or self.passwd == "" or " " in self.passwd:
            if self.passwd != self.passwd1:
                print(f"\n\u001b[33m\u26A0  Warning: Password does not match!\u001b[0m") # ⚠ \u26A0
            else:
                print(f"\n\u001b[33m\u26A0  Warning: Not a valid password!\u001b[0m")
            self.passwd, self.passwd1 = getpass.getpass("New Password: "), getpass.getpass("Re-enter Password: ")

        salt = os.urandom(32) # Generate a string of size random bytes suitable for cryptographic use.
        salted_password = pbkdf2_hmac('sha256', self.passwd.encode(), salt, 100000) # Hash the password with pbkdf2_hmac, SHA-256 algorithm
        salted_hash = (salt + salted_password).hex() # Prepend salt to salted password and get the hex

        clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"ADDUSER {self.customer_name} {salted_hash}")) # Send ADDUSER for user to be added in the FileSystem
        
        self.login_mode = True

    # Login as root, admin mode
    def login_system(self):
        self.captcha()

        self.customer_name = input("Login username: ")
        self.passwd = getpass.getpass()
        if len(self.customer_name) > 0:
            clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"CHECKUSER {self.customer_name}")) # Send CHECKUSER to check if user is in the system
            user_in_system = cryptothingy.decrypt_ciphertext(clientsocket.recv(4096)).decode()
        else:
            user_in_system = "FALSE"

        if user_in_system == "TRUE":
            # Checking if password is correct
            clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"SENDSALT {self.customer_name}")) # Send SENDSALT to recieve the salt value of user
            salt = cryptothingy.decrypt_ciphertext(clientsocket.recv(4096)).decode()
            new_salted_password = pbkdf2_hmac('sha256', self.passwd.encode(), bytes.fromhex(salt), 100000)
            clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"VERIFYLOGIN {self.customer_name} {new_salted_password.hex()}")) # Send VERIFYLOGIN to check if user credentials is correct
            verified = cryptothingy.decrypt_ciphertext(clientsocket.recv(4096)).decode()

            if  self.customer_name == "root" and verified == "TRUE":
                print(f"Login successful, welcome back {self.customer_name}.")
                self.login_mode = True
                self.admin_mode = True
                self.discount_mode = True
                spam_menus.extend(["Edit Menu","Shutdown Server"]) # Admin's options
            elif verified == "TRUE":
                print(f"Login successful, welcome back {self.customer_name}.")
                self.login_mode = True
                self.discount_mode = True
            else:
                print(f"\n\u001b[33m\u26A0  Warning: Login unsuccessful!\u001b[0m")

            # Loops and allows to retry if wrong password
            while user_in_system == "TRUE" and not self.discount_mode:
                retry = input("Do you want to retry? 'Y' to retry, 'N' to exit: ")
                if retry == "Y" or retry == "y":
                    self.login_system()
                else:
                    self.login = "break"
                    break

        else:
            self.login = "not found"

    # Function to generate a captcha image
    def captcha(self):
        print(u"\u001b[36mNote: A captcha verification is required to proceed to login.\u001b[0m \n")
        captchavalidation = "FALSE"
        while captchavalidation == "FALSE": # Continue looping until captcha is correct
            clientsocket.sendall(cryptothingy.encrpyt_plaintext("CAPTCHA")) # Send CAPTCHA to receive a image captcha bytes
            captcha = clientsocket.recv(16384)
            with open('client\captcha.png', 'wb') as captcha_image: # Create a .png file with the captcha bytes
                captcha_image.write(captcha)
                captcha_image.close()
            
            import sys
            imageViewerFromCommandLine = {'linux':'xdg-open',
                                  'win32':'explorer',
                                  'darwin':'open'}[sys.platform]
            captcha_image = subprocess.Popen([imageViewerFromCommandLine, r"client\captcha.png"], shell=False) # Open the captcha.png image
            
            raw_captcha = input("Enter the characters in captcha.png: ")
            if len(raw_captcha) <= 0:
                raw_captcha = "INVALIDCAPTCHA" 
            
            if sys.platform == "win32":
                subprocess.Popen(f"taskkill /F /IM Microsoft.Photos.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # Close the captcha.png image
            
            clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"CAPTCHAVALIDATION {raw_captcha}".strip())) # Send CAPTCHAVALIDATION to verify if captcha is valid
            try:
                captchavalidation = cryptothingy.decrypt_ciphertext(clientsocket.recv(1024)).decode()
            except:
                captchavalidation = "FALSE"

            if captchavalidation == "FALSE":
                print("\n\u001b[33m\u26A0  Warning: You have failed verfication, try again!\u001b[0m")
            
        else:
            print(u"\u001b[36mNote: You have been verified. You can now proceed to login.\u001b[0m \n")


# SPAM Function
def sp_automated_menu():
    global choice_of_action, cart #Globalize to be used in a function
    server_shutdown = False
    
    try:
        while len(choice_of_action) != 0:
            print(f"\n{' Welcome to SPAM ':=^45}")
            # Loops and print the spam_menus list
            for counter, menu_item in enumerate(spam_menus, 1):
                print(f"{counter}. {menu_item}")
            choice_of_action = input("Please input your choice of action (ENTER to exit): ")

            if choice_of_action == "1" or choice_of_action == "2":
                option, day = select_menu_day(choice_of_action) # Function to select which day to reieve food menu

                if choice_of_action == "1":
                    # Loops and print menu dictionary
                    for counter, menu in enumerate(food_menus, 1):
                        if customer.discount_mode: # True prints discounted price
                            print(f"{counter}. {menu:<25}:{'$':>10}{(food_menus[menu][0] * (1-food_menus[menu][1])):.2f}")
                        else:
                            print(f"{counter}. {menu:<25}:{'$':>10}{food_menus[menu][0]:.2f}")
                    input(f"{'Press any key to continue...':<45}")
                else:
                    search_menu(option, day)

            elif choice_of_action == "3":
                display_cart()
            elif choice_of_action == "4":
                edit_cart()
            elif choice_of_action == "5":
                check_out()
            elif choice_of_action == "6" and customer.admin_mode: # Only allows if both are True
                edit_menu()
            elif choice_of_action == "7" and customer.admin_mode: # Stop server if both are True
                print(f"Server stopped at {today}")
                clientsocket.sendall(cryptothingy.encrpyt_plaintext("SHUTDOWN"))
                clientsocket.close()
                server_shutdown = True
                break
            elif choice_of_action == "":
                pass
            else:
                print(f"\u001b[33m\u26A0  Warning: Please pick a valid input\u001b[0m") # ⚠ \u26A0
        else:
            print("Thank you for using my automated menu!")

    except KeyboardInterrupt:
        print("Thank you for using my automated menu!")

    except:
        print("\u001b[31mError: Oof! Something went wrong!\u001b[0m")
        return "ERROR"

    finally:
        if not server_shutdown:
            if len(preorder) > 0:
                clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"PREORDER|{customer.customer_name}|{json.dumps(preorder)}")) # Send PREORDER to the server for food preordered to be recorded in FileSystem
            food_ordered = ", ".join([f'{cart_item} x{quantity}' for (cart_item, quantity) in cart.items()]) 
            food_ordered = f"RECORDTRANSACTION|{customer.customer_name}|{food_ordered}"
            message_to_send = food_ordered.encode()+b"$"+base64.b64encode(cryptothingy.create_digital_signature(food_ordered))
            clientsocket.sendall(cryptothingy.encrpyt_plaintext(message_to_send.decode())) # Send RECORDTRANSACTION to the server for food ordered to be recorded in FileSystem

        
# Option 1. Display today's menu
def display_today_menu():
    clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"RETRIVEMENU {weekday}")) # Send RETRIVEMENU to receive today's menu
    plaintext_with_signature = cryptothingy.decrypt_ciphertext(clientsocket.recv(4096)).decode()
    plaintext = plaintext_with_signature.split('$')[0]
    signature = plaintext_with_signature.split('$')[1]
    if cryptothingy.verify_digital_signature(plaintext, signature):
        process_foodmenu(plaintext)
        print(f"\n{f' Menu for {weekdays[weekday-1]} ':=^45}")
    else:
        print("Oops, menu is invalid! Try again.")

# Option 1. Display other days' menu
def display_otherdays_menu():
    day = input(f"\n{f' Which day? ':=^45}\n1. Monday\n2. Tuesday\n3. Wednesday\n4. Thursday\n5. Friday\n6. Saturday\n7. Sunday\n>> ")
    while not day.isnumeric() or int(day) <= 0 or int(day) > 7:
        print(f"\u001b[33m\u26A0  Warning: Input number 1-7\u001b[0m")
        day = input(f"\n{f' Which day? ':=^45}\n1. Monday\n2. Tuesday\n3. Wednesday\n4. Thursday\n5. Friday\n6. Saturday\n7. Sunday\n>> ")
    
    clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"RETRIVEMENU {weekday}")) # Send RETRIVEMENU to receive selected day's menu
    plaintext_with_signature = cryptothingy.decrypt_ciphertext(clientsocket.recv(4096)).decode()
    plaintext = plaintext_with_signature.split('$')[0]
    signature = plaintext_with_signature.split('$')[1]
    if cryptothingy.verify_digital_signature(plaintext, signature):
        process_foodmenu(plaintext)
        print(f"\n{f' Menu for {weekdays[int(day)-1]} ':=^45}")
    else:
        print("Oops, menu is invalid! Try again.")

    return day

# Option 2. Search menu
def search_menu(option, day):
    global cart, preorder #Globalize to be used in a function
    matches = []
    menu_query = input("Please input food to search: ").strip()
        
    # Appending matches of query in the list 'matches'
    for menu in food_menus:
        if menu_query.strip().lower() in menu.strip().lower():
            matches.append(menu)

    # Printing of matched item, price and ordering
    if len(matches) > 0:
        print(f"\n{f' Yes, we serve the following ':=^45}")
        for counter, menu in enumerate(matches, 1):
            if customer.discount_mode: # True prints discounted price
                print(f"{counter}. {menu:<25}:{'$':>10}{(food_menus[menu][0] * (1-food_menus[menu][1])):.2f}")
            else:
                print(f"{counter}. {menu:<25}:{'$':>10}{food_menus[menu][0]:.2f}")

        if (option == "1") or (option == "2" and day == str(weekday)):
            order_more = input("\nWould you like to order the menu above? any key for yes, (ENTER to exit): ")
        elif option == "2" and day != str(weekday) and customer.customer_name != "Guest":
            order_more = input(f"\nSorry, menu on {weekdays[int(day)-1]} is not served today.\nWould you like to preorder the menu above? any key for yes, (ENTER to exit): ")
        else:
            return print("\nSorry, you can only preorder with an account")

        # Loops until user enter to exit
        while order_more != "":
            dish_order = input(f"Input number 1-{len(matches)} of the food would you like to order: ")

            # Make sure dish_order must be a number and in the range of length of matches
            while not dish_order.isnumeric() or int(dish_order) < 1 or int(dish_order) > len(matches):
                print(f"\u001b[33m\u26A0  Warning: Input number 1-{len(matches)}\u001b[0m")
                dish_order = input(f"Input number 1-{len(matches)} of the food would you like to order: ")

            quantity = input(f"Enter the amount of {matches[int(dish_order)-1]} you wish to order: ")

            # Make sure quantity order must be a number and more than 0
            while not quantity.isnumeric() or int(quantity) < 1:
                quantity = input(f"\u001b[33m\u26A0  Warning: Enter a valid amount of {matches[int(dish_order)-1]} you wish to order: \u001b[0m")
            
            if (option == "1") or (option == "2" and day == str(weekday)): # Goes into the statement if selected food menu is current day
                # Checks if item is in cart
                if not matches[int(dish_order)-1] in cart:
                    cart[matches[int(dish_order)-1]] = int(quantity) # Set quantity
                else:
                    cart[matches[int(dish_order)-1]] += int(quantity) # Add quantity
                print(f"{matches[int(dish_order)-1]} added to cart.")

            elif option == "2" and day != str(weekday) and customer.customer_name != "Guest": # Preordering food for other days
                if weekdays[int(day)-1] not in preorder:
                    preorder[weekdays[int(day)-1]] = {}
                # Checks if item is in preorder
                if not matches[int(dish_order)-1] in list(preorder[weekdays[int(day)-1]]):
                    preorder[weekdays[int(day)-1]][matches[int(dish_order)-1]] = int(quantity) # Set quantity
                else:
                    preorder[weekdays[int(day)-1]][matches[int(dish_order)-1]] += int(quantity) # Add quantity
                print(f"{matches[int(dish_order)-1]} added to preorder.")

            order_more = input("Would you like to order more? any key for yes, (ENTER to exit): ")
    else:
        print(f"Sorry, {menu_query} is not served at this time.")

# Option 3. Display cart
def display_cart():
    print(f"\n{' Item(s) in cart ':=^45}")
    if len(cart) > 0:
        for counter, cart_item in enumerate(cart, 1):
            print(f"{counter}. {cart_item:<25}:{'x':>10}{cart[cart_item]} qty")
        input(f"{'Press any key to continue...':<45}")
    else:
        print("There's no item in your cart")

# Option 4. Edit cart
def edit_cart():
    edit_action = " "
    print(f"\n{' Item(s) in cart ':=^45}")

    # If length of cart is more than 0
    if len(cart) > 0:
        while edit_action != "":
            if len(cart)==0:
                print("Nothing left in cart. Exiting edit cart.")
                return
            for counter, cart_item in enumerate(cart, 1):
                print(f"{counter}. {cart_item:<25}:{'x':>10}{cart[cart_item]} qty")
            edit_action = input("\n1. Change quantity\n2. Remove item\nPlease input your choice of action (ENTER to exit): ")

            # 1. Change quantity
            if edit_action == "1":
                edit_action = input(f"Input number 1-{len(cart)} of the food would you like to change quantity: ")
                while not edit_action.isnumeric() or int(edit_action) < 1 or int(edit_action) > len(cart):
                    edit_action = input(f"\u001b[33m\u26A0  Warning: Input number 1-{len(cart)} of the food would you like to change quantity: \u001b[0m")

                quantity = input(f"Input the number of {list(cart)[int(edit_action)-1]}'s quantity: ")
                while not quantity.isnumeric() or int(quantity) < 0:
                    quantity = input(f"\u001b[33m\u26A0  Warning: Input the number of {list(cart)[int(edit_action)-1]}'s quantity: \u001b[0m")
                if int(quantity) == 0:
                    print(f"You have remove {list(cart)[int(edit_action)-1]} ({cart.pop(list(cart)[int(edit_action)-1])} qty)")
                else:
                    cart[list(cart)[int(edit_action)-1]] = int(quantity)

            # 2. Remove item in cart
            elif edit_action == "2":
                edit_action = input(f"Input number 1-{len(cart)} of the food would you like to remove: ")
                while not edit_action.isnumeric() or int(edit_action) < 1 or int(edit_action) > len(cart):
                    print(f"\u001b[33m\u26A0  Warning: Input number 1-{len(cart)}\u001b[0m")
                    edit_action = input(f"Input number 1-{len(cart)} of the food would you like to remove: ")
                print(f"You have removed {list(cart)[int(edit_action)-1]} ({cart.pop(list(cart)[int(edit_action)-1])} qty)")
                
            elif edit_action == "":
                pass
            else:
                print(f"\u001b[33m\u26A0  Warning: Input a valid choice\u001b[0m")
    else:
        print("There's no item in your cart")

# Option 5. Check out
def check_out():
    global total

    clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"RETRIVEMENU {weekday}")) # Send RETRIVEMENU to recieve current day's food menu
    plaintext_with_signature = cryptothingy.decrypt_ciphertext(clientsocket.recv(4096)).decode()
    plaintext = plaintext_with_signature.split('$')[0]
    signature = plaintext_with_signature.split('$')[1]
    if cryptothingy.verify_digital_signature(plaintext, signature):
        process_foodmenu(plaintext)
    else:
        print("Oops, something went wrong! Try again later.")
        return

    print(f"\n{' Check out ':=^45}")
    if len(cart) > 0:
        for counter, cart_item in enumerate(cart, 1):
            if customer.discount_mode:
                total += float(cart[cart_item] * (food_menus[cart_item][0] * (1-food_menus[cart_item][1])))
                print(f"{counter}. {cart_item:<18} x{cart[cart_item]:<10}:{'$':>5}{cart[cart_item] * (food_menus[cart_item][0] * (1-food_menus[cart_item][1])):.2f}")
            else:
                total += float(cart[cart_item] * food_menus[cart_item][0])
                print(f"{counter}. {cart_item:<18} x{cart[cart_item]:<10}:{'$':>5}{cart[cart_item] * food_menus[cart_item][0]:.2f}")

        confirm_payment = input(f"Please check your order, total of {total:.2f}. Pay now? Y/N: ")
        if confirm_payment.lower() == 'n':
            total = 0.00
            return
        while confirm_payment.lower() != 'y' and confirm_payment.lower() != 'n':
            confirm_payment = input(f"\u001b[33m\u26A0  Warning: Please check your order, total of {total:.2f}. Pay now? Y/N: \u001b[0m")
            if confirm_payment.lower() == 'n':
                total = 0.00
                return
            
        payment = input(f"Thank you for using SPAM. Please pay the total of {total:.2f}: ")
        while not isfloat(payment) or float(payment) < float(format(total, '.2f')):
            print(f"\u001b[33m\u26A0  Warning:", end=" ")
            if isfloat(payment) and float(payment) < float(format(total, '.2f')):
                print(f"You're short by {abs(total-float(payment)):.2f}", end=", ")
            payment = input(f"please pay the total of {total:.2f}: \u001b[0m")

        if float(payment) > total:
            print(f"Thank you, here is your change, ${abs(total-float(payment)):.2f}", end=", ")
        else:
            print("Thank you for eating at our restaurant", end=", ")

        raise KeyboardInterrupt # raise KeyboardInterrupt to display custom message and return orders

    else:
        print(f"There's no item in your cart")

# Option 6. Edit Menu
def edit_menu():
    try:
        print(f"\n{' Admin Mode ':=^45}")
        update_menu = input("1) Add a new menu item & corresponding price\n2) Remove a menu item\n3) Change menu item's price & discount\nPlease enter request or '0' to quit: ")
        # loop while update_menu is not "0"
        while update_menu != "0":
            option, day = select_menu_day(choice_of_action) # Select which day's food menu to add/remove/edit

            # 1) Add a new menu item
            if update_menu == "1":
                # Loops and print today's menu dictionary
                for counter, menu in enumerate(food_menus, 1):
                    if customer.discount_mode: # True prints discounted price
                        print(f"{counter}. {menu:<25}:{'$':>10}{(food_menus[menu][0] * (1-food_menus[menu][1])):.2f}")
                    else:
                        print(f"{counter}. {menu:<25}:{'$':>10}{food_menus[menu][0]:.2f}")
                # new_menu = "New Dish : Price, Discount | Another Dish : Price, Discount"
                print("Note: Discount has to be 0-100")
                new_menu = input("Please input 'new menu : price, discount' seperate by '|' (Type 'quit' to exit): ")
                if new_menu.lower() == "quit":
                    return
                while not ':' in new_menu or not ',' in new_menu:
                    new_menu = input("\u001b[33m\u26A0  Warning: Input 'new menu : price, discount' seperate by '|' (Type 'quit' to exit): \u001b[0m")
                    if new_menu.lower() == "quit":
                        return

                pairs = new_menu.strip().split(sep='|') # Split pairs into list if there are more than 1 item
                for pair in pairs:
                    new_menu = pair.strip().split(':')
                    price_discount = new_menu[1].strip().split(',')
                    if not isfloat(price_discount[0].strip()) or not isfloat(price_discount[1].strip()) or float(price_discount[0]) < 0 or float(price_discount[1]) < 0 or float(price_discount[1]) > 100:
                        print(f"\n\u001b[33m\u26A0  Warning: Ignoring '{new_menu[0].strip()}' as price/discount is not a float or discount is less than 0 or more than 100\u001b[0m ")
                        break
                    food_menus[new_menu[0].strip()] = [float(price_discount[0].strip()), float(price_discount[1].strip())/100]
                    clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"ADDMENU|{day}|{new_menu[0].strip()}|{price_discount[0].strip()}|{price_discount[1].strip()}")) # Send ADDMENU to server for new food menu to be added to the FileSystem
            
            # 2) Remove a menu item
            elif update_menu == "2":
                # Loops and print today's menu dictionary
                for counter, menu in enumerate(food_menus, 1):
                    if customer.discount_mode: # True prints discounted price
                        print(f"{counter}. {menu:<25}:{'$':>10}{(food_menus[menu][0] * (1-food_menus[menu][1])):.2f}")
                    else:
                        print(f"{counter}. {menu:<25}:{'$':>10}{food_menus[menu][0]:.2f}")
                if len(food_menus) > 0:
                    delete_row = input(f"Input 1-{len(food_menus)} to delete (Type 'quit' to exit): ")
                    if delete_row.lower() == "quit":
                        return
                    while not delete_row.isnumeric() or int(delete_row) <= 0 or int(delete_row) > len(food_menus):
                        delete_row = input(f"\u001b[33m\u26A0  Warning: Please input 1-{len(food_menus)} to delete (Type 'quit' to exit): \u001b[0m")
                        if delete_row.lower() == "quit":
                            return
                    confirmation = input(f"Are you sure you want to remove {list(food_menus)[int(delete_row)-1]}? Y/N: ")
                    while True:
                        if confirmation == "Y" or confirmation == "y":
                            print(f"You have removed {list(food_menus)[int(delete_row)-1]}.")
                            del(food_menus[list(food_menus)[int(delete_row)-1]])
                            clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"REMOVEMENU {day} {delete_row}")) # Send REMOVEMENU to server for food menu to be removed from the FileSystem
                            break
                        elif confirmation == "N" or confirmation == "n":
                            break
                        else:
                            confirmation = input(f"Are you sure you want to remove {list(food_menus)[int(delete_row)-1]}? Y/N: ")
                else:
                    print(f"There's no item in the food menu")

            # 3) Change menu item's price & discount
            elif update_menu == "3":
                for counter, menu in enumerate(food_menus, 1):
                    print(f"{counter}. {menu:<25}:{'$':>10}{food_menus[menu][0]} X {int(food_menus[menu][1]*100)}%")
                
                edit_price = input(f"Input 1-{len(food_menus)} to edit the price (Type 'quit' to exit): ")
                if edit_price.lower() == "quit":
                    return
                while not edit_price.isnumeric() or int(edit_price) <= 0 or int(edit_price) > len(food_menus):
                    edit_price = input(f"Please input 1-{len(food_menus)} to edit the price (Type 'quit' to exit): ")
                    if edit_price.lower() == "quit":
                        return

                confirmation = input(f"Are you sure you want to edit the price of {list(food_menus)[int(edit_price)-1]}? Y/N: ")
                while True:
                    if confirmation == "Y" or confirmation == "y":
                        new_price = input(f"Input the new price of {list(food_menus)[int(edit_price)-1]}: ")
                        new_discount = input(f"Input the new discount (0-100)% of {list(food_menus)[int(edit_price)-1]}: ")
                        while not isfloat(new_price) or float(new_price) < 0:
                            new_price = input(f"\u001b[33m\u26A0  Warning: Input the new price of {list(food_menus)[int(edit_price)-1]}: \u001b[0m")
                        while not isfloat(new_discount) or float(new_discount) < 0 or float(new_discount) > 100:
                            new_discount = input(f"\u001b[33m\u26A0  Warning: Input the new discount (0-100)% of {list(food_menus)[int(edit_price)-1]}: \u001b[0m")
                        food_menus[list(food_menus)[int(edit_price)-1]] = [float(new_price), float(new_discount)/100]
                        clientsocket.sendall(cryptothingy.encrpyt_plaintext(f"EDITMENU {day} {edit_price} {new_price} {new_discount}")) # Send EDITMENU to server to edit the food menu price/discount 
                        if int(edit_price) == 0:
                            print(f"\u001b[33m\u26A0  Warning: You have set {list(food_menus)[int(edit_price)-1]} to be free\u001b[0m")
                        else:
                            print(f"{list(food_menus)[int(edit_price)-1]}'s price and discount has been changed to {new_price} at {float(new_discount)}% discount.\n")
                        break
                    elif confirmation == "N" or confirmation == "n":
                        break
                    else:
                        confirmation = input(f"Are you sure you want to change the price & discount {list(food_menus)[int(edit_price)-1]}? Y/N: ")
            else:
                print(f"\u001b[33m\u26A0  Warning: Select a valid option. \u001b[0m\n")
            update_menu = input("1) Add a new menu item & corresponding price\n2) Remove a menu item\n3) Change menu item's price & discount\nPlease enter request or '0' to quit: ")
    except:
        print("\u001b[31mError: Something went wrong! Ignoring request\u001b[0m") # Quick and dirty way to escape any improper validation error.

# Is float check function
def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Process string of foodmenu into a dictionary
def process_foodmenu(todays_menu):
    global food_menus

    food_menus.clear()
    todays_menu = todays_menu.strip('|').split(sep='|')
    
    for menu in todays_menu:
        price = menu.strip().split(sep=':')[1].strip().split(',')
        food_menus[menu.strip().split(sep=':')[0].strip()] = [float(price[0]),float(price[1])]
    return food_menus

# Function to select a day's menu
def select_menu_day(choice_of_action):
    keyword = "Search" if choice_of_action == "2" else "Edit" if choice_of_action == "6" else "Display"

    option = input(f"\n{f' {keyword} Menu ':=^45}\n1. {keyword} Today's Menu\n2. {keyword} Other Days Menu\n>> ")
    while not option.isnumeric() or int(option) < 1 or int(option) > 2:
        print(f"\u001b[33m\u26A0  Warning: Input a valid option\u001b[0m")
        option = input(f"\n{f' Display Menu ':=^45}\n1. View Today's Menu\n2. View Other Days Menu\n>> ")
    if option == "1":
        display_today_menu()
        day = weekday
    else:
        day = display_otherdays_menu()
    return option, day

class Cryptostuff:
    def __init__(self): #This function generates the RSA key for server/client side.
        for fname in os.listdir('./client'):
            if fname.endswith('.pem'):
                self.client_public_key=open("client/public.pem","r").read()
                self.client_private_key=open("client/private.pem","r").read()
                break
        else:
            # Generate a 1024-bit or 2024-bit long RSA Key pair.
            self.rsa_keypair=RSA.generate(2048)
            # store the private key to private.pem
            # store the public key to public.pem
            with open("client/private.pem","w") as f:
                print(self.rsa_keypair.exportKey().decode() ,file=f)
            f.close()
            self.client_private_key = self.rsa_keypair.exportKey().decode()
            with open("client/public.pem","w") as f:
                print(self.rsa_keypair.publickey().exportKey().decode() ,file=f)
            f.close()
            self.client_public_key = self.rsa_keypair.publickey().exportKey().decode()
        clientsocket.sendall(f"CLIENTPUBLICKEY${self.client_public_key}".encode())
        self.server_public_key = clientsocket.recv(4096).decode()
    
    def generate_aes_key(self): #This function generates the AES key
        self.aes_key = get_random_bytes(AES.block_size)

        return self.aes_key

    def rsa_encrpytion(self): # Encrpyt AES key to become a session key
        self.rsa_cipher = PKCS1_OAEP.new(RSA.import_key(self.server_public_key.encode()))
        self.session_key = self.rsa_cipher.encrypt(self.generate_aes_key()) # Encrpyted AES key with RSA
        self.aes_cipher = AES.new(self.aes_key,AES.MODE_CBC)
        self.aes_iv = self.aes_cipher.iv # retrieve the randomly generated iv value 

        return self.session_key, self.aes_iv

    def send_session_key(self):
        server_recieved = "0$"
        while server_recieved != "1$":
            session_key, aes_iv = self.rsa_encrpytion()
            session_key = session_key.hex()
            aes_iv = aes_iv.hex()
            clientsocket.sendall(f"1${session_key}${aes_iv}".encode())
            server_recieved = clientsocket.recv(4096).decode()

    def encrpyt_plaintext(self, plaintext):
        self.send_session_key()
        ciphertext = self.aes_cipher.encrypt(pad(plaintext.encode(), AES.block_size))

        return base64.b64encode(ciphertext)

    def decrypt_ciphertext(self, ciphertext):
        self.aes_cipher = AES.new(self.aes_key,AES.MODE_CBC,iv=self.aes_iv)
        plain_text = unpad(self.aes_cipher.decrypt(ciphertext), AES.block_size)

        return plain_text

    def create_digital_signature(self, plaintext):
        digest = SHA256.new(plaintext.encode()) # plaintext is in bytes
        signer = pkcs1_15.new(self.rsa_keypair)
        signature = signer.sign(digest)
        return signature

    def verify_digital_signature(self, plaintext, signature):
        signature = base64.b64decode(signature)
        digest = SHA256.new(plaintext.encode()) # plaintext is in bytes
        verifier = pkcs1_15.new(RSA.import_key(self.server_public_key.encode()))
        try:
            verifier.verify(digest,signature)
            # print("The signature is valid")
            return True
        except:
            # print("The signature is not valid")
            return False

# Start Program
cryptothingy = Cryptostuff()
customer = Customers()
customer.user_tracking()