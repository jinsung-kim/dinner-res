from models import Restaurant, User
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

EMAIL: str = os.getenv("EMAIL")
PASSWORD: str = os.getenv("PASSWORD")

def main():
    user: User = User(EMAIL, PASSWORD)
    # Good Good Culture Club
    ggcc: Restaurant = Restaurant("3560 18th Street San Francisco, CA 94110")

    ggcc.look_for_table(datetime.strptime(os.getenv("DATE"), "%m/%d/%Y"), int(os.getenv("SEATS")), user)

if __name__ == "__main__":
    main()