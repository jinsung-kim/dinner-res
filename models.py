import os
import sys
import requests
import logging
import time
import re
import math
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

    def look_for_table(self, date: datetime, party_size: int, table_time: float, user: User) -> tuple:
        """
        :param date: date the bot should look for
        :param party_size: number we should look for
        :param table_time: slot time
        :param user: User that will look for the table

        :rtype (bool, list): Whether a table is found, times available as a list
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

            decimal_available_times = []
            for i in range (0, len(available_times)):
                decimal_available_times.append(available_times[i][1] + available_times[i][2] / 60)
                
            absolute_difference_function = lambda list_value : abs(list_value - table_time)
            decimal_closest_time = min(decimal_available_times, key= absolute_difference_function)
            closest_time = available_times[decimal_available_times.index(decimal_closest_time)][0]
            
            best_table = [k for k in open_slots if k['date']['start'] == closest_time][0]
            return (True, best_table)
        
        return (False, None)

    def try_for_table(self, user: User, slot: dict, earliest_time: float, latest_time: float, party_size: int):
        """
        :param user: 
        :param slot: The best table available
        """
        if slot is not None:
            hour =  datetime.strptime(slot['date']['start'],"%Y-%m-%d %H:%M:00").hour + \
                    datetime.strptime(slot['date']['start'],"%Y-%m-%d %H:%M:00").minute / 60
            if (hour >= earliest_time) and (hour <= latest_time):
                config_id: str = slot['config']['token']
                # self.make_reservation(config_id, party_size, datetime.strptime(slot['date']['start'],"%Y-%m-%d"), user)
                digital_hour: str = str(int(math.floor(hour))) + ':' + str(int((hour % (math.floor(hour))) * 60))

                logging.info("Booked successfully reservation at {} @ {}".format(self.restaurant_name, digital_hour))
            else:
                logging.info("No tables will ever be available within that time range or size")
                time.sleep(5)
        
        else:
            time.sleep(1)
            logging.info("Waiting for reservations to open up. The current time is: " + datetime.now())

    def make_reservation(self, config_id: str, party_size: int, date: datetime, user: User):
        """
        :param config_id: generated from token for slot
        :param party_size: number of people in reservation
        :param date: datetime for when the spot should be grabbed
        :param user: the user securing the reservation

        Makes the actual reservation
        """
        day = date.strftime('%Y-%m-%d')
        party_size = str(party_size)
        params = (
            ('x-resy-auth-token', user.auth_token),
            ('config_id', str(config_id)),
            ('day', day),
            ('party_size', str(party_size)),
        )
        details_request = requests.get('https://api.resy.com/3/details', headers=headers, params=params)

        details = details_request.json()
        book_token = details['book_token']['value']
        headers['x-resy-auth-token'] = user.auth_token
        data: dict = {
            'book_token': book_token,
            'struct_payment_method': user.payment_method_string,
            'source_id': 'resy.com-venue-details'
        }

        response = requests.post('https://api.resy.com/3/book', headers=headers, data=data)