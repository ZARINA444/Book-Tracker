import json
import os
from tkinter import *
from tkinter import ttk, messagebox

DATA_FILE = "books.json"


class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("800x500")
        self.root.resizable(True, True)

        self.books = []  # список книг
        self.load_data()

        # Переменные для полей ввода
        self.title_var = StringVar()
        self.author_var = StringVar()
        self.genre_var = StringVar()
        self.pages_var = StringVar()

        # Переменные для фильтров
        self.filter_genre_var = StringVar()
        self.filter_pages_var = StringVar(value="all")  # all, more_200

        self.create_widgets()

    def create_widgets(self):
        # Панель ввода новой книги
        input_frame = LabelFrame(self.root, text="Добавить новую книгу", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        Label(input_frame, text="Название:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        Entry(input_frame, textvariable=self.title_var, width=30).grid(row=0, column=1, padx=5, pady=2)

        Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        Entry(input_frame, textvariable=self.author_var, width=25).grid(row=0, column=3, padx=5, pady=2)

        Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        Entry(input_frame, textvariable=self.genre_var, width=30).grid(row=1, column=1, padx=5, pady=2)

        Label(input_frame, text="Кол-во страниц:").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        Entry(input_frame, textvariable=self.pages_var, width=25).grid(row=1, column=3, padx=5, pady=2)

        Button(input_frame, text="Добавить книгу", command=self.add_book, bg="lightgreen").grid(row=2, column=0,
                                                                                                columnspan=4, pady=10)

        # Панель фильтрации
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5)
        Entry(filter_frame, textvariable=self.filter_genre_var, width=20).grid(row=0, column=1, padx=5)
        Button(filter_frame, text="Применить фильтр жанра", command=self.refresh_table).grid(row=0, column=2, padx=5)

        Label(filter_frame, text="Фильтр по страницам:").grid(row=0, column=3, padx=5)
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_pages_var, values=["all", "more_200"],
                                    state="readonly", width=10)
        filter_combo.grid(row=0, column=4, padx=5)
        Button(filter_frame, text="Применить фильтр страниц", command=self.refresh_table).grid(row=0, column=5, padx=5)

        Button(filter_frame, text="Сбросить все фильтры", command=self.reset_filters, bg="lightyellow").grid(row=0,
                                                                                                             column=6,
                                                                                                             padx=10)

        # Таблица с книгами
        table_frame = Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Название", "Автор", "Жанр", "Страниц")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        btn_frame = Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        Button(btn_frame, text="Сохранить в JSON", command=self.save_data, bg="lightblue").pack(side="left", padx=5)
        Button(btn_frame, text="Загрузить из JSON", command=self.load_data, bg="lightblue").pack(side="left", padx=5)
        Button(btn_frame, text="Удалить выбранную книгу", command=self.delete_book, bg="salmon").pack(side="left",
                                                                                                      padx=5)

        # Обновляем таблицу после создания всех виджетов
        self.refresh_table()

    def add_book(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        genre = self.genre_var.get().strip()
        pages_str = self.pages_var.get().strip()

        # Валидация
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        if not pages_str.isdigit():
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
            return

        pages = int(pages_str)

        new_book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(new_book)
        self.save_data()
        self.refresh_table()

        # Очистка полей
        self.title_var.set("")
        self.author_var.set("")
        self.genre_var.set("")
        self.pages_var.set("")

        messagebox.showinfo("Успех", f"Книга \"{title}\" добавлена!")

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления!")
            return

        # Получаем индекс выбранной книги
        for item in selected:
            item_text = self.tree.item(item, "values")
            # Ищем книгу в self.books по совпадению всех полей (простой способ)
            for i, book in enumerate(self.books):
                if (book["title"] == item_text[0] and book["author"] == item_text[1] and
                        book["genre"] == item_text[2] and str(book["pages"]) == item_text[3]):
                    del self.books[i]
                    break

        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Книга удалена!")

    def filter_books(self):
        filtered = self.books[:]

        # Фильтр по жанру
        genre_filter = self.filter_genre_var.get().strip().lower()
        if genre_filter:
            filtered = [b for b in filtered if genre_filter in b["genre"].lower()]

        # Фильтр по страницам
        pages_filter = self.filter_pages_var.get()
        if pages_filter == "more_200":
            filtered = [b for b in filtered if b["pages"] > 200]

        return filtered

    def refresh_table(self):
        # Проверяем, существует ли tree
        if not hasattr(self, 'tree'):
            return

        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered_books = self.filter_books()
        for book in filtered_books:
            self.tree.insert("", END, values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    def reset_filters(self):
        self.filter_genre_var.set("")
        self.filter_pages_var.set("all")
        self.refresh_table()

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
                messagebox.showinfo("Загрузка", f"Загружено {len(self.books)} книг")
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", str(e))
                self.books = []
        else:
            self.books = []

        if hasattr(self, 'tree'):
            self.refresh_table()


if __name__ == "__main__":
    root = Tk()
    app = BookTrackerApp(root)
    root.mainloop()