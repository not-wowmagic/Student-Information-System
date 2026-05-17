from tkinter import StringVar
from tkinter.scrolledtext import ScrolledText

from ttkbootstrap import Label, Entry, Frame, Menubutton, Menu, Combobox, Radiobutton, DateEntry
from ttkbootstrap.constants import LEFT

from constants import FONT_DEFAULT_NAME


class Fields:
    def __init__(self, parent, type_of_field: str, column_index, placeholder_text="", field_label_text="", options:list[str] =["test"]):

        self.date_entry = None
        self.radio_button = None
        self.menu_btn = None
        self.option_var = None
        self.entry = None
        self.label = None
        self.option_var = StringVar()
        self.frame = Frame(parent)
        self.frame.grid(row=0, column=column_index, sticky='nsew', padx=(0, 24))

        match type_of_field:
            case "entry":
                self.create_entry(field_label_text, placeholder_text)
            case "menu":
                self.create_menu(field_label_text, options)
            case "combo_box":
                self.create_combo_box(field_label_text, placeholder_text, options)
            case "radio_button":
                self.create_radio_button(field_label_text, options)
            case "date_entry":
                self.create_date_entry(field_label_text)
            case "scrolled_text":
                self.create_scrolled_text(field_label_text)

    def create_entry(self, field_label, placeholder_text):
        self.label = Label(self.frame, text=field_label, font=("Segoe UI", 11, "bold"))
        self.label.pack(anchor="w")

        self.entry = ser_input = Entry(self.frame, font=(FONT_DEFAULT_NAME, 11))
        self.entry.pack(fill="x", ipady=4, pady=(4, 8))
        self.entry.insert(0, placeholder_text)

    def create_menu(self, field_label, options: list[str]):
        self.label = Label(self.frame, text=field_label, font=("Segoe UI", 11, "bold"))
        self.label.pack(anchor="w")

        self.menu_btn = Menubutton(self.frame, bootstyle="dark", text=f"Select {field_label}")
        self.menu_btn.pack(anchor="w", fill="x")

        self.menu = Menu(self.menu_btn, tearoff=0)

        for option in options:
            self.menu.add_radiobutton(
                label=option,
                variable=self.option_var
            )

        self.menu_btn['menu'] = self.menu

    def create_combo_box(self, field_label_text, placeholder_text, options):
        self.label = Label(self.frame, text=field_label_text, font=("Segoe UI", 11, "bold"))
        self.label.pack(anchor="w")

        self.combo_box = Combobox(self.frame, values=options, state="readonly")

        # Set a placeholder that is NOT in the options list
        self.combo_box.set(f"Select {placeholder_text}")

        self.combo_box.pack(fill="x", ipady=4, anchor="center")

    def create_radio_button(self, field_label_text, options: list[str]):
        self.label = Label(self.frame, text=field_label_text, font=("Segoe UI", 11, "bold"))
        self.label.pack(anchor="w")
        self.option_var = StringVar(value=options[0])

        for option in options:
            self.radio_button = Radiobutton(self.frame, text=option, variable=self.option_var, value=option)
            self.radio_button.pack(side=LEFT, padx=(0, 18), anchor="center")

    def create_date_entry(self, field_label_text):
        self.label = Label(self.frame, text=field_label_text, font=("Segoe UI", 11, "bold"))
        self.label.pack(anchor="w")
        
        
        self.date_entry = DateEntry(self.frame, dateformat='%m/%d/%Y')
        self.date_entry.pack(fill="x", ipady=4)
        
    def create_scrolled_text(self, field_label):
        self.label = Label(self.frame, text=field_label, font=("Segoe UI", 11, "bold"))
        self.label.pack(anchor="w")
        self.scrolled_text = ScrolledText(self.frame, font=(FONT_DEFAULT_NAME, 11), height=6)
        self.scrolled_text.pack(fill="x", pady=(4, 8))

    def get_input(self):
        if self.entry is not None:
            return self.entry.get()

        if self.menu_btn is not None:
            return self.option_var.get()

        if hasattr(self, 'combo_box') and self.combo_box is not None:
            return self.combo_box.get()

        if self.date_entry is not None:
            return self.date_entry.entry.get()

        if self.radio_button is not None:
            return self.option_var.get()

        if hasattr(self, 'scrolled_text') and self.scrolled_text is not None:
            return self.scrolled_text.get("1.0", "end-1c")

        return None