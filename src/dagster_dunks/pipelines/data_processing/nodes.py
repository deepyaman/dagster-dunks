"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.11
"""

from ibis import _


def prepare_results_by_team(results):
    results = results.rename(location="WLoc")

    per_team_columns = [col[1:] for col in results.columns if col.startswith("W")]
    assert per_team_columns == [
        col[1:] for col in results.columns if col.startswith("L")
    ]

    results_by_winning_team = results.rename(
        **{col: f"W{col}" for col in per_team_columns},
        **{f"opponent_{col}": f"L{col}" for col in per_team_columns},
    )
    results_by_losing_team = results.rename(
        **{col: f"L{col}" for col in per_team_columns},
        **{f"opponent_{col}": f"W{col}" for col in per_team_columns},
    ).mutate(location=_.location.cases(("H", "A"), ("A", "H"), else_="N"))
    return results_by_winning_team.union(results_by_losing_team)
