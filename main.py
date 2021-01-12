from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.properties import ListProperty
from kivy.lang import Builder

from kivymd.uix.label import MDLabel

from plyer import filechooser

import pandas as pd
import os, time

from bhartipay import StartProccess
import chromedriver_autoinstaller
from selenium import webdriver
import pandas as pd
from datetime import datetime

url = 'https://dcrgpay.com/payment/'

class WelcomeScreen(Screen):
	pass

class Reports(Screen):
	pass

class Second_Screen(Screen):
	file = None
	alert = None

	selection = ListProperty([])

	def choose(self):
		if self.alert:
			self.remove_widget(self.alert)
		filechooser.open_file(on_selection=self.handle_selection, filters=[("Excel Files", "*.csv")])

	def handle_selection(self, selection):
	    self.selection = selection

	def on_selection(self, *a, **k):
		self.ids.result.text = self.selection[0]
		self.file = self.selection[0]

	def StartRunning(self):
		if self.file and os.path.isfile(self.file):
			df = pd.read_csv(self.file)
			df['date'] = pd.to_datetime(df.date)
			chromedriver_autoinstaller.install()
			driver = webdriver.Chrome()
			for index, row in df.iterrows():
			    n_trans = 2
			    retry = 2
			    failed = 0
			    success_status = 0
			    while n_trans != success_status:
			        if failed == 3:
			            break
			        driver.get(url)
			        sp = StartProccess(driver, row.to_dict())
			        if not sp.Completed():
			            failed += 1
			            print("failed")
			            continue
			        else:
			            if sp.getStatus():
			                success_status += 1
			                print("success")
			            else:
			                retry -= 1
			                print("not success")
			        if retry == 0:
			            if success_status > 0:
			                retry = n_trans - success_status
			            else:
			                break
		else:
			print("in else")
			if not self.alert:
				self.alert = MDLabel(text="Please Select File",
                    halign="center",
                    theme_text_color='Error')
				self.add_widget(self.alert)


class WindowManager(ScreenManager):
    pass

class MainApp(MDApp):
	pass


if __name__ == "__main__":
    MainApp().run()
