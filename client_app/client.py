import requests
import re
import json

session = requests.Session()
GlobalURL = None
NewsSites = []

def client_get_agencies():
		global NewsSites

		response = session.get("https://newssites.pythonanywhere.com/api/directory/")
		
		if response.status_code == 200:
			agencies = json.loads(response.content.decode('utf-8'))
			for agency in agencies:
				NewsSites.append(agency)
			return 0
		else:
			if response.json()['message'] is not None:
				print(response.json()['message'])
				return 1
			else:
				print("An error occurred. Please try again.")
				return 1

def client_login(choice):
	global GlobalURL
	try:
		url = choice.split(" ")[1]
	except IndexError:
		print("Invalid URL. Please try again.")
		return

	if (not url.startswith("http://")) and (not url.startswith("https://")):
		print("Invalid URL. Please try again.")
		return
	
	if GlobalURL is not None:
		print("You are already logged in to a URL. Please logout first.")
		return

	username = input("Enter username: ")
	password = input("Enter password: ")
	
	print(url + "/api/login")
	response = session.post(url + "/api/login", data={"username": username, "password": password})
	print(response.json()['message'])
	if response.status_code == 200:
		GlobalURL = url

def client_logout():
	global GlobalURL
	if GlobalURL is None:
		print("Login for a valid URL first")
		return
	
	csrf_token = session.cookies.get('csrftoken')
	headers = {'X-CSRFToken': csrf_token} if csrf_token else {}

	response = session.post(GlobalURL + "/api/logout", headers=headers)
	GlobalURL = None
	print(response.json()['message'])

def client_post_story():
	global GlobalURL
	if GlobalURL is None:
		print("Login for a valid URL first")
		return
	
	csrf_token = session.cookies.get('csrftoken')
	headers = {'X-CSRFToken': csrf_token} if csrf_token else {}

	headline = input("Enter headline: ")
	category = input("Enter category: ")
	region = input("Enter region: ")
	details = input("Enter details: ")

	response = session.post(GlobalURL + "/api/stories", headers=headers, json={
		"headline": headline,
		"category": category,
		"region": region,
		"details": details
	})
	print(response.json()['message'])

def client_get_stories(choice):
	global GlobalURL
	global NewsSites
	if GlobalURL is None:
		print("Login for a valid URL first")
		return

	csrf_token = session.cookies.get('csrftoken')
	headers = {'X-CSRFToken': csrf_token} if csrf_token else {}

	pattern = r'^news(?:\s+-id=\'?\w*\'?)?(?:\s+-cat=\'?\w*\'?)?(?:\s+-reg=\'?\w*\'?)?(?:\s+-date=\'?\d{1,2}/\d{1,2}/\d{4}\'?)?$'

	if not re.match(pattern, choice):
		print("Invalid parameters. Please try again.")
		return
	
	matches = re.findall(r'(?:-([\w]+)=\'?([^\'\s]*)\'?)|(?:([^=&\s]+)=([^=&\s]+))', choice)

	id_value = None
	cat_value = None
	reg_value = None
	date_value = None

	for match in matches:
		if match[0] == "id":
			if not re.match(r'^[A-Z]{3}\d{2}$', match[1]):
				print("Invalid id. Please try again.")
				return
			id_value = match[1]
		elif match[0] == "cat":
			if not re.match(r'(pol|art|tech|trivia)', match[1]):
				print("Invalid category. Please try again.")
				return
			cat_value = match[1]
		elif match[0] == "reg":
			if not re.match(r'(uk|eu|w)', match[1]):
				print("Invalid region. Please try again.")
				return
			reg_value = match[1]
		elif match[0] == "date":
			date_value = match[1]
	
	responses = None
	if id_value is not None:
		found = False
		for site in NewsSites:
			print(site)
			if site['agency_code'] == id_value:
				found = True
				agency_name = site['agency_name']
				url = site['url']
				agency_code = site['agency_code']
				print(url + "/api/stories?story_cat=" + (cat_value if cat_value else "*") + "&story_region=" + (reg_value if reg_value else "*") + "&story_date=" + (date_value if date_value else "*"))
				responses = session.get(url + "/api/stories?story_cat=" + (cat_value if cat_value else "*") + "&story_region=" + (reg_value if reg_value else "*") + "&story_date=" + (date_value if date_value else "*"), headers=headers)
			if found:
				break
		if not found:
			print("Invalid agency code. Please try again.")
			return
	else:
		for site in NewsSites:
			print(url + "/api/stories?story_cat=" + (cat_value if cat_value else "*") + "&story_region=" + (reg_value if reg_value else "*") + "&story_date=" + (date_value if date_value else "*"))
			responses.append(session.get(site['url'] + "/api/stories?story_cat=" + (cat_value if cat_value else "*") + "&story_region=" + (reg_value if reg_value else "*") + "&story_date=" + (date_value if date_value else "*"), headers=headers))
	for response in responses:
		print(response)
		'''
		if response.status_code == 200:
			print('---------------')
			for story in response.json()['stories']:
				print('Key:', story['key'])
				print('Headline:', story['headline'])
				print('Category:', story['story_cat'])
				print('Region:', story['story_region'])
				print('Author:', story['author'])
				print('Date:', story['story_date'])
				print('Details:', story['story_details'])
				print('---------------')
		else:
			print(response.json()['message'])
		'''

def client_delete_story(choice):
	global GlobalURL
	if GlobalURL is None:
		print("Login for a valid URL first")
		return

	try:
		news_id = choice.split(" ")[1]
	except IndexError:
		print("Invalid story key. Please try again.")
		return

	if not news_id.isdigit():
		print("Invalid news id. Please try again.")
		return
	
	csrf_token = session.cookies.get('csrftoken')
	headers = {'X-CSRFToken': csrf_token} if csrf_token else {}
	
	response = session.post(GlobalURL + "/api/stories/" + news_id, headers=headers, data={"id": news_id})
	print(response.json()['message'])

def main():

  # Commands
	commands = { 
						 1 : "For Login type \'login [url]\'",
						 2 : "For Logout type \'logout\'",
						 3 : "For Post Story type \'post\'",
						 4 : "For Get Story type \'news -id=[id] -cat=[cat] -reg=[reg] -date=[date]\' note that the date should be in the format DD/MM/YYYY",
						 5 : "For List Sites type \'list\'",
						 6 : "For Delete Story type \'delete [story_key]\'",
						 7 : "Exit"
						 }
	
	if (client_get_agencies()):
		return

	while True:
		# Display the available commands

		print("Available commands:")

		for key, value in commands.items():
			print(f"{key}. {value}")
		
		# Get the user's input
		choice = input("Enter your choice: ")
		
		if choice.startswith("login "):
			client_login(choice)
		elif choice == "logout":
			client_logout()
		elif choice == "post":
			client_post_story()
		elif choice.startswith("news"):
			client_get_stories(choice)
		elif choice == "list":
			print("----------")
			for site in NewsSites:
				print(site['agency_name'])
				print(site['url'])
				print(site['agency_code'])
				print("----------")
		elif choice.startswith("delete "):
			client_delete_story(choice)
		else:
			print("Invalid choice. Please try again.")

if __name__ == "__main__":
	main()