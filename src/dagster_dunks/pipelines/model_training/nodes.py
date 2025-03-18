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

    X = model_input_table.drop("y").execute().to_numpy()
    y = model_input_table.y.execute().to_numpy()
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


def make_out_of_fold_predictions(model_input_table, iteration_counts, params):
    """
    This function takes the model input table and the number of iterations
    for each fold and returns the out-of-fold predictions.
    """

    logger = logging.getLogger(__name__)

    X = model_input_table.drop("y").execute().to_numpy()
    y = model_input_table.y.execute().to_numpy()

    repeat_cv = 3  # recommend 10

    oof_preds = []
    for i in range(repeat_cv):
        logger.info("Fold repeater %d", i)
        preds = y.copy()
        kfold = KFold(n_splits=5, shuffle=True, random_state=i)
        for train_index, val_index in kfold.split(X, y):
            dtrain_i = xgb.DMatrix(X[train_index], label=y[train_index])
            dval_i = xgb.DMatrix(X[val_index], label=y[val_index])
            model = xgb.train(
                params=params,
                dtrain=dtrain_i,
                num_boost_round=iteration_counts[i],
                verbose_eval=50,
            )
            preds[val_index] = model.predict(dval_i)
        oof_preds.append(np.clip(preds, -30, 30))

    return oof_preds
