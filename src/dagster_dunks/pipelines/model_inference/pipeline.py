"""
This is a boilerplate pipeline 'model_inference'
generated using Kedro 0.19.11
"""

from kedro.pipeline import Pipeline, node, pipeline  # noqa

from dagster_dunks.pipelines.feature_engineering.nodes import (
    join_season_stats,
    join_win_ratios,
    join_team_quality_scores,
    join_seeds,
    encode_location,
    calculate_avg_score_diff,
    calculate_seed_diff,
    create_model_input_table,
)
from .nodes import (
    extract_unit_of_analysis_columns,
    make_predictions,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=extract_unit_of_analysis_columns,
                inputs=["sample_submission"],
                outputs="sample_submission_with_unit_of_analysis_columns",
            ),
            node(
                func=join_season_stats,
                inputs=[
                    "sample_submission_with_unit_of_analysis_columns",
                    "regular_season_averages",
                    "params:box_score_cols",
                ],
                outputs="sample_submission_with_season_stats",
            ),
            node(
                func=join_win_ratios,
                inputs=["sample_submission_with_season_stats", "win_ratios"],
                outputs="sample_submission_with_win_ratios",
            ),
            node(
                func=join_team_quality_scores,
                inputs=["sample_submission_with_win_ratios", "team_quality_scores"],
                outputs="sample_submission_with_team_quality_scores",
            ),
            node(
                func=join_seeds,
                inputs=["sample_submission_with_team_quality_scores", "seeds"],
                outputs="inference_master_table",
            ),
            node(
                func=encode_location,
                inputs="inference_master_table",
                outputs="inference_encoded_location",
            ),
            node(
                func=calculate_avg_score_diff,
                inputs=["inference_master_table"],
                outputs="inference_avg_score_diff",
            ),
            node(
                func=calculate_seed_diff,
                inputs=["inference_master_table"],
                outputs="inference_seed_diff",
            ),
            node(
                func=create_model_input_table,
                inputs=[
                    "inference_master_table",
                    "sample_submission",  # hack
                    "inference_encoded_location",
                    "inference_avg_score_diff",
                    "inference_seed_diff",
                ],
                outputs="inference_model_input_table",
            ),
            node(
                func=make_predictions,
                inputs=[
                    "inference_model_input_table",
                    "model_input_table_pandas",
                    "iteration_counts",
                    "spline_model",
                    "params:xgb_cv",
                ],
                outputs="submission",
            ),
        ]
    )
