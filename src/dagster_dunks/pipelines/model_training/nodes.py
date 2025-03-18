"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 0.19.11
"""

import logging

import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.interpolate import UnivariateSpline
from sklearn.metrics import log_loss
from sklearn.model_selection import KFold


def find_iteration_counts(model_input_table, params):
    """
    This function takes the model input table and the cross-validation
    parameters and returns the number of iterations for each fold.
    """

    logger = logging.getLogger(__name__)

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

    X = (
        model_input_table.copy()
        .drop(columns=["Season", "TeamID", "opponent_TeamID", "y"])
        .to_numpy()
    )
    y = model_input_table.copy()["y"]

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


def fit_spline_model(master_table, oof_preds):
    """
    This function takes the master table and the out-of-fold predictions
    and fits a spline model.
    """

    logger = logging.getLogger(__name__)

    tourney_data = master_table.execute()
    y = tourney_data["Score"] - tourney_data["opponent_Score"]

    repeat_cv = 3  # recommend 10

    val_cv = []
    spline_model = []

    for i in range(repeat_cv):
        dat = list(zip(oof_preds[i], np.where(y > 0, 1, 0)))
        dat = sorted(dat, key=lambda x: x[0])
        datdict = {}
        for k in range(len(dat)):
            datdict[dat[k][0]] = dat[k][1]
        spline_model.append(
            UnivariateSpline(list(datdict.keys()), list(datdict.values()))
        )
        spline_fit = spline_model[i](oof_preds[i])
        spline_fit = np.clip(spline_fit, 0.025, 0.975)
        spline_fit[
            (tourney_data.Seed == 1)
            & (tourney_data.opponent_Seed == 16)
            & (tourney_data.Score > tourney_data.opponent_Score)
        ] = 1.0
        spline_fit[
            (tourney_data.Seed == 2)
            & (tourney_data.opponent_Seed == 15)
            & (tourney_data.Score > tourney_data.opponent_Score)
        ] = 1.0
        spline_fit[
            (tourney_data.Seed == 3)
            & (tourney_data.opponent_Seed == 14)
            & (tourney_data.Score > tourney_data.opponent_Score)
        ] = 1.0
        spline_fit[
            (tourney_data.Seed == 4)
            & (tourney_data.opponent_Seed == 13)
            & (tourney_data.Score > tourney_data.opponent_Score)
        ] = 1.0
        spline_fit[
            (tourney_data.Seed == 16)
            & (tourney_data.opponent_Seed == 1)
            & (tourney_data.Score < tourney_data.opponent_Score)
        ] = 0.0
        spline_fit[
            (tourney_data.Seed == 15)
            & (tourney_data.opponent_Seed == 2)
            & (tourney_data.Score < tourney_data.opponent_Score)
        ] = 0.0
        spline_fit[
            (tourney_data.Seed == 14)
            & (tourney_data.opponent_Seed == 3)
            & (tourney_data.Score < tourney_data.opponent_Score)
        ] = 0.0
        spline_fit[
            (tourney_data.Seed == 13)
            & (tourney_data.opponent_Seed == 4)
            & (tourney_data.Score < tourney_data.opponent_Score)
        ] = 0.0

        val_cv.append(
            pd.DataFrame(
                {
                    "y": np.where(y > 0, 1, 0),
                    "pred": spline_fit,
                    "season": tourney_data.Season,
                }
            )
        )
        logger.info(
            "adjusted logloss of cvsplit %d: %f",
            i,
            log_loss(np.where(y > 0, 1, 0), spline_fit),
        )

    val_cv = pd.concat(val_cv)
    val_cv.groupby("season").apply(lambda x: log_loss(x.y, x.pred))

    return spline_model
