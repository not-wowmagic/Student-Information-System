import tkinter as tk
from database.crud.students import get_student_gwa, get_student_subjects

NAV_BG        = "#001f5b"
WHITE         = "#ffffff"
TEXT_PRIMARY  = "#111827"
TEXT_MUTED    = "#6b7280"
CARD_BORDER   = "#e2e8f0"


def build_grades_tab(parent, switch_cb, conn, student_id=None):
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    subject_rows = get_student_subjects(conn, student_id) if student_id else []
    gwa = get_student_gwa(conn, student_id) if student_id else None
    total_credits = sum(float(row[7]) for row in subject_rows) if subject_rows else 0

    top_row = tk.Frame(container, bg=WHITE)
    top_row.pack(fill="x", pady=(48, 24), padx=48)

    left_card_outer = tk.Frame(top_row, bg=CARD_BORDER)
    left_card_outer.pack(side="left", fill="both", expand=True, padx=(0, 16))
    left_card = tk.Frame(left_card_outer, bg="#f8fafc")
    left_card.pack(padx=1, pady=1, fill="both", expand=True)
    left_inner = tk.Frame(left_card, bg="#f8fafc")
    left_inner.pack(padx=24, pady=24, fill="both", expand=True)

    tk.Label(left_inner, text="CUMULATIVE GRADE", font=("Segoe UI", 12), fg="#1e3a8a", bg="#f8fafc").pack(anchor="w")
    grade_f = tk.Frame(left_inner, bg="#f8fafc")
    grade_f.pack(anchor="w", pady=(12, 16))
    tk.Label(grade_f, text=f"{gwa:.2f}" if gwa is not None else "N/A", font=("Segoe UI", 48), fg=TEXT_PRIMARY, bg="#f8fafc").pack(side="left")
    slash_f = tk.Frame(grade_f, bg="#f8fafc")
    slash_f.pack(side="left", fill="y")
    tk.Label(slash_f, text=" / 5.00", font=("Segoe UI", 16), fg=TEXT_PRIMARY, bg="#f8fafc").pack(side="bottom", pady=(0, 10))

    badge_f = tk.Frame(left_inner, bg="#f8fafc")
    badge_f.pack(anchor="w", side="bottom")
    tk.Label(badge_f, text="GWA", font=("Segoe UI", 8, "bold"), fg="#1e3a8a", bg="#dbeafe", padx=6, pady=2).pack(side="left")
    tk.Label(badge_f, text="Computed from enrolled subjects", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg="#f8fafc").pack(side="left", padx=(8, 0))

    right_card_outer = tk.Frame(top_row, bg=CARD_BORDER)
    right_card_outer.pack(side="left", fill="both", expand=True)
    right_card = tk.Frame(right_card_outer, bg="#1e3a8a")
    right_card.pack(padx=1, pady=1, fill="both", expand=True)
    right_inner = tk.Frame(right_card, bg="#1e3a8a")
    right_inner.pack(padx=24, pady=24, fill="both", expand=True)

    tk.Label(right_inner, text="TOTAL EARNED CREDITS", font=("Segoe UI", 10, "bold"), fg="#93c5fd", bg="#1e3a8a").pack(anchor="w")
    tk.Label(right_inner, text=str(int(total_credits)), font=("Segoe UI", 48, "bold"), fg=WHITE, bg="#1e3a8a").pack(anchor="w", pady=(4, 16))
    prog_bg = tk.Frame(right_inner, bg="#3b82f6", height=6)
    prog_bg.pack(fill="x", pady=(0, 8))
    prog_bg.pack_propagate(False)
    tk.Frame(prog_bg, bg="#bfdbfe", width=250).pack(side="left", fill="y")
    tk.Label(right_inner, text="Seeded transcript data", font=("Segoe UI", 10), fg="#bfdbfe", bg="#1e3a8a").pack(anchor="e")

    tk.Label(container, text="Current Semester Transcript", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="w", pady=(16, 16), padx=48)

    table_outer = tk.Frame(container, bg=CARD_BORDER)
    table_outer.pack(fill="both", expand=True, padx=48)
    table_bg = tk.Frame(table_outer, bg=WHITE)
    table_bg.pack(padx=1, pady=1, fill="both", expand=True)

    header = tk.Frame(table_bg, bg="#002d72", height=40)
    header.pack(fill="x")
    header.pack_propagate(False)
    for col in range(4):
        header.columnconfigure(col, weight=1 if col == 1 else 0, minsize=150 if col != 1 else 0)
    tk.Label(header, text="Course Code", font=("Segoe UI", 10), fg=WHITE, bg="#002d72").grid(row=0, column=0, sticky="w", padx=24, pady=10)
    tk.Label(header, text="Course Title", font=("Segoe UI", 10), fg=WHITE, bg="#002d72").grid(row=0, column=1, sticky="w", pady=10)
    tk.Label(header, text="Units", font=("Segoe UI", 10), fg=WHITE, bg="#002d72").grid(row=0, column=2, sticky="e", padx=(0, 48), pady=10)
    tk.Label(header, text="Grades", font=("Segoe UI", 10), fg=WHITE, bg="#002d72").grid(row=0, column=3, sticky="w", padx=24, pady=10)

    if not subject_rows:
        tk.Label(table_bg, text="No grades available.", font=("Segoe UI", 10), fg=TEXT_MUTED, bg=WHITE).pack(anchor="w", padx=24, pady=24)

    for i, subject in enumerate(subject_rows):
        code = subject[5]
        title = subject[4]
        units = subject[7]
        grade = subject[3] if subject[3] is not None else "N/A"
        bg_col = "#dcfce7" if subject[3] is not None and float(subject[3]) <= 3.0 else "#fef3c7"
        fg_col = "#166534" if subject[3] is not None and float(subject[3]) <= 3.0 else "#854d0e"

        row_bg = WHITE if i % 2 == 0 else "#f8fafc"
        row_f = tk.Frame(table_bg, bg=row_bg, height=60)
        row_f.pack(fill="x")
        row_f.pack_propagate(False)
        for col in range(4):
            row_f.columnconfigure(col, weight=1 if col == 1 else 0, minsize=150 if col != 1 else 0)

        tk.Label(row_f, text=code, font=("Segoe UI", 10, "bold"), fg="#1e3a8a", bg=row_bg).grid(row=0, column=0, sticky="w", padx=24, pady=20)
        tk.Label(row_f, text=title, font=("Segoe UI", 10, "bold"), fg="#4b5563", bg=row_bg).grid(row=0, column=1, sticky="w", pady=20)
        tk.Label(row_f, text=units, font=("Segoe UI", 10), fg="#4b5563", bg=row_bg).grid(row=0, column=2, sticky="e", padx=(0, 48), pady=20)

        badge_wrap = tk.Frame(row_f, bg=row_bg)
        badge_wrap.grid(row=0, column=3, sticky="w", padx=24, pady=20)
        tk.Label(badge_wrap, text=grade, font=("Segoe UI", 10, "bold"), fg=fg_col, bg=bg_col, width=4).pack()

    footer = tk.Frame(container, bg=WHITE)
    footer.pack(fill="x", pady=(16, 32), padx=48)

    def show_notification(e=None):
        notif = tk.Frame(container, bg=NAV_BG, highlightthickness=0)
        notif.place(relx=1.0, rely=0.0, x=-32, y=32, anchor="ne")
        tk.Label(notif, text="✓ Transcript downloaded", font=("Segoe UI", 10, "bold"), fg=WHITE, bg=NAV_BG, padx=16, pady=12).pack()
        container.after(3000, notif.destroy)

    btn_download = tk.Button(footer, text="📥 Download Unofficial Transcript", font=("Segoe UI", 9, "bold"), fg=NAV_BG, bg=WHITE, relief="solid", bd=1, padx=16, pady=6, cursor="hand2", command=show_notification)
    btn_download.pack(side="right")
