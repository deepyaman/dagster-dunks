"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 0.19.11
"""

from kedro.pipeline import Pipeline, node, pipeline  # noqa

from .nodes import find_iteration_counts


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=find_iteration_counts,
                inputs=["model_input_table", "params:xgb_cv"],
                outputs="iteration_counts",
            ),
        ]
    )
