from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from faker import Faker
from random import randint
from db import DB

f = Faker()

card_url = 'https://merchant.bhartipay.com/crm/jsp/paymentPage.jsp'
response_url = 'https://merchant.bhartipay.com/crm/jsp/response.jsp'
otp_url = 'https://prdrupayias.insolutionsglobal.com/NPCI_IAS_NSDL/authOTP.do'

bhartipay = {'card': 'cardNumber', 'month': 'ccExpiryMonth', 'year': 'ccExpiryYear', 'cvv': 'cvvNumber', 'name': 'cardName', 'submit': 'ccSubmit'}


class StartProccess():
	amount = None
	cname = None
	cphone = None
	cemail = None
	driver = None
	card_id = None
	dc = {}
	status = False
	response_dc = {}

	def __init__(self, driver, dc):
		self.amount = str(1)
		self.cname = f.name()
		self.cphone = randint(9000000000, 9999999999)
		self.cemail = f.email()
		self.driver = driver
		self.dc = dc
		print(self.dc)

	def FormFill(self):
		elem = self.driver.find_element_by_id("amount")
		elem.send_keys(self.amount)
		elem = self.driver.find_element_by_id("cname")
		elem.send_keys(self.cname)
		elem = self.driver.find_element_by_id("cphone")
		elem.send_keys(self.cphone)
		elem = self.driver.find_element_by_id("cemail")
		elem.send_keys(self.cemail)
		elem = self.driver.find_element_by_id("button")
		elem.click()
		db = DB('Cards')
		db.InsertOne(self.dc.copy())
		self.card_id = db.getDetail(**{'card_num': self.dc['card_num']})[0]

	def PaymentPage(self):
		assert 'DCRG TECHNOLOGIES PVT LTD' in self.driver.page_source
		elem = self.driver.find_element_by_id('totalAmount')
		assert self.amount in elem.text
		elem = self.driver.find_element_by_id(bhartipay['card'])
		elem.send_keys(self.dc['card_num'])
		elem = Select(self.driver.find_element_by_id(bhartipay['month']))
		elem.select_by_value('%02d' % self.dc['date'].month)
		elem = Select(self.driver.find_element_by_id(bhartipay['year']))
		elem.select_by_value(str(self.dc['date'].year))
		elem = self.driver.find_element_by_id(bhartipay['cvv'])
		elem.send_keys(self.dc['cvv'])
		elem = self.driver.find_element_by_id(bhartipay['name'])
		elem.send_keys(self.cname)
		elem = self.driver.find_element_by_id(bhartipay['submit'])
		elem.click()
	
	def OtpForm(self):
		elem = self.driver.find_element_by_id("txtipin")
		elem.send_keys(self.dc['pin'])
		elem = self.driver.find_element_by_id("btnverify")
		elem.click()

	def TransactionResponse(self):
		device_list_table = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
		result = device_list_table.find_elements_by_tag_name('tr')
		for i in range(len(result)):
		    device_list_elements = result[i].find_elements_by_tag_name('td')
		    if len(device_list_elements)>1:
		        key, value = device_list_elements[1].text.strip(), device_list_elements[3].text.strip()
		        if 'ID' in key:
		        	self.response_dc['tid'] = value
		        elif 'STATUS' in key:
		        	self.response_dc['status'] = value
		        elif 'MESSAGE' in key:
		        	self.response_dc['message'] = value

		self.response_dc['amount'] = self.amount
		self.response_dc['card_id'] = self.card_id
		print(self.response_dc)
		db = DB('Transactions')
		db.InsertOne(self.response_dc)

	def WaitForResponse(self, forurl):
		while self.driver.current_url != forurl:
			time.sleep(1)
			if self.driver.current_url == response_url:
				return self.TransactionResponse()
				break

	def Completed(self):
		try:
			self.FormFill()
			self.WaitForResponse(card_url)
			self.PaymentPage()
			self.WaitForResponse(otp_url)
			self.OtpForm()
		except Exception as e:
			print('in exception',e)
			return False
		else:
			while self.driver.current_url != response_url:
				time.sleep(1)
				self.TransactionResponse()
		finally:
			if self.response_dc['status'] == 'Success':
				self.status = True
				return True
			else:
				return False


	def getStatus(self):
		return self.status