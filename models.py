import os
import sys
import requests
import logging
import time
import re
from dotenv import load_dotenv
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.location import Location

logging.basicConfig(level=logging.INFO)
load_dotenv()

API_KEY: str = os.getenv("API_KEY")

# Helpers (finding ranges)
months: dict = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
                5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
                9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

days_in: list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Headers
headers = {
	 'origin': 'https://resy.com',
	 'accept-encoding': 'gzip, deflate, br',
	 'x-origin': 'https://resy.com',
	 'accept-language': 'en-US,en;q=0.9',
	 'authorization': 'ResyAPI api_key="{}"'.format(API_KEY),
	 'content-type': 'application/x-www-form-urlencoded',
	 'accept': 'application/json, text/plain, */*',
	 'referer': 'https://resy.com/',
	 'authority': 'api.resy.com',
	 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
}

class User:

    def __init__(self, username: str, password: str):
        """
        :param username: email of the user
        :param password: password of the associated username
        """
        
        # Logs into the user
        data = {
            "email": username,
            "password": password
        }

        response = requests.post("https://api.resy.com/3/auth/password", headers=headers, data=data)
        response_data = response.json()

        try:
            auth_token = response_data["token"]
        except KeyError:
            logging.info("Incorrect credentials provided")
            sys.exit()

        self.first_name: str = response_data["first_name"]
        self.last_name: str = response_data["last_name"]
        self.payment_method_string = '{"id":' + str(response_data['payment_method_id']) + '}'
        self.auth_token: str = auth_token

        logging.info("Logged in as the user successfully")


class Restaurant:

    def __init__(self, address: str):
        """
        :param address: address of the restaurant

        venue_id: the id that is used to find the venue name and ID
        address: identifiable address for restaurant
        restaurant_name: name of establishment
        """
        self.address: str = address
        self.venue_id: str= ""
        self.restaurant_name: str = ""

    def look_for_table(self, date: datetime, party_size: int, user: User):
        """
        :param date: date the bot should look for
        :param party_size: number we should look for
        :param user: User that will look for the table
        """

        # Geolocator -> Convert address into params for resy search
        geolocator: Nominatim = Nominatim(user_agent="Me")
        try:
            location: Location = geolocator.geocode(self.address, exactly_one=True)
        except AttributeError:
            logging.info("This is an invalid address")

        # Finding the restaurant using the address
        day = date.strftime('%Y-%m-%d')
        params: tuple = (
            ('x-resy-auth-token', user.auth_token),
            ('day', day),
            ('lat', str(location.latitude)),
            ('long', str(location.longitude)),
            ('party_size', str(party_size)),
        )

        response: requests.Response = requests.get('https://api.resy.com/4/find', headers=headers, params=params)
        data: requests.Response.json = response.json()

        try:
            restaurant_name = re.search('"name": (.*?) "type":', response.text).group(1)
            restaurant_name = re.search('"name": "(.*?)",', restaurant_name).group(1)
            venue_id = re.search('{"resy": (.*?)}', response.text).group(1)

            self.venue_id = venue_id
            self.restaurant_name = restaurant_name

        except:
            logging.info("That address is not bookable on Resy")
            time.sleep(5)
            sys.exit()

        params: tuple = (
            ('x-resy-auth-token', user.auth_token),
            ('day', day),
            ('lat', '0'),
            ('long', '0'),
            ('party_size', str(party_size)),
            ('venue_id', str(self.venue_id)),
        )

        response = requests.get('https://api.resy.com/4/find', headers=headers, params=params)
        data = response.json()
        results = data['results']
        
        if len(results['venues']) > 0:
            open_slots = results['venues'][0]['slots']
        
        if len(open_slots) > 0:
            available_times = [(k['date']['start'], datetime.strptime(k['date']['start'],"%Y-%m-%d %H:%M:00").hour, datetime.strptime(k['date']['start'],"%Y-%m-%d %H:%M:00").minute) for k in open_slots]
            print(available_times)
            print(self.restaurant_name)
            print(self.venue_id)

    def print_date(self, date: tuple):
        return "{} {}".format(months[date[0]], date[1])