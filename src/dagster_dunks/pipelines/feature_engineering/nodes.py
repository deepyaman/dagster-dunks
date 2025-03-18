"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.11
"""

from ibis import _


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
