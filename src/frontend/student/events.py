import tkinter as tk
from datetime import datetime
from database.crud.events import get_events
from database.db_utils import find_by_column

NAV_BG        = "#001f5b"
WHITE         = "#ffffff"
TEXT_PRIMARY  = "#111827"
TEXT_MUTED    = "#6b7280"
CARD_BORDER   = "#e2e8f0"

def build_events_tab(parent, switch_cb, conn, student_id=None):
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    # Header
    top_row = tk.Frame(container, bg=WHITE)
    top_row.pack(fill="x", pady=(48, 32), padx=48)
    tk.Label(top_row, text="Campus Events", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left")

    def show_notification(e=None):
        notif = tk.Frame(container, bg="#10b981", highlightthickness=0)
        notif.place(relx=1.0, rely=0.0, x=-32, y=32, anchor="ne")
        tk.Label(notif, text="✓ Suggestion portal opened", font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#10b981", padx=16, pady=12).pack()
        container.after(3000, notif.destroy)

    btn_suggest = tk.Button(top_row, text="➕ Suggest Event", font=("Segoe UI", 9, "bold"), fg=WHITE, bg=NAV_BG, relief="flat", padx=16, pady=6, cursor="hand2", command=show_notification)
    btn_suggest.pack(side="right")

    # Grid Container
    grid_container = tk.Frame(container, bg=WHITE)
    grid_container.pack(fill="both", expand=True, padx=48)

    events_data = get_events(conn)

    for i in range(3):
        grid_container.columnconfigure(i, weight=1, uniform="col")

    def show_rsvp(e=None):
        notif = tk.Frame(container, bg="#10b981", highlightthickness=0)
        notif.place(relx=1.0, rely=0.0, x=-32, y=32, anchor="ne")
        tk.Label(notif, text="✓ Successfully RSVP'd for event", font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#10b981", padx=16, pady=12).pack()
        container.after(3000, notif.destroy)

    if not events_data:
        tk.Label(grid_container, text="No events available.", font=("Segoe UI", 12), fg=TEXT_MUTED, bg=WHITE).grid(row=0, column=0, sticky="w", pady=24)

    for i, data in enumerate(events_data):
        row = i // 3
        col = i % 3
        card = tk.Frame(grid_container, bg=WHITE, highlightthickness=1, highlightbackground=CARD_BORDER)
        card.grid(row=row, column=col, sticky="nsew", padx=(0 if col==0 else 12, 12 if col!=2 else 0), pady=(0 if row == 0 else 16, 0))
        
        # Date block
        title = data[1]
        event_type = data[2]
        event_date = data[3]
        start_time = data[4] if data[4] else "—"
        end_time = data[5] if data[5] else "—"
        location = data[6] if data[6] else "—"
        dept_id = data[7]
        dept_data = find_by_column(conn, "DEPARTMENT", "id", dept_id) if dept_id else None
        dept_name = dept_data[1] if dept_data else "All Departments"
        if isinstance(event_date, str):
            try:
                parsed_date = datetime.strptime(event_date, "%Y-%m-%d")
                day = str(parsed_date.day)
                month = parsed_date.strftime("%b").upper()
            except ValueError:
                day = event_date
                month = ""
        else:
            day = str(event_date)
            month = ""

        date_f = tk.Frame(card, bg=NAV_BG)
        date_f.pack(fill="x")
        date_inner = tk.Frame(date_f, bg=NAV_BG, pady=16)
        date_inner.pack()
        tk.Label(date_inner, text=month, font=("Segoe UI", 10, "bold"), fg=WHITE, bg=NAV_BG).pack()
        tk.Label(date_inner, text=day, font=("Segoe UI", 28, "bold"), fg=WHITE, bg=NAV_BG).pack()

        # Content block
        content = tk.Frame(card, bg=WHITE)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(content, text=event_type, font=("Segoe UI", 8, "bold"), fg=NAV_BG, bg=WHITE).pack(anchor="w", pady=(0, 8))
        
        title_f = tk.Frame(content, bg=WHITE, height=48)
        title_f.pack(fill="x", pady=(0, 16))
        title_f.pack_propagate(False)
        tk.Label(title_f, text=title, font=("Segoe UI", 12, "bold"), fg=TEXT_PRIMARY, bg=WHITE, wraplength=200, justify="left").pack(anchor="w")

        tk.Label(content, text=f"🕒 {start_time} - {end_time}", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=WHITE).pack(anchor="w", pady=(0, 4))
        tk.Label(content, text=f"📍 {location}", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=WHITE).pack(anchor="w")
        tk.Label(content, text=dept_name, font=("Segoe UI", 8), fg=TEXT_MUTED, bg=WHITE).pack(anchor="w", pady=(4, 0))

        # RSVP button
        btn_rsvp = tk.Button(content, text="RSVP Now", font=("Segoe UI", 9, "bold"), fg=NAV_BG, bg=WHITE, relief="solid", bd=1, pady=6, cursor="hand2", command=show_rsvp)
        btn_rsvp.pack(fill="x", side="bottom", pady=(24,0))
