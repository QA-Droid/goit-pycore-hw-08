from collections import UserDict
from datetime import datetime
import pickle

class Field:
    """Record fields to address book"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """Class to record name for address book"""
    def __init__(self, name: str):
        super().__init__(name)

class Phone(Field):
    """Class for address book record name field"""
    def __init__(self, phone: str):
        self.value = self.__validate_phone(phone)

    def __validate_phone(self, phone: str) -> str:
        """Phone validation"""
        if len(phone) != 10:
            raise ValueError("The phone number must contain 10 digits")

        if not phone.isdigit():
            raise ValueError("The phone number must contain only numbers")

        return phone

class Birthday(Field):
    """Class for address book record birthday field"""
    def __init__(self, birthday: str):
        self.value = self.__validate_birthday(birthday)

    def __validate_birthday(self, birthday: str) -> datetime:
        """Birthday validation and conversion to datetime"""
        try:
            return datetime.strptime(birthday, "%d.%m.%Y").date()
        except ValueError as e:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from e

class Record:
    """Class for address book to add, remove, edit and find phone number and birthday"""
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        """Method to add a phone number"""
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def remove_phone(self, phone: str):
        """Method to remove a phone number"""
        phone_obj = self.find_phone(phone)
        self.phones.remove(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str):
        """Method to edit a phone number"""
        old_phone_obj = self.find_phone(old_phone)
        new_phone_obj = Phone(new_phone)
        index = self.phones.index(old_phone_obj)
        self.phones[index] = new_phone_obj

    def find_phone(self, phone: str) -> Phone:
        """Method to find a phone number"""
        for p in self.phones:
            if p.value == phone:
                return p
        raise ValueError("Phone number not found.")

    def add_birthday(self, birthday: str):
        """Method to add a birthday"""
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        """Method to calculate days to next birthday"""
        if not self.birthday:
            return None
        today = datetime.now().date()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

class AddressBook(UserDict):
    """Class for address book"""
    def add_record(self, record: Record):
        """Method to add a record"""
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        """Method to find a record"""
        return self.data.get(name)

    def delete(self, name: str):
        """Method to delete a record"""
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found.")

    def get_upcoming_birthdays(self, days: int = 7):
        """Method to get upcoming birthdays"""
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                days_to_birthday = record.days_to_birthday()
                if days_to_birthday is not None and days_to_birthday <= days:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return inner

@input_error
def add_contact(args, book: AddressBook):
    """Function to add a new contact or update an existing contact's phone number"""
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    """Function to change an existing contact's phone number"""
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."

@input_error
def show_phone(args, book: AddressBook):
    """Function to show a contact's phone numbers"""
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    phones = '; '.join(phone.value for phone in record.phones)
    return f"{name}'s phone numbers: {phones}"

def show_all_contacts(book: AddressBook):
    """Function to show all contacts in the address book"""
    if not book.data:
        return "Address book is empty."
    result = "All contacts:\n"
    for record in book.data.values():
        result += f"{record}\n"
    return result

@input_error
def add_birthday(args, book):
    """Function to add a birthday to a contact"""
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    """Function to show a contact's birthday"""
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if not record.birthday:
        return "No birthday set for this contact."
    return f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book):
    """Function to show upcoming birthdays in the next week"""
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next week."
    result = "Upcoming birthdays:\n"
    for record in upcoming_birthdays:
        result += f"{record.name.value}: {record.birthday.value.strftime('%d.%m.%Y')}\n"
    return result

def parse_input(user_input):
    """Function to parse user input into command and arguments"""
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def save_data(book, filename="addressbook.pkl"):
    """Function to save address book data to a file."""
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    """Function to load address book data from a file."""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    """Main function to run the assistant bot"""
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()