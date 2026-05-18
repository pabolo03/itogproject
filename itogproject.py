import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x500")

        # Файл для хранения избранных пользователей
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Верхняя панель: поле поиска
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill="x")

        tk.Label(top_frame, text="GitHub Username:").pack(side="left", padx=5)
        self.search_entry = tk.Entry(top_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(top_frame, text="Search", command=self.search_user).pack(side="left")

        # Основная область: отображение результатов
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10, fill="both", expand=True)

        # Список результатов
        self.results_listbox = tk.Listbox(main_frame, height=15, width=60)
        self.results_listbox.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.results_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_listbox.config(yscrollcommand=scrollbar.set)

        # Нижняя панель: кнопки управления
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10)

        tk.Button(bottom_frame, text="Add to Favorites", command=self.add_to_favorites).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Show Favoritesites", command=self.show_favorites).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Clear", command=self.clear_results).pack(side="left", padx=5)

        # Статус-бар
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

    def search_user(self):
        username = self.search_entry.get().strip()

        if not username:
            messagebox.showerror("Error", "Search field cannot be empty!")
            self.status_var.set("Error: Search field is empty")
            return

        try:
            response = requests.get(f"https://api.github.com/users/{username}")

            if response.status_code == 200:
                user_data = response.json()
                self.display_user_info(user_data)
                self.status_var.set(f"User '{username}' found successfully")
            else:
                messagebox.showerror("Error", f"User not found (HTTP {response.status_code})")
                self.status_var.set("User not found")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Network error: {e}")
            self.status_var.set("Network error")

    def display_user_info(self, user_data):
        self.results_listbox.delete(0, tk.END)
        fields = [
            f"Name: {user_data.get('name', 'N/A')}",
            f"Username: {user_data['login']}",
            f"Public Repos: {user_data['public_repos']}",
            f"Followers: {user_data['followers']}",
            f"Following: {user_data['following']}",
            f"Location: {user_data.get('location', 'N/A')}",
            f"Bio: {user_data.get('bio', 'N/A')}"
        ]
        for field in fields:
            self.results_listbox.insert(tk.END, field)

    def add_to_favorites(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a user from the results first!")
            return

        username_line = self.results_listbox.get(1)  # Вторая строка — username
        if username_line.startswith("Username: "):
            username = username_line.split(": ")[1]

            if username in self.favorites:
                messagebox.showinfo("Info", f"'{username}' is already in favorites!")
            else:
                self.favorites.append(username)
                self.save_favorites()
                messagebox.showinfo("Success", f"'{username}' added to favorites!")
                self.status_var.set(f"'{username}' added to favorites")

    def show_favorites(self):
        self.results_listbox.delete(0, tk.END)
        if self.favorites:
            for user in self.favorites:
                self.results_listbox.insert(tk.END, user)
        else:
            self.results_listbox.insert(tk.END, "No favorites yet.")

    def clear_results(self):
        self.results_listbox.delete(0, tk.END)
        self.status_var.set("Results cleared")

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_favorites(self):
        with open(self.favorites_file, 'w') as f:
            json.dump(self.favorites, f, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
