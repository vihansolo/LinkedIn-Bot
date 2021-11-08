"""
LinkedIn Profile Scraper Bot

@2020 Created by Vihang Garud.

"""

# Importing libraries
import time
import pandas as pd
from selenium import webdriver
import tkinter as tk
from tkinter import messagebox

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


def scrape_profiles():

	"""
	Driver function to scrape profiles

	"""

	# User leaves a field empty before clicking scrape profiles button
	if user_email_entry.get() == '' or user_password_entry.get() == '' or query_entry.get() == '' or location_entry.get() == '':
		messagebox.showwarning("Field(s) Empty", "Field(s) cannot be empty.")

	# Incorrect email id format
	elif '@' not in user_email_entry.get():
		messagebox.showerror("Incorrent Email", "Please enter a proper email ID.")

	# The number of profiles exceeds the limit
	elif no_of_profiles_entry.get() > 80:
		messagebox.showinfo("Try a lower number", "The number of profiles entered might lead to an account block.")

	else:

		# Chrome.exe path
		options = Options()
		options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"

		# Open chrome web and navigate to LinkedIn
		driver = webdriver.Chrome(options = options, executable_path = "chromedriver.exe")
		driver.get("https://www.linkedin.com/")

		# Login with username/password
		driver.find_element_by_class_name("nav__button-secondary").click()
		time.sleep(1)

		# Find and enter the user email id and password
		driver.find_element_by_id("username").send_keys(user_email_entry.get())
		driver.find_element_by_id("password").send_keys(user_password_entry.get())

		# Find and click the sign in button
		driver.find_element_by_css_selector(".btn__primary--large").click()

		try:
			# Search for the query
			driver.get("https://www.linkedin.com/search/results/index/?keywords=" + query_entry.get())
			time.sleep(2)

			# Search based on a location
			driver.find_element_by_xpath("//button[@aria-label='People']").click()
			time.sleep(5)
			driver.find_element_by_xpath("//button[contains(@aria-label, 'Locations filter.')]").click()
			driver.find_element_by_xpath("//input[@aria-label='Add a location']").send_keys(location_entry.get())
			time.sleep(2)
			driver.find_element_by_xpath("//span[@class='search-typeahead-v2__hit-text t-14 t-black ']").click()
			time.sleep(3)
			driver.find_element_by_xpath("(//button[contains(@aria-label, 'Apply')])[2]").click()
			time.sleep(3)

			connect_or_get_profile_data(driver)

			driver.close()

		except:
			messagebox.showerror("Problem Connecting", "There was a network loss connecting to LinkedIn. Please try again.")


def connect_or_get_profile_data(driver):

	"""
	Connects to a new profile or gets required data for each profile:
	1. Name 
	2. Email ID
	3. Designation

	:param driver: Gets the chrome driver

	"""

	profiles = driver.find_element_by_xpath("//*[@id='main']/div/div/div[2]/ul").find_elements_by_tag_name("li")

	data = []
	profile = []
	profile_no = 1

	# Scraping the provided number of profiles (10 profiles on 1 page)
	for page in range(no_of_profiles_entry.get() // 10):

		for _ in profiles:

			# Sends a connection request if the profile is not in connections already
			try:
				driver.find_element_by_xpath(("//*[@id='main']/div/div/div[2]/ul/li[" + str(profile_no) + "]/div/div/div[3]/button/span[text()='Connect']"))

				# Clicks 'Send' button followed by 'Connect'
				try:
					driver.find_element_by_xpath("//*[@id='main']/div/div/div[2]/ul/li[" + str(profile_no) + "]/div/div/div[3]/button").click()
					time.sleep(2)
					driver.find_element_by_xpath("//button[contains(@aria-label, 'Send')]").click()
					time.sleep(2)

				# If prompted to verify email
				except:
					time.sleep(5)
					driver.find_element_by_xpath("(//button[@aria-label='Dismiss'])[1]").click()

			except:
				pass

			# Connection request is pending
			try: 
				driver.find_element_by_xpath(("//*[@id='main']/div/div/div[2]/ul/li[" + str(profile_no) + "]/div/div/div[3]/button/span[text()='Pending']"))

			except:
				pass

			# Skipping companies
			try: 
				driver.find_element_by_xpath(("//*[@id='main']/div/div/div[2]/ul/li[" + str(profile_no) + "]/div/div/div[3]/button/span[text()='Follow']"))

			except:
				pass

			# Scrapes the connection (profile)
			try:
				time.sleep(5)
				driver.find_element_by_xpath(("//*[@id='main']/div/div/div[2]/ul/li[" + str(profile_no) + "]/div/div/div[3]/button/span[text()='Message']"))
				driver.find_element_by_xpath("//*[@id='main']/div/div/div[2]/ul/li[" + str(profile_no) + "]/div/div/div[2]/div[1]/div/div[1]/span/div/span[1]/span/a").click()

				# Get name, email id and designation of the connection
				# Name
				try:
					profile.append(driver.find_element_by_xpath("//li[@class='inline t-24 t-black t-normal break-words']").text)
				except:
					profile.append("?")

				# Email ID
				try:
					driver.find_element_by_xpath("//a[@data-control-name='contact_see_more']").click()
					time.sleep(2)
					profile.append(driver.find_element_by_xpath("//a[contains(@href, 'mailto')]").text)
					driver.find_element_by_xpath("//button[contains(@aria-label,'Dismiss')]").click()
					time.sleep(2)
				except:
					profile.append("?")

				# Designation
				try:
					profile.append(driver.find_element_by_xpath("//h2[contains(@class, 'mt1 t-18')]").text)
				except:
					profile.append("?")

				data.append(profile)
				driver.execute_script("window.history.go(-1)")

			except:
				pass

			profile_no += 1

		# Next page until the limit
		driver.get(driver.current_url + "&page=" + str(page + 2))
		profile_no = 1

	# There's no data to write to a csv file
	if len(data) == 0:
		messagebox.showinfo("All new Connections", "All the profiles parsed were not in the connections list. CSV file was not created.")

	else:

		# Writing scraped data to a csv file
		try:
			convert_to_csv("LinkedIn_" + query_entry.get() + "_" + location_entry.get() + ".csv", data)
			messagebox.showinfo("Scraping Done", "CSV file would now be available.")

		except:
			messagebox.showerror("No data scraped/csv exists", "There was no data to scrape or a csv file with the same name exists already.")


def convert_to_csv(file_name, data):

	"""
	Converts data list into a CSV file

	:param file_name: Name of the CSV file to be created
	:param data: Scraped data

	"""

	pd.DataFrame(data).to_csv(file_name, index = False, header = ["Name", "Email ID", "Designation"])


if __name__ == "__main__":

	# Configure GUI
	window = tk.Tk()
	window.title("LinkedIn Profile Scraper")
	window.configure(bg="white")
	window.state("zoomed")
	window.grid_rowconfigure(0, weight=1)
	window.grid_columnconfigure(0, weight=1)

	# Initialize entry variables
	user_email_entry = tk.StringVar()
	user_password_entry = tk.StringVar()
	query_entry = tk.StringVar()
	location_entry = tk.StringVar()
	no_of_profiles_entry = tk.IntVar()

	# Title of the application
	tk.Label(window, text = "LinkedIn Profile Scraper", font = ("Gill Sans MT", 40), bg = "white").grid(row = 0, columnspan = 2, pady = 70)

	# Username label and entry field
	tk.Label(window, text = "Email ID", font = ("Gill Sans MT", 14), bg = "white").grid(row = 1, column = 0, pady = 20, padx = 200)
	tk.Entry(window, font = ("Gill Sans MT", 14), width = 50, textvariable = user_email_entry).grid(row = 1, column = 1, padx = 200)

	# Password label and entry field
	tk.Label(window, text = "Password", font = ("Gill Sans MT", 14), bg = "white").grid(row = 2, column = 0, pady = 20, padx = 200)
	tk.Entry(window, font = ("Gill Sans MT", 14), width = 50, show = "\u2022", textvariable = user_password_entry).grid(row = 2, column = 1, padx = 200)

	# Query label and entry field
	tk.Label(window, text = "Query to search", font = ("Gill Sans MT", 14), bg = "white").grid(row = 3, column = 0, pady = 20, padx = 200)
	tk.Entry(window, font = ("Gill Sans MT", 14), width = 50, textvariable = query_entry).grid(row = 3, column = 1, padx = 200)

	# Location label and entry field
	tk.Label(window, text = "Location", font = ("Gill Sans MT", 14), bg = "white").grid(row = 4, column = 0, pady = 20, padx = 200)
	tk.Entry(window, font = ("Gill Sans MT", 14), width = 50, textvariable = location_entry).grid(row = 4, column = 1, padx = 200)

	# Number of profiles to scrape label and entry field
	tk.Label(window, text = "Number of profiles", font = ("Gill Sans MT", 14), bg = "white").grid(row = 5, column = 0, pady = 20, padx = 200)
	tk.Entry(window, font = ("Gill Sans MT", 14), width = 50, textvariable = no_of_profiles_entry).grid(row = 5, column = 1, padx = 200)

	# Scraping profiles button
	tk.Button(window, text = "Scrape Profiles/Connect", font = ("Gill Sans MT", 14), width = 50, bg = "white", command = scrape_profiles).grid(row = 6, columnspan = 2, pady = 100)

	window.mainloop()
