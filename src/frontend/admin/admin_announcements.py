import tkinter as tk
from tkinter import ttk as tkttk

from ttkbootstrap.widgets import ToastNotification
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import PRIMARY
from backend.backend import create_new_announcement
from database.db_utils import find_by_column
from frontend.components.fields import Fields
from frontend.components.form import Form

NAV_BG        = "#001f5b"
WHITE         = "#ffffff"
TEXT_PRIMARY  = "#111827"
TEXT_MUTED    = "#6b7280"
CARD_BORDER   = "#e2e8f0"

def build_announcements_list_tab(parent, switch_cb, conn):
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    # Header
    top_bar = tk.Frame(container, bg=WHITE)
    top_bar.pack(fill="x", pady=(48, 16), padx=48)
    tk.Label(top_bar, text="Announcement Management", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left")

    btn_add = tk.Button(top_bar, text="➕ Post Announcement", font=("Segoe UI", 9, "bold"), fg=WHITE, bg=NAV_BG, relief="flat", padx=16, pady=6, cursor="hand2", command=lambda: switch_cb("Add Announcement"))
    btn_add.pack(side="right")

    tk.Frame(container, bg=CARD_BORDER, height=1).pack(fill="x", padx=48, pady=16)

    # ── Fetch data ──
    from database.crud.announcement import get_announcements

    announcements = get_announcements(conn)

    coldata = [
        {"text": "Title", "stretch": True},
        {"text": "Category", "stretch": True},
        {"text": "Department", "stretch": True},
        {"text": "Content Preview", "stretch": True},
        {"text": "Date Posted", "stretch": True},
    ]

    rowdata = []
    for ann in announcements:
        dept_id = ann[1]
        title = ann[2]
        category = ann[3]
        content = ann[4]
        created_at = ann[5]

        if dept_id is None:
            dept_name = "All Departments"
        else:
            dept_data = find_by_column(conn, "DEPARTMENT", "id", dept_id)
            dept_name = dept_data[1] if dept_data else "Unknown"

        # Truncate long content for preview
        preview = content[:50] + "..." if len(content) > 50 else content

        rowdata.append((title, category, dept_name, preview, created_at))


    # ── Tableview ──
    table = Tableview(
        master=container,
        coldata=coldata,
        rowdata=rowdata,
        paginated=True,
        searchable=True,
        bootstyle=PRIMARY,
        pagesize=15,
        height=15,
        autofit=True,
        disable_right_click=True
    )
    table.pack(fill="both", expand=True, padx=48, pady=(0, 48))


def build_add_announcement_tab(parent, switch_cb, conn):
    tab_container = tk.Frame(parent, bg=WHITE)
    tab_container.pack(fill="both", expand=True)

    container_content = tk.Frame(tab_container, bg=WHITE)
    container_content.pack(fill="both", expand=True, padx=40, pady=(34, 0))


    tk.Label(container_content, text="Post New Announcement", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="center")

    rows_config = [
        (0, 1),
        (0, 1),
        (0, 1),
        (0, 1)  # ← add 4th row
    ]

    class AnnouncementForm(Form):
        def onSubmit(self):
            title = title_field.get_input()
            category = category_field.get_input()
            department = department_field.get_input()
            content = content_field.get_input()

            if not title or title == "e.g System Maintenance Notice":
                print("no title!")
                return

            if not category:
                print("no category!")
                return

            if not content or not content.strip():
                print("no content!")
                return


            department_id = None if department == "All Departments" else department

            print("DEPARTMENT ID: ", department_id)
            announcement_data = [
                title,
                category,
                content,
                department_id
            ]

            create_new_announcement(conn, announcement_data)

            toast = ToastNotification(
                title="Successfully Posted.",
                message=f"Announcement '{title}' has been posted.",
                duration=5000,
            )
            toast.show_toast()
            switch_cb("Announcement List")


    announcement_form = AnnouncementForm(container_content, rows_config)

    row_1_frame = announcement_form._get_rows_field(0)
    title_field = Fields(row_1_frame, "entry", column_index=0,  # ← renamed
                         field_label_text="Title",
                         placeholder_text="e.g System Maintenance Notice")



    row_2_frame = announcement_form._get_rows_field(1)
    category_field = Fields(row_2_frame, "combo_box", column_index=0,  # ← renamed
                            field_label_text="Category",
                            options=["URGENT", "ACADEMICS", "CAMPUS"])

    row_3_frame = announcement_form._get_rows_field(2)
    department_field = Fields(row_3_frame, "combo_box", column_index=0, field_label_text="Department",
                              options=[
                                  "All Departments",
                                  "College of Information Technology",
                                  "College of Business",
                                  "College of Education",
                                  "College of Hospitality Management",
                                  "College of Psychology"
                              ])

    row_4_frame = announcement_form._get_rows_field(3)
    content_field = Fields(row_4_frame, "scrolled_text", column_index=0,  # ← renamed
                           field_label_text="Announcement Content")



