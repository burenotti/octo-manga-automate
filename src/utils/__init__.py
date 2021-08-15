
def get_stars_score(score: float, max_score: float = 5.0):
    decimal_score = int(score / max_score * 10)
    stars = '💛' * decimal_score
    moons = '🖤' * (10 - decimal_score)
    return f"{stars}{moons} ({score} / {max_score})"
