"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 0.19.11
"""

import logging

import numpy as np
import xgboost as xgb
from sklearn.model_selection import KFold


def find_iteration_counts(model_input_table, params):
    """
    This function takes the model input table and the cross-validation
    parameters and returns the number of iterations for each fold.
    """

    logger = logging.getLogger(__name__)

    X = model_input_table.drop("y")
    y = model_input_table.y
    dtrain = xgb.DMatrix(X, label=y)

    def cauchyobj(preds, dtrain):
        labels = dtrain.get_label()
        c = 5000
        x = preds - labels
        grad = x / (x**2 / c**2 + 1)
        hess = -(c**2) * (x**2 - c**2) / (x**2 + c**2) ** 2
        return grad, hess

    xgb_cv = []
    repeat_cv = 3  # recommend 10

    for i in range(repeat_cv):
        logger.info("Fold repeater %d", i)
        xgb_cv.append(
            xgb.cv(
                params=params,
                dtrain=dtrain,
                obj=cauchyobj,
                num_boost_round=3000,
                folds=KFold(n_splits=5, shuffle=True, random_state=i),
                early_stopping_rounds=25,
                verbose_eval=50,
            )
        )

    iteration_counts = [np.argmin(x["test-mae-mean"].values) for x in xgb_cv]
    val_mae = [np.min(x["test-mae-mean"].values) for x in xgb_cv]
    logger.info("%s", (iteration_counts, val_mae))
    return iteration_counts
