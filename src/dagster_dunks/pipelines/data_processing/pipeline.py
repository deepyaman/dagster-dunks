"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.11
"""

import ibis
from kedro.pipeline import Pipeline, node, pipeline  # noqa


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=ibis.union,
                inputs=[
                    "mens_ncaa_tourney_seeds",
                    "womens_ncaa_tourney_seeds",
                ],
                outputs="ncaa_tourney_seeds",
            ),
            node(
                func=ibis.union,
                inputs=[
                    "mens_regular_season_results",
                    "womens_regular_season_results",
                ],
                outputs="regular_season_results",
            ),
            node(
                func=ibis.union,
                inputs=[
                    "mens_ncaa_tourney_results",
                    "womens_ncaa_tourney_results",
                ],
                outputs="ncaa_tourney_results",
            ),
        ]
    )
