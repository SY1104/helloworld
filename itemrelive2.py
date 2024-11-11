class Item:
    """
    表示一个物品，包含名称、描述和联系信息。
    """

    def __init__(self, name, description, contact_info):
        self.name = name
        self.description = description
        self.contact_info = contact_info

    def __repr__(self):
        """
        返回物品的字符串表示，便于打印。
        """
        return f"Item(Name: {self.name}, Description: {self.description}, Contact Info: {self.contact_info})"


class ItemManager:
    """
    管理物品信息的类，支持添加、删除、显示和查找物品。
    """

    def __init__(self):
        self.items = {}

    def add_or_update_item(self, name, description, contact_info):
        """
        添加或更新物品信息。如果物品已存在，则更新其信息。
        """
        if not name or not description or not contact_info:
            print("Error: All fields are required.")
            return

        if name in self.items:
            print(f"Item '{name}' already exists. Updating information.")
        self.items[name] = Item(name, description, contact_info)
        print(f"Item '{name}' added/updated successfully.")

    def delete_item(self, name):
        """
        删除指定名称的物品。如果物品不存在，则打印错误消息。
        """
        if name in self.items:
            del self.items[name]
            print(f"Item '{name}' deleted successfully.")
        else:
            print(f"Item '{name}' not found.")

    def display_items(self):
        """
        显示所有物品的信息。如果没有物品，则打印相应消息。
        """
        if not self.items:
            print("No items found.")
        else:
            for item in self.items.values():
                print(item)

    def find_item(self, name):
        """
        查找并显示指定名称的物品信息。如果物品不存在，则打印错误消息。
        """
        item = self.items.get(name)
        if item:
            print(item)
        else:
            print(f"Item '{name}' not found.")


def main():
    """
    主函数，提供用户与ItemManager交互的界面。
    """
    manager = ItemManager()

    while True:
        print("\nItem Manager Menu")
        print("1. Add/Update Item")
        print("2. Delete Item")
        print("3. Display All Items")
        print("4. Find Item")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            name = input("Enter item name: ").strip()
            description = input("Enter item description: ").strip()
            contact_info = input("Enter contact info: ").strip()
            manager.add_or_update_item(name, description, contact_info)
        elif choice == '2':
            name = input("Enter item name to delete: ").strip()
            manager.delete_item(name)
        elif choice == '3':
            manager.display_items()
        elif choice == '4':
            name = input("Enter item name to find: ").strip()
            manager.find_item(name)
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()