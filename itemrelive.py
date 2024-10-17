class Item:
    def __init__(self, name, description, contact_info):
        self.name = name
        self.description = description
        self.contact_info = contact_info


class ItemManager:
    def __init__(self):
        self.items = {}

    def add_item(self, name, description, contact_info):
        if name in self.items:
            print(f"Item '{name}' already exists. Updating information.")
        self.items[name] = Item(name, description, contact_info)
        print(f"Item '{name}' added/updated successfully.")

    def delete_item(self, name):
        if name in self.items:
            del self.items[name]
            print(f"Item '{name}' deleted successfully.")
        else:
            print(f"Item '{name}' not found.")

    def display_items(self):
        if not self.items:
            print("No items found.")
        else:
            for name, item in self.items.items():
                print(f"Name: {item.name}, Description: {item.description}, Contact Info: {item.contact_info}")

    def find_item(self, name):
        item = self.items.get(name)
        if item:
            print(f"Found item: Name: {item.name}, Description: {item.description}, Contact Info: {item.contact_info}")
        else:
            print(f"Item '{name}' not found.")


def main():
    manager = ItemManager()

    while True:
        print("\nItem Manager")
        print("1. Add/Update Item")
        print("2. Delete Item")
        print("3. Display All Items")
        print("4. Find Item")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter item name: ")
            description = input("Enter item description: ")
            contact_info = input("Enter contact info: ")
            manager.add_item(name, description, contact_info)
        elif choice == '2':
            name = input("Enter item name to delete: ")
            manager.delete_item(name)
        elif choice == '3':
            manager.display_items()
        elif choice == '4':
            name = input("Enter item name to find: ")
            manager.find_item(name)
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()