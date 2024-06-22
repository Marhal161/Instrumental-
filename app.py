import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json

# Функции для работы с файлом

def load_data():
    try:
        with open("cinema_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "users": [],
            "movies": [
                {
                    "id": 1,
                    "title": "Фильм 1",
                    "description": "Описание фильма 1",
                    "poster": "poster1.jpg"
                },
                {
                    "id": 2,
                    "title": "Фильм 2",
                    "description": "Описание фильма 2",
                    "poster": "poster2.jpg"
                },
                {
                    "id": 3,
                    "title": "Фильм 3",
                    "description": "Описание фильма 3",
                    "poster": "poster3.jpg"
                }
            ],
            "showtimes": [
                {
                    "id": 1,
                    "movie_id": 1,
                    "datetime": "2023-12-25 19:00"
                },
                {
                    "id": 2,
                    "movie_id": 2,
                    "datetime": "2023-12-25 21:00"
                },
                {
                    "id": 3,
                    "movie_id": 3,
                    "datetime": "2023-12-26 18:00"
                }
            ],
            "tickets": []
        }

def save_data(data):
    with open("cinema_data.json", "w") as f:
        json.dump(data, f)

def register_user(data, username, password):
    if any(user["username"] == username for user in data["users"]):
        return False
    data["users"].append({"username": username, "password": password})
    save_data(data)
    return True

def authenticate_user(data, username, password):
    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            return True
    return False

def get_movies(data):
    return data["movies"]

def get_showtimes_for_movie(data, movie_id):
    return [showtime for showtime in data["showtimes"] if showtime["movie_id"] == movie_id]

def get_seats_for_showtime(data, showtime_id):
    return [ticket for ticket in data["tickets"] if ticket["showtime_id"] == showtime_id]

def book_ticket(data, user_id, showtime_id, seat_row, seat_col):
    if any(
        ticket["showtime_id"] == showtime_id
        and ticket["seat_row"] == seat_row
        and ticket["seat_col"] == seat_col
        for ticket in data["tickets"]
    ):
        return False
    data["tickets"].append(
        {"user_id": user_id, "showtime_id": showtime_id, "seat_row": seat_row, "seat_col": seat_col}
    )
    save_data(data)
    return True

def get_tickets_for_user(data, user_id):
    return [ticket for ticket in data["tickets"] if ticket["user_id"] == user_id]

def delete_ticket(data, ticket_id):
    data["tickets"] = [ticket for ticket in data["tickets"] if ticket["id"] != ticket_id]
    save_data(data)

# Графический интерфейс

class CinemaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Кинотеатр")

        # Загрузка данных из файла
        self.data = load_data()

        # Фрейм для регистрации/авторизации
        self.auth_frame = tk.Frame(self)
        self.auth_frame.pack()

        self.username_label = tk.Label(self.auth_frame, text="Имя пользователя:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.auth_frame)
        self.username_entry.pack()

        self.password_label = tk.Label(self.auth_frame, text="Пароль:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.auth_frame, show="*")
        self.password_entry.pack()

        self.register_button = tk.Button(self.auth_frame, text="Регистрация", command=self.register)
        self.register_button.pack()
        self.login_button = tk.Button(self.auth_frame, text="Вход", command=self.login)
        self.login_button.pack()

        # Фрейм для выбора фильма
        self.movie_frame = tk.Frame(self)
        self.movie_frame.pack(fill="both", expand=True)

        self.movie_listbox = tk.Listbox(self.movie_frame, width=40)
        self.movie_listbox.pack(side="left", fill="both", expand=True)

        self.movie_details_frame = tk.Frame(self.movie_frame)
        self.movie_details_frame.pack(side="right", fill="both")
        self.movie_title_label = tk.Label(self.movie_details_frame, text="")
        self.movie_title_label.pack()
        self.movie_description_label = tk.Label(self.movie_details_frame, text="")
        self.movie_description_label.pack()
        self.movie_poster_label = tk.Label(self.movie_details_frame, text="")
        self.movie_poster_label.pack()

        self.movie_listbox.bind("<<ListboxSelect>>", self.display_movie_details)

        # Фрейм для выбора сеанса
        self.showtime_frame = tk.Frame(self)
        self.showtime_frame.pack(fill="both", expand=True)

        self.showtime_listbox = tk.Listbox(self.showtime_frame, width=40)
        self.showtime_listbox.pack(side="left", fill="both", expand=True)

        self.seat_frame = tk.Frame(self.showtime_frame)
        self.seat_frame.pack(side="right", fill="both", expand=True)

        # Фрейм для просмотра билетов
        self.tickets_frame = tk.Frame(self)
        self.tickets_frame.pack(fill="both", expand=True)

        self.tickets_listbox = tk.Listbox(self.tickets_frame, width=40)
        self.tickets_listbox.pack(side="left", fill="both", expand=True)

        self.delete_ticket_button = tk.Button(self.tickets_frame, text="Удалить билет", command=self.delete_ticket)
        self.delete_ticket_button.pack(side="right")

        # Пользовательские атрибуты
        self.current_user = None

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if register_user(self.data, username, password):
            tk.messagebox.showinfo("Успех", "Вы успешно зарегистрированы!")
        else:
            tk.messagebox.showerror("Ошибка", "Имя пользователя уже существует!")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if authenticate_user(self.data, username, password):
            self.current_user = username
            self.auth_frame.pack_forget()
            self.update_movies()
        else:
            tk.messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def update_movies(self):
        self.movie_listbox.delete(0, tk.END)
        movies = get_movies(self.data)
        for movie in movies:
            self.movie_listbox.insert(tk.END, movie["title"])

    def display_movie_details(self, event):
        selection = self.movie_listbox.curselection()
        if selection:
            index = selection[0]
            movie_id = get_movies(self.data)[index]["id"]
            movie_title = get_movies(self.data)[index]["title"]
            movie_description = get_movies(self.data)[index]["description"]
            movie_poster = get_movies(self.data)[index]["poster"]  # Placeholder

            self.movie_title_label.config(text=movie_title)
            self.movie_description_label.config(text=movie_description)
            self.movie_poster_label.config(text=movie_poster)

            self.showtime_listbox.delete(0, tk.END)
            showtimes = get_showtimes_for_movie(self.data, movie_id)
            for showtime in showtimes:
                self.showtime_listbox.insert(tk.END, showtime["datetime"])
            self.showtime_listbox.bind("<<ListboxSelect>>", self.display_seats)

    def display_seats(self, event):
        selection = self.showtime_listbox.curselection()
        if selection:
            index = selection[0]
            showtime_id = get_showtimes_for_movie(self.data, get_movies(self.data)[self.movie_listbox.curselection()[0]]["id"])[index]["id"]

            for child in self.seat_frame.winfo_children():
                child.destroy()

            for row in range(10):
                for col in range(10):
                    button = tk.Button(self.seat_frame, text=f"{row+1}-{col+1}",
                                       command=lambda r=row, c=col: self.book_seat(showtime_id, r, c))
                    button.grid(row=row, column=col)

            booked_seats = get_seats_for_showtime(self.data, showtime_id)
            for seat in booked_seats:
                button = self.seat_frame.grid_slaves(row=seat["seat_row"]-1, column=seat["seat_col"]-1)[0]
                button.config(state="disabled", bg="red")

    def book_seat(self, showtime_id, row, col):
        user_id = self.data["users"][self.data["users"].index({"username": self.current_user})]["id"]
        if book_ticket(self.data, user_id, showtime_id, row+1, col+1):
            tk.messagebox.showinfo("Успех", "Билет успешно забронирован!")
            self.update_tickets()
        else:
            tk.messagebox.showerror("Ошибка", "Это место уже занято!")

    def update_tickets(self):
        self.tickets_listbox.delete(0, tk.END)
        tickets = get_tickets_for_user(self.data, self.data["users"][self.data["users"].index({"username": self.current_user})]["id"])
        for ticket in tickets:
            movie_title = get_movies(self.data)[get_showtimes_for_movie(self.data, ticket["showtime_id"])[0]["movie_id"]-1]["title"]
            self.tickets_listbox.insert(tk.END, f"{ticket['seat_row']}-{ticket['seat_col']} на {movie_title} в {get_showtimes_for_movie(self.data, ticket['showtime_id'])[0]['datetime']}")

    def delete_ticket(self):
        selection = self.tickets_listbox.curselection()
        if selection:
            index = selection[0]
            ticket_id = get_tickets_for_user(self.data, self.data["users"][self.data["users"].index({"username": self.current_user})]["id"])[index]["id"]
            delete_ticket(self.data, ticket_id)
            self.update_tickets()

if __name__ == "__main__":
    app = CinemaApp()
    app.mainloop()