import tkinter as tk
from database.crud.students import get_student_subjects

NAV_BG        = "#001f5b"
WHITE         = "#ffffff"
TEXT_PRIMARY  = "#111827"
TEXT_MUTED    = "#6b7280"
CARD_BORDER   = "#e2e8f0"

def build_subjects_tab(parent, switch_cb, conn, student_id=None):
    # Main container
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    # --- TOP ROW ---
    top_row = tk.Frame(container, bg=WHITE)
    top_row.pack(fill="x", pady=(48, 32), padx=48)
    
    tk.Label(top_row, text="Enrolled Subjects", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left")
    
    def show_notification(e=None):
        notif = tk.Frame(container, bg=NAV_BG, highlightthickness=0)
        notif.place(relx=1.0, rely=0.0, x=-32, y=32, anchor="ne")
        tk.Label(notif, text="✓ Schedule exported as PDF", font=("Segoe UI", 10, "bold"), fg=WHITE, bg=NAV_BG, padx=16, pady=12).pack()
        container.after(3000, notif.destroy)

    btn_export = tk.Button(top_row, text="📅 Export Schedule", font=("Segoe UI", 9, "bold"), fg=NAV_BG, bg=WHITE, relief="solid", bd=1, padx=16, pady=4, cursor="hand2", command=show_notification)
    btn_export.pack(side="right")

    # --- GRID OF CARDS ---
    grid_container = tk.Frame(container, bg=WHITE)
    grid_container.pack(fill="both", expand=True, padx=48)
    
    subjects_data = get_student_subjects(conn, student_id) if student_id else []

    for i in range(3):
        grid_container.columnconfigure(i, weight=1, uniform="col")
        
    if not subjects_data:
        tk.Label(grid_container, text="No enrolled subjects found.", font=("Segoe UI", 12), fg=TEXT_MUTED, bg=WHITE).grid(row=0, column=0, sticky="w", pady=24)

    for i, data in enumerate(subjects_data):
        row = i // 3
        col = i % 3
        card_outer = tk.Frame(grid_container, bg=NAV_BG) # Top blue border effect
        card_outer.grid(row=row, column=col, sticky="nsew", padx=(0 if col==0 else 12, 12 if col!=2 else 0), pady=(0 if row == 0 else 16, 0))
        
        # Thick blue border at top
        tk.Frame(card_outer, bg=NAV_BG, height=6).pack(fill="x")
        
        card_body = tk.Frame(card_outer, bg=WHITE, highlightthickness=1, highlightbackground=CARD_BORDER)
        card_body.pack(fill="both", expand=True)
        
        # --- Card Content ---
        content = tk.Frame(card_body, bg=WHITE)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        title_text = data[4]
        code_text = data[5]
        teacher_text = data[6]
        units_text = data[7]
        day_text = data[8]
        start_text = data[9]
        end_text = data[10]
        
        # Tags row
        tags_row = tk.Frame(content, bg=WHITE)
        tags_row.pack(fill="x", pady=(0, 16))
        
        # Code pill
        tk.Label(tags_row, text=code_text, font=("Segoe UI", 8, "bold"), fg="#1e3a8a", bg="#f1f5f9", padx=8, pady=4).pack(side="left")
        
        # Status pill
        status_f = tk.Frame(tags_row, bg="#f0fdf4")
        status_f.pack(side="right")
        tk.Label(status_f, text="●", font=("Segoe UI", 8), fg="#22c55e", bg=status_f["bg"], padx=4).pack(side="left")
        tk.Label(status_f, text="Enrolled", font=("Segoe UI", 8, "bold"), fg="#166534", bg=status_f["bg"], padx=4, pady=4).pack(side="left")

        # Title
        title_f = tk.Frame(content, bg=WHITE, height=54)
        title_f.pack(fill="x", pady=(0, 16))
        title_f.pack_propagate(False)
        tk.Label(title_f, text=title_text, font=("Segoe UI", 12, "bold"), fg="#1e3a8a", bg=WHITE, justify="left", wraplength=220).pack(anchor="w")
        
        # Professor
        prof_f = tk.Frame(content, bg=WHITE)
        prof_f.pack(fill="x", pady=(0, 12))
        tk.Label(prof_f, text="👤", font=("Segoe UI Emoji", 8), fg=TEXT_MUTED, bg=WHITE).pack(side="left", padx=(0, 4))
        tk.Label(prof_f, text=teacher_text, font=("Segoe UI", 9), fg=TEXT_MUTED, bg=WHITE).pack(side="left")
        
        # Divider
        tk.Frame(content, bg=CARD_BORDER, height=1).pack(fill="x", pady=(0, 16))
        
        # Schedule Info
        info_f = tk.Frame(content, bg=WHITE)
        info_f.pack(fill="x", pady=(0, 16))
        
        time_f = tk.Frame(info_f, bg=WHITE)
        time_f.pack(side="left", fill="both", expand=True)
        tk.Label(time_f, text="🕒", font=("Segoe UI Emoji", 9), fg=TEXT_MUTED, bg=WHITE).pack(side="left", anchor="n", padx=(0, 6))
        time_txt_f = tk.Frame(time_f, bg=WHITE)
        time_txt_f.pack(side="left")
        tk.Label(time_txt_f, text=day_text, font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="w")
        tk.Label(time_txt_f, text=f"{start_text} - {end_text}", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=WHITE).pack(anchor="w")
        
        loc_f = tk.Frame(info_f, bg=WHITE)
        loc_f.pack(side="left", fill="both", expand=True)
        tk.Label(loc_f, text="🏢", font=("Segoe UI Emoji", 9), fg=TEXT_MUTED, bg=WHITE).pack(side="left", anchor="n", padx=(0, 6))
        loc_txt_f = tk.Frame(loc_f, bg=WHITE)
        loc_txt_f.pack(side="left")
        tk.Label(loc_txt_f, text=f"Year {data[11]}", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="w")
        tk.Label(loc_txt_f, text=f"Units: {units_text}", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=WHITE).pack(anchor="w")
        
        # Footer
        footer_f = tk.Frame(content, bg=WHITE)
        footer_f.pack(fill="x", side="bottom")
        tk.Label(footer_f, text=f"{units_text} credits", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=WHITE).pack(side="left")
        tk.Label(footer_f, text="View Syllabus ➔", font=("Segoe UI", 8, "bold"), fg="#1e3a8a", bg=WHITE, cursor="hand2").pack(side="right")
