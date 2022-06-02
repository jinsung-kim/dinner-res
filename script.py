from models import Restaurant, User
from dotenv import load_dotenv
from datetime import datetime
import os
import logging
import sys

load_dotenv()

EMAIL: str = os.getenv("EMAIL")
PASSWORD: str = os.getenv("PASSWORD")
SEATS: int = int(os.getenv("SEATS"))
DATE: str = os.getenv("DATE")

def main():
    user: User = User(EMAIL, PASSWORD)
    # Good Good Culture Club
    ggcc: Restaurant = Restaurant("3560 18th Street San Francisco, CA 94110")

    table_time: str = os.getenv("DESIRED")
    earliest_time: str = os.getenv("EARLY")
    latest_time: str = os.getenv("LAST")

    table_time: float = float(table_time.split(":")[0]) + (float(table_time.split(":")[1]) / 60)
    earliest_time: float = float(earliest_time.split(":")[0]) + (float(earliest_time.split(":")[1]) / 60)
    latest_time: float = float(latest_time.split(":")[0]) + (float(latest_time.split(":")[1]) / 60)

    # Validating inputs
    if (earliest_time > table_time or latest_time < table_time or earliest_time > latest_time):
        logging.info("Invalid time parameters")
        sys.exit()

    res = ggcc.look_for_table(datetime.strptime(DATE, "%m/%d/%Y"), SEATS, table_time, user)

    if ():
        ggcc.try_for_table(user, res[1], earliest_time, latest_time, SEATS)
    

if __name__ == "__main__":
    main()