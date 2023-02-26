"""Desktop GUI designed to create a grocery list from user input and 
format a msg to given phone number"""

import os
import sys
import smtplib
import PySimpleGUI as sg
from dotenv import load_dotenv
from item_class import Item

load_dotenv()

CONNECTION = os.getenv("MY_CONNECTION")
PORT = os.getenv("PORT")
ITEMS_LIST = []
GROCERIES_DICT = {}
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("EMAIL_PWD")
CARRIERS = {
    "Verizon": "@vtext.com",
    "T-Mobile": "@tmomail.net",
    "Sprint": "@messaging.sprintpcs.com",
    "AT&T": "@txt.att.net",
    "Boost Mobile": "@smsmyboostmobile.com",
    "Cricket": "@sms.cricketwireless.net",
    "U.S. Cellular": "@email.uscc.net",
}


def main():
    """Initializes GUI window, then triggers the email to be texted when user has finished."""
    number, carrier = primary_window()
    send_email(number, carrier)


def primary_window():
    """Primary window which contains the user's list and button commands to edit/finalize.

    :return: phone number and carrier information
    :rtype: tuple
    """
    layout_1 = [
        [sg.Text("Enter items and quantity below.")],
        [sg.Text()],
        [sg.Text("Input Item")],
        [sg.Input(key="-IN1-", do_not_clear=False)],
        [sg.Text("Input quantity: ")],
        [sg.Input(key="-IN2-", do_not_clear=False)],
        [sg.Button("Add Item")],
        [sg.Text("\n")],
        [
            sg.Listbox(
                ITEMS_LIST,
                right_click_menu=["", ["Delete", "Update Quantity", "Rename"]],
                size=(45, 15),
                key="-LIST-",
                enable_events=True,
            )
        ],
        [sg.Button("Finalize List"), sg.Button("Exit")],
    ]

    window = sg.Window("Groceries Lister", layout_1, enable_close_attempted_event=True)

    while True:
        event, values = window.read()
        name = values["-IN1-"]

        # .lower() being used to roughly negate case-sensitive differences for now

        if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, "Exit"):
            exit_window()

        if event == "Add Item":
            if name.lower() in Item.items_dict:
                repeated_item_window()
            else:
                item = Item(values["-IN1-"].lower(), values["-IN2-"])
                ITEMS_LIST.append(item)
                window["-LIST-"].update(ITEMS_LIST)

        if event == "Finalize List":
            check = confirm()
            if check:
                return get_phone_info()

        if event == "Delete":
            item = values["-LIST-"][0]
            ITEMS_LIST.remove(item)
            del Item.items_dict[item.name]
            window["-LIST-"].update(ITEMS_LIST)

        if event == "Update Quantity":
            item = values["-LIST-"][0]
            quantity_window(item)
            window["-LIST-"].update(ITEMS_LIST)

        if event == "Rename":
            item = values["-LIST-"][0]
            rename_window(item)
            window["-LIST-"].update(ITEMS_LIST)


def repeated_item_window():
    """Error window that occurs when a user enters an item that already exists in their list"""
    layout = [
        [
            sg.Text(
                "That item already exists in your list. Right click an item to modify it."
            )
        ],
        [sg.Button("OK")],
    ]
    window = sg.Window("Repeated Item Error", layout, modal=True)

    while True:

        event, _ = window.read()
        if event in ["OK", "Cancel", sg.WIN_CLOSED]:
            break

    window.close()


def confirm():
    """Window to confirm the user wishes to finalize their list

    :return: Returns True if the user confirms finalization
    :rtype: Bool
    """
    layout = [
        [
            sg.Text(
                "Are you sure you want to finalize your list?\n"
                "You will not be able to edit your list beyond this point."
            )
        ],
        [sg.Button("Confirm"), sg.Button("Cancel")],
    ]

    window = sg.Window("Confirm Finalization", layout, modal=True)

    while True:
        event, _ = window.read()

        if event == "Confirm":
            return True
        if event in ("Cancel", sg.WIN_CLOSED):
            break

    window.close()


def get_phone_info():
    """Window for user to input phone number and select which carrier the number is assigned to.

    :return: Tuple of the phone number and carrier name selected from CARRIERS dict
    :rtype: Tuple
    """
    layout = [
        [sg.Text("Enter Number and select Carrier, then click Finalize.")],
        [sg.Input(key="-IN1-")],
        [sg.DropDown(list(CARRIERS), key="-IN2-")],
        [sg.Button("Finalize")],
    ]

    window = sg.Window(
        "Phone Information", layout, modal=True, enable_close_attempted_event=True
    )

    while True:
        event, values = window.read()
        phone = values["-IN1-"]
        carrier = values["-IN2-"]

        if event == "Finalize":
            while values["-IN1-"] and values["-IN2-"]:
                return phone, carrier

        if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
            exit_window()


def quantity_window(item):
    """Window which allows user to edit their selected item's quantity

    :param item: Item object which was selected via highlight/right click in the primary window
    :type item: Item_Class.Item
    """
    layout = [
        [sg.Text("Enter quantity")],
        [sg.Input(key="-IN1-")],
        [sg.Button("Update"), sg.Button("Cancel")],
    ]

    window = sg.Window("Update Quantity", layout, modal=True)

    while True:
        event, values = window.read()
        new_quantity = values["-IN1-"]

        if event in ["Update"]:
            item.update_quantity(new_quantity)
            break

        if event in ["Cancel"]:
            break

    window.close()


def rename_window(item):
    """Window which allows user to change their selected item's name

    :param item: Item object which was selected via highlight/right click in the primary window
    :type item: Item_Class.Item
    """
    layout = [
        [sg.Text("Enter new name")],
        [sg.Input(key="-IN1-")],
        [sg.Button("Update"), sg.Button("Cancel")],
    ]

    window = sg.Window("Rename Item", layout, modal=True)

    while True:
        event, values = window.read()

        if event == "Update":
            item.rename(values["-IN1-"].lower())
            break

        if event == "Cancel":
            break

    window.close()


def exit_window():
    """Window for user to confirm termination of the program without completing list"""
    layout = [
        [sg.Text("This will clear your list, are you sure?")],
        [sg.Button("Yes, Exit"), sg.Button("Cancel")],
    ]

    window = sg.Window(
        "Exit Window",
        layout,
        modal=True,
    )

    while True:
        event, _ = window.read()

        if event in ["Cancel", sg.WIN_CLOSED]:
            window.close()
        else:
            sys.exit()


def send_email(number, carrier):
    """Formats message to be sent, opens smtp connection, and sends it.

    :param number: phone number
    :type number: str
    :param carrier: carrier name
    :type carrier: str
    """
    send_to = number + CARRIERS[carrier]
    grocery_items = [item.name + " " + item.quantity for item in ITEMS_LIST]
    grocery_list_final = "\n".join(grocery_items)

    with smtplib.SMTP(CONNECTION, port=PORT) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=send_to,
            msg=f"Subject:Grocery List! \n\n \nItems:\n{grocery_list_final}",
        )


if __name__ == "__main__":
    main()
