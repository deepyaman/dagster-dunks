"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 0.19.11
"""

from kedro.pipeline import Pipeline, node, pipeline  # noqa

from .nodes import find_iteration_counts, fit_spline_model, make_out_of_fold_predictions


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=find_iteration_counts,
                inputs=["model_input_table", "params:xgb_cv"],
                outputs="iteration_counts",
            ),
            node(
                func=make_out_of_fold_predictions,
                inputs=["model_input_table", "iteration_counts", "params:xgb_cv"],
                outputs="out_of_fold_predictions",
            ),
            node(
                func=fit_spline_model,
                inputs=["model_input_table", "out_of_fold_predictions", "master_table"],
                outputs="spline_model",
            ),
        ]
    )
