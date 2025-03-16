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
                    "mncaa_tourney_detailed_results",
                    "wncaa_tourney_detailed_results",
                ],
                outputs="tourney_results",
            )
        ]
    )
