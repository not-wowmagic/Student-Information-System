import tkinter as tk
from tkinter import ttk as tkttk
from ttkbootstrap.widgets import ToastNotification

from backend.backend import create_new_subject
from frontend.components.fields import Fields
from frontend.components.form import Form
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import PRIMARY
from database.crud.subjects import get_subjects
from database.db_utils import find_by_column

NAV_BG        = "#001f5b"
WHITE         = "#ffffff"
TEXT_PRIMARY  = "#111827"
TEXT_MUTED    = "#6b7280"
CARD_BORDER   = "#e2e8f0"

def build_subjects_list_tab(parent, switch_cb, conn):
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    # Header
    top_bar = tk.Frame(container, bg=WHITE)
    top_bar.pack(fill="x", pady=(48, 16), padx=48)
    tk.Label(top_bar, text="Subject Management", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left")

    btn_add = tk.Button(top_bar, text="➕ Add Subject", font=("Segoe UI", 9, "bold"), fg=WHITE, bg=NAV_BG, relief="flat", padx=16, pady=6, cursor="hand2", command=lambda: switch_cb("Add Subject"))
    btn_add.pack(side="right")

    tk.Frame(container, bg=CARD_BORDER, height=1).pack(fill="x", padx=48, pady=16)

    # ── Fetch data ──
    subjects = get_subjects(conn)

    coldata = [
        {"text": "Course Code",   "stretch": True},
        {"text": "Course Title",  "stretch": True},
        {"text": "Course",        "stretch": True},
        {"text": "Teacher",       "stretch": True},
        {"text": "Units",         "stretch": True},
        {"text": "Day",           "stretch": True},
        {"text": "Start Time",    "stretch": True},
        {"text": "End Time",      "stretch": True},
    ]

    rowdata = []
    for subject in subjects:
        # subject_id, subject_name, subject_code, teacher, course_id, units, scheduled_day, start_time, end_time
        subject_name  = subject[1]
        subject_code  = subject[2]
        year_level    = subject[3]
        teacher       = subject[4]
        course_id     = subject[5]
        units         = subject[6]
        scheduled_day = subject[7]
        start_time    = subject[8]
        end_time      = subject[9]

        # Convert course_id → course_name
        course_data = find_by_column(conn, "COURSES", "course_id", course_id)
        course_name = course_data[1] if course_data else "Unknown"

        rowdata.append((subject_code, subject_name, course_name, teacher, units, scheduled_day, start_time, end_time))

    # ── Tableview ──
    style = tkttk.Style()
    style.configure("Treeview", rowheight=40)

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


def build_add_subject_tab(parent, switch_cb, conn):
    # Main container
    tab_container = tk.Frame(parent, bg=WHITE)
    tab_container.pack(fill="both", expand=True)

    container_content = tk.Frame(tab_container, bg=WHITE)
    container_content.pack(fill="both", expand=True, padx=40, pady=(34, 0))

    tk.Label(container_content, text="Add New Subject", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="center")

    rows_config = [
        (0, 1),
        (0, 2),
        (0, 2),
        (0, 1),
        (0, 1),
        (0, 2)
    ]

    class SubjectForm(Form):
        def onSubmit(self):
            course_code = course_code_field.get_input()
            course_title = course_title_field.get_input()
            year_level: str = year_level_field.get_input()
            teacher = teachers_field.get_input()
            units = course_units_field.get_input()
            department = department_field.get_input()
            scheduled_day = scheduled_day_field.get_input()
            start_time = start_time_field.get_input()
            end_time = end_time_field.get_input()

            # ── Validation ──
            if not course_code or course_code == "e.g CS 101":
                print("no course code!")
                return

            if not course_title or course_title == "e.g Introduction to Computing":
                print("no course title!")
                return

            if not teacher or teacher == "e.g John Christian Lorr":
                print("no teacher!")
                return

            if not units or units == "e.g 3":
                print("no units!")
                return

            if not scheduled_day:
                print("no scheduled day!")
                return

            if not start_time or start_time == "eg. 7:00 AM":
                print("no start time!")
                return

            if not end_time or end_time == "eg. 12:00 PM":
                print("no end time!")
                return

            subject_data = [
                course_code,
                course_title,
                int(year_level[0]),
                teacher,
                department,
                float(units),  # units is REAL in DB
                scheduled_day,
                start_time,
                end_time
            ]

            is_sucess, error = create_new_subject(conn, subject_data)

            if is_sucess:
                toast = ToastNotification(
                    title="Successfully Added.",
                    message=f"Subject {course_title} has been added to the database",
                    duration=5000,
                    bootstyle="success"
                )
                toast.show_toast()
                switch_cb("Subjects List")
            else:
                toast = ToastNotification(
                    title="Failed to create a subject",
                    message=error,
                    duration=5000,
                    bootstyle="danger"
                )
                toast.show_toast()
                switch_cb("Subjects List")



    subject_form = SubjectForm(container_content, rows_config)

    row_1_frame = subject_form._get_rows_field(0)
    course_code_field = Fields(row_1_frame, "entry", column_index=0, field_label_text="Course Code",
                              placeholder_text="e.g CS 101" )

    row_2_frame = subject_form._get_rows_field(1)
    course_title_field = Fields(row_2_frame, "entry", column_index=0, field_label_text="Course Title",
                               placeholder_text="e.g Introduction to Computing")
    year_level_field = Fields(row_2_frame, "combo_box", column_index=1,
                              field_label_text="Year Level",
                              options=["1st year", "2nd year", "3rd year", "4th year"])

    row_3_frame = subject_form._get_rows_field(2)
    teachers_field = Fields(row_3_frame, "entry", column_index=0, field_label_text="Proffesor Name",
                               placeholder_text="e.g John Christian Lorr")
    course_units_field = Fields(row_3_frame, "entry", column_index=1, field_label_text="Units",
                               placeholder_text="e.g 3")

    row_4_frame = subject_form._get_rows_field(3)
    department_field = Fields(row_4_frame, "combo_box", column_index=0,field_label_text="Course",
                    options=['BS Information Technology',
                    'BS Computer Science',
                    'BS Hospital Management',
                    'BS Education',
                    'BS Business Administration',
                    'BS Psychology'])

    row_5_frame = subject_form._get_rows_field(4)

    # Day of the week
    scheduled_day_field = Fields(row_5_frame, "combo_box", column_index=0,
                                 field_label_text="Day",
                                 options=["Monday", "Tuesday", "Wednesday",
                                          "Thursday", "Friday", "Saturday"])


    row_6_frame = subject_form._get_rows_field(5)
    start_time_field = Fields(row_6_frame, "entry", column_index=0,
                              field_label_text="Start Time", placeholder_text="eg. 7:00 AM")

    # End time
    end_time_field = Fields(row_6_frame, "entry", column_index=1,
                            field_label_text="End Time", placeholder_text="eg. 12:00 PM")
