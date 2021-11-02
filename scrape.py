import requests
from bs4 import BeautifulSoup
from json import dump
from datetime import datetime

def get_data(lanternurl: str, dailyurl:str ):

    lantern_html = requests.get(f"{lanternurl}").text
    lantern_soup = BeautifulSoup(lantern_html, "html.parser")

    money = lantern_soup.find_all(class_="single-project-top-dollar")[0].text.strip()

    # html = requests.get(f"{baseurl}").text
    # soup = BeautifulSoup(html, "html.parser")

    # money = soup.find_all(class_="single-project-top-dollar")[0].text.strip()

    return {
        "data": {
          "lantern": money,
          "daily": " "
        }
    }


def main():
    lanternurl = "https://buckeyefunder.osu.edu/project/21918"
    dailyurl=""
    data = get_data(lanternurl, dailyurl)
    with open("data.json", "w") as f:
        dump(data, f, indent=2)


if __name__ == "__main__":
    main()
