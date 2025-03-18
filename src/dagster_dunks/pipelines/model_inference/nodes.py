"""
This is a boilerplate pipeline 'model_inference'
generated using Kedro 0.19.11
"""

import logging

import ibis
import numpy as np
import pandas as pd
import xgboost as xgb
from ibis import _


def extract_unit_of_analysis_columns(sample_submission):
    return sample_submission.mutate(
        Season=_.ID.substr(0, 4).cast(int),
        TeamID=_.ID.substr(5, 4).cast(int),
        opponent_TeamID=_.ID.substr(10, 4).cast(int),
        location=ibis.literal("N"),
    )


def make_predictions(
    inference_model_input_table,
    model_input_table,
    iteration_counts,
    spline_model,
    params,
):
    logger = logging.getLogger(__name__)

    sub = inference_model_input_table.execute()

    Xsub = sub.drop(
        columns=["Season", "TeamID", "opponent_TeamID", "location"]
    ).to_numpy()
    dtest = xgb.DMatrix(Xsub)

    X = (
        model_input_table.copy()
        .drop(columns=["Season", "TeamID", "opponent_TeamID", "y"])
        .to_numpy()
    )
    y = model_input_table.copy()["y"]
    dtrain = xgb.DMatrix(X, label=y)

    def cauchyobj(preds, dtrain):
        labels = dtrain.get_label()
        c = 5000
        x = preds - labels
        grad = x / (x**2 / c**2 + 1)
        hess = -(c**2) * (x**2 - c**2) / (x**2 + c**2) ** 2
        return grad, hess

    repeat_cv = 3  # recommend 10

    sub_models = []
    for i in range(repeat_cv):
        logger.info("Fold repeater %d", i)
        sub_models.append(
            xgb.train(
                params=params,
                dtrain=dtrain,
                num_boost_round=int(iteration_counts[i] * 1.05),
                verbose_eval=50,
            )
        )

    sub_preds = []
    for i in range(repeat_cv):
        sub_preds.append(
            np.clip(
                spline_model[i](np.clip(sub_models[i].predict(dtest), -30, 30)),
                0.025,
                0.975,
            )
        )

    sub["ID"] = (
        sub["Season"].astype(str)
        + "_"
        + sub["TeamID"].astype(str)
        + "_"
        + sub["opponent_TeamID"].astype(str)
    )
    sub["Pred"] = pd.DataFrame(sub_preds).mean(axis=0)
    return sub[["ID", "Pred"]]
