"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.11
"""

from kedro.pipeline import Pipeline, node, pipeline  # noqa

from .nodes import (
    calculate_avg_score_diff,
    calculate_season_stats,
    calculate_seed_diff,
    calculate_seeds,
    calculate_team_quality_scores,
    calculate_win_ratios,
    create_model_input_table,
    create_target,
    encode_location,
    join_season_stats,
    join_seeds,
    join_team_quality_scores,
    join_win_ratios,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                calculate_season_stats,
                inputs=["regular_season_results_by_team", "params:box_score_cols"],
                outputs="regular_season_averages",
            ),
            node(
                join_season_stats,
                inputs=[
                    "ncaa_tourney_results_by_team",
                    "regular_season_averages",
                    "params:box_score_cols",
                ],
                outputs="ncaa_tourney_results_with_regular_season_averages",
            ),
            node(
                calculate_win_ratios,
                inputs=["regular_season_results_by_team"],
                outputs="win_ratios",
            ),
            node(
                join_win_ratios,
                inputs=[
                    "ncaa_tourney_results_with_regular_season_averages",
                    "win_ratios",
                ],
                outputs="ncaa_tourney_results_with_win_ratios",
            ),
            node(
                calculate_team_quality_scores,
                inputs=[
                    "regular_season_results_by_team",
                    "ncaa_tourney_seeds",
                    "params:seasons",
                ],
                outputs="team_quality_scores",
            ),
            node(
                join_team_quality_scores,
                inputs=[
                    "ncaa_tourney_results_with_win_ratios",
                    "team_quality_scores",
                ],
                outputs="ncaa_tourney_results_with_team_quality_scores",
            ),
            node(
                calculate_seeds,
                inputs="ncaa_tourney_seeds",
                outputs="seeds",
            ),
            node(
                join_seeds,
                inputs=["ncaa_tourney_results_with_team_quality_scores", "seeds"],
                outputs="master_table",
            ),
            node(
                encode_location,
                inputs="master_table",
                outputs="encoded_location",
            ),
            node(
                calculate_avg_score_diff,
                inputs="master_table",
                outputs="avg_score_diff",
            ),
            node(
                calculate_seed_diff,
                inputs="master_table",
                outputs="seed_diff",
            ),
            node(
                create_target,
                inputs="master_table",
                outputs="target",
            ),
            node(
                create_model_input_table,
                inputs=[
                    "master_table",
                    "ncaa_tourney_results_by_team",
                    "encoded_location",
                    "avg_score_diff",
                    "seed_diff",
                    "target",
                ],
                outputs="model_input_table",
            ),
        ]
    )
