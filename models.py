import os
import sys
import requests
from dotenv import load_dotenv
import logging

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


class Restaurant:

    def __init__(self, name: str, range: list[tuple]):
        """
        :param name: name of restaurant to look for
        :param range: range in which the search needs to be done
            - format: (month, day)

        Used to generate restaurant objects
        """
        self.start: tuple = (range[0][0], range[0][1])
        self.end: tuple = (range[1][0], range[1][1])

        # Convert to URL form
        self.name: str = name.replace(" ", "-").lower()

    def __str__(self):
        return "Res for: {}, range: {} to {}".format(self.name, self.print_date(self.start), self.print_date(self.end))

    def make_res_range(self, city: str = "sf", seats: int = 2):
        """
        Looks for reservations that match the range of the request
        This function is used for a multiple dates
        """

        

    def print_date(self, date: tuple):
        return "{} {}".format(months[date[0]], date[1])