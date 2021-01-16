import os

os.environ['KIVY_GL_BECKEND'] = 'angle_sdl2'

from kivymd.app import MDApp

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.label import MDLabel

from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.lang import Builder

from plyer import filechooser

import pandas as pd
import os, time

from bhartipay import StartProccess
import chromedriver_autoinstaller
from selenium import webdriver
import pandas as pd
from datetime import datetime
from report_table import Reports

from kivy import Config

Config.set('graphics', 'multisamples', '0')

# url = 'https://dcrgpay.com/payment/'

url = 'https://merchant.bhartipay.com/formpay/i/97099'

class WelcomeScreen(Screen):
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
			df = pd.read_csv(self.file, converters={'cvv': lambda x: str(x), 'pin': lambda x: str(x)})
			df['date'] = pd.to_datetime(df.date)
			chromedriver_autoinstaller.install()
			driver = webdriver.Chrome()
			for index, row in df.iterrows():
				n_trans = 5
				retry = 5
				failed = 0
				success_status = 0
				print("row is", row)
				while (n_trans != success_status) and (retry!=0) and (failed!=3):
					print("ntrans", n_trans, "success", success_status, "retry", retry, "failed", failed)
					if failed == 3:
						print("failed break")
						break
					driver.get(url)
					sp = StartProccess(driver, row.to_dict())
					if not sp.Completed():
					    failed += 1
					    print("failed")
					else:
					    if sp.getStatus():
					        success_status += 1
					        print("success")
					    else:
					        retry -= 1
					        print("not success")

					if retry == 0:
					    if success_status > 0 and success_status < n_trans:
					        retry = n_trans - success_status
					        print("in retry if")
					    else:
					    	print("in retry else")
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
