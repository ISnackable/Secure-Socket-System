#Server socket python
# Importing stuff
import os
import socket
import json
from hashlib import pbkdf2_hmac
from datetime import datetime
from openpyxl import Workbook, load_workbook
from captcha.image import ImageCaptcha

# Get today's day
today = datetime.today()
today_day = today.isoweekday()
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Loading a excel file in Python
wb = load_workbook(filename='AssignmentData.xlsx')
membership_sheet = wb['Membership'] # Set membership_sheet to Membership sheet
customers_sheet = wb['Customers'] # Set customers_seet to Customers sheet
preorder_sheet = wb['Preorder'] # Set membership_sheet to Membership sheet


# Login functions
class Login():
    def __init__(self):
        self.membership = {}

        # Creating dictionary of username : salted password
        for row in membership_sheet.iter_rows(min_row=2, max_col=3, max_row=membership_sheet.max_row, values_only=True):
            self.membership[row[1]] = row[2]

    # Function to check if user is in filesystem
    def user_in_system(self, user):
        if user in self.membership:
            return True
        else:
            return False

    # Function to add a registered user to filesystem
    def add_new_user(self, user, hash):
        membership_sheet.append([len(self.membership)+1, user, hash])
        self.membership[user] = hash

    # Function to retrieve salt of user and return it
    def send_salt(self, user):
        return self.membership[user][:64]

    # Function to check if user credential matches  
    def verify_login(self, user, hash):
        if hash == self.membership[user][64:]:
            return True
        else:
            return False

    #  Function to generate a random captcha image
    def captcha(self):
        image = ImageCaptcha()
        self.random_captcha = os.urandom(2).hex()
        data = image.generate(self.random_captcha)
        return data.getvalue()

    # Function to validate if captcha was correctly inputed
    def captcha_validation(self, raw_captcha):
        if raw_captcha == self.random_captcha:
            return True
        else:
            return False


# FileSystem's functions
class FileSystem:
    try:
        # Function to retrieve a selected day food menu
        def process_foodmenu(self, day=today_day):
            sheet = wb[weekdays[int(day)-1]] # Set sheet to current day of the week

            # Creating string of "menu:price,discount |" based on the current day of the week
            food_menus = ""
            for row in sheet.iter_rows(min_row=2, max_col=3, max_row=sheet.max_row, values_only=True):
                food_menus += f"{row[0]}:{str(row[1])},{str(row[2])}|"

            return food_menus

        # Function to add a new menu item on a given day
        def add_new_menu(self, day, foodname, price, discount):
            sheet = wb[weekdays[int(day)-1]] # Set sheet to current day of the week
            sheet.append([foodname.strip(), float(price.strip()), float(discount.strip())/100])

        # Function to remove a menu item on a given day
        def remove_menu(self, day, row):
            sheet = wb[weekdays[int(day)-1]] # Set sheet to current day of the week
            sheet.delete_rows(int(row)+1, 1)

        # Function to edit a menu item's price/discount on a given day
        def edit_menu(self, day, row, price, discount):
            sheet = wb[weekdays[int(day)-1]] # Set sheet to current day of the week
            sheet["B"+str(int(row)+1)], sheet["C"+str(int(row)+1)] = float(price), float(discount)/100 # at current day sheet cell B(whichever number of choice + 1) to be set price and cell C(whichever number of choice + 1) to be set discount

        # Function to append the user's preordered food
        def preorder(self, user, food_preordered):
            preorder_sheet.append([user, food_preordered])

        # Function to check a user's preorder if any.
        def check_preorder(self, user):
            for row_number, row in enumerate(preorder_sheet.iter_rows(min_row=2, max_col=2, max_row=preorder_sheet.max_row, values_only=True), 2):
                if row[0] == user and weekdays[today_day-1] in row[1]:
                    preorder = json.loads(row[1])
                    preorder_to_send = preorder[weekdays[today_day-1]]

                    del preorder[weekdays[today_day-1]]
                    preorder_sheet.delete_rows(row_number)
                    if len(preorder) > 0:
                        preorder_sheet.insert_rows(row_number)
                        preorder_sheet["A"+str(row_number)], preorder_sheet["B"+str(row_number)] = user, json.dumps(preorder)

                    return json.dumps(preorder_to_send)
            else:
                return "NULL"

        def record_transaction(self, user, food_ordered):
            customers_sheet.append([today.strftime("%c"), user, food_ordered])

    finally:
        # Saves the excel file
        wb.save('AssignmentData.xlsx')


def start_server():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        soc.bind(('127.0.0.1', 8089)) # Binds localhost and port 8089 to socket
    except socket.error as msg:
        import sys
        print('Bind failed. Error : ' + str(sys.exc_info()))
        print(msg.with_traceback())
        sys.exit() # Exit if any error

    soc.listen(1) # Listen for 1 connections
    while True:
        print("waiting a new call at accept()")
        connection, address = soc.accept() # Accept a connection
        if handler(connection) == 'SHUTDOWN':
            break
    soc.close()
    print(f"Server stopped at {today}")

def handler(con):
    print("client connected")

    while True:
        buf = con.recv(4096) # buf is of the type of byte
        content = buf.decode() # decode buf into a string
        if len(buf) > 0:
            print(f"Request from Client: {content.split()}")

            if content == 'SHUTDOWN':
                break

            if content.startswith("CHECKUSER"):
                if login.user_in_system(content.split()[1].strip()):
                    con.sendall(b'TRUE')
                else:
                    con.sendall(b'FALSE')

            elif content.startswith("ADDUSER"):
                user = content.split()[1].strip()
                hash = content.split()[2].strip()
                login.add_new_user(user, hash)

            elif content == "CAPTCHA":
                con.sendall(login.captcha())

            elif content.startswith("CAPTCHAVALIDATION"):
                raw_captcha = content.split()[1].strip()
                if login.captcha_validation(raw_captcha):
                    con.sendall(b'TRUE')
                else:
                    con.sendall(b'FALSE')

            elif content.startswith("SENDSALT"):
                con.sendall(login.send_salt(content.split()[1]).encode())

            elif content.startswith("VERIFYLOGIN"):
                user = content.split()[1].strip()
                hash = content.split()[2].strip()
                if login.verify_login(user, hash):
                    con.sendall(b'TRUE')
                else:
                    con.sendall(b'FALSE')

            elif content.startswith("CHECKPREORDER"):
                user = content.split()[1].strip()
                con.sendall(FileSystem().check_preorder(user).encode())

            elif content.startswith("RETRIVEMENU") and content[-1].isnumeric():
                con.sendall(FileSystem().process_foodmenu(content[-1].strip()).encode())

            elif content.startswith("ADDMENU"):
                day = content.split('|')[1].strip()
                foodname = content.split('|')[2].strip()
                price = content.split('|')[3].strip()
                discount = content.split('|')[4].strip()
                FileSystem().add_new_menu(day, foodname, price, discount)

            elif content.startswith("REMOVEMENU") and content[-1].isnumeric():
                day = content.split()[1].strip()
                row = content.split()[2].strip()
                FileSystem().remove_menu(day, row)

            elif content.startswith("EDITMENU"):
                day = content.split()[1].strip()
                row = content.split()[2].strip()
                price = content.split()[3].strip()
                discount = content.split()[4].strip()
                FileSystem().edit_menu(day, row, price, discount)

            elif content.startswith("PREORDER"):
                user = content.split('|')[1].strip()
                preorder = content.split('|')[2].strip()
                FileSystem().preorder(user, preorder)

            elif content.startswith("RECORDTRANSACTION"):
                user = content.split('|')[1].strip()
                food_ordered = content.split('|')[2].strip()
                FileSystem().record_transaction(user, food_ordered)
        else: # 0 length buf implies client has dropped the con.
            print("client disconnected")
            break # quit this handler immediately and return ""
    # Saves the excel file
    wb.save('AssignmentData.xlsx')
    con.close() #exit from the loop when client sent q or x
    return buf.decode()

# Start program
login = Login()
start_server()