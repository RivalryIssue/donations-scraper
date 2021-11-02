import requests
from bs4 import BeautifulSoup
from json import dump
from datetime import datetime
from zoneinfo import ZoneInfo


def num(n: str):
    return float(n.replace(",", "").replace("%", ""))


def get_canvass_report(url: str, time: str):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    head = soup.find("div", attrs={"class": "gheader"}).find_all(
        "td", attrs={"align": "left"})

    table = soup.find_all("table")[1]

    precincts = table.find_all("tr")
    precincts.pop()
    precincts.pop(0)

    data = list()

    total_precincts = 0.0

    for precinct in precincts:
        datum = precinct.find_all("td")
        total_precincts += 2 if "&" in datum[0].text else 1
        data.append({
            "Precinct": datum[0].text,
            "Yes": num(datum[1].text.strip()),
            "No": num(datum[2].text.strip())
        })

    return {
        "meta": {
            "title": soup.find("font", attrs={"class", "h2"}).text,
            # "time": soup.find("font", attrs={"class": "h4"}).text[21:],
            "time": time,
            "registered_voters": num(head[1].text),
            "ballots_cast": num(head[3].text),
            "voter_turnout": num(head[5].text),
            "total_precincts": total_precincts,
            # "total_precincts": num(head[7].text),
            # "full_count_precincts": num(head[9].text),
            # "full_count_precincts_percent": num(head[11].text),
            # "partial_count_precincts": num(head[15].text)
        },
        "data": data
    }


def get_summary_row(row):
    label = row[1]
    return {
        "label": label.text.replace('\xa0', ' ').strip(),
        "call": "bold" in label["class"],
        "in_precinct_votes": num(row[2].text),
        "absentee_votes": num(row[3].text),
        "total_votes": num(row[4].text),
        "percent_votes": num(row[5].text)
    }


def get_data(baseurl: str, time: str, indices: list):
    NOT_COUNTED = "not-counted"
    PARTIALLY_COUNTED = "partially-counted"
    FULLY_COUNTED = "fully-counted"

    html = requests.get(f"{baseurl}/index.jsp").text
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    summary = tables[2].find_all("tr")

    precincts_counted = tables[3]
    reported = dict()
    precincts = precincts_counted.find_all("tr")
    precincts.pop(0)
    for precinct in precincts:
        text = precinct.find("td").text.strip()
        pclass = precinct.find("td")["class"]
        if "red" in pclass:
            reported[text] = NOT_COUNTED
        elif "blue" in pclass:
            reported[text] = PARTIALLY_COUNTED
        else:
            reported[text] = FULLY_COUNTED

    data = list()

    for index in indices:
        details = summary[index * 3 + 1]
        name = details.find(
            "td", attrs={"class": "headertr", "colspan": "3"}).text
        canvass = details.find(
            "td", attrs={"class": "headertr", "colspan": "2"}).find("a")["href"]
        canvass = f"{baseurl}/{canvass}"

        yes = get_summary_row(summary[index * 3 + 2].contents)
        no = get_summary_row(summary[index * 3 + 3].contents)

        report = get_canvass_report(canvass, time)

        full_count_precincts: float = 0.0
        partial_count_precincts: float = 0.0
        for i in range(len(report["data"])):
            count = reported[report["data"][i]["Precinct"]]
            report["data"][i]["counted"] = count
            if count == FULLY_COUNTED:
                full_count_precincts += 1
            elif count == PARTIALLY_COUNTED:
                partial_count_precincts += 1

        report["meta"]["full_count_precincts"] = full_count_precincts
        report["meta"]["full_count_precincts_percent"] = full_count_precincts / \
            report["meta"]["total_precincts"] * 100
        report["meta"]["partial_count_precincts"] = partial_count_precincts

        data.append({
            "name": name,
            "options": [yes, no],
            "report": report
        })

    data[-1]["name"] = "Ann Arbor Prop D $25,000 Limit"

    return {
        "meta": {
            "title": soup.find("font", attrs={"class", "h2"}).text,
            # "time": soup.find("font", attrs={"class": "h4"}).text[21:]
            "time": time
        },
        "data": data
    }


def main():
    east = ZoneInfo("America/New_York")
    time = datetime.now(tz=east).strftime("%A, %b %d, %Y %I:%M:%S %p")
    url = "https://electionresults.ewashtenaw.org/electionreporting/nov2021"
    data = get_data(url, time, [13, 14, 15, 16])
    with open("data.json", "w") as f:
        dump(data, f, indent=2)


if __name__ == "__main__":
    main()
