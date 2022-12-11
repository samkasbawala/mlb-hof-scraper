from typing import List, Tuple
from bs4 import BeautifulSoup, Tag
import pandas as pd
import requests
import re

BASE_URL = "https://www.baseball-reference.com/"


def get_hof_df(year: int) -> pd.DataFrame:
    """
    Returns a pd.DataFrame object containing the data of the voting results from the
    year specified. No modifications have been done to that data. Instead, three
    additional fields have been added that wasn't already in the data.

    Args:
        year (int): the year to pull the data from.

    Returns:
        pd.DataFrame: dataframe containing the data pulled from the page.
    """
    html = _get_hof_html(year)
    columns, total_ballots, data = _parse_html_hof(html, year)

    # Adding extra column name for playerId since that was generated from the href
    df = pd.DataFrame(data, columns=columns + ["playerId"])
    df["total_ballots"] = total_ballots
    df["year"] = year

    return df


def _get_hof_html(year: int) -> str:
    """
    Gets the html of the voting results page.

    Args:
        year (int): year to pull html of.

    Raises:
        RuntimeError: if the year inserted returns a 404.

    Returns:
        str: the html of the page.
    """

    url = BASE_URL + f"awards/hof_{year}.shtml"
    response = requests.get(url)

    if not response.ok:
        raise RuntimeError(f"404 Response from {url}")

    html = response.text

    return html


def _parse_html_hof(html: str, year: int) -> Tuple[List[str], int, List[List[str]]]:
    """Parses the html code to pull out the table columns, total number of ballots, and
    table data. Returns these three items in a tuple.

    Args:
        html (str): html of the page
        year (int): year

    Raises:
        ValueError: If there is no official results for th year yet.

    Returns:
        Tuple[List[str], int, List[List[str]]]: table columns, total number of ballots,
            andtable data
    """
    soup = BeautifulSoup(html, "html.parser")

    if "hall of fame voting" not in soup.title.string.lower():
        raise ValueError(f"There are no voting results for the given year {year}")

    table_section_heading = soup.find(id="hof_BBWAA_sh")
    table = soup.find(id="hof_BBWAA")

    header = table.find("thead")
    body = table.find("tbody")

    columns = _parse_header(header)
    total_ballots = _get_total_ballots(table_section_heading)
    data = _parse_table_body(body)

    return (columns, total_ballots, data)


def _parse_header(header: Tag) -> List[str]:
    """Parses header to get column names.

    Args:
        header (Tag): Tag object containing the header html.

    Returns:
        List[str]: Column names.
    """
    fields: List[Tag] = header("tr")[1].find_all("th")

    return [field.get_text().strip() for field in fields]


def _get_total_ballots(table_section_heading: Tag) -> int:
    """Gets the total number of ballots for a given year.

    Args:
        table_section_heading (Tag): Tag object containing the table section heading
            html.

    Returns:
        int: Number of ballots for the given year.
    """
    section_heading_text = table_section_heading.find(class_="section_heading_text")
    text = section_heading_text.find("li")

    pattern = re.compile(r"^(\d+)")  # total ballots is at the beginning of the string
    matched = pattern.match(text.get_text()).group(0)

    return int(matched.strip())


def _parse_table_body(body: Tag) -> List[List[str]]:
    """Parses the data in the body of the table and returns a list of a list of strings,
    where each inner list reperesents a row of data from the table. The playerId is
    added as an extra field.

    Args:
        body (Tag): Tag object containing the body of the table.

    Returns:
        List[List[str]]: A nested list containg the data in the table.
    """

    rows: List[Tag] = body("tr")
    players_data: List[List[str]] = []

    for row in rows:
        player_data = []
        player_id: str = None

        rank = row.find("th").get_text()
        player_data.append(rank)

        items: List[Tag] = row("td")

        for item in items:

            # Player field
            if player := item.find("a"):

                # Player Name
                player_data.append(player.get_text())

                # Player ID
                player_id = _get_player_id(player)

            else:
                player_data.append(item.get_text())

        # Since player_id is a new field, add it to the end
        player_data.append(player_id)
        players_data.append(player_data)

    return players_data


def _get_player_id(player: Tag) -> str:
    """Parses the player_id from the href

    Args:
        player (Tag): Tag object containing the player information

    Returns:
        str: player_id
    """

    href = player["href"]
    pattern = re.compile(r"([A-Za-z.]+\d+)(\.shtml$)")
    player_id = pattern.search(href).group(1)

    return player_id
