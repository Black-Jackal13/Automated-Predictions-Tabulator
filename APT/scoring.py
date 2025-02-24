def _calculate_player_score(predicted: list[str, str, str], actual: list[str, str, str]) -> int:
    """
    Calculate points based on a player's prediction and the actual results.

    :param predicted: The player's predicted top 3 finishers.
    :param actual: The actual top 3 finishers.

    :return: The total points awarded to the player based on prediction accuracy.
    """
    points = 0
    # Define the base points for each position
    point_values = {0: 5, 1: 4, 2: 3}

    for i, predicted_finisher in enumerate(predicted):
        if predicted_finisher in actual:
            # Find the actual position of the predicted finisher
            actual_position = actual.index(predicted_finisher)

            # Calculate points with penalty
            points += max(point_values[i] - abs(i - actual_position), 0)

    return points
