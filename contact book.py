import os

class ContactBook:
    CONTACTS_FILE = "contacts.txt"

    def __init__(self):
        self.contacts = self.load_contacts()

    def load_contacts(self):
        contacts = {}
        if os.path.exists(self.CONTACTS_FILE):
            with open(self.CONTACTS_FILE, "r") as file:
                for line in file:
                    if "," in line:
                        name, phone = line.strip().split(",", 1)
                        contacts[name.lower()] = (name, phone)
        return contacts

    def save_contacts(self):
        with open(self.CONTACTS_FILE, "w") as file:
            for _, (name, phone) in self.contacts.items():
                file.write(f"{name},{phone}\n")

    def is_valid_phone(self, phone):
        return phone.isdigit() and 7 <= len(phone) <= 15

    def add_contact(self):
        name = input("Enter contact name: ").strip()
        phone = input("Enter phone number: ").strip()

        if not name or not phone:
            print("❌ Name and phone number cannot be empty.")
            return

        if not self.is_valid_phone(phone):
            print("❌ Invalid phone number format.")
            return

        key = name.lower()
        if key in self.contacts:
            print(f"⚠️ Contact '{name}' already exists.")
        else:
            self.contacts[key] = (name, phone)
            print(f"✅ Contact '{name}' added successfully!")

    def search_contact(self):
        name = input("Enter name to search: ").strip().lower()
        contact = self.contacts.get(name)
        if contact:
            print(f"🔍 Found: {contact[0]} - {contact[1]}")
        else:
            print("❌ Contact not found.")

    def delete_contact(self):
        name = input("Enter name to delete: ").strip().lower()
        if name in self.contacts:
            confirm = input(f"Are you sure you want to delete '{self.contacts[name][0]}'? (y/n): ").lower()
            if confirm == 'y':
                del self.contacts[name]
                print(f"🗑️ '{name.capitalize()}' deleted successfully.")
            else:
                print("❎ Deletion cancelled.")
        else:
            print("❌ Contact not found.")

    def list_contacts(self):
        if not self.contacts:
            print("📭 Your contact list is empty.")
        else:
            print("\n📒 Your Contacts:")
            for _, (name, phone) in sorted(self.contacts.items()):
                print(f"• {name} - {phone}")

    def run(self):
        while True:
            print("\n===== 📞 Contact Book Menu =====")
            print("1. Add Contact")
            print("2. Search Contact")
            print("3. Delete Contact")
            print("4. List All Contacts")
            print("5. Exit")
            print("=================================")

            choice = input("Choose an option (1-5): ").strip()

            match choice:
                case "1": self.add_contact()
                case "2": self.search_contact()
                case "3": self.delete_contact()
                case "4": self.list_contacts()
                case "5":
                    self.save_contacts()
                    print("✅ Contacts saved. Goodbye!")
                    break
                case _: print("❌ Invalid option. Please choose between 1–5.")

if __name__ == "__main__":
    ContactBook().run()
# contact book.py
# A simple contact book application to manage contacts with add, search, delete, and list functionalities
