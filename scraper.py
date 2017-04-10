from bs4 import BeautifulSoup
import urllib
from datetime import datetime
from time import mktime, time

urls = {
    "general": "https://travel.gc.ca/travelling/advisories",
    "specific": "https://travel.gc.ca/destinations/"
}

advisory_codes = {
    "Avoid all travel": 4,
    "Avoid all travel (with regional advisories)": 4,
    "Avoid non-essential travel": 3,
    "Avoid non-essential travel (with regional advisories)": 3,
    "Exercise a high degree of caution": 2,
    "Exercise a high degree of caution (with regional advisories)": 2,
    "Exercise normal security precautions": 1,
    "Exercise normal security precautions (with regional advisories)": 1
}


def pull_data(url):
    """
    Pulls the raw HTML from a given URL, and returns a BeautifulSoup object of the raw data.
    """
    data = urllib.urlopen(url).read()

    return BeautifulSoup(data, "html.parser")


def advisory_general(sort=None):
    """
    Pulls the general advisory information for every country listed on the
    Travel Advice and Advisory page.

    :param soup: a beautiful soup object representing the raw HTML page
    :param sort:
    :return: dictionary containing an overview of the travel advisory for
        every country on the Canadian Travel Advisory page
    """
    soup = pull_data(urls["general"])
    rows = soup.find_all("tr", class_="gradeX")

    countries = {}

    for row in rows:
        # grab the most important information
        key_info = row.find_all("td")
        # get name
        name = key_info[1].a.get_text()

        countries[name.lower()] = organize_general_advisory(key_info)

    # sorting (note: this converts the dictionary to a list -> dictionaries
    # cannot be sorted ... duh!)
    if sort == "name":
        return sorted(countries.itervalues(), key=(lambda v: v["name"]))
    if sort == "advisory":
        return sorted(countries.itervalues(), key=(lambda v: v["advisory_code"]), reverse=True)
    if sort == "last_updated":
        return sorted(countries.itervalues(), key=(lambda v: v["last_updated_absolute"]), reverse=True)

    return countries


def organize_general_advisory(td):
    """
    This function takes all of the td elements for a specific country in the
    general advisory format and return a dictionary with the information
    organized.

    :param td: The td elements that were scraped for a particular country
    :return: {}
    """
    return {
        "slug": td[0].get_text(),
        "name": td[1].a.get_text(),
        "url": td[1].a["href"],
        "advisory": td[2].get_text(),
        "advisory_code": advisory_codes[td[2].get_text()],
        "advisory_code_max": max(advisory_codes.itervalues(), key=lambda v: v),
        "last_updated": td[-1].get_text(),
        "last_updated_absolute": date_to_absolute(td[-1].get_text())
    }


def date_to_absolute(date):
    """
    This function converts a date in the format YYYY-MM-DD HH-MM-SS to its
    absolute time (in seconds) since Epoch.

    :param date: A date string of the format YYYY-MM-DD HH-MM-SS
    :return: float
    """
    return mktime(datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple())


def advisory_country(country):
    """
    Pulls a country-specific advisory summary from the Travel Advice and
    Advisory page.

    :param country: a string that represents a country name
    :return: {}
    """
    return advisory_general()[country.lower()]


def main():
    pass


if __name__ == "__main__":
    main()


