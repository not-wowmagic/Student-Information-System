import tkinter as tk
from tkinter import ttk as tkttk

from ttkbootstrap.widgets import ToastNotification
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import PRIMARY
from database.crud.events import get_events
from database.db_utils import find_by_column
from backend.backend import create_new_event
from frontend.components.fields import Fields
from frontend.components.form import Form

NAV_BG        = "#001f5b"
WHITE         = "#ffffff"
TEXT_PRIMARY  = "#111827"
TEXT_MUTED    = "#6b7280"
CARD_BORDER   = "#e2e8f0"

def build_events_list_tab(parent, switch_cb, conn):
    container = tk.Frame(parent, bg=WHITE)
    container.pack(fill="both", expand=True)

    # Header
    top_bar = tk.Frame(container, bg=WHITE)
    top_bar.pack(fill="x", pady=(48, 16), padx=48)
    tk.Label(top_bar, text="Event Management", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left")

    btn_add = tk.Button(top_bar, text="➕ Add Event", font=("Segoe UI", 9, "bold"), fg=WHITE, bg=NAV_BG, relief="flat", padx=16, pady=6, cursor="hand2", command=lambda: switch_cb("Add Event"))
    btn_add.pack(side="right")

    tk.Frame(container, bg=CARD_BORDER, height=1).pack(fill="x", padx=48, pady=16)

    # ── Fetch data ──
    events = get_events(conn)
    print(events)
    coldata = [
        {"text": "Title",      "stretch": True},
        {"text": "Type",       "stretch": True},
        {"text": "Department", "stretch": True},
        {"text": "Location", "stretch": True},
        {"text": "Start Time", "stretch": True},
        {"text": "End Time",   "stretch": True},
        {"text": "Date", "stretch": True},
    ]

    rowdata = []
    for event in events:
        # id, title, event_type, event_date, start_time, end_time, location, department_id
        title       = event[1]
        event_type  = event[2]
        event_date  = event[3]
        start_time  = event[4] if event[4] else "—"
        end_time    = event[5] if event[5] else "—"
        location    = event[6] if event[6] else "—"
        dept_id     = event[7]

        if dept_id is None:
            dept_name = "All Departments"
        else:
            dept_data = find_by_column(conn, "DEPARTMENT", "id", dept_id)
            dept_name = dept_data[1] if dept_data else "Unknown"

        rowdata.append((title, event_type, dept_name, location, start_time, end_time, event_date))

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


def build_add_event_tab(parent, switch_cb, conn):
    # Main container
    tab_container = tk.Frame(parent, bg=WHITE)
    tab_container.pack(fill="both", expand=True)

    container_content = tk.Frame(tab_container, bg=WHITE)
    container_content.pack(fill="both", expand=True, padx=40, pady=(34, 0))

    tk.Label(container_content, text="Create New Event", font=("Georgia", 24), fg=TEXT_PRIMARY, bg=WHITE).pack(anchor="center")

    rows_config = [
        (0, 1),
        (0, 1),
        (0, 2),
        (0, 1),
        (0, 1),
        (0, 1)
    ]

    class EventForm(Form):
        def onSubmit(self):
            title = event_title_field.get_input()
            event_date = event_date_time_field.get_input()
            start_time = start_time_field.get_input()
            end_time = end_time_field.get_input()
            event_type = event_type_field.get_input()
            department = department_field.get_input()

            # ── Optional fields ──
            LOCATION_PLACEHOLDER = "e.g Unversity Grand Hall"
            raw_location = event_location_field.get_input()
            location = None if (not raw_location or raw_location == LOCATION_PLACEHOLDER) else raw_location

            START_PLACEHOLDER = "eg. 7:00 AM"
            END_PLACEHOLDER = "eg. 12:00 PM"
            start_time = None if (not start_time or start_time == START_PLACEHOLDER) else start_time
            end_time = None if (not end_time or end_time == END_PLACEHOLDER) else end_time

            department = None if department == "All Departments" else department

            # ── Validation ──
            if not title or title == "e.g Annual Tech Symposium":
                print("no title!")
                return

            if not event_date:
                print("no date!")
                return

            if not event_type:
                print("no event type!")
                return

            if not department:
                print("no department!")
                return

            event_data = [
                title,
                event_type,
                event_date,
                start_time,
                end_time,
                location,
                department
            ]

            create_new_event(conn, event_data)

            toast = ToastNotification(
                title="Successfully Added.",
                message=f"Event '{title}' has been added.",
                duration=5000,
            )
            toast.show_toast()
            switch_cb("Events List")

    event_form = EventForm(container_content, rows_config)

    row_1_frame = event_form._get_rows_field(0)
    event_title_field = Fields(row_1_frame, "entry", column_index=0, field_label_text="Event Title",
                              placeholder_text="e.g Annual Tech Symposium" )

    row_2_frame = event_form._get_rows_field(1)
    event_date_time_field = Fields(row_2_frame, "date_entry", column_index=0, field_label_text="Date")

    row_3_frame =  event_form._get_rows_field(2)
    start_time_field = Fields(row_3_frame, "entry", column_index=0,
                              field_label_text="Start Time", placeholder_text="eg. 7:00 AM")
    end_time_field = Fields(row_3_frame, "entry", column_index=1,
                            field_label_text="End Time", placeholder_text="eg. 12:00 PM")

    row_4_frame = event_form._get_rows_field(3)
    event_location_field = Fields(row_4_frame, "entry", column_index=0, field_label_text="Location",
                               placeholder_text="e.g Unversity Grand Hall")


    row_5_frame = event_form._get_rows_field(4)
    event_type_field = Fields(row_5_frame, "combo_box", column_index=0, field_label_text="Event Type",
                               options=[
                                   "Academic Sports",
                                   "Seminar"
                               ]
                               )

    row_6_frame = event_form._get_rows_field(5)
    department_field = Fields(row_6_frame, "combo_box", column_index=0, field_label_text="Department",
                              options=[
                                  "All Departments",
                                  "College of Information Technology",
                                  "College of Business",
                                  "College of Education",
                                  "College of Hospitality Management",
                                  "College of Psychology"
                              ])