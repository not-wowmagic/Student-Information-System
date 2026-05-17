import os
import sys

import ttkbootstrap


# If this file is executed as a script (e.g., `python src/main.py`), Python adds
# `src/` (not the project root) to sys.path, so `import src...` fails.
if __package__ in (None, ""):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        if project_root not in sys.path:
                sys.path.insert(0, project_root)

from constants import CUSTOM_BACKGROUND_COLOR
from src.database.db_config import connect_db

def main() -> None:
        from ttkbootstrap import Window

        window = Window()
        import tkinter as tk
        window.withdraw()

        from src.frontend.login.login import open_login_window
        from src.frontend.student.dashboard import open_dashboard_window
        from frontend.admin.admin_dashboard import open_admin_dashboard


        # INITIALIZE DATABASE
        conn = connect_db()

        # custom colors don't touch - aizen
        window.style.configure('BG_FRAME.TFrame', background=CUSTOM_BACKGROUND_COLOR)
        window.style.configure('BG_BUTTON.TButton', anchor="w", font=("Segoi UI", 10), padding=15, borderwidth=0, background=CUSTOM_BACKGROUND_COLOR)
        window.style.configure('BG_BUTTON_DANGER.TButton', foreground="#ff2414", anchor="w", font=("Segoi UI", 10), padding=15, borderwidth=0, background=CUSTOM_BACKGROUND_COLOR)
        window.style.configure("BG_CHECKBOX.TCheckbutton", background=CUSTOM_BACKGROUND_COLOR)
        window.style.configure("BG_ENTRY.TEntry", background=CUSTOM_BACKGROUND_COLOR)
        window.style.configure("BG_LABEL.TLabel", background=CUSTOM_BACKGROUND_COLOR, foreground="white")
        window.style.configure("White.TFrame", background="white")


        def on_logout(win):
                open_login_window(win, conn, on_login_success=on_login_success)

        def on_login_success(login_win: ttkbootstrap.Window, role: str | None, user_id: str | int | None = None) -> None:
                if not role:
                        print("[LOGIN SERVICE]: Please input a role!")
                        return

                login_win.withdraw()

                if role == "admin":
                        open_admin_dashboard(window, conn, on_logout=on_logout)
                else:
                        open_dashboard_window(window, conn, on_logout=on_logout, student_id=user_id)


        open_login_window(window, conn, on_login_success=on_login_success)

        window.mainloop()

if __name__ == "__main__":
        main()
