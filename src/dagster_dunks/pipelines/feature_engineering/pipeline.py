"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.11
"""

from kedro.pipeline import Pipeline, node, pipeline  # noqa

from .nodes import calculate_season_stats


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                calculate_season_stats,
                inputs=["regular_season_results_by_team", "params:box_score_cols"],
                outputs="regular_season_averages",
            )
        ]
    )
