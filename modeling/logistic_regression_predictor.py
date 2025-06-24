
# logistic_regression_predictor.py
import pandas as pd
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

def logistic_predict(df, features, target, test_size=0.2, threshold=0.5):
    df_clean = df[features + [target]].dropna()
    X = df_clean[features]
    y = df_clean[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    X_train_sm = sm.add_constant(X_train)
    model = sm.Logit(y_train, X_train_sm).fit(disp=0)

    X_test_sm = sm.add_constant(X_test)
    y_prob = model.predict(X_test_sm)
    y_pred = (y_prob >= threshold).astype(int)

    return {
        "model": model,
        "f1_score": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "auc": roc_auc_score(y_test, y_prob)
    }
