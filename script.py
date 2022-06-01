from models import Restaurant, User
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL: str = os.getenv("EMAIL")
PASSWORD: str = os.getenv("PASSWORD")

def main():
    user: User = User(EMAIL, PASSWORD)
    

if __name__ == "__main__":
    main()