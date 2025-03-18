"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.11
"""

from ibis import _

SELECTION_SUNDAY_DAY_NUM = 132


def calculate_season_stats(regular_season_results_by_team, box_score_cols: list[str]):
    """Calculate season averages for each team."""
    return regular_season_results_by_team.group_by(["Season", "TeamID"]).agg(
        {
            f"avg_{col}": _[col].mean()
            for col in (*box_score_cols, *(f"opponent_{col}" for col in box_score_cols))
        }
    )


def join_season_stats(
    ncaa_tourney_results_by_team, season_stats, box_score_cols: list[str]
):
    """Join season stats and opposing team's season stats to results."""
    return ncaa_tourney_results_by_team.join(season_stats, ("Season", "TeamID")).join(
        season_stats.rename("opponent_{name}").rename(Season="opponent_Season"),
        ("Season", "opponent_TeamID"),
    )


def calculate_win_ratios(regular_season_results_by_team, num_days: int = 14):
    """Calculate win ratio for each team."""
    return (
        regular_season_results_by_team.filter(
            _.DayNum > SELECTION_SUNDAY_DAY_NUM - num_days
        )
        .group_by(["Season", "TeamID"])
        .agg({f"win_ratio_{num_days}d": (_.Score - _.opponent_Score > 0).mean()})
    )


def join_win_ratios(ncaa_tourney_results_by_team, win_ratios):
    """Join win ratio and opposing team's win ratio to results."""
    return ncaa_tourney_results_by_team.join(win_ratios, ("Season", "TeamID")).join(
        win_ratios.rename("opponent_{name}").rename(Season="opponent_Season"),
        ("Season", "opponent_TeamID"),
    )
