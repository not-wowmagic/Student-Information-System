import os
import tkinter as tk
from tkinter import ttk as tkttk
from ttkbootstrap import Separator
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import PRIMARY
from database.crud.students import get_students
from database.db_utils import find_by_column


from backend.backend import create_new_students
from frontend.admin.admin_grade_subjects import build_student_grades_tab
from frontend.components.form import Form, RowField
from src.frontend.components.fields import Fields
from ttkbootstrap import Frame
from ttkbootstrap.widgets.scrolled import ScrolledFrame
from ttkbootstrap.toast import ToastNotification

from constants import FONT_DEFAULT_NAME
from icon_utils import apply_window_icon

from frontend.admin.admin_dashboard_home import build_dashboard_tab
from frontend.admin.admin_subjects import build_subjects_list_tab, build_add_subject_tab
from frontend.admin.admin_events import build_events_list_tab, build_add_event_tab
from frontend.admin.admin_announcements import build_announcements_list_tab, build_add_announcement_tab

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
NAV_HOVER     = NAV_BG      # hover/active state (kept uniform)
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
TABLE_OUTER   = "#1a305e"   # navy card holding the table
TABLE_HEADER_BG = "#d1d5db" # light grey header row inside table
TABLE_BODY_BG   = "#e8eaf0" # light grey table body area
BADGE_GREEN_BG  = "#22c55e"
BADGE_RED_BG    = "#ef4444"
DEPT_BAR_BG     = "#001f5b"
DEPT_BAR_TRACK  = "#e5e7eb"

DASHBOARD_VERSION = "v5-figma-match"

# Store buttons for active state toggling
nav_btns = {}

# ── Helper: nav button ─────────────────────────────────────────────────────────
def _make_nav_btn(parent, text, icon, command=None):
    f = tk.Frame(parent, bg=NAV_BG, cursor="hand2", highlightthickness=0, bd=0)
    f.pack(fill="x", pady=0)
    inner = tk.Frame(f, bg=NAV_BG, highlightthickness=0, bd=0)
    inner.pack(fill="x", padx=8, pady=6)
    
    # Store references to images if any are used, to prevent garbage collection
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
             padx=22).pack(fill="x", pady=(10, 2))


# ── Helper: stat card (white rounded-border card) ──────────────────────────────
def _stat_card(parent, title, value, subtitle=None, icon_text="👥",
               badge_text=None, badge_bg=None, trend_text=None):
    # Outer border frame (simulates rounded border via 1-px colored frame)
    outer = tk.Frame(parent, bg=CARD_BORDER, highlightthickness=0, bd=0)
    outer.pack(side="left", fill="both", expand=True, padx=(0, 14))

    inner = tk.Frame(outer, bg=CARD_BG, highlightthickness=0, bd=0)
    inner.pack(padx=1, pady=1, fill="both", expand=True)

    pad = tk.Frame(inner, bg=CARD_BG)
    pad.pack(fill="both", expand=True, padx=18, pady=16)

    # Top row: icon + badge/label
    top = tk.Frame(pad, bg=CARD_BG)
    top.pack(fill="x")

    tk.Label(top, text=icon_text, font=("Segoe UI Emoji", 20),
             fg=TEXT_MUTED, bg=CARD_BG).pack(side="left")

    if badge_text and badge_bg:
        badge_f = tk.Frame(top, bg=badge_bg, highlightthickness=0, bd=0)
        badge_f.pack(side="right")
        tk.Label(badge_f, text=badge_text, font=("Segoe UI", 8, "bold"),
                 fg=WHITE, bg=badge_bg).pack(padx=9, pady=3)
    else:
        tk.Label(top, text="OVERALL", font=("Segoe UI", 8),
                 fg=TEXT_MUTED, bg=CARD_BG).pack(side="right")

    # Title
    tk.Label(pad, text=title, font=("Segoe UI", 10),
             fg=TEXT_MUTED, bg=CARD_BG, anchor="w").pack(fill="x", pady=(12, 2))

    # Big value
    tk.Label(pad, text=value, font=("Segoe UI", 28, "bold"),
             fg=TEXT_PRIMARY, bg=CARD_BG, anchor="w").pack(fill="x")

    # Trend arrow (green)
    if trend_text:
        tr = tk.Frame(pad, bg=CARD_BG)
        tr.pack(fill="x", pady=(6, 0))
        tk.Label(tr, text="↗  " + trend_text, font=("Segoe UI", 9),
                 fg=ACCENT_GREEN, bg=CARD_BG, anchor="w").pack(side="left")

    # Subtitle (muted small text)
    if subtitle:
        tk.Label(pad, text=subtitle, font=("Segoe UI", 9),
                 fg=TEXT_MUTED, bg=CARD_BG, anchor="w").pack(fill="x", pady=(4, 0))


# ── Helper: department load bar ────────────────────────────────────────────────
def _dept_bar(parent, dept_name, count, total):
    row = tk.Frame(parent, bg=WHITE)
    row.pack(fill="x", pady=5)

    hdr = tk.Frame(row, bg=WHITE)
    hdr.pack(fill="x")
    tk.Label(hdr, text=dept_name, font=("Segoe UI", 9, "bold"),
             fg=TEXT_PRIMARY, bg=WHITE).pack(side="left")
    tk.Label(hdr, text=f"{count:,} students", font=("Segoe UI", 9),
             fg=TEXT_MUTED, bg=WHITE).pack(side="right")

    track = tk.Frame(row, bg=DEPT_BAR_TRACK, height=6)
    track.pack(fill="x", pady=(4, 0))
    fill_w = min(count / total, 1.0) if total > 0 else 0
    tk.Frame(track, bg=DEPT_BAR_BG, height=6).place(
        relx=0, rely=0, relheight=1, relwidth=fill_w)

# ── VIEW BUILDERS ────────────────────────────────────────────────────────────
def build_dashboard_tab(parent, switch_cb, conn):
    # ── Fetch data ──
    from database.crud.students import get_students
    from database.db_utils import find_by_column

    students = get_students(conn)
    total     = len(students)
    active    = len([s for s in students if len(s) > 7 and s[7] == "Active"])
    inactive  = len([s for s in students if len(s) > 7 and s[7] == "Inactive"])

    # ── STAT CARDS ──
    cards_row = tk.Frame(parent, bg=CONTENT_BG)
    cards_row.pack(fill="x", padx=24, pady=(22, 16))

    _stat_card(cards_row, "Total Students",    str(total),    None, "👥")
    _stat_card(cards_row, "Active Students",   str(active),   None, "✅")
    _stat_card(cards_row, "Inactive Students", str(inactive), None, "🚫")

    # ── LOWER ROW ──
    lower = tk.Frame(parent, bg=CONTENT_BG)
    lower.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    # ── STUDENTS TABLE ──
    table_card = tk.Frame(lower, bg=TABLE_OUTER, highlightthickness=0, bd=0)
    table_card.pack(side="left", fill="both", expand=True, padx=(0, 16))

    tk.Label(table_card, text="Students", font=("Segoe UI", 12, "bold"),
             fg=WHITE, bg=TABLE_OUTER, anchor="w").pack(anchor="w", padx=16, pady=(14, 10))

    tree_holder = tk.Frame(table_card, bg="#c8cdd8", highlightthickness=0, bd=0)
    tree_holder.pack(fill="both", expand=True, padx=10, pady=(0, 14))

    style = tkttk.Style()
    style.configure("FigmaTree.Treeview",
                    background="#d8dde8", foreground=TEXT_PRIMARY,
                    fieldbackground="#d8dde8", rowheight=28, font=("Segoe UI", 10))
    style.configure("FigmaTree.Treeview.Heading",
                    background="#c0c6d4", foreground=TEXT_PRIMARY,
                    font=("Segoe UI", 10, "bold"), relief="flat")
    style.map("FigmaTree.Treeview",
              background=[("selected", "#a0b4d0")],
              foreground=[("selected", TEXT_PRIMARY)])

    tree = tkttk.Treeview(tree_holder,
                          columns=("id", "name", "course", "year"),
                          show="headings",
                          style="FigmaTree.Treeview",
                          height=14)
    tree.heading("id",     text="ID")
    tree.heading("name",   text="Name")
    tree.heading("course", text="Course")
    tree.heading("year",   text="Year")
    tree.column("id",     width=100, anchor="center", minwidth=80)
    tree.column("name",   width=200, anchor="w",      minwidth=140)
    tree.column("course", width=200, anchor="center", minwidth=130)
    tree.column("year",   width=70,  anchor="center", minwidth=50)

    # ── Populate tree ──
    for s in students:
        student_id = s[0]
        full_name  = s[1]
        course_id  = s[2]
        year_level = s[3]

        course_data = find_by_column(conn, "COURSES", "course_id", course_id)
        course_name = course_data[1] if course_data else "Unknown"

        tree.insert("", "end", values=(student_id, full_name, course_name, year_level))

    tree.bind("<Double-1>", lambda e: switch_cb("Student Profile"))

    tree_vsb = tkttk.Scrollbar(tree_holder, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=tree_vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    tree_vsb.pack(side="right", fill="y")

    # ── RIGHT PANEL ──
    right_panel = tk.Frame(lower, bg=CONTENT_BG, width=290)
    right_panel.pack(side="left", fill="both")
    right_panel.pack_propagate(False)

    # Campus card
    campus_frame = tk.Frame(right_panel, bg="#0d2447", height=130)
    campus_frame.pack(fill="x", pady=(0, 14))
    campus_frame.pack_propagate(False)
    campus_overlay = tk.Frame(campus_frame, bg="#0d2447")
    campus_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(campus_overlay, text="Enchong Dee University",
             font=("Segoe UI", 11, "bold"), fg=WHITE, bg="#0d2447",
             anchor="w", wraplength=260, justify="left").pack(anchor="w", padx=16, pady=(24, 4))
    tk.Label(campus_overlay, text="Student Information System",
             font=("Segoe UI", 9), fg="#aab4c8", bg="#0d2447",
             anchor="w", wraplength=260, justify="left").pack(anchor="w", padx=16)

    # ── Department Load card ──
    dept_outer = tk.Frame(right_panel, bg=CARD_BORDER)
    dept_outer.pack(fill="x")
    dept_white = tk.Frame(dept_outer, bg=WHITE)
    dept_white.pack(padx=1, pady=1, fill="both", expand=True)
    dept_pad = tk.Frame(dept_white, bg=WHITE)
    dept_pad.pack(fill="both", padx=16, pady=14)

    tk.Label(dept_pad, text="Department Load", font=("Segoe UI", 11, "bold"),
             fg=TEXT_PRIMARY, bg=WHITE, anchor="w").pack(anchor="w", pady=(0, 8))

    # Count students per course
    course_counts = {}
    for s in students:
        course_id   = s[2]
        course_data = find_by_column(conn, "COURSES", "course_id", course_id)
        course_name = course_data[1] if course_data else "Unknown"
        course_counts[course_name] = course_counts.get(course_name, 0) + 1

    for course_name, count in course_counts.items():
        _dept_bar(dept_pad, course_name, count, total)

    tk.Button(dept_pad, text="View Full Analytics",
              font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg=WHITE,
              relief="solid", bd=1, cursor="hand2", pady=6,
              activebackground="#f3f4f6").pack(fill="x", pady=(14, 0))

def build_student_profile_tab(parent, switch_cb, conn=None, student_id=None):
    from database.crud.students import search_student, get_student_gwa, get_student_subjects

    student = search_student(conn, student_id) if conn and student_id else None
    course_name = "Unknown"
    gwa_value = "N/A"
    credit_value = 0

    if student and conn:
        course_data = find_by_column(conn, "COURSES", "course_id", student[2])
        course_name = course_data[1] if course_data else "Unknown"
        gwa = get_student_gwa(conn, student_id)
        if gwa is not None:
            gwa_value = f"{gwa:.2f}"
        credit_value = sum(float(row[7]) for row in get_student_subjects(conn, student_id))
    # Top breadcrumb
    bc = tk.Frame(parent, bg=CONTENT_BG)
    bc.pack(fill="x", padx=24, pady=(16, 10))
    tk.Label(bc, text="Student Profile", font=("Segoe UI", 12, "bold"),
             fg=TEXT_PRIMARY, bg=CONTENT_BG).pack(side="left")

    # 2 columns layout
    cols = tk.Frame(parent, bg=CONTENT_BG)
    cols.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    # LEFT COLUMN (Profile Summary)
    left_col = tk.Frame(cols, bg=CARD_BORDER, width=320)
    left_col.pack(side="left", fill="y", padx=(0, 16))
    left_col.pack_propagate(False)

    left_inner = tk.Frame(left_col, bg=CARD_BG)
    left_inner.pack(padx=1, pady=1, fill="both", expand=True)

    # Avatar
    avatar_wrap = tk.Frame(left_inner, bg=CARD_BG, pady=24)
    avatar_wrap.pack(fill="x")
    avatar = tk.Label(avatar_wrap, text="👤", font=("Segoe UI Emoji", 48), fg="#cbd5e1", bg="#f1f5f9", width=3, height=1)
    avatar.pack(pady=10)

    tk.Label(left_inner, text=student[1] if student else "Student Profile", font=("Segoe UI", 16, "bold"), fg=NAV_BG, bg=CARD_BG).pack()
    tk.Label(left_inner, text=course_name, font=("Segoe UI", 10), fg=TEXT_MUTED, bg=CARD_BG).pack()

    # Badges
    badges = tk.Frame(left_inner, bg=CARD_BG)
    badges.pack(pady=12)
    tk.Label(badges, text="Enrolled", font=("Segoe UI", 9, "bold"), fg="#16a34a", bg="#dcfce7", padx=8, pady=2).pack(side="left", padx=4)
    tk.Label(badges, text="Freshman Year", font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED, bg="#f1f5f9", padx=8, pady=2).pack(side="left", padx=4)

    # Details
    det = tk.Frame(left_inner, bg=CARD_BG)
    det.pack(fill="x", padx=24, pady=16)

    def _detail_row(p, label, val):
        r = tk.Frame(p, bg=CARD_BG)
        r.pack(fill="x", pady=6)
        tk.Label(r, text=label, font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED, bg=CARD_BG).pack(side="left")
        tk.Label(r, text=val, font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg=CARD_BG).pack(side="right")

    _detail_row(det, "Student ID", student[0] if student else "")
    _detail_row(det, "Admission Date", student[8] if student else "")
    _detail_row(det, "Email Address", student[4] if student else "")
    _detail_row(det, "Phone", student[5] if student else "")

    # Bottom Academic Summary Card
    acad = tk.Frame(left_inner, bg=NAV_BG)
    acad.pack(fill="x", side="bottom", padx=16, pady=16)
    tk.Label(acad, text="Academic Summary", font=("Segoe UI", 9), fg=WHITE, bg=NAV_BG).pack(anchor="w", padx=12, pady=(12, 4))

    acad_grid = tk.Frame(acad, bg=NAV_BG)
    acad_grid.pack(fill="x", padx=12, pady=(0, 12))
    grade = tk.Frame(acad_grid, bg="#1a3a7a")
    grade.pack(side="left", fill="both", expand=True, padx=(0, 4))
    tk.Label(grade, text="Grade", font=("Segoe UI", 8), fg="#aab4c8", bg="#1a3a7a").pack(anchor="w", padx=8, pady=(8, 0))
    tk.Label(grade, text=gwa_value, font=("Segoe UI", 16, "bold"), fg=WHITE, bg="#1a3a7a").pack(anchor="w", padx=8, pady=(0, 8))

    cred = tk.Frame(acad_grid, bg="#1a3a7a")
    cred.pack(side="right", fill="both", expand=True, padx=(4, 0))
    tk.Label(cred, text="Credits", font=("Segoe UI", 8), fg="#aab4c8", bg="#1a3a7a").pack(anchor="w", padx=8, pady=(8, 0))
    tk.Label(cred, text=str(int(credit_value)), font=("Segoe UI", 16, "bold"), fg=WHITE, bg="#1a3a7a").pack(anchor="w", padx=8, pady=(0, 8))

    # RIGHT COLUMN
    right_col = tk.Frame(cols, bg=CARD_BORDER)
    right_col.pack(side="left", fill="both", expand=True)

    right_inner = tk.Frame(right_col, bg=CARD_BG)
    right_inner.pack(padx=1, pady=1, fill="both", expand=True)

    # Tabs inside right col
    tab_hdr = tk.Frame(right_inner, bg="#f8fafc")
    tab_hdr.pack(fill="x")
    tk.Label(tab_hdr, text="Academic Info", font=("Segoe UI", 10, "bold"), fg=NAV_BG, bg=CARD_BG, padx=16, pady=12).pack(side="left")
    tk.Frame(tab_hdr, bg=CARD_BORDER, height=1).pack(side="bottom", fill="x")

    content = tk.Frame(right_inner, bg=CARD_BG)
    content.pack(fill="both", expand=True, padx=24, pady=24)

    row1 = tk.Frame(content, bg=CARD_BG)
    row1.pack(fill="x")

    maj_card = tk.Frame(row1, bg="#f8fafc", highlightthickness=1, highlightbackground=CARD_BORDER, bd=0)
    maj_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
    tk.Label(maj_card, text="PRIMARY MAJOR", font=("Segoe UI", 8, "bold"), fg=NAV_BG, bg="#f8fafc").pack(anchor="w", padx=16, pady=(16, 4))
    tk.Label(maj_card, text=course_name, font=("Segoe UI", 11, "bold"), fg=TEXT_PRIMARY, bg="#f8fafc").pack(anchor="w", padx=16)
    tk.Label(maj_card, text=f"Year {student[3]}" if student else "", font=("Segoe UI", 9), fg=TEXT_MUTED, bg="#f8fafc").pack(anchor="w", padx=16, pady=(0, 16))

    adv_card = tk.Frame(row1, bg="#f8fafc", highlightthickness=1, highlightbackground=CARD_BORDER, bd=0)
    adv_card.pack(side="right", fill="both", expand=True, padx=(8, 0))
    tk.Label(adv_card, text="ACADEMIC ADVISOR", font=("Segoe UI", 8, "bold"), fg=NAV_BG, bg="#f8fafc").pack(anchor="w", padx=16, pady=(16, 4))
    adv_in = tk.Frame(adv_card, bg="#f8fafc")
    adv_in.pack(fill="x", padx=16, pady=(0, 16))
    tk.Label(adv_in, text="👤", font=("Segoe UI", 18), bg="#e2e8f0").pack(side="left", padx=(0, 10))
    a_t = tk.Frame(adv_in, bg="#f8fafc")
    a_t.pack(side="left")
    tk.Label(a_t, text="Student Advisor", font=("Segoe UI", 10, "bold"), fg=TEXT_PRIMARY, bg="#f8fafc").pack(anchor="w")
    tk.Label(a_t, text="Seeded demo profile", font=("Segoe UI", 9), fg=TEXT_MUTED, bg="#f8fafc").pack(anchor="w")

    tk.Label(content, text="SCHOLARSHIPS & HONORS", font=("Segoe UI", 9, "bold"), fg=NAV_BG, bg=CARD_BG).pack(anchor="w", pady=(32, 8))

    schol = tk.Frame(content, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0)
    schol.pack(fill="x", ipady=40)
    # Dashed effect simulated with a flat border for now
    tk.Label(schol, text="🎖️", font=("Segoe UI Emoji", 24), bg=CARD_BG).pack(pady=(20, 4))
    tk.Label(schol, text="No records yet.", font=("Segoe UI", 12, "bold"), fg=TEXT_MUTED, bg=CARD_BG).pack()
    tk.Label(schol, text="Additional honors and scholarship awards will be\ndisplayed once verified by the registrar's office.", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=CARD_BG, justify="center").pack()

    # Buttons bottom
    btm = tk.Frame(right_inner, bg=CARD_BG)
    btm.pack(fill="x", side="bottom", padx=24, pady=24)

    tk.Button(btm, text="← Back to List", font=("Segoe UI", 10), cursor="hand2", command=lambda: switch_cb("Dashboard"),
              bg=WHITE, fg=TEXT_PRIMARY, relief="solid", bd=1, padx=16, pady=6).pack(side="left")

    tk.Button(btm, text="✎ Edit Record", font=("Segoe UI", 10, "bold"), cursor="hand2", command=lambda: switch_cb("Edit Student"),
              bg=NAV_BG, fg=WHITE, relief="flat", bd=0, padx=16, pady=6).pack(side="right")
    tk.Button(btm, text="Generate Report", font=("Segoe UI", 10), cursor="hand2",
              bg=WHITE, fg=TEXT_PRIMARY, relief="solid", bd=1, padx=16, pady=6).pack(side="right", padx=12)



def build_add_student_tab(parent, switch_cb, conn):
    # Main container
    tab_container = tk.Frame(parent, bg=WHITE)
    tab_container.pack(fill="both", expand=True)


    container_content = tk.Frame(tab_container, bg=WHITE)
    container_content.pack(fill="both", expand=True, padx=40, pady=(34, 0))

    # Title
    tk.Label(container_content, text="New Student Record", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="center")

    rows_config = [
        (0, 2),
        (0, 2),
        (0, 2),
        (0, 1),
        (0, 2)
    ]

    # student_id TEXT PRIMARY KEY NOT NULL,
    # full_name TEXT NOT NULL,
    # course_id INTEGER NOT NULL,
    # year_level INTEGER NOT NULL,
    # email_address TEXT NOT NULL,
    # contact_Number INTEGER NOT NULL,
    # house_number TEXT NOT NULL,
    # account_status TEXT NOT NULL,
    # enrollment_date TEXT, NOT NULL
    # password TEXT NOT NULL,

    class StudentForm(Form):
        def onSubmit(self):

            def parse_year(value):
                if not value:
                    return None
                digits = "".join(ch for ch in str(value) if ch.isdigit())
                return int(digits) if digits else None


            student_id = student_id_field.get_input()
            full_name = full_name_field.get_input()
            course_text = course_field.get_input()
            year_level = parse_year(year_level_field.get_input())
            email_address = email_address_field.get_input()
            contact_number = contact_number_field.get_input()
            enrollment_date = enrollment_date_field.get_input()
            account_status = account_status_field.get_input()

            if year_level is None:
                ToastNotification(
                    title="Missing year level.",
                    message="Please select a valid year level.",
                    duration=3000,
                    bootstyle="danger"
                ).show_toast()
                return

            # ── Optional field ──
            HOUSE_PLACEHOLDER = "House No., Street, Barangay, City, Province"
            CONTACT_PLACEHOLDER = "+63 000 000 0000"

            raw_house = house_number_field.get_input()
            house_number = None if (not raw_house or raw_house == HOUSE_PLACEHOLDER) else raw_house

            raw_contact = contact_number_field.get_input()
            contact_number = None if (not raw_contact or raw_contact == CONTACT_PLACEHOLDER) else raw_contact

            student_data = [
                student_id,
                full_name,
                course_text,
                year_level,
                email_address,
                contact_number,
                house_number,
                account_status,
                enrollment_date
            ]

            is_sucess, err_message = create_new_students(conn, student_data)

            if is_sucess:
                toast = ToastNotification(
                    title="Sucessfully Added.",
                    message=f"Student {student_id} has been added to the database",
                    duration=5000,
                    bootstyle="success"
                )

                toast.show_toast()

                switch_cb("Student List")
                has_submit = True
            else:
                toast = ToastNotification(
                    title="Failed to create a student.",
                    message=err_message,
                    duration=5000,
                    bootstyle="danger"
                )

                toast.show_toast()
                switch_cb("Student List")
                has_submit = True





    student_form = StudentForm(container_content, rows_config)


    row_1_frame= student_form._get_rows_field(0)
    student_id_field = Fields(row_1_frame, "entry", column_index=0,field_label_text="Student ID", placeholder_text="e.g 25-2751")
    full_name_field = Fields(row_1_frame, "entry", column_index=1, field_label_text="Full Name",  placeholder_text="Surname, Full name, M.I")

    row_2_frame = student_form._get_rows_field(1)
    course_field = Fields(row_2_frame, "combo_box", column_index=0,field_label_text="Course",
                    options=['BS Information Technology',
                    'BS Computer Science',
                    'BS Hospital Management',
                    'BS Education',
                    'BS Business Administration',
                    'BS Psychology'])

    year_level_field = Fields(row_2_frame, "combo_box", column_index=1, field_label_text="Year Level",  options=["1st Year", "2nd Year", "3rd Year", "4th Year"])

    row_3_frame = student_form._get_rows_field(2)
    email_address_field = Fields(row_3_frame, "entry", column_index=0, field_label_text="Email Address",
                              placeholder_text="student@university.edu")
    contact_number_field = Fields(row_3_frame, "entry", column_index=1, field_label_text="Contact",
                       placeholder_text="+63 000 000 0000")

    row_4_frame = student_form._get_rows_field(3)
    house_number_field = Fields(row_4_frame, "entry", column_index=0, field_label_text="Home Address",
                              placeholder_text="House No., Street, Barangay, City, Province")

    row_5_frame = student_form._get_rows_field(4)
    account_status_field = Fields(row_5_frame, "radio_button", column_index=0, field_label_text="Account Status", options=["Active", "Inactive"])
    enrollment_date_field = Fields(row_5_frame, "date_entry", column_index=1, field_label_text="Entrollment Date")


def build_edit_student_tab(parent, switch_cb, conn):
    from database.crud.students import search_student, update_student
    from database.db_utils import find_by_column

    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    tk.Label(container, text="Edit Student Record", font=("Georgia", 24),
             fg=TEXT_PRIMARY, bg=WHITE).pack(pady=(48, 0), padx=48, anchor="w")
    tk.Label(container, text="Search for a student to edit their record.",
             font=("Segoe UI", 10), fg=TEXT_MUTED, bg=WHITE).pack(pady=(4, 32), padx=48, anchor="w")

    # ── Search Bar ──
    top_bar = tk.Frame(container, bg=WHITE)
    top_bar.pack(fill="x", padx=48, pady=(0, 16))

    tk.Label(top_bar, text="Student ID:", font=("Segoe UI", 10, "bold"),
             fg=TEXT_PRIMARY, bg=WHITE).pack(side="left", padx=(0, 12))

    search_f = tk.Frame(top_bar, bg="#f4f4f5", height=40)
    search_f.pack(side="left", fill="x", expand=True, padx=(0, 12))
    search_f.pack_propagate(False)

    e_search = tk.Entry(search_f, font=("Segoe UI", 10), bg="#f4f4f5",
                        fg=TEXT_PRIMARY, relief="flat", bd=0, insertbackground=TEXT_PRIMARY)
    e_search.pack(fill="both", expand=True, padx=16, pady=8)
    e_search.insert(0, "e.g. 26-1234")

    tk.Frame(container, bg="#e2e8f0", height=1).pack(fill="x", padx=48, pady=(0, 16))

    # ── Form area (hidden until search) ──
    form_container = tk.Frame(container, bg=WHITE)
    form_container.pack(fill="both", expand=True, padx=48)

    found_student = {"data": None}
    form_fields   = {"built": False}

    # These will hold field references after form is built
    fields = {}

    def build_form(student):
        # Clear previous form
        for w in form_container.winfo_children():
            w.destroy()

        course_data = find_by_column(conn, "COURSES", "course_id", student[2])
        course_name = course_data[1] if course_data else ""

        rows_config = [
            (0, 2),
            (0, 2),
            (0, 2),
            (0, 1),
            (0, 2)
        ]

        class EditForm(Form):
            def onSubmit(self):
                new_full_name      = fields["full_name"].get_input()
                new_course_text    = fields["course"].get_input()
                new_year_level     = int(fields["year_level"].get_input()[0])
                new_email          = fields["email"].get_input()
                new_contact        = fields["contact"].get_input()
                new_account_status = fields["account_status"].get_input()

                HOUSE_PLACEHOLDER   = "House No., Street, Barangay, City, Province"
                CONTACT_PLACEHOLDER = "+63 000 000 0000"

                raw_house    = fields["house"].get_input()
                new_house    = None if (not raw_house    or raw_house    == HOUSE_PLACEHOLDER)   else raw_house
                raw_contact2 = fields["contact"].get_input()
                new_contact  = None if (not raw_contact2 or raw_contact2 == CONTACT_PLACEHOLDER) else raw_contact2

                # Convert course name → course_id
                course_row = find_by_column(conn, "COURSES", "course_name", new_course_text)
                new_course_id = course_row[0] if course_row else student[2]

                update_student(conn, student[0], {
                    "full_name":      new_full_name,
                    "course_id":      new_course_id,
                    "year_level":     new_year_level,
                    "email_address":  new_email,
                    "contact_number": new_contact,
                    "house_number":   new_house,
                    "account_status": new_account_status
                })

                toast = ToastNotification(
                    title="Successfully Updated.",
                    message=f"Student '{student[0]}' has been updated.",
                    duration=5000,
                )
                toast.show_toast()
                switch_cb("Student List")

        edit_form = EditForm(form_container, rows_config)

        row_1_frame = edit_form._get_rows_field(0)
        Fields(row_1_frame, "entry", column_index=0,
               field_label_text="Student ID",
               placeholder_text=student[0]).entry.config(state="disabled")
        sid_field = Fields(row_1_frame, "entry", column_index=0,
                           field_label_text="Student ID",
                           placeholder_text=student[0])
        # rebuild properly
        for w in row_1_frame.winfo_children():
            w.destroy()

        sid_field   = Fields(row_1_frame, "entry", column_index=0,
                             field_label_text="Student ID",
                             placeholder_text=student[0])
        sid_field.entry.config(state="disabled")

        fields["full_name"] = Fields(row_1_frame, "entry", column_index=1,
                                     field_label_text="Full Name",
                                     placeholder_text=student[1])

        row_2_frame = edit_form._get_rows_field(1)
        fields["course"] = Fields(row_2_frame, "combo_box", column_index=0,
                                  field_label_text="Course",
                                  options=['BS Information Technology',
                                           'BS Computer Science',
                                           'BS Hospital Management',
                                           'BS Education',
                                           'BS Business Administration',
                                           'BS Psychology'])
        fields["course"].combo_box.set(course_name)

        fields["year_level"] = Fields(row_2_frame, "combo_box", column_index=1,
                                      field_label_text="Year Level",
                                      options=["1st Year", "2nd Year", "3rd Year", "4th Year"])
        fields["year_level"].combo_box.set(f"{student[3]}{'st' if student[3] == 1 else 'nd' if student[3] == 2 else 'rd' if student[3] == 3 else 'th'} Year")

        row_3_frame = edit_form._get_rows_field(2)
        fields["email"]   = Fields(row_3_frame, "entry", column_index=0,
                                   field_label_text="Email Address",
                                   placeholder_text=student[4])
        fields["contact"] = Fields(row_3_frame, "entry", column_index=1,
                                   field_label_text="Contact",
                                   placeholder_text=student[5] if student[5] else "+63 000 000 0000")

        row_4_frame = edit_form._get_rows_field(3)
        fields["house"] = Fields(row_4_frame, "entry", column_index=0,
                                 field_label_text="Home Address",
                                 placeholder_text=student[6] if student[6] else "House No., Street, Barangay, City, Province")

        row_5_frame = edit_form._get_rows_field(4)
        fields["account_status"] = Fields(row_5_frame, "radio_button", column_index=0,
                                          field_label_text="Account Status",
                                          options=["Active", "Inactive"])
        fields["account_status"].option_var.set(student[7] if len(student) > 7 else "Active")

        Fields(row_5_frame, "date_entry", column_index=1,
               field_label_text="Enrollment Date")

        form_fields["built"] = True

    def do_search():
        query = e_search.get().strip()
        if not query or query == "e.g. 26-1234":
            return

        student = search_student(conn, query)
        if not student:
            for w in form_container.winfo_children():
                w.destroy()
            tk.Label(form_container, text="Student not found.",
                     font=("Segoe UI", 12), fg="#e11d48", bg=WHITE).pack(anchor="w")
            found_student["data"] = None
            return

        found_student["data"] = student
        build_form(student)

    btn_search = tk.Button(top_bar, text="Search", font=("Segoe UI", 9, "bold"),
                           fg=WHITE, bg=NAV_BG, relief="flat", padx=16, pady=4,
                           cursor="hand2", command=do_search)
    btn_search.pack(side="left")
    e_search.bind("<Return>", lambda e: do_search())



def build_remove_student_tab(parent, switch_cb, conn):
    from database.crud.students import search_student, delete_student
    from database.db_utils import find_by_column

    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    tk.Label(container, text="Remove Student", font=("Georgia", 24),
             fg=TEXT_PRIMARY, bg=WHITE).pack(pady=(48, 0), padx=48, anchor="w")
    tk.Label(container, text="Search for a student to remove their record permanently.",
             font=("Segoe UI", 10), fg=TEXT_MUTED, bg=WHITE).pack(pady=(4, 32), padx=48, anchor="w")

    # ── Search Bar ──
    top_bar = tk.Frame(container, bg=WHITE)
    top_bar.pack(fill="x", padx=48, pady=(0, 16))

    tk.Label(top_bar, text="Student ID:", font=("Segoe UI", 10, "bold"),
             fg=TEXT_PRIMARY, bg=WHITE).pack(side="left", padx=(0, 12))

    search_f = tk.Frame(top_bar, bg="#f4f4f5", height=40)
    search_f.pack(side="left", fill="x", expand=True, padx=(0, 12))
    search_f.pack_propagate(False)

    e_search = tk.Entry(search_f, font=("Segoe UI", 10), bg="#f4f4f5",
                        fg=TEXT_PRIMARY, relief="flat", bd=0,
                        insertbackground=TEXT_PRIMARY)
    e_search.pack(fill="both", expand=True, padx=16, pady=8)
    e_search.insert(0, "e.g. 26-1234")

    def _clear_placeholder(e):
        if e_search.get() == "e.g. 26-1234":
            e_search.delete(0, "end")
            e_search.config(fg=TEXT_PRIMARY)

    def _restore_placeholder(e):
        if not e_search.get().strip():
            e_search.insert(0, "e.g. 26-1234")
            e_search.config(fg=TEXT_MUTED)

    e_search.bind("<FocusIn>",  _clear_placeholder)
    e_search.bind("<FocusOut>", _restore_placeholder)

    tk.Frame(container, bg="#e2e8f0", height=1).pack(fill="x", padx=48, pady=(0, 24))

    # ── Result card (hidden initially) ──
    result_card = tk.Frame(container, bg="#fff1f2",
                           highlightthickness=1,
                           highlightbackground="#fecdd3")
    result_card.pack_forget()

    result_inner = tk.Frame(result_card, bg="#fff1f2")
    result_inner.pack(fill="both", expand=True, padx=32, pady=24)

    # ── Header row inside card ──
    card_header = tk.Frame(result_inner, bg="#fff1f2")
    card_header.pack(fill="x", pady=(0, 16))

    tk.Label(card_header, text="Student Found", font=("Segoe UI", 10, "bold"),
             fg="#e11d48", bg="#fff1f2").pack(side="left")

    # ── Student info labels ──
    name_lbl   = tk.Label(result_inner, text="", font=("Segoe UI", 16, "bold"),
                          fg=TEXT_PRIMARY, bg="#fff1f2")
    course_lbl = tk.Label(result_inner, text="", font=("Segoe UI", 10),
                          fg=TEXT_MUTED, bg="#fff1f2")
    email_lbl  = tk.Label(result_inner, text="", font=("Segoe UI", 10),
                          fg=TEXT_MUTED, bg="#fff1f2")
    status_lbl = tk.Label(result_inner, text="", font=("Segoe UI", 10),
                          fg=TEXT_MUTED, bg="#fff1f2")

    divider = tk.Frame(result_inner, bg="#fecdd3", height=1)

    warning_lbl = tk.Label(result_inner,
                           text="⚠  Warning: Deleting this record is irreversible and will remove all associated grades and history.",
                           font=("Segoe UI", 9), fg="#e11d48", bg="#fff1f2",
                           wraplength=700, justify="left")

    found_student = {"data": None}

    def show_result(student):
        course_data = find_by_column(conn, "COURSES", "course_id", student[2])
        course_name = course_data[1] if course_data else "Unknown"

        name_lbl.config(text=f"👤  {student[1]}")
        course_lbl.config(text=f"Course: {course_name}   |   Year {student[3]}")
        email_lbl.config(text=f"Email: {student[4]}")
        status_lbl.config(text=f"Status: {student[7]}")

        name_lbl.pack(anchor="w")
        course_lbl.pack(anchor="w", pady=(4, 0))
        email_lbl.pack(anchor="w", pady=(2, 0))
        status_lbl.pack(anchor="w", pady=(2, 16))
        divider.pack(fill="x", pady=(0, 16))
        warning_lbl.pack(anchor="w", pady=(0, 20))
        btn_del.pack(anchor="w")

        result_card.pack(fill="x", padx=48, pady=(0, 24))

    def hide_result():
        for w in [name_lbl, course_lbl, email_lbl, status_lbl,
                  divider, warning_lbl, btn_del]:
            w.pack_forget()
        result_card.pack_forget()

    def show_not_found():
        name_lbl.config(text="❌  No student found with that ID.", fg="#e11d48")
        course_lbl.config(text="")
        email_lbl.config(text="")
        status_lbl.config(text="")

        name_lbl.pack(anchor="w")
        course_lbl.pack_forget()
        email_lbl.pack_forget()
        status_lbl.pack_forget()
        divider.pack_forget()
        warning_lbl.pack_forget()
        btn_del.pack_forget()

        result_card.pack(fill="x", padx=48, pady=(0, 24))

    def do_search():
        query = e_search.get().strip()
        if not query or query == "e.g. 26-1234":
            return

        hide_result()

        student = search_student(conn, query)

        if not student:
            show_not_found()
            found_student["data"] = None
            return

        found_student["data"] = student
        name_lbl.config(fg=TEXT_PRIMARY)
        show_result(student)

    def do_delete():
        student = found_student["data"]
        if not student:
            return

        delete_student(conn, student[0])

        hide_result()
        found_student["data"] = None
        e_search.delete(0, "end")
        e_search.insert(0, "e.g. 26-1234")
        e_search.config(fg=TEXT_MUTED)

        toast = ToastNotification(
            title="Student Deleted.",
            message=f"Student '{student[1]}' has been permanently removed.",
            duration=5000,
            bootstyle="danger"
        )
        toast.show_toast()
        switch_cb("Student List")

    btn_search = tk.Button(top_bar, text="Search",
                           font=("Segoe UI", 9, "bold"), fg=WHITE, bg=NAV_BG,
                           relief="flat", padx=16, pady=4, cursor="hand2",
                           command=do_search)
    btn_search.pack(side="left")

    e_search.bind("<Return>", lambda e: do_search())

    btn_del = tk.Button(result_inner, text="🗑  Delete Student Record",
                        font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#e11d48",
                        relief="flat", padx=16, pady=8, cursor="hand2",
                        command=do_delete)

def build_search_tab(parent, switch_cb, conn):
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    tk.Label(container, text="Student Search", font=("Georgia", 24),
             fg=TEXT_PRIMARY, bg=WHITE).pack(pady=(48, 32), padx=48, anchor="w")

    # ── Filters ──
    filters_f = tk.Frame(container, bg=WHITE)
    filters_f.pack(fill="x", padx=48)

    def _make_filter(p, label, opts):
        f = tk.Frame(p, bg=WHITE)
        f.pack(side="left", padx=(0, 24))
        tk.Label(f, text=label, font=("Segoe UI", 9, "bold"),
                 fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="w")
        cb = tkttk.Combobox(f, font=("Segoe UI", 10), state="readonly", width=20)
        cb["values"] = opts
        cb.set(opts[0])
        cb.pack(pady=4)
        return cb

    course_cb = _make_filter(filters_f, "Course", [
        "All Courses", "BS Information Technology", "BS Computer Science",
        "BS Business Administration", "BS Education",
        "BS Hospital Management", "BS Psychology"
    ])
    year_cb   = _make_filter(filters_f, "Year Level", ["All Years", "1", "2", "3", "4"])
    status_cb = _make_filter(filters_f, "Status", ["All", "Active", "Inactive"])

    # ── Fetch students ──
    students = get_students(conn)

    coldata = [
        {"text": "ID",     "stretch": True},
        {"text": "Name",   "stretch": True},
        {"text": "Course", "stretch": True},
        {"text": "Year",   "stretch": True},
        {"text": "Status", "stretch": True},
    ]

    def build_rowdata(course_filter="All Courses", year_filter="All Years", status_filter="All"):
        rows = []
        for s in students:
            student_id     = s[0]
            full_name      = s[1]
            course_id      = s[2]
            year_level     = str(s[3])
            account_status = s[7]

            course_data = find_by_column(conn, "COURSES", "course_id", course_id)
            course_name = course_data[1] if course_data else "Unknown"

            if course_filter != "All Courses" and course_name != course_filter:
                continue
            if year_filter != "All Years" and year_level != year_filter:
                continue
            if status_filter != "All" and account_status != status_filter:
                continue

            rows.append((student_id, full_name, course_name, year_level, account_status))
        return rows

    # ── Tableview (single one) ──
    style = tkttk.Style()
    style.configure("Treeview", rowheight=40)

    table = Tableview(
        master=container,
        coldata=coldata,
        rowdata=build_rowdata(),
        paginated=True,
        searchable=True,
        bootstyle=PRIMARY,
        pagesize=15,
        height=15,
        autofit=True,
        disable_right_click=True
    )
    table.pack(fill="both", expand=True, padx=48, pady=(16, 48))

    # ── Double click → Student Profile ──
    def on_double_click(event):
        selected = table.view.selection()
        if not selected:
            return
        values = table.view.item(selected[0])["values"]
        if values:
            switch_cb("Student Profile", values[0])

    table.view.bind("<Double-1>", on_double_click)

    # ── Apply filters ──
    def apply_filters():
        filtered = build_rowdata(
            course_cb.get(),
            year_cb.get(),
            status_cb.get()
        )
        table.build_table_data(coldata, filtered)

    btn_apply = tk.Button(filters_f, text="Apply Filters",
                          font=("Segoe UI", 9, "bold"), fg=WHITE, bg=NAV_BG,
                          relief="flat", padx=16, pady=4, cursor="hand2",
                          command=apply_filters)
    btn_apply.pack(side="left", pady=(16, 0))

def build_reports_tab(parent, switch_cb):
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    header = tk.Frame(container, bg=WHITE)
    header.pack(fill="x", pady=(48, 32), padx=48)
    
    tk.Label(header, text="System Reports", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left")

    def generate_pdf(e=None):
        try:
            from tkinter import filedialog
            path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Save Report")
            if not path:
                return
            
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=15, style='B')
                pdf.cell(200, 10, txt="Enchong Dee University - System Report", ln=1, align='C')
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="", ln=1)
                pdf.cell(200, 10, txt="Total Students: ", ln=1)
                pdf.cell(200, 10, txt="Active Students: ", ln=1)
                pdf.cell(200, 10, txt="Inactive Students: ", ln=1)
                pdf.cell(200, 10, txt="", ln=1)
                pdf.cell(200, 10, txt="Recent Enrollments:", ln=1)
                
                pdf.output(path)
                
                notif = tk.Frame(container, bg="#10b981", highlightthickness=0)
                notif.place(relx=1.0, rely=0.0, x=-32, y=32, anchor="ne")
                tk.Label(notif, text="✓ Report exported successfully", font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#10b981", padx=16, pady=12).pack()
                container.after(3000, notif.destroy)
            except ImportError:
                notif = tk.Frame(container, bg="#f59e0b", highlightthickness=0)
                notif.place(relx=1.0, rely=0.0, x=-32, y=32, anchor="ne")
                tk.Label(notif, text="⚠ fpdf library not installed. Showing mock success.", font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#f59e0b", padx=16, pady=12).pack()
                container.after(3000, notif.destroy)
            except Exception as ex:
                notif = tk.Frame(container, bg="#dc2626", highlightthickness=0)
                notif.place(relx=1.0, rely=0.0, x=-32, y=32, anchor="ne")
                tk.Label(notif, text=f"✗ Error generating PDF", font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#dc2626", padx=16, pady=12).pack()
                container.after(3000, notif.destroy)
        except Exception:
            pass

    btn_export = tk.Button(header, text="Export to PDF", font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#dc2626", relief="flat", padx=16, pady=6, cursor="hand2", command=generate_pdf)
    btn_export.pack(side="right")

    # Metrics
    metrics_f = tk.Frame(container, bg=WHITE)
    metrics_f.pack(fill="x", padx=48, pady=(0, 32))
    
    def _metric(p, title, val, color):
        card = tk.Frame(p, bg=color, highlightthickness=1, highlightbackground=color)
        card.pack(side="left", fill="x", expand=True, padx=(0, 16))
        tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg=WHITE, bg=color).pack(anchor="w", padx=16, pady=(16, 4))
        tk.Label(card, text=val, font=("Segoe UI", 24, "bold"), fg=WHITE, bg=color).pack(anchor="w", padx=16, pady=(0, 16))
        
    _metric(metrics_f, "Total Students", "", "#2563eb") # blue
    _metric(metrics_f, "Active Students", "", "#16a34a") # green
    _metric(metrics_f, "Inactive Students", "", "#64748b") # slate

    # Preview Table
    tk.Label(container, text="Recent Enrollments Preview", font=("Segoe UI", 12, "bold"), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="w", padx=48, pady=(0, 16))
    grid_f = tk.Frame(container, bg=WHITE, highlightthickness=1, highlightbackground="#e2e8f0")
    grid_f.pack(fill="both", expand=True, padx=48, pady=(0, 48))

    cols = ("Date", "ID", "Name", "Course")
    tree = tkttk.Treeview(grid_f, columns=cols, show="headings", height=10)
    for c in cols: tree.heading(c, text=c); tree.column(c, anchor="w", width=150)
    # No data — will be populated by database
    tree.pack(fill="both", expand=True)

def build_settings_tab(parent, switch_cb):
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)
    
    tk.Label(container, text="System Configuration", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(pady=(48, 32), padx=120, anchor="w")

    form = tk.Frame(container, bg=WHITE)
    form.pack(fill="both", expand=True, padx=120)

    # Col 1: Academic Settings
    col1 = tk.Frame(form, bg=WHITE)
    col1.pack(side="left", fill="both", expand=True, padx=(0, 16))
    
    tk.Label(col1, text="Academic Settings", font=("Segoe UI", 12, "bold"), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="w", pady=(0, 16))
    
    def _make_field(parent_frame, label_text, placeholder):
        f = tk.Frame(parent_frame, bg=WHITE)
        f.pack(fill="x", pady=(0, 24))
        tk.Label(f, text=label_text, font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="w", pady=(0, 8))
        inner = tk.Frame(f, bg="#f4f4f5", height=48)
        inner.pack(fill="x"); inner.pack_propagate(False)
        e = tk.Entry(inner, font=("Segoe UI", 10), bg="#f4f4f5", fg=TEXT_PRIMARY, relief="flat", bd=0, insertbackground=TEXT_PRIMARY)
        e.pack(fill="both", expand=True, padx=16, pady=12)
        e.insert(0, placeholder)

    _make_field(col1, "Current Academic Year", "2026-2027")
    _make_field(col1, "Current Semester", "1st Semester")

    # Col 2: System Toggles
    col2 = tk.Frame(form, bg=WHITE)
    col2.pack(side="left", fill="both", expand=True, padx=(16, 0))

    tk.Label(col2, text="System Preferences", font=("Segoe UI", 12, "bold"), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="w", pady=(0, 16))
    
    def _toggle(p, text, on=False):
        f = tk.Frame(p, bg=WHITE)
        f.pack(fill="x", pady=(0, 16))
        tk.Label(f, text="☑" if on else "☐", font=("Segoe UI Emoji", 14), fg=NAV_BG if on else "#94a3b8", bg=WHITE).pack(side="left")
        tk.Label(f, text=text, font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left", padx=(8, 0))

    _toggle(col2, "Allow New Enrollments", True)
    _toggle(col2, "Enable Student Portal Login", True)
    _toggle(col2, "Maintenance Mode (Admin Only)", False)

    def show_notification(e=None):
        notif = tk.Frame(container, bg="#10b981", highlightthickness=0)
        notif.place(relx=1.0, rely=0.0, x=-32, y=32, anchor="ne")
        tk.Label(notif, text="✓ Settings saved successfully", font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#10b981", padx=16, pady=12).pack()
        container.after(3000, notif.destroy)

    footer = tk.Frame(form, bg=WHITE)
    footer.pack(side="bottom", fill="x", pady=(48, 0))
    btn_save = tk.Button(footer, text="Save Settings", font=("Segoe UI", 10, "bold"), fg=WHITE, bg=NAV_BG, relief="flat", padx=32, pady=8, cursor="hand2", command=show_notification)
    btn_save.pack(anchor="w")


# ── Main entry ─────────────────────────────────────────────────────────────────
def open_admin_dashboard(window, conn, on_logout=None):

    win = tk.Toplevel(window)
    win.title(f"Admin Dashboard — EDU SIS")
    
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
    win.minsize(1280, 800)
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

    def _load_transparent_icon(path, size):
        try:
            from PIL import Image, ImageTk
        except Exception:
            return None

        if not os.path.exists(path):
            return None

        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            bg = img.getpixel((0, 0))
            if len(bg) == 4 and bg[3] == 255:
                r0, g0, b0, _ = bg
                new_pixels = []
                for r, g, b, a in img.getdata():
                    if abs(r - r0) <= 8 and abs(g - g0) <= 8 and abs(b - b0) <= 8:
                        new_pixels.append((r, g, b, 0))
                    else:
                        new_pixels.append((r, g, b, a))
                img.putdata(new_pixels)

            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    lbl_logo = tk.Label(logo_row, bg=NAV_BG)
    lbl_logo.pack(side="left", padx=(0, 12))

    logo_path = os.path.join(assets_dir, "edu-icon.png")
    logo_photo = _load_transparent_icon(logo_path, (42, 42))
    if logo_photo:
        lbl_logo.config(image=logo_photo)
        lbl_logo.image = logo_photo
    else:
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

    # ── TAB SWITCHING LOGIC ───────────────────────────────────────────────────
    current_tab_frame = None

    def switch_tab(tab_name, student_id=None):
        nonlocal current_tab_frame
        if current_tab_frame:
            current_tab_frame.destroy()

        main_frame = tk.Frame(content_wrap, bg=CONTENT_BG)
        main_frame.grid(row=0, column=0, sticky="nsew")
        current_tab_frame = main_frame

        _set_active_nav(tab_name)

        try:
            win.topbar_title_lbl.config(text=tab_name)
        except Exception:
            pass

        if tab_name == "Dashboard":
            build_dashboard_tab(main_frame, switch_tab, conn)
        elif tab_name == "Student Profile":
            build_student_profile_tab(main_frame, switch_tab, conn, student_id)  # ← pass student_id
        elif tab_name == "Student List" or tab_name == "Search":
            build_search_tab(main_frame, switch_tab, conn)
        elif tab_name == "Add Student":
            build_add_student_tab(main_frame, switch_tab, conn)
        elif tab_name == "Edit Student":
            build_edit_student_tab(main_frame, switch_tab, conn)
        elif tab_name == "Remove Student" or tab_name == "Remove":
            build_remove_student_tab(main_frame, switch_tab, conn)
        elif tab_name == "Subjects List":
            build_subjects_list_tab(main_frame, switch_tab, conn)
        elif tab_name == "Add Subject":
            build_add_subject_tab(main_frame, switch_tab, conn)
        elif tab_name == "Student Grades":
            build_student_grades_tab(main_frame, switch_tab, conn)
        elif tab_name == "Events List":
            build_events_list_tab(main_frame, switch_tab, conn)
        elif tab_name == "Add Event":
            build_add_event_tab(main_frame, switch_tab, conn)
        elif tab_name == "Announcement List":
            build_announcements_list_tab(main_frame, switch_tab, conn)
        elif tab_name == "Add Announcement":
            build_add_announcement_tab(main_frame, switch_tab, conn)
        elif tab_name == "Reports":
            build_reports_tab(main_frame, switch_tab)
        elif tab_name == "Settings":
            build_settings_tab(main_frame, switch_tab)
        else:
            tk.Label(main_frame, text=f"{tab_name}\n(Under Construction)",
                     font=("Segoe UI", 20), fg=TEXT_MUTED, bg=CONTENT_BG,
                     justify="center").pack(expand=True)

        win.after(50, lambda: _force_bg(main_frame))

    # Initialize buttons
    btn_dashboard, lbl_dash = _make_nav_btn(nav, "Dashboard", "⊞", command=lambda: switch_tab("Dashboard"))
    
    _section_label(nav, "STUDENTS")
    btn_search, lbl_search = _make_nav_btn(nav, "Student List", "🔍", command=lambda: switch_tab("Student List"))
    btn_add, lbl_add = _make_nav_btn(nav, "Add Student", "+", command=lambda: switch_tab("Add Student"))
    btn_edit, lbl_edit = _make_nav_btn(nav, "Edit Student", "✎", command=lambda: switch_tab("Edit Student"))
    btn_remove, lbl_rem = _make_nav_btn(nav, "Remove Student", "✕", command=lambda: switch_tab("Remove Student"))
    
    _section_label(nav, "SUBJECTS")
    btn_sub_list, lbl_sub_list = _make_nav_btn(nav, "Subjects List", "📚", command=lambda: switch_tab("Subjects List"))
    btn_add_sub, lbl_add_sub = _make_nav_btn(nav, "Add Subject", "+", command=lambda: switch_tab("Add Subject"))

    _section_label(nav, "GRADES")
    btn_grades, lbl_grades = _make_nav_btn(nav, "Student Grades", "📝",
                                           command=lambda: switch_tab("Student Grades"))

    _section_label(nav, "EVENTS")
    btn_ev_list, lbl_ev_list = _make_nav_btn(nav, "Events List", "🎉", command=lambda: switch_tab("Events List"))
    btn_add_ev, lbl_add_ev = _make_nav_btn(nav, "Add Event", "+", command=lambda: switch_tab("Add Event"))
    
    _section_label(nav, "ANNOUNCEMENTS")
    btn_ann_list, lbl_ann_list = _make_nav_btn(nav, "Announcement List", "🔊", command=lambda: switch_tab("Announcement List"))
    btn_add_ann, lbl_add_ann = _make_nav_btn(nav, "Add Announcement", "+", command=lambda: switch_tab("Add Announcement"))
    
    _section_label(nav, "SYSTEM")
    btn_reports, lbl_rep = _make_nav_btn(nav, "Reports", "📄", command=lambda: switch_tab("Reports"))
    btn_settings, lbl_set = _make_nav_btn(nav, "Settings", "⚙", command=lambda: switch_tab("Settings"))

    # Helper to load an icon safely
    def _apply_nav_icon(btn, lbl, filename, size=(20, 20)):
        try:
            path = os.path.join(assets_dir, filename)
            photo = _load_transparent_icon(path, size)
            if photo:
                lbl.configure(image=photo, text="")
                lbl.image = photo
                btn._image_refs.append(photo)
        except Exception:
            pass

    # Load image icons into nav buttons
    _apply_nav_icon(btn_dashboard, lbl_dash, "dashboard-50.png", (22, 22))
    _apply_nav_icon(btn_search, lbl_search, "search-64.png", (22, 22))
    _apply_nav_icon(btn_add, lbl_add, "add-64.png", (22, 22))
    _apply_nav_icon(btn_edit, lbl_edit, "edit-64.png", (22, 22))
    _apply_nav_icon(btn_remove, lbl_rem, "erase-64.png", (22, 22))
    _apply_nav_icon(btn_sub_list, lbl_sub_list, "elective-50.png", (22, 22))
    _apply_nav_icon(btn_ev_list, lbl_ev_list, "events-64.png", (22, 22))
    _apply_nav_icon(btn_ann_list, lbl_ann_list, "announcement-64.png", (22, 22))
    _apply_nav_icon(btn_reports, lbl_rep, "reports-48.png", (22, 22))
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
            on_logout(win)

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

    win.topbar_title_lbl = tk.Label(left_top, text="Dashboard", font=("Segoe UI", 12, "bold"),
             fg=WHITE, bg=NAV_BG)
    win.topbar_title_lbl.pack(side="left", padx=(0, 16), pady=0)
    # bind vertical centering
    left_top.pack_configure(pady=0)

    tk.Frame(left_top, bg="#2d4d8a", width=1).pack(side="left", fill="y",
                                                    pady=14)

    search_wrap = tk.Frame(left_top, bg="#0d2d6b",
                           highlightthickness=1,
                           highlightbackground="#2d4d8a",
                           highlightcolor="#2d4d8a", bd=0)
    search_wrap.pack(side="left", padx=(16, 0), pady=15)
    tk.Label(search_wrap, text="🔍", font=("Segoe UI", 9),
             fg="#8fa8cc", bg="#0d2d6b").pack(side="left", padx=(8, 2))
    
    # Updated to have a white background and black text on focus
    search_entry = tk.Entry(search_wrap, font=("Segoe UI", 10),
                            fg="#8fa8cc", bg=WHITE,
                            insertbackground="black",
                            relief="flat", bd=0, width=26)
    search_entry.insert(0, "Search student ID or name...")
    search_entry.pack(side="left", pady=4, padx=(4, 10))

    def _fi(e):
        if search_entry.get() == "Search student ID or name...":
            search_entry.delete(0, "end")
            search_entry.config(fg=TEXT_PRIMARY)

    def _fo(e):
        if not search_entry.get().strip():
            search_entry.insert(0, "Search student ID or name...")
            search_entry.config(fg="#8fa8cc")

    search_entry.bind("<FocusIn>",  _fi)
    search_entry.bind("<FocusOut>", _fo)

    # Right: Admin User pill button
    right_top = tk.Frame(tb_inner, bg=NAV_BG)
    right_top.pack(side="right", fill="y")

    admin_pill = tk.Frame(right_top, bg=NAV_BG,
                          highlightthickness=1,
                          highlightbackground="#4a6fa5",
                          highlightcolor="#4a6fa5", bd=0,
                          cursor="hand2")
    admin_pill.pack(side="right", pady=15)

    # Small avatar circle (simulated with a colored label)
    avatar_f = tk.Frame(admin_pill, bg="#2d4d8a",
                        width=26, height=26,
                        highlightthickness=0, bd=0)
    avatar_f.pack(side="left", padx=(8, 6), pady=6)
    avatar_f.pack_propagate(False)
    tk.Label(avatar_f, text="👤", font=("Segoe UI Emoji", 12),
             fg=WHITE, bg="#2d4d8a").place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(admin_pill, text="Admin User", font=("Segoe UI", 10),
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
        try:
            if not widget.winfo_exists():
                return
        except Exception:
            return

        if hasattr(widget, '_my_bg'):
            try:
                widget.configure(bg=widget._my_bg)
            except Exception:
                pass

        if hasattr(widget, '_my_fg'):
            try:
                widget.configure(fg=widget._my_fg)
            except Exception:
                pass

        try:
            for child in widget.winfo_children():
                _force_bg(child)
        except Exception:
            pass

    win.update_idletasks()
    
    # Init default tab
    switch_tab("Dashboard")
    
    win.after(100, lambda: _force_bg(win))
