"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.11
"""

from ibis import _


def calculate_season_stats(results_by_team, box_score_cols: list[str]):
    """Calculate season averages for each team."""
    return results_by_team.group_by(["Season", "TeamID"]).agg(
        {
            f"avg_{col}": _[col].mean()
            for col in (*box_score_cols, *(f"opponent_{col}" for col in box_score_cols))
        }
    )
