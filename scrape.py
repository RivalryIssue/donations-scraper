import requests
import requests
import json
from bs4 import BeautifulSoup
from json import dump
from datetime import datetime

def get_data(lanternurl: str, dailyurl:str ):

    lantern_html = requests.get(f"{lanternurl}").text
    lantern_soup = BeautifulSoup(lantern_html, "html.parser")

    money = lantern_soup.find_all(class_="single-project-top-dollar")[0].text.strip()


    daily_url = "https://give-webhooks.communityfunded.com/graphql"

    payload="{\"query\":\"query publicStoryPageStats($storyId: Int!) {\\n  storyById(id: $storyId) {\\n    storyInitiativesByStoryId {\\n      nodes {\\n        id\\n        fundraisingGoalType\\n        calculatedGoal\\n        monetaryGoal\\n        totalNumberOfCalculatedItemsRaised\\n        totalAmountOfGifts\\n        totalNumberOfGifts\\n        totalNumberOfUniqueDonors\\n        calculatedFundraisingGoalName\\n        calculatedFundraisingGoalValue\\n        participantCountType\\n        participantGoal\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"storyId\":33211}}"
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", daily_url, headers=headers, data=payload)

    return {
        "data": {
          "lantern": money,
          "daily": "$" + response.json()["data"]["storyById"]["storyInitiativesByStoryId"]["nodes"][0]["totalAmountOfGifts"]
        }
    }


def main():
    lanternurl = "https://buckeyefunder.osu.edu/project/28518"
    dailyurl=""
    data = get_data(lanternurl, dailyurl)
    with open("data.json", "w") as f:
        dump(data, f, indent=2)


if __name__ == "__main__":
    main()
