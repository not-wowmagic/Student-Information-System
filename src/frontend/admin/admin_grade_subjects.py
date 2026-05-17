import tkinter as tk
from ttkbootstrap import Entry
from ttkbootstrap.widgets import ToastNotification

NAV_BG        = "#001f5b"
WHITE         = "#ffffff"
TEXT_PRIMARY  = "#111827"
TEXT_MUTED    = "#6b7280"
CARD_BORDER   = "#e2e8f0"


def build_student_grades_tab(parent, switch_cb, conn):
    from database.crud.students import search_student, get_student_subjects
    from database.crud.students import update_student_grade
    from database.db_utils import find_by_column

    main_page = tk.Frame(parent, bg=WHITE)
    main_page.pack(fill="both", expand=True)

    tk.Label(main_page, text="Student Grades", font=("Georgia", 24),
             fg=TEXT_PRIMARY, bg=WHITE).pack(pady=(48, 0), padx=48, anchor="w")

    tk.Label(main_page,
             text="Search for a student to assign or update their subject grades.",
             font=("Segoe UI", 10), fg=TEXT_MUTED, bg=WHITE).pack(
        pady=(4, 32), padx=48, anchor="w")

    # ── SEARCH BAR ────────────────────────────────────────────────────────────
    search_section = tk.Frame(main_page, bg=WHITE)
    search_section.pack(fill="x", padx=48, pady=(0, 16))

    tk.Label(search_section, text="Student ID:",
             font=("Segoe UI", 10, "bold"),
             fg=TEXT_PRIMARY, bg=WHITE).pack(side="left", padx=(0, 12))

    search_input_frame = tk.Frame(search_section, bg="#f4f4f5", height=40)
    search_input_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))
    search_input_frame.pack_propagate(False)

    student_id_input = tk.Entry(
        search_input_frame,
        font=("Segoe UI", 10), bg="#f4f4f5", fg=TEXT_MUTED,
        relief="flat", bd=0, insertbackground=TEXT_PRIMARY
    )
    student_id_input.pack(fill="both", expand=True, padx=16, pady=8)
    student_id_input.insert(0, "e.g. 25-0000")

    def _clear_ph(e):
        if student_id_input.get() == "e.g. 25-0000":
            student_id_input.delete(0, "end")
            student_id_input.config(fg=TEXT_PRIMARY)

    def _restore_ph(e):
        if not student_id_input.get().strip():
            student_id_input.insert(0, "e.g. 25-0000")
            student_id_input.config(fg=TEXT_MUTED)

    student_id_input.bind("<FocusIn>",  _clear_ph)
    student_id_input.bind("<FocusOut>", _restore_ph)

    tk.Frame(main_page, bg=CARD_BORDER, height=1).pack(fill="x", padx=48, pady=(0, 24))

    # ── RESULTS AREA ──────────────────────────────────────────────────────────
    results_area = tk.Frame(main_page, bg=WHITE)
    results_area.pack(fill="both", expand=True, padx=48)

    # ── GRADE FORM ────────────────────────────────────────────────────────────
    def build_grade_form(student_data):
        for w in results_area.winfo_children():
            w.destroy()

        grade_entries  = {}   # subject_id → Entry widget
        include_in_gwa = {}   # subject_id → BooleanVar (checkbox state)

        course_info = find_by_column(conn, "COURSES", "course_id", student_data[2])
        course_name = course_info[1] if course_info else "Unknown"

        # ── Student info banner ──
        banner = tk.Frame(results_area, bg="#f0f4ff",
                          highlightthickness=1, highlightbackground="#c7d2fe")
        banner.pack(fill="x", pady=(0, 20))
        inner = tk.Frame(banner, bg="#f0f4ff")
        inner.pack(fill="x", padx=24, pady=14)

        tk.Label(inner, text=f"👤  {student_data[1]}",
                 font=("Segoe UI", 14, "bold"), fg=NAV_BG, bg="#f0f4ff").pack(side="left")
        tk.Label(inner,
                 text=f"{course_name}  |  Year {student_data[3]}  |  {student_data[7]}",
                 font=("Segoe UI", 10), fg=TEXT_MUTED, bg="#f0f4ff").pack(side="left", padx=(16, 0))

        # ── Fetch subjects ──
        subject_list = get_student_subjects(conn, student_data[0])
        print(subject_list)
        if not subject_list:
            tk.Label(results_area, text="No subjects found for this student.",
                     font=("Segoe UI", 12), fg=TEXT_MUTED, bg=WHITE).pack(anchor="w")
            return

        # ── Table header ──
        hdr = tk.Frame(results_area, bg="#f8fafc",
                       highlightthickness=1, highlightbackground=CARD_BORDER)
        hdr.pack(fill="x")

        for col_text, col_width, anchor in [
            ("Subject Code", 14, "w"),
            ("Subject Name", 32, "w"),
            ("Units",         7, "w"),
            ("Grade",        12, "w"),
            ("In GWA",        8, "center"),
            ("Edit",          5, "center"),
        ]:
            tk.Label(hdr, text=col_text, width=col_width, anchor=anchor,
                     font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED,
                     bg="#f8fafc").pack(side="left", padx=(16 if col_text == "Subject Code" else 0, 0), pady=10)

        # ── Table rows ──
        rows_frame = tk.Frame(results_area, bg=WHITE)
        rows_frame.pack(fill="x")

        def make_row(subject_row):
            subject_id    = subject_row[2]
            subject_name  = subject_row[4]
            subject_code  = subject_row[5]
            subject_units = subject_row[7]
            current_grade = subject_row[3]

            row = tk.Frame(rows_frame, bg=WHITE,
                           highlightthickness=1, highlightbackground=CARD_BORDER)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=subject_code, width=14, anchor="w",
                     font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left", padx=16, pady=10)

            tk.Label(row, text=subject_name, width=32, anchor="w",
                     font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg=WHITE).pack(side="left", pady=10)

            tk.Label(row, text=str(subject_units), width=7, anchor="w",
                     font=("Segoe UI", 10), fg=TEXT_MUTED, bg=WHITE).pack(side="left", pady=10)

            # Grade entry (readonly by default)
            grade_entry = Entry(row, width=12, state="normal")
            grade_entry.pack(side="left", padx=(0, 8), pady=10)
            grade_entry.insert(0, str(current_grade) if current_grade is not None else "N/A")
            grade_entry.config(state="readonly")
            grade_entries[subject_id] = grade_entry

            # ── GWA checkbox ──
            gwa_var = tk.BooleanVar(value=True)
            include_in_gwa[subject_id] = gwa_var

            chk = tk.Checkbutton(
                row, variable=gwa_var,
                bg=WHITE, activebackground=WHITE,
                cursor="hand2", width=7,
                command=lambda: recalculate_gwa()
            )
            chk.pack(side="left", pady=10)

            # ── Per-row edit icon ──
            edit_state = {"on": False}

            def toggle_row_edit(entry=grade_entry, r=row, st=edit_state, btn_ref=[None]):
                st["on"] = not st["on"]
                if st["on"]:
                    # Switch to editable: clear N/A so user can type cleanly
                    entry.config(state="normal")
                    if entry.get().strip().upper() == "N/A":
                        entry.delete(0, "end")
                    btn_ref[0].config(text="✓", fg="#16a34a", bg="#dcfce7")
                    r.config(highlightbackground="#93c5fd")
                else:
                    entry.config(state="readonly")
                    if not entry.get().strip():
                        entry.config(state="normal")
                        entry.insert(0, "N/A")
                        entry.config(state="readonly")
                    btn_ref[0].config(text="✎", fg=NAV_BG, bg="#e0e7ff")
                    r.config(highlightbackground=CARD_BORDER)
                    recalculate_gwa()

            edit_btn = tk.Button(
                row, text="✎",
                font=("Segoe UI", 9), fg=NAV_BG, bg="#e0e7ff",
                relief="flat", padx=8, pady=3,
                cursor="hand2",
                command=toggle_row_edit
            )
            edit_btn.pack(side="left", padx=(0, 12), pady=8)

            # give toggle_row_edit a reference to its own button
            # via the mutable default list trick
            edit_btn.config(command=lambda b=edit_btn, e=grade_entry, r=row, st=edit_state:
                            toggle_row_edit_with_btn(b, e, r, st))

        def toggle_row_edit_with_btn(btn, entry, row, st):
            st["on"] = not st["on"]
            if st["on"]:
                entry.config(state="normal")
                if entry.get().strip().upper() == "N/A":
                    entry.delete(0, "end")
                btn.config(text="✓", fg="#16a34a", bg="#dcfce7")
                row.config(highlightbackground="#93c5fd")
            else:
                entry.config(state="readonly")
                if not entry.get().strip():
                    entry.config(state="normal")
                    entry.insert(0, "N/A")
                    entry.config(state="readonly")
                btn.config(text="✎", fg=NAV_BG, bg="#e0e7ff")
                row.config(highlightbackground=CARD_BORDER)
                recalculate_gwa()

        for subj in subject_list:
            make_row(subj)

        # ── GWA card ──
        gwa_card = tk.Frame(results_area, bg="#f0f4ff",
                            highlightthickness=1, highlightbackground="#c7d2fe")
        gwa_card.pack(fill="x", pady=(16, 0))

        gwa_inner = tk.Frame(gwa_card, bg="#f0f4ff")
        gwa_inner.pack(fill="x", padx=24, pady=14)

        gwa_label = tk.Label(gwa_inner, text="GWA: N/A",
                             font=("Segoe UI", 16, "bold"),
                             fg=NAV_BG, bg="#f0f4ff")
        gwa_label.pack(side="left")


        def recalculate_gwa():
            total       = 0.0
            total_units = 0.0

            for subj in subject_list:
                sid   = subj[2]
                units = float(subj[7])

                # Skip if user unchecked this subject
                if not include_in_gwa.get(sid, tk.BooleanVar(value=True)).get():
                    continue

                entry = grade_entries.get(sid)
                if not entry:
                    continue

                raw = entry.get().strip()
                if not raw or raw.upper() == "N/A":
                    continue

                try:
                    total       += float(raw) * units
                    total_units += units
                except ValueError:
                    pass

            gwa_label.config(
                text=f"GWA: {round(total / total_units, 2)}" if total_units > 0 else "GWA: N/A"
            )

        tk.Button(gwa_inner, text="↻ Recalculate",
                  command=recalculate_gwa,
                  font=("Segoe UI", 9), fg=NAV_BG, bg="#e0e7ff",
                  relief="flat", padx=12, pady=4).pack(side="left", padx=(16, 0))

        tk.Label(gwa_inner,
                 text="Tip: uncheck ✓ on a row to exclude that subject from GWA",
                 font=("Segoe UI", 9), fg=TEXT_MUTED, bg="#f0f4ff").pack(side="left", padx=(20, 0))

        # ── Footer ──
        footer = tk.Frame(results_area, bg=WHITE)
        footer.pack(fill="x", pady=(20, 48))

        tk.Button(footer, text="← Back",
                  command=lambda: switch_cb("Student List"),
                  bg=WHITE, fg=TEXT_PRIMARY,
                  relief="solid", bd=1,
                  padx=16, pady=8).pack(side="left")

        def save_grades():
            skipped = []

            for subj in subject_list:
                sid   = subj[2]
                code  = subj[5]
                entry = grade_entries.get(sid)
                if not entry:
                    continue

                raw = entry.get().strip()
                if not raw or raw.upper() == "N/A":
                    continue   # nothing entered — leave grade as NULL

                try:
                    grade_value = float(raw)
                    update_student_grade(conn, student_data[0], sid, grade_value)
                except ValueError:
                    skipped.append(code)

            if skipped:
                ToastNotification(
                    title="Some grades were skipped",
                    message=f"Invalid values in: {', '.join(skipped)}",
                    duration=4000,
                    bootstyle="warning"
                ).show_toast()
            else:
                ToastNotification(
                    title="Grades Saved",
                    message=f"Grades for {student_data[1]} have been updated.",
                    duration=3000,
                    bootstyle="success"
                ).show_toast()
                switch_cb("Student List")

        tk.Button(footer, text="💾 Save Grades",
                  command=save_grades,
                  bg=NAV_BG, fg=WHITE,
                  relief="flat",
                  padx=20, pady=8).pack(side="right")

    # ── SEARCH ACTION ─────────────────────────────────────────────────────────
    def search_student_action():
        query = student_id_input.get().strip()
        if not query or query == "e.g. 25-0000":
            return

        for w in results_area.winfo_children():
            w.destroy()

        student_data = search_student(conn, query)

        if not student_data:
            tk.Label(results_area, text="❌ Student not found",
                     fg="#e11d48", bg=WHITE,
                     font=("Segoe UI", 12)).pack(anchor="w")
            return

        build_grade_form(student_data)

    tk.Button(search_section, text="Search",
              command=search_student_action,
              fg=WHITE, bg=NAV_BG,
              font=("Segoe UI", 9, "bold"),
              relief="flat",
              padx=16, pady=4).pack(side="left")

    student_id_input.bind("<Return>", lambda e: search_student_action())