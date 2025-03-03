import bs4
import requests


def fetch_race_data(race_name: str, race_year: str) -> list[str]:
    """
    Fetches the top ten finishers of a race from the ProcyclingStats website.

    :param race_name: name of the race
    :param race_year: year of the specific race
    :return: list of top ten finishers
    """
    # Get HTML
    website_link = f"https://www.procyclingstats.com/race/{race_name.lower().replace(" ", "-")}/{race_year}"
    website_soup = bs4.BeautifulSoup(requests.get(website_link).text, "html.parser")

    # Narrow Down to Find Table
    website_soup = website_soup.find("body").find("div", {"class": "wrapper"})
    website_soup = website_soup.find("div", {"class": "content"})
    website_soup = website_soup.find("div", {"class": "page-content page-object default"})
    website_soup = website_soup.find("div", {"class": "w50 left mb_w100 mg_r2"})
    website_soup = website_soup.find("span", {"class": "table-cont"})

    # Table not there (Not a finished race)
    try:
        table_body = website_soup.find("table").find("tbody")
    except AttributeError:
        return []

    # Find the Finishers
    top_ten_finishers = []
    for row in table_body.find_all("tr"):
        finisher_details = row.find_all("td")
        finisher_details = [col.text.strip() for col in finisher_details]
        finisher_lastname = finisher_details[1].split(" ")[0].capitalize()
        top_ten_finishers.append(finisher_lastname)

    return top_ten_finishers


def scoring_algorithm(
        tier: str,  # (GOLD, SILVER or BRONZE)
        predicted_finishers: dict[str, tuple[str, ]],
        top_ten_finishers: list[str]
) -> tuple[dict[str, int], list[tuple[str, int]]]:
    """
    Calculate points based on a player's prediction and the top_ten_finishers results.

    :param tier: The race tier (GOLD, SILVER, or BRONZE).
    :type tier: str
    :param predicted_finishers: Players and their predicted top 3 finishers (first, second, third).
    :type predicted_finishers: dict[str: tuple[str, str, str]]
    :param top_ten_finishers: The top_ten_finishers top 3 finishers.
    :type top_ten_finishers: list[str, str, str]

    :return: The total points awarded to the player based on prediction accuracy.
    """
    # Point values
    point_values = {
        "GOLD": {
            "podium": (15, 12, 9),
            "miss": -3,
            "joker": 3,
            "ppp": 15
        },
        "SILVER": {
            "podium": (10, 8, 6),
            "miss": -2,
            "joker": 2,
            "ppp": 10
        },
        "BRONZE": {
            "podium": (5, 4, 3),
            "miss": -1,
            "joker": 1,
            "ppp": 5
        },
    }
    current_values = point_values[tier]

    scores = {player: 0 for player in predicted_finishers.keys()}
    standings = []

    # Get Prediction Frequencies
    prediction_frequency = {}
    for player in predicted_finishers:
        for finisher in predicted_finishers[player]:
            if finisher in prediction_frequency:
                prediction_frequency[finisher] += 1
            else:
                prediction_frequency[finisher] = 1

    # Cycle Players
    top_three_finishers = top_ten_finishers[:3]
    for player in predicted_finishers:

        for index, predicted_finisher in enumerate(predicted_finishers[player]):

            # Correct Predictions
            if predicted_finisher == top_three_finishers[index]:
                scores[player] += current_values["podium"][index]

                # Double Points (more than 6 players)
                if prediction_frequency[predicted_finisher] <= 2 and len(predicted_finishers.keys()) >= 6:
                    scores[player] += current_values["podium"][index]

                # Triple Points (more than 6 players)
                elif prediction_frequency[predicted_finisher] == 1 and len(predicted_finishers.keys()) >= 6:
                    scores[player] += current_values["podium"][index]

            # Missed Predictions
            elif predicted_finisher in top_three_finishers and predicted_finisher != top_three_finishers[index]:
                scores[player] += min(
                    current_values["podium"][index],
                    current_values["podium"][top_three_finishers.index(predicted_finisher)]
                )

                scores[player] += current_values["miss"]*max(
                    index-top_three_finishers.index(predicted_finisher),
                    top_three_finishers.index(predicted_finisher)-index
                )

        # PPP
        if predicted_finishers[player] == top_three_finishers:
            scores[player] += current_values["ppp"]

        # Place in Standings
        temp_standings = standings.copy()
        for index, _, score in enumerate(temp_standings):
            if score < scores[player]:
                standings.insert(index, (player, scores[player]))
                break

    # TODO: Joker Points
    # A unique but incorrect podium prediction who nevertheless finishes in the top ten earns the equivalent of third
    # place points for the pertinent category.

    return scores, standings
