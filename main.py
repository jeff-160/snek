from dotenv import load_dotenv
from os import environ
from bot import *

if __name__=="__main__":
    load_dotenv()
    snek.run(environ.get("TOKEN"))