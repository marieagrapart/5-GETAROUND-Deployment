import os
import argparse
import pandas as pd
import time
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Set your variables for your environment
EXPERIMENT_NAME = "car-price"
mlflow.set_tracking_uri(os.environ["APP_URI"])
mlflow.set_experiment(EXPERIMENT_NAME)
experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

print("training model...")

# Time execution
start_time = time.time()

# Call mlflow autolog
mlflow.sklearn.autolog(log_models=False)  # We won't log models right away

# Import dataset
df = pd.read_csv("get_around_pricing_project.csv")

del df["Unnamed: 0"]

target_name = "rental_price_per_day"

Y = df.loc[:, target_name]
X = df.drop(target_name, axis=1)  # All columns are kept, except the target

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

# Create pipeline for numeric features
numeric_features = ["mileage", "engine_power"]
numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median"),
        ),  # missing values will be replaced by columns' median (it could be mean, the 2 are really close in our dataset)
        ("scaler", StandardScaler()),
    ]
)

# Create pipeline for categorical features
categorical_features = [
    "model_key",
    "fuel",
    "paint_color",
    "car_type",
    "private_parking_available",
    "has_gps",
    "has_air_conditioning",
    "automatic_car",
    "has_getaround_connect",
    "has_speed_regulator",
    "winter_tires",
]  # Names of categorical columns in X_train/X_test
categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent"),
        ),  # missing values will be replaced by most frequent value
        (
            "encoder",
            OneHotEncoder(drop="first", handle_unknown="ignore"),
        ),  # first column will be dropped to avoid creating correlations between features
    ]
)

# Use ColumnTransformer to make a preprocessor object that describes all the treatments to be done
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

# Log experiment to MLFlow

model = Pipeline(
    steps=[("Preprocessing", preprocessor), ("Regressor", LinearRegression())]
)

# model = LinearRegression()

with mlflow.start_run(experiment_id=experiment.experiment_id):
    model.fit(X_train, Y_train)
    predictions = model.predict(X_train)

    # Log model seperately to have more flexibility on setup
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="car-price-path",
        registered_model_name="car-price-registered",
        signature=infer_signature(X_train, predictions),
    )


Y_train_pred = model.predict(X_train)
Y_test_pred = model.predict(X_test)

print("R2 score on training set : ", r2_score(Y_train, Y_train_pred))
print("R2 score on test set : ", r2_score(Y_test, Y_test_pred))


print("...Done!")
print(f"---Total training time: {time.time()-start_time}")
