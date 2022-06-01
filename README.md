# Reservation Notifications

## About

This bot is a script that fetches reservations for popular restaurants that are on the Resy site.
The intention of its creation is to notify users when spots open up on certain dates and book them.

## Features

The frequency of the bot can be altered, the number of places to check for can be changed.
The number of emails that you intend to send out can all be changed through the script.

## Running

1. If you are going to run this locally - set up the virtual environment to run this script on.

```shell
python3 -m venv env
```

2. Activate the venv and install the required libraries listed in requirements.txt.

```shell
# Activate the virtual environment
source env/bin/activate

# Install required libraries
pip3 install -r requirements.txt
```

3. Optional: Run tests to check if things are working

```shell
python3 tests.py
```

4. Run the server

```shell
python3 script.py
```
