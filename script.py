from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
import smtplib, ssl
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from schedule import every, repeat, run_pending
import logging

from models import Restaurant, Email

logging.basicConfig(level=logging.INFO)

load_dotenv()

# ENV variables that will depend on the user
# NOTE: You must fill this in yourself
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
REFRESH_TIMER = os.getenv("REFRESH_RATE")

sender_email = Email()

# Webdriver for the scraper
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
service = Service(os.environ.get("CHROMEDRIVER_PATH"))
DRIVER = webdriver.Chrome(service=service, options=chrome_options)


def find_reservation(month: int, day: int, restaurant: str) -> str:
    """
    Finds if there are any reservations open at a restaurant on a particular day
    """
    month = "0" + str(month)
    if day < 10:
        day = "0" + str(day)
    link = "https://resy.com/cities/ny/{}?date=2022-{}-{}&seats=2".format(
        restaurant, month, day
    )

    logging.info("MAKING CALL TO: " + link)
    DRIVER.get(link)

    time.sleep(2)

    DRIVER.find_element(
        By.XPATH,
        "/html/body/div[1]/main/div/div[2]/div/article[1]/section[1]/resy-inline-booking/div/div/div[3]/div/resy-reservation-button-list",
    )

    return link


def send_email(month: int, day: int, link: str, restaurant: str) -> None:
    """
    Sends an email to myself if there is an opening at selected restaurant on selected day
    """
    month_map = {1: "January", 2: "February"}
    message = (
        "{} HAS AN OPENING ON ".format(restaurant)
        + month_map[month]
        + " "
        + str(day)
        + ". Make a reservation at: "
        + link
    )

    # Creating the email
    sender = "niangmodou100@gmail.com"
    receivers = ["niangmodou100@gmail.com"]

    msg = MIMEText(message, "html")
    msg["Subject"] = "{} HAS AN OPENING".format(restaurant)
    msg["From"] = sender
    msg["To"] = ",".join(receivers)

    # Sending the email using Simple Mail Transfer Protocool
    s = smtplib.SMTP_SSL(host="smtp.gmail.com", port=465)
    s.login(user=EMAIL, password=PASSWORD)
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()

    logging.info("SUCCESS!")


@repeat(every(REFRESH_TIMER).minutes)
def scrape():
    """
    Scrapes the list of restaurants every 5 minutes
    """
    month, day = 6, 14

    # Carbone
    try:
        link = find_reservation(month, day, "carbone")
        send_email(month, day, link, "CARBONE")
    except Exception as _:
        logging.info("CARBONE NOT FOUND!")

    # L'Artusi
    try:
        link = find_reservation(month, day, "lartusi-ny")
        send_email(month, day, link, "L'ARTUSI")
    except Exception as _:
        logging.info("L'ARTUSI NOT FOUND!")


def main():
    while True:
        run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()