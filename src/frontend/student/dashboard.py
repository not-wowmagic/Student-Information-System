import os
import tkinter as tk
from tkinter import ttk as tkttk
from PIL import Image, ImageTk

from constants import CUSTOM_BACKGROUND_COLOR
from icon_utils import apply_window_icon
from database.crud.announcement import get_announcements
from database.crud.events import get_events
from database.crud.students import get_student_gwa, get_student_subjects, search_student
from database.db_utils import find_by_column
from src.frontend.student.grade import build_grades_tab
from src.frontend.student.subjects import build_subjects_tab
from src.frontend.student.announcements import build_announcements_tab
from src.frontend.student.events import build_events_tab
from src.frontend.student.settings import build_settings_tab

# ── TKINTER OVERRIDES TO FIX TTKBOOTSTRAP STYLING INTERFERENCE ──────────────
original_frame = tk.Frame
class ThemedFrame(original_frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "bg" in kwargs: self._my_bg = kwargs["bg"]
        if "background" in kwargs: self._my_bg = kwargs["background"]

original_label = tk.Label
class ThemedLabel(original_label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "bg" in kwargs: self._my_bg = kwargs["bg"]
        if "background" in kwargs: self._my_bg = kwargs["background"]
        if "fg" in kwargs: self._my_fg = kwargs["fg"]
        if "foreground" in kwargs: self._my_fg = kwargs["foreground"]

tk.Frame = ThemedFrame
tk.Label = ThemedLabel

# ── Colour tokens (from Figma design) ─────────────────────────────────────────
NAV_BG        = "#001f5b"   # deep navy sidebar / topbar
NAV_HOVER     = "#1a3a7a"   # hover state
WHITE         = "#ffffff"
CONTENT_BG    = "#edf0f5"   # light blue-grey page background
TEXT_PRIMARY  = "#111827"
TEXT_MUTED    = "#6b7280"
TEXT_NAV      = "#ffffff"
ACCENT_GREEN  = "#22c55e"
ACCENT_RED    = "#ef4444"
SEPARATOR     = "#e5e7eb"
CARD_BG       = "#ffffff"
CARD_BORDER   = "#e2e8f0"

DASHBOARD_VERSION = "v6-student-figma"

nav_btns = {}

# ── Helper: nav button ─────────────────────────────────────────────────────────
def _make_nav_btn(parent, text, icon, command=None):
    f = tk.Frame(parent, bg=NAV_BG, cursor="hand2", highlightthickness=0, bd=0)
    f.pack(fill="x", pady=0)
    inner = tk.Frame(f, bg=NAV_BG, highlightthickness=0, bd=0)
    inner.pack(fill="x", padx=8, pady=6)
    
    if not hasattr(f, "_image_refs"):
        f._image_refs = []
        
    icon_lbl = tk.Label(inner, text=icon, font=("Segoe UI", 16),
                        fg=WHITE, bg=NAV_BG)
    icon_lbl.pack(side="left", padx=(8, 14))
    text_lbl = tk.Label(inner, text=text, font=("Segoe UI", 13),
                        fg=WHITE, bg=NAV_BG, anchor="w")
    text_lbl.pack(side="left", fill="x")

    all_w = [f, inner, icon_lbl, text_lbl]
    nav_btns[text] = all_w

    def _enter(e):
        for w in all_w: 
            if getattr(w, '_is_active', False) == False:
                w.config(bg=NAV_HOVER)

    def _leave(e):
        for w in all_w: 
            if getattr(w, '_is_active', False) == False:
                w.config(bg=NAV_BG)

    for w in all_w:
        w.bind("<Enter>", _enter)
        w.bind("<Leave>", _leave)
        if command:
            w.bind("<Button-1>", lambda e, cmd=command: cmd())
    return f, icon_lbl

def _set_active_nav(text):
    for name, widgets in nav_btns.items():
        is_active = (name == text)
        bg_col = NAV_HOVER if is_active else NAV_BG
        for w in widgets:
            w._is_active = is_active
            w.config(bg=bg_col)

def _section_label(parent, text):
    tk.Label(parent, text=text, font=("Segoe UI", 8, "bold"),
             fg="#7a9cc7", bg=NAV_BG, anchor="w",
             padx=22).pack(fill="x", pady=(16, 2))


def build_dashboard_tab(parent, switch_cb, conn, student_id=None):
    student = search_student(conn, student_id) if student_id else None
    student_name = student[1] if student else "Student"
    course_name = "Unknown"
    year_level = "-"
    account_status = "-"
    gwa_value = "N/A"
    credits_value = 0

    subjects = get_student_subjects(conn, student_id) if student_id else []
    gwa = get_student_gwa(conn, student_id) if student_id else None
    if gwa is not None:
        gwa_value = f"{gwa:.2f}"
    credits_value = sum(int(row[7]) for row in subjects) if subjects else 0

    if student:
        course_data = find_by_column(conn, "COURSES", "course_id", student[2])
        course_name = course_data[1] if course_data else "Unknown"
        year_level = student[3]
        account_status = student[7]

    banner_outer = tk.Frame(parent, bg=CARD_BORDER)
    banner_outer.pack(fill="x", padx=24, pady=(24, 16))
    banner = tk.Frame(banner_outer, bg=NAV_BG)
    banner.pack(padx=1, pady=1, fill="both", expand=True)

    banner_pad = tk.Frame(banner, bg=NAV_BG)
    banner_pad.pack(fill="x", padx=32, pady=30)

    avatar_bg = tk.Frame(banner_pad, bg=WHITE, width=100, height=100)
    avatar_bg.pack(side="left", padx=(0, 24))
    avatar_bg.pack_propagate(False)
    avatar_inner = tk.Frame(avatar_bg, bg="#a0aab8", width=90, height=90)
    avatar_inner.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(avatar_inner, text="👤", font=("Segoe UI Emoji", 48), fg=WHITE, bg="#a0aab8").place(relx=0.5, rely=0.5, anchor="center")

    text_f = tk.Frame(banner_pad, bg=NAV_BG)
    text_f.pack(side="left", fill="y", pady=6)
    tk.Label(text_f, text=student_name, font=("Segoe UI", 24, "bold"), fg=WHITE, bg=NAV_BG).pack(anchor="w")
    tk.Label(text_f, text=f"{course_name} | Year {year_level}", font=("Segoe UI", 12), fg=WHITE, bg=NAV_BG).pack(anchor="w", pady=(4, 0))
    tk.Label(text_f, text=f"Status: {account_status}", font=("Segoe UI", 10), fg="#aab4c8", bg=NAV_BG).pack(anchor="w", pady=(4, 0))

    cols = tk.Frame(parent, bg=CONTENT_BG)
    cols.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    left_col = tk.Frame(cols, bg=CARD_BORDER, width=420)
    left_col.pack(side="left", fill="y", padx=(0, 16))
    left_col.pack_propagate(False)

    left_inner = tk.Frame(left_col, bg=CARD_BG)
    left_inner.pack(padx=1, pady=1, fill="both", expand=True)

    tk.Label(left_inner, text="Today's Schedule", font=("Segoe UI", 12, "bold"), fg=NAV_BG, bg=CARD_BG).pack(anchor="w", padx=24, pady=(24, 12))
    if subjects:
        for index, subj in enumerate(subjects[:4]):
            item = tk.Frame(left_inner, bg=CARD_BG)
            item.pack(fill="x", padx=24, pady=(0, 14))
            dot = tk.Frame(item, bg=NAV_BG if index == 0 else "#cbd5e1", width=10, height=10)
            dot.pack(side="left", pady=4)
            dot.pack_propagate(False)
            content = tk.Frame(item, bg=CARD_BG)
            content.pack(side="left", fill="x", expand=True, padx=(12, 0))
            tk.Label(content, text=subj[5], font=("Segoe UI", 10, "bold"), fg=TEXT_PRIMARY, bg=CARD_BG).pack(anchor="w")
            tk.Label(content, text=f"{subj[8]} • {subj[9]} - {subj[10]}", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=CARD_BG).pack(anchor="w")
    else:
        tk.Label(left_inner, text="No enrolled subjects found.", font=("Segoe UI", 10), fg=TEXT_MUTED, bg=CARD_BG).pack(anchor="w", padx=24, pady=(0, 24))

    right_col = tk.Frame(cols, bg=CONTENT_BG)
    right_col.pack(side="left", fill="both", expand=True)

    quotes_outer = tk.Frame(right_col, bg=CARD_BORDER)
    quotes_outer.pack(fill="x", pady=(0, 16))
    quotes = tk.Frame(quotes_outer, bg=NAV_BG)
    quotes.pack(padx=1, pady=1, fill="both", expand=True)
    tk.Label(quotes, text="Academic Snapshot", font=("Segoe UI", 14), fg=WHITE, bg=NAV_BG).pack(anchor="w", padx=24, pady=(24, 8))
    tk.Label(quotes, text=f"GWA: {gwa_value}", font=("Segoe UI", 22, "bold"), fg=WHITE, bg=NAV_BG).pack(anchor="w", padx=24)
    tk.Label(quotes, text=f"Total credits earned: {credits_value}", font=("Segoe UI", 10), fg="#aab4c8", bg=NAV_BG).pack(anchor="w", padx=24, pady=(0, 24))

    row2 = tk.Frame(right_col, bg=CONTENT_BG)
    row2.pack(fill="x", pady=(0, 16))

    def _navy_stat(parent, icon, title, val):
        outer = tk.Frame(parent, bg=CARD_BORDER)
        outer.pack(side="left", fill="both", expand=True, padx=(0, 16))
        c = tk.Frame(outer, bg=NAV_BG)
        c.pack(padx=1, pady=1, fill="both", expand=True)
        c_in = tk.Frame(c, bg=NAV_BG)
        c_in.pack(expand=True, padx=24, pady=24)
        tk.Label(c_in, text=icon, font=("Segoe UI", 32), fg=WHITE, bg=NAV_BG).pack(side="left", padx=(0, 18))
        r = tk.Frame(c_in, bg=NAV_BG)
        r.pack(side="left")
        tk.Label(r, text=title, font=("Segoe UI", 11), fg="#aab4c8", bg=NAV_BG).pack(anchor="w")
        tk.Label(r, text=val, font=("Segoe UI", 18, "bold"), fg=WHITE, bg=NAV_BG).pack(anchor="w")

    _navy_stat(row2, "★", "Grade", gwa_value)
    _navy_stat(row2, "👤", "Attendance", "Active")

    row3 = tk.Frame(right_col, bg=CONTENT_BG)
    row3.pack(fill="x")
    _navy_stat(row3, "≡", "Credits Earned", str(credits_value))



# ── Main entry ─────────────────────────────────────────────────────────────────
def open_dashboard_window(window, conn, on_logout=None, student_id=None):
    win = tk.Toplevel(window)
    win.title(f"Student Dashboard — EDU SIS")
    
    # Make it wide and dynamically as tall as the screen allows without capping
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    width = 1440
    height = min(1000, screen_height - 80)
    
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    
    # Prevent negative coordinates if screen is smaller than window
    x = max(0, x)
    y = max(0, y)
    
    win.geometry(f"{width}x{height}+{x}+{y}")
    win.minsize(1100, 720)
    win.configure(bg=NAV_BG)

    apply_window_icon(win, calling_file=__file__)

    win.columnconfigure(0, weight=0, minsize=260)
    win.columnconfigure(1, weight=1)
    win.rowconfigure(0, weight=1)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    SIDEBAR_W = 260
    sidebar_container = tk.Frame(win, bg=NAV_BG, width=SIDEBAR_W)
    sidebar_container.grid(row=0, column=0, sticky="nsew")
    sidebar_container.grid_propagate(False)

    # Logout (bottom) - PINNED TO BOTTOM OF CONTAINER
    bottom = tk.Frame(sidebar_container, bg=NAV_BG, highlightthickness=0, bd=0)
    bottom.pack(side="bottom", fill="x", padx=4, pady=8)

    sidebar_scrollbar = tkttk.Scrollbar(sidebar_container, orient="vertical")
    sidebar_scrollbar.pack(side="right", fill="y")

    sidebar_canvas = tk.Canvas(sidebar_container, bg=NAV_BG,
                               highlightthickness=0, borderwidth=0, bd=0, yscrollcommand=sidebar_scrollbar.set)
    sidebar_canvas.pack(side="left", fill="both", expand=True)
    sidebar_scrollbar.configure(command=sidebar_canvas.yview)

    sidebar = tk.Frame(sidebar_canvas, bg=NAV_BG, highlightthickness=0, bd=0)
    _sb_win = sidebar_canvas.create_window(0, 0, anchor="nw",
                                           window=sidebar)

    def _resize_sb(e):
        sidebar_canvas.itemconfig(_sb_win, width=e.width)
        sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
        sidebar_canvas.delete("bg_rect")
        sidebar_canvas.create_rectangle(0, 0, e.width, max(e.height, sidebar.winfo_reqheight()), fill=NAV_BG, outline="", tags="bg_rect")
        sidebar_canvas.tag_lower("bg_rect")

    sidebar_canvas.bind("<Configure>", _resize_sb)
    sidebar.bind("<Configure>", lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))

    def _on_mousewheel(event):
        if sidebar.winfo_reqheight() > sidebar_canvas.winfo_height():
            if hasattr(event, 'delta') and event.delta:
                sidebar_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif event.num == 4: sidebar_canvas.yview_scroll(-1, "units")
            elif event.num == 5: sidebar_canvas.yview_scroll(1, "units")

    sidebar_container.bind("<Enter>", lambda e: sidebar_container.bind_all("<MouseWheel>", _on_mousewheel) or sidebar_container.bind_all("<Button-4>", _on_mousewheel) or sidebar_container.bind_all("<Button-5>", _on_mousewheel))
    sidebar_container.bind("<Leave>", lambda e: sidebar_container.unbind_all("<MouseWheel>") or sidebar_container.unbind_all("<Button-4>") or sidebar_container.unbind_all("<Button-5>"))

    # Logo row
    logo_row = tk.Frame(sidebar, bg=NAV_BG, highlightthickness=0, bd=0)
    logo_row.pack(fill="x", padx=18, pady=(16, 8))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir  = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "assets"))

    lbl_logo = tk.Label(logo_row, bg=NAV_BG)
    lbl_logo.pack(side="left", padx=(0, 12))
    
    try:
        from PIL import Image, ImageTk
        path = os.path.join(assets_dir, "edu-icon.png")
        if os.path.exists(path):
            img = Image.open(path).resize((42, 42), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl_logo.config(image=photo)
            lbl_logo.image = photo
        else:
            lbl_logo.config(text="🎓", font=("Segoe UI Emoji", 28), fg=WHITE)
    except Exception:
        lbl_logo.config(text="🎓", font=("Segoe UI Emoji", 28), fg=WHITE)

    text_col = tk.Frame(logo_row, bg=NAV_BG, highlightthickness=0, bd=0)
    text_col.pack(side="left")
    tk.Label(text_col, text="ENCHONG DEE\nUNIVERSITY",
             font=("Segoe UI", 13, "bold"), fg=WHITE, bg=NAV_BG,
             justify="left", anchor="w").pack(anchor="w")
    tk.Label(text_col, text="STUDENT INFORMATION SYSTEM",
             font=("Segoe UI", 7), fg="#8fa8cc", bg=NAV_BG,
             justify="left", anchor="w").pack(anchor="w")

    # Divider
    tk.Frame(sidebar, bg="#1e3d7a", height=1,
             highlightthickness=0, bd=0).pack(fill="x", padx=14, pady=(4, 8))

    # Nav buttons
    nav = tk.Frame(sidebar, bg=NAV_BG)
    nav.pack(fill="x", padx=4)

    current_tab_frame = None

    def switch_tab(tab_name):
        nonlocal current_tab_frame
        if current_tab_frame:
            current_tab_frame.destroy()
        
        main_frame = tk.Frame(content_wrap, bg=CONTENT_BG)
        main_frame.grid(row=0, column=0, sticky="nsew")
        current_tab_frame = main_frame

        _set_active_nav(tab_name)

        if tab_name == "Dashboard":
            title_lbl.config(text="Dashboard")
            build_dashboard_tab(main_frame, switch_tab, conn, student_id)
        elif tab_name == "Grades":
            title_lbl.config(text="Grades")
            build_grades_tab(main_frame, switch_tab, conn, student_id)
        elif tab_name == "Subjects":
            title_lbl.config(text="Enrolled Subjects")
            build_subjects_tab(main_frame, switch_tab, conn, student_id)
        elif tab_name == "Announcements":
            title_lbl.config(text="Announcements")
            build_announcements_tab(main_frame, switch_tab, conn, student_id)
        elif tab_name == "Events":
            title_lbl.config(text="Events")
            build_events_tab(main_frame, switch_tab, conn, student_id)
        elif tab_name == "Settings":
            title_lbl.config(text="Settings")
            build_settings_tab(main_frame, switch_tab)
        else:
            title_lbl.config(text=tab_name)
            tk.Label(main_frame, text=f"{tab_name}\n(Under Construction)", font=("Segoe UI", 20), fg=TEXT_MUTED, bg=CONTENT_BG, justify="center").pack(expand=True)
            
        win.after(50, lambda: _force_bg(main_frame))

    btn_dashboard, lbl_dash   = _make_nav_btn(nav, "Dashboard", "⊞", command=lambda: switch_tab("Dashboard"))
    
    _section_label(nav, "ACADEMICS")
    btn_grades, lbl_grades     = _make_nav_btn(nav, "Grades", "🗂️", command=lambda: switch_tab("Grades"))
    btn_subjects, lbl_subjects = _make_nav_btn(nav, "Subjects", "📚", command=lambda: switch_tab("Subjects"))
    
    _section_label(nav, "CAMPUS LIFE")
    btn_ann, lbl_ann           = _make_nav_btn(nav, "Announcements", "🔊", command=lambda: switch_tab("Announcements"))
    btn_events, lbl_events     = _make_nav_btn(nav, "Events", "🎉", command=lambda: switch_tab("Events"))
    
    _section_label(nav, "SYSTEM")
    btn_settings, lbl_set      = _make_nav_btn(nav, "Settings", "⚙", command=lambda: switch_tab("Settings"))

    # Helper to load an icon safely
    def _apply_nav_icon(btn, lbl, filename, size=(20, 20)):
        try:
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                img = Image.open(path).resize(size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl.configure(image=photo, text="")
                lbl.image = photo
                btn._image_refs.append(photo)
        except Exception as e:
            print(f"Failed to load icon {filename}: {e}")

    # Load image icons into nav buttons
    _apply_nav_icon(btn_dashboard, lbl_dash, "dashboard-50.png", (22, 22))
    _apply_nav_icon(btn_grades, lbl_grades, "rating-64.png", (22, 22))
    _apply_nav_icon(btn_subjects, lbl_subjects, "elective-50.png", (22, 22))
    _apply_nav_icon(btn_ann, lbl_ann, "announcement-64.png", (22, 22))
    _apply_nav_icon(btn_events, lbl_events, "events-64.png", (22, 22))
    _apply_nav_icon(btn_settings, lbl_set, "settings-24.png", (22, 22))


    # Logout (bottom) is already packed above in sidebar_container
    tk.Frame(bottom, bg="#1e3d7a", height=1,
             highlightthickness=0, bd=0).pack(fill="x", padx=14, pady=(0, 6))

    logout_f = tk.Frame(bottom, bg=NAV_BG, cursor="hand2",
                        highlightthickness=0, bd=0)
    logout_f.pack(fill="x")
    lo_inner = tk.Frame(logout_f, bg=NAV_BG, highlightthickness=0, bd=0)
    lo_inner.pack(fill="x", padx=10, pady=6)
    
    logout_f._image_refs = []

    lbl_lo_icon = tk.Label(lo_inner, text="◼", font=("Segoe UI", 16),
                           fg=ACCENT_RED, bg=NAV_BG)
    lbl_lo_icon.pack(side="left", padx=(8, 14))
    lbl_lo_text = tk.Label(lo_inner, text="Logout", font=("Segoe UI", 13),
                           fg=ACCENT_RED, bg=NAV_BG, anchor="w")
    lbl_lo_text.pack(side="left")
    
    _apply_nav_icon(logout_f, lbl_lo_icon, "log-out-64.png", (22, 22))

    def do_logout():
        win.destroy()
        if on_logout:
            on_logout(window)

    for w in (logout_f, lo_inner, lbl_lo_icon, lbl_lo_text):
        w.bind("<Button-1>", lambda e: do_logout())

    # ── RIGHT SIDE (topbar + content) ─────────────────────────────────────────
    right_side = tk.Frame(win, bg=NAV_BG, highlightthickness=0, bd=0)
    right_side.grid(row=0, column=1, sticky="nsew")
    right_side.rowconfigure(1, weight=1)
    right_side.columnconfigure(0, weight=1)

    # ── TOP BAR (dark navy, same as sidebar) ──────────────────────────────────
    topbar = tk.Frame(right_side, bg=NAV_BG, height=60,
                      highlightthickness=0, bd=0)
    topbar.grid(row=0, column=0, sticky="ew")
    topbar.grid_propagate(False)

    tb_inner = tk.Frame(topbar, bg=NAV_BG, highlightthickness=0, bd=0)
    tb_inner.pack(fill="both", expand=True, padx=20)

    # Left: "Dashboard" title + divider + search
    left_top = tk.Frame(tb_inner, bg=NAV_BG)
    left_top.pack(side="left", fill="y")

    title_lbl = tk.Label(left_top, text="Dashboard", font=("Segoe UI", 12, "bold"),
             fg=WHITE, bg=NAV_BG)
    title_lbl.pack(side="left", padx=(0, 16), pady=0)
    # bind vertical centering
    left_top.pack_configure(pady=0)



    # Right: Student User pill button
    right_top = tk.Frame(tb_inner, bg=NAV_BG)
    right_top.pack(side="right", fill="y")

    user_pill = tk.Frame(right_top, bg=NAV_BG,
                          highlightthickness=1,
                          highlightbackground="#4a6fa5",
                          highlightcolor="#4a6fa5", bd=0,
                          cursor="hand2")
    user_pill.pack(side="right", pady=15)

    # Small avatar circle (simulated with a colored label)
    avatar_f = tk.Frame(user_pill, bg="#2d4d8a",
                        width=26, height=26,
                        highlightthickness=0, bd=0)
    avatar_f.pack(side="left", padx=(8, 6), pady=6)
    avatar_f.pack_propagate(False)
    tk.Label(avatar_f, text="🎓", font=("Segoe UI Emoji", 12),
             fg=WHITE, bg="#2d4d8a").place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(user_pill, text="", font=("Segoe UI", 10),
             fg=WHITE, bg=NAV_BG).pack(side="left", padx=(0, 12), pady=6)

    # ── CONTENT AREA (light grey page) ────────────────────────────────────────
    content_wrap = tk.Frame(right_side, bg=CONTENT_BG,
                            highlightthickness=0, bd=0)
    content_wrap.grid(row=1, column=0, sticky="nsew")
    content_wrap.rowconfigure(0, weight=1)
    content_wrap.columnconfigure(0, weight=1)

    # ── FORCE BACKGROUNDS ─────────────────────────────────────────────────────
    # ttkbootstrap's theme engine can override tk widget bg colors.
    # Walk the entire widget tree and re-apply each widget's intended bg.
    def _force_bg(widget):
        if hasattr(widget, '_my_bg'):
            try: widget.configure(bg=widget._my_bg)
            except Exception: pass
        if hasattr(widget, '_my_fg'):
            try: widget.configure(fg=widget._my_fg)
            except Exception: pass
        for child in widget.winfo_children():
            _force_bg(child)

    win.update_idletasks()
    
    switch_tab("Dashboard")
    
    win.after(100, lambda: _force_bg(win))
