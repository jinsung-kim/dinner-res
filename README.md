# Reservation Notifications

## About

Do you need a reservation for a date or a dinner party? Are you tired of struggling to get a dinner spot at Dorsia?
This bot will find reservations for even the most sought out establishments.
The intention of its creation is to notify users when spots open up on certain dates and book them.

![Patrick Bateman](https://i.ytimg.com/vi/TOecxTy4ZJE/hqdefault.jpg)

## Features

The frequency of the bot can be altered, the number of places to check for can be changed.
The number of emails that you intend to send out can all be changed through the script.

## Running

1.) If you are going to run this locally - set up the virtual environment to run this script on.

```shell
python3 -m venv env
```

2.) Activate the venv and install the required libraries listed in requirements.txt.

```shell
# Activate the virtual environment
source env/bin/activate

# Install required libraries
pip3 install -r requirements.txt
```

3.) Add all the credentials needed in the .env file. You need to make your own. The format is as follows:

```shell
API_KEY="YOUR RESY KEY HERE"
EMAIL="EMAIL CREDENTIALS"
PASSWORD="CORRESPONDING PASSWORD"
DATE="06/02/2022"
DESIRED="19:15"
EARLY="18:45"
LAST="20:15"
SEATS=2
```

4.) Optional: Run tests to check if things are working

```shell
python3 tests.py
```

5.) Run the server

```shell
python3 script.py
```
