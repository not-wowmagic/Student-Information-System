import tkinter as tk
from abc import ABC, abstractmethod
from ttkbootstrap import Button, Frame
from ttkbootstrap.constants import LEFT
from ttkbootstrap.widgets.scrolled import ScrolledFrame


class Form(ABC):
    def __init__(self, parent, row_configs):
        self.form_field = ScrolledFrame(parent, autohide=True, style="White.TFrame")
        self.form_field.pack(fill="both", expand=True)
        self.form_field.autohide_scrollbar()
        self.has_submit = False
        self.rows_field = []
        self.build_rows(row_configs)

        self.frame_button_container = Frame(self.form_field, style="White.TFrame")
        self.frame_button_container.pack(fill="x", pady=(18, 0))

        self.button = Button(self.frame_button_container, bootstyle="primary", text="Submit", command=self.onSubmit)
        self.button.pack(side=LEFT, ipady=3, ipadx=14, padx=(0, 12))
        self.button = Button(self.frame_button_container, bootstyle="primary", text="Cancel", command=self.onSubmit)
        self.button.pack(side=LEFT, ipady=3, ipadx=14, padx=(0, 12))
    def build_rows(self, row_configs: list[tuple[int, int]]):
        for config in row_configs:
            rows = config[0]
            columns = config[1]

            row_field = RowField(self.form_field, rows, columns)
            row_field.row.pack(fill="x", pady=14)

            self.rows_field.append(row_field)

    def _get_rows_field(self, row_number: int):
        return self.rows_field[row_number].get_row_widget()

    @abstractmethod
    def onSubmit(self):
        """
        submit must be implemented
        :return:
        """
        pass



class RowField:
    def __init__(self, parent, rows: int, columns: int):
        self.row = tk.Frame(parent, bg="white")

        for index in range(0, columns):
            self.row.columnconfigure(index, weight=1)


        for index in range(0, rows):
            self.row.rowconfigure(index, weight=1)


    def get_row_widget(self):
        return self.row