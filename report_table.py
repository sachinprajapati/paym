from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.picker import MDDatePicker
from kivy.metrics import dp

from db import DB

class Reports(Screen):
    date = None
    date_widget = None
    alert = None

    def get_date(self, date):
        self.date = date
        db = DB('Transaction')
        self.clear_widgets()
        ls = db.DateFilter(date)
        len(ls)
        self.data_tables = MDDataTable(
            size_hint=(0.9, 0.8),
            use_pagination=True,
            pos_hint={"center_x": .5, "center_y": .6},
            column_data=[
                ("Card Number", dp(60)),
                ("CVV", dp(30)),
                ('Expiry', dp(30)),
                ("Pin", dp(20)),
                ("Success Count", dp(30)),
            ],
            row_data=ls,
        )
        self.add_widget(self.data_tables)
    
    def show_date_picker(self):
        if self.alert:
            self.remove_widget(self.alert)
        date_dialog = MDDatePicker(callback=self.get_date)
        date_dialog.open()