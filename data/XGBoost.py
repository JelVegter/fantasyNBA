import numpy as np
import pandas as pd
import xgboost as xgb
from full_player_stats import calculate_points, get_dataframe
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

ind_variables = [
    # 'FGM', 'FGA', 'FG%', '3PTM', '3PA', '3P%', 'FTM', 'FTA', 'Points',
    #    'FT%', 'ORB', 'DRB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'PTS','+/-',
    "AvPoints",
    "RollBckw2",
    "RollBckw4",
]

dep_variables = "RollFwrd1"
# ,'RollFwrd3'
data = get_dataframe(refresh=True)
data = calculate_points(data, roll_backwards=[2, 4], roll_forward=[1, 3])
data = data.loc[~data[dep_variables].isnull()]
X, y = data[ind_variables], data[dep_variables]
# cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
data_dmatrix = xgb.DMatrix(data=X, label=y)


#
# xgb_cv = xgb.cv(dtrain=data_dmatrix, params=params, nfold=3,
#                     num_boost_round=50, early_stopping_rounds=10, metrics="auc", as_pandas=True, seed=123)
#


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

xg_reg = xgb.XGBRegressor(
    objective="reg:squarederror",
    colsample_bytree=0.3,
    learning_rate=0.1,
    max_depth=5,
    alpha=10,
    n_estimators=10,
)
#
#
#
# xgb_cv = cv(dtrain=data_dmatrix, params=params, nfold=3,
#                     num_boost_round=50, early_stopping_rounds=10, metrics="auc", as_pandas=True, seed=123)


xg_reg.fit(X_train, y_train)
preds = xg_reg.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, preds))
print("RMSE: %f" % (rmse))

preds = xg_reg.predict(X)
data["Prediction"] = preds
print(data.loc[data["Player"] == "Joe Harris"])
