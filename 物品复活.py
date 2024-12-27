import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import json


# 初始化数据库
def init_db():
    conn = sqlite3.connect('revival_system.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            address TEXT,
            contact TEXT,
            email TEXT,
            approved INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS item_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT UNIQUE,
            attributes TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_id INTEGER,
            name TEXT,
            description TEXT,
            contact_info TEXT,
            address TEXT,
            email TEXT,
            attributes TEXT,
            owner TEXT,
            FOREIGN KEY(type_id) REFERENCES item_types(id)
        )
    ''')
    conn.commit()
    conn.close()


# 管理员界面
class AdminPanel(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("管理员面板")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        tk.Button(self, text="添加物品类型", command=self.add_item_type).pack(pady=10)
        tk.Button(self, text="修改或删除物品类型", command=self.modify_item_type).pack(pady=10)
        tk.Button(self, text="批准或拒绝用户", command=self.approve_or_reject_user).pack(pady=10)

    def add_item_type(self):
        type_name = simpledialog.askstring("输入", "输入物品类型名称：")
        attributes = simpledialog.askstring("输入", "输入物品类型属性（用逗号分隔）：")
        if type_name and attributes:
            conn = sqlite3.connect('revival_system.db')
            c = conn.cursor()
            c.execute('SELECT * FROM item_types WHERE type_name = ?', (type_name,))
            if c.fetchone():
                messagebox.showerror("错误", "物品类型已存在")
            else:
                c.execute('INSERT INTO item_types (type_name, attributes) VALUES (?, ?)', (type_name, attributes))
                conn.commit()
                messagebox.showinfo("成功", "物品类型添加成功")
            conn.close()

    def modify_item_type(self):
        self.modify_window = tk.Toplevel(self)
        self.modify_window.title("修改或删除物品类型")
        self.modify_window.geometry("500x400")

        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('SELECT id, type_name, attributes FROM item_types')
        types = c.fetchall()
        conn.close()

        if not types:
            messagebox.showinfo("信息", "没有可修改的物品类型")
            self.modify_window.destroy()
            return

        self.type_list = ttk.Treeview(self.modify_window, columns=("ID", "Type Name", "Attributes"), show="headings")
        self.type_list.heading("ID", text="类型 ID")
        self.type_list.heading("Type Name", text="类型名称")
        self.type_list.heading("Attributes", text="属性")
        self.type_list.pack(fill=tk.BOTH, expand=True)

        for item_type in types:
            self.type_list.insert("", "end", values=item_type)

        modify_button = tk.Button(self.modify_window, text="修改选定类型", command=self.modify_selected_type)
        modify_button.pack(pady=10)

        delete_button = tk.Button(self.modify_window, text="删除选定类型", command=self.delete_selected_type)
        delete_button.pack(pady=10)

    def modify_selected_type(self):
        selected_item = self.type_list.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个物品类型")
            return

        type_id, current_name, current_attributes = self.type_list.item(selected_item, "values")
        new_name = simpledialog.askstring("修改名称", "输入新的类型名称：", initialvalue=current_name)
        new_attributes = simpledialog.askstring("修改属性", "输入新的属性（用逗号分隔）：",
                                                initialvalue=current_attributes)

        if new_name and new_attributes:
            conn = sqlite3.connect('revival_system.db')
            c = conn.cursor()
            try:
                c.execute('UPDATE item_types SET type_name = ?, attributes = ? WHERE id = ?',
                          (new_name, new_attributes, type_id))
                conn.commit()
                messagebox.showinfo("成功", "物品类型已修改")
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "类型名称已存在")
            conn.close()
            self.modify_window.destroy()

    def delete_selected_type(self):
        selected_item = self.type_list.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个物品类型")
            return

        type_id = self.type_list.item(selected_item, "values")[0]

        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        try:
            c.execute('DELETE FROM item_types WHERE id = ?', (type_id,))
            conn.commit()
            messagebox.showinfo("成功", "物品类型已删除")
            self.type_list.delete(selected_item)
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "无法删除物品类型，因为它可能正在使用中")
        conn.close()

    def approve_or_reject_user(self):
        self.approval_window = tk.Toplevel(self)
        self.approval_window.title("批准或拒绝用户")
        self.approval_window.geometry("700x300")

        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('SELECT id, username, address, contact, email FROM users WHERE approved = 0')
        users = c.fetchall()
        conn.close()

        if not users:
            messagebox.showinfo("信息", "没有待批准的用户")
            self.approval_window.destroy()
            return

        self.user_list = ttk.Treeview(self.approval_window, columns=("ID", "Username", "Address", "Contact", "Email"),
                                      show="headings")
        self.user_list.heading("ID", text="用户 ID")
        self.user_list.heading("Username", text="用户名")
        self.user_list.heading("Address", text="地址")
        self.user_list.heading("Contact", text="联系方式")
        self.user_list.heading("Email", text="邮箱")
        self.user_list.pack(fill=tk.BOTH, expand=True)

        for user in users:
            self.user_list.insert("", "end", values=user)

        approve_button = tk.Button(self.approval_window, text="批准选定用户", command=self.approve_selected_user)
        approve_button.pack(side=tk.LEFT, padx=5, pady=10)

        reject_button = tk.Button(self.approval_window, text="拒绝选定用户", command=self.reject_selected_user)
        reject_button.pack(side=tk.RIGHT, padx=5, pady=10)

    def approve_selected_user(self):
        selected_item = self.user_list.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个用户")
            return

        user_id = self.user_list.item(selected_item, "values")[0]
        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('UPDATE users SET approved = 1 WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("成功", "用户已批准")
        self.user_list.delete(selected_item)

    def reject_selected_user(self):
        selected_item = self.user_list.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个用户")
            return

        user_id = self.user_list.item(selected_item, "values")[0]
        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("成功", "用户注册申请已拒绝")
        self.user_list.delete(selected_item)


# 普通用户界面
class UserPanel(tk.Toplevel):
    def __init__(self, master=None, username=None):
        super().__init__(master)
        self.title(f"用户面板 - {username}")
        self.geometry("400x400")
        self.username = username
        self.contact_info, self.user_email = self.get_user_contact_info_and_email(username)
        self.create_widgets()

    def create_widgets(self):
        tk.Button(self, text="添加物品", command=self.add_item).pack(pady=10)
        tk.Button(self, text="显示或删除物品", command=self.show_items).pack(pady=10)
        tk.Button(self, text="查找物品", command=self.search_item).pack(pady=10)

    def get_user_contact_info_and_email(self, username):
        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('SELECT contact, email FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()
        return (result[0], result[1]) if result else ("", "")

    def add_item(self):
        self.add_item_window = tk.Toplevel(self)
        self.add_item_window.title("添加物品")
        self.add_item_window.geometry("400x600")

        # 获取物品类型
        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('SELECT id, type_name, attributes FROM item_types')
        self.types = c.fetchall()
        conn.close()

        if not self.types:
            messagebox.showinfo("信息", "没有可用的物品类型")
            self.add_item_window.destroy()
            return

        tk.Label(self.add_item_window, text="选择物品类型：").pack(pady=5)
        self.type_var = tk.StringVar()
        self.type_menu = ttk.Combobox(self.add_item_window, textvariable=self.type_var)
        self.type_menu['values'] = [f"{t[1]} (属性: {t[2]})" for t in self.types]
        self.type_menu.pack(pady=5)
        self.type_menu.bind("<<ComboboxSelected>>", self.display_attributes)

        tk.Label(self.add_item_window, text="物品名称：").pack(pady=5)
        self.item_name = tk.Entry(self.add_item_window)
        self.item_name.pack(pady=5)

        tk.Label(self.add_item_window, text="物品描述：").pack(pady=5)
        self.item_description = tk.Entry(self.add_item_window)
        self.item_description.pack(pady=5)

        tk.Label(self.add_item_window, text="物品地址：").pack(pady=5)
        self.item_address = tk.Entry(self.add_item_window)
        self.item_address.pack(pady=5)

        tk.Label(self.add_item_window, text="联系人信息：").pack(pady=5)
        self.contact_info_entry = tk.Entry(self.add_item_window)
        self.contact_info_entry.pack(pady=5)
        self.contact_info_entry.insert(0, self.contact_info)  # 预填入用户注册的联系方式

        tk.Label(self.add_item_window, text="联系人邮箱：").pack(pady=5)
        self.contact_email_entry = tk.Entry(self.add_item_window)
        self.contact_email_entry.pack(pady=5)
        self.contact_email_entry.insert(0, self.user_email)  # 预填入用户注册的邮箱

        self.attribute_entries = {}

        submit_button = tk.Button(self.add_item_window, text="添加物品", command=self.submit_item)
        submit_button.pack(pady=10)

    def display_attributes(self, event):
        # 清除先前的属性输入框
        for label in self.attribute_entries.values():
            label[0].destroy()
            label[1].destroy()
        self.attribute_entries.clear()

        selected_index = self.type_menu.current()
        if selected_index == -1:
            return

        attributes = self.types[selected_index][2].split(',')
        for attribute in attributes:
            label = tk.Label(self.add_item_window, text=f"{attribute.strip()}：")
            label.pack(pady=5)
            entry = tk.Entry(self.add_item_window)
            entry.pack(pady=5)
            self.attribute_entries[attribute.strip()] = (label, entry)

    def submit_item(self):
        type_selection = self.type_menu.get()
        if not type_selection:
            messagebox.showwarning("警告", "请选择物品类型")
            return

        item_name = self.item_name.get()
        item_description = self.item_description.get()
        contact_info = self.contact_info_entry.get()
        item_address = self.item_address.get()
        contact_email = self.contact_email_entry.get()

        if not item_name or not item_description or not contact_info or not item_address or not contact_email:
            messagebox.showwarning("警告", "请填写所有信息")
            return

        # 获取所选类型的 ID
        selected_index = self.type_menu.current()
        type_id = self.types[selected_index][0]

        # 获取所有属性信息
        attributes_info = {attr: entry[1].get() for attr, entry in self.attribute_entries.items()}

        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO items (type_id, name, description, contact_info, address, email, attributes, owner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
        type_id, item_name, item_description, contact_info, item_address, contact_email, json.dumps(attributes_info),
        self.username))
        conn.commit()
        conn.close()
        messagebox.showinfo("成功", "物品已添加")
        self.add_item_window.destroy()

    def show_items(self):
        self.show_items_window = tk.Toplevel(self)
        self.show_items_window.title("物品列表")
        self.show_items_window.geometry("900x400")

        self.item_list = ttk.Treeview(self.show_items_window, columns=(
        "Type", "Name", "Description", "Address", "Contact", "Email", "Attributes"), show="headings")
        self.item_list.heading("Type", text="物品类型")
        self.item_list.heading("Name", text="物品名称")
        self.item_list.heading("Description", text="物品描述")
        self.item_list.heading("Address", text="物品地址")
        self.item_list.heading("Contact", text="联系人信息")
        self.item_list.heading("Email", text="联系人邮箱")
        self.item_list.heading("Attributes", text="属性")
        self.item_list.pack(fill=tk.BOTH, expand=True)

        delete_button = tk.Button(self.show_items_window, text="删除选定物品", command=self.delete_selected_item)
        delete_button.pack(pady=5)

        modify_button = tk.Button(self.show_items_window, text="修改选定物品", command=self.modify_selected_item)
        modify_button.pack(pady=5)

        self.load_items()

    def load_items(self):
        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('''
            SELECT item_types.type_name, items.name, items.description, items.address, items.contact_info, items.email, items.attributes 
            FROM items 
            JOIN item_types ON items.type_id = item_types.id 
            WHERE items.owner = ?
        ''', (self.username,))
        items = c.fetchall()
        conn.close()

        # 清除先前的列表内容
        for item in self.item_list.get_children():
            self.item_list.delete(item)

        for item in items:
            # 将属性信息从 JSON 格式转换为可读格式
            attributes_info = json.loads(item[6])
            readable_attributes = ', '.join([f"{k}: {v}" for k, v in attributes_info.items()])
            self.item_list.insert("", "end",
                                  values=(item[0], item[1], item[2], item[3], item[4], item[5], readable_attributes))

    def delete_selected_item(self):
        selected_item = self.item_list.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个物品")
            return

        item_values = self.item_list.item(selected_item, "values")
        item_name = item_values[1]

        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('DELETE FROM items WHERE name = ? AND owner = ?', (item_name, self.username))
        conn.commit()
        conn.close()
        self.item_list.delete(selected_item)
        messagebox.showinfo("成功", "物品已删除")

    def modify_selected_item(self):
        selected_item = self.item_list.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个物品")
            return

        item_values = self.item_list.item(selected_item, "values")
        item_type = item_values[0]
        item_name = item_values[1]

        self.modify_item_window = tk.Toplevel(self)
        self.modify_item_window.title("修改物品信息")
        self.modify_item_window.geometry("400x600")

        tk.Label(self.modify_item_window, text="物品类型：").pack(pady=5)
        item_type_entry = tk.Entry(self.modify_item_window)
        item_type_entry.pack(pady=5)
        item_type_entry.insert(0, item_type)
        item_type_entry.config(state='readonly')  # 不允许修改物品类型

        tk.Label(self.modify_item_window, text="物品名称：").pack(pady=5)
        item_name_entry = tk.Entry(self.modify_item_window)
        item_name_entry.pack(pady=5)
        item_name_entry.insert(0, item_values[1])

        tk.Label(self.modify_item_window, text="物品描述：").pack(pady=5)
        item_description_entry = tk.Entry(self.modify_item_window)
        item_description_entry.pack(pady=5)
        item_description_entry.insert(0, item_values[2])

        tk.Label(self.modify_item_window, text="物品地址：").pack(pady=5)
        item_address_entry = tk.Entry(self.modify_item_window)
        item_address_entry.pack(pady=5)
        item_address_entry.insert(0, item_values[3])

        tk.Label(self.modify_item_window, text="联系人信息：").pack(pady=5)
        contact_info_entry = tk.Entry(self.modify_item_window)
        contact_info_entry.pack(pady=5)
        contact_info_entry.insert(0, item_values[4])

        tk.Label(self.modify_item_window, text="联系人邮箱：").pack(pady=5)
        contact_email_entry = tk.Entry(self.modify_item_window)
        contact_email_entry.pack(pady=5)
        contact_email_entry.insert(0, item_values[5])

        # 解析和显示属性信息
        attributes_info = json.loads(item_values[6])
        attribute_entries = {attr: tk.Entry(self.modify_item_window) for attr in attributes_info}
        for attr, entry in attribute_entries.items():
            tk.Label(self.modify_item_window, text=f"{attr}：").pack(pady=5)
            entry.pack(pady=5)
            entry.insert(0, attributes_info[attr])

        def update_item():
            new_name = item_name_entry.get()
            new_description = item_description_entry.get()
            new_address = item_address_entry.get()
            new_contact_info = contact_info_entry.get()
            new_email = contact_email_entry.get()
            new_attributes = {attr: entry.get() for attr, entry in attribute_entries.items()}

            if not new_name or not new_description or not new_contact_info or not new_address or not new_email:
                messagebox.showwarning("警告", "请填写所有信息")
                return

            conn = sqlite3.connect('revival_system.db')
            c = conn.cursor()
            c.execute('''
                UPDATE items SET name = ?, description = ?, address = ?, contact_info = ?, email = ?, attributes = ?
                WHERE name = ? AND owner = ?
            ''', (
            new_name, new_description, new_address, new_contact_info, new_email, json.dumps(new_attributes), item_name,
            self.username))
            conn.commit()
            conn.close()
            messagebox.showinfo("成功", "物品已更新")
            self.load_items()
            self.modify_item_window.destroy()

        submit_button = tk.Button(self.modify_item_window, text="更新物品", command=update_item)
        submit_button.pack(pady=10)

    def search_item(self):
        self.search_item_window = tk.Toplevel(self)
        self.search_item_window.title("查找物品")
        self.search_item_window.geometry("500x400")

        # 获取物品类型
        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('SELECT id, type_name FROM item_types')
        self.types = c.fetchall()
        conn.close()

        if not self.types:
            messagebox.showinfo("信息", "没有可用的物品类型")
            self.search_item_window.destroy()
            return

        tk.Label(self.search_item_window, text="选择物品类型：").pack(pady=5)
        self.search_type_var = tk.StringVar()
        self.search_type_menu = ttk.Combobox(self.search_item_window, textvariable=self.search_type_var)
        self.search_type_menu['values'] = [t[1] for t in self.types]
        self.search_type_menu.pack(pady=5)

        tk.Label(self.search_item_window, text="输入关键字：").pack(pady=5)
        self.keyword_entry = tk.Entry(self.search_item_window)
        self.keyword_entry.pack(pady=5)

        search_button = tk.Button(self.search_item_window, text="搜索", command=self.perform_search)
        search_button.pack(pady=10)

        self.result_list = ttk.Treeview(self.search_item_window,
                                        columns=("Name", "Description", "Contact", "Address", "Email"), show="headings")
        self.result_list.heading("Name", text="物品名称")
        self.result_list.heading("Description", text="物品描述")
        self.result_list.heading("Contact", text="联系人信息")
        self.result_list.heading("Address", text="物品地址")
        self.result_list.heading("Email", text="联系人邮箱")
        self.result_list.pack(fill=tk.BOTH, expand=True)

    def perform_search(self):
        type_selection = self.search_type_menu.get()
        keyword = self.keyword_entry.get().strip()

        if not type_selection or not keyword:
            messagebox.showwarning("警告", "请选择物品类型并输入关键字")
            return

        # 获取所选类型的 ID
        selected_index = self.search_type_menu.current()
        type_id = self.types[selected_index][0]

        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('''
            SELECT name, description, contact_info, address, email FROM items
            WHERE type_id = ? AND (name LIKE ? OR description LIKE ?)
        ''', (type_id, f'%{keyword}%', f'%{keyword}%'))
        results = c.fetchall()
        conn.close()

        # 清除先前的搜索结果
        for item in self.result_list.get_children():
            self.result_list.delete(item)

        for result in results:
            self.result_list.insert("", "end", values=result)


# 主界面
class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("物品复活系统")
        self.geometry("300x250")
        self.create_widgets()

    def create_widgets(self):
        tk.Button(self, text="管理员登录", command=self.admin_login).pack(pady=10)
        tk.Button(self, text="用户注册", command=self.user_register).pack(pady=10)
        tk.Button(self, text="用户登录", command=self.user_login).pack(pady=10)

    def admin_login(self):
        username = simpledialog.askstring("管理员登录", "输入管理员用户名：")
        password = simpledialog.askstring("管理员登录", "输入密码：", show='*')

        # 验证管理员身份
        if username == "sy" and password == "123":
            AdminPanel(self)
        else:
            messagebox.showerror("错误", "管理员用户名或密码不正确")

    def user_register(self):
        username = simpledialog.askstring("注册", "输入用户名：")
        address = simpledialog.askstring("注册", "输入地址：")
        contact = simpledialog.askstring("注册", "输入联系方式：")
        email = simpledialog.askstring("注册", "输入邮箱：")
        if username and address and contact and email:
            conn = sqlite3.connect('revival_system.db')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users (username, address, contact, email) VALUES (?, ?, ?, ?)',
                          (username, address, contact, email))
                conn.commit()
                messagebox.showinfo("成功", "注册成功，等待管理员批准")
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "用户名已存在")
            conn.close()

    def user_login(self):
        username = simpledialog.askstring("登录", "输入用户名：")
        if not username:
            return

        conn = sqlite3.connect('revival_system.db')
        c = conn.cursor()
        c.execute('SELECT approved FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()

        if result is None:
            messagebox.showerror("错误", "用户不存在")
        elif result[0] == 0:
            messagebox.showerror("错误", "用户尚未获得批准")
        else:
            UserPanel(self, username)


if __name__ == "__main__":
    init_db()
    app = MainApplication()
    app.mainloop()