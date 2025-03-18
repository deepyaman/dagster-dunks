"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.11
"""

import ibis
import pandas as pd
import statsmodels.api as sm
from ibis import _
from ibis import selectors as s

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


def calculate_team_quality_scores(
    regular_season_results_by_team, ncaa_tourney_seeds, seasons: list[int]
):
    """Calculate quality score for each team playing in NCAA tourney."""
    team_quality_scores = []
    for season in seasons:
        seeded_teams = ncaa_tourney_seeds.filter(_.Season == season).TeamID.execute()
        formula = "win ~ -1 + TeamID + opponent_TeamID"
        data = regular_season_results_by_team.filter(
            (_.Season == season)
            & (_.TeamID.isin(seeded_teams))
            & (_.opponent_TeamID.isin(seeded_teams))
        ).select(
            _.TeamID.cast(str).name("TeamID"),
            _.opponent_TeamID.cast(str).name("opponent_TeamID"),
            (_.Score - _.opponent_Score > 0).name("win"),
        )
        glm = sm.GLM.from_formula(
            formula, data=data.execute(), family=sm.families.Binomial()
        ).fit()
        quality_scores = pd.DataFrame(glm.params).reset_index()
        quality_scores.columns = ["TeamID", "quality_score"]
        team_quality_scores.append(
            ibis.memtable(quality_scores)
            .filter(_.TeamID.startswith("TeamID"))
            .select(
                Season=season,
                TeamID=_.TeamID.substr(len("TeamID["), 4).cast(int),
                quality_score=_.quality_score,
            )
        )

    return ibis.union(*team_quality_scores)


def join_team_quality_scores(ncaa_tourney_results_by_team, team_quality_scores):
    """Join quality score and opposing team's quality score to results."""
    return (
        ncaa_tourney_results_by_team.join(
            team_quality_scores, ("Season", "TeamID"), how="left"
        )
        .drop(s.endswith("_right"))
        .join(
            team_quality_scores.rename("opponent_{name}").rename(
                Season="opponent_Season"
            ),
            ("Season", "opponent_TeamID"),
            how="left",
        )
        .drop(s.endswith("_right"))
    )


def calculate_seeds(ncaa_tourney_seeds):
    """Calculate seeds for each team."""
    return ncaa_tourney_seeds.mutate(Seed=_.Seed.substr(1, 2).cast(int))


def join_seeds(ncaa_tourney_results_by_team, seeds):
    """Join seeds to results."""
    return (
        ncaa_tourney_results_by_team.join(seeds, ("Season", "TeamID"), how="left")
        .drop(s.endswith("_right"))
        .join(
            seeds.rename("opponent_{name}").rename(Season="opponent_Season"),
            ("Season", "opponent_TeamID"),
            how="left",
        )
        .drop(s.endswith("_right"))
    )
