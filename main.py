import tkinter as tk
from login_window import LoginWindow
from gui import KiloWatchApp

def start_main_app(username):
    root = tk.Tk()
    app = KiloWatchApp(root, username=username)
    root.mainloop()
    # When mainloop exits (logout or close), re-show login
    LoginWindow(on_success=start_main_app)

LoginWindow(on_success=start_main_app)