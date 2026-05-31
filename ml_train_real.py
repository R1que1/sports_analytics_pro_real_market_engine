
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
from pathlib import Path

DATASET = Path("data/matches_dataset.csv")
MODEL = Path("data/model_random_forest.joblib")

df = pd.read_csv(DATASET)
features = ["home_form","away_form","home_goals_avg","away_goals_avg","home_conceded_avg","away_conceded_avg","home_advantage"]

X = df[features]
y = df["result"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)

print("Accuracy:", round(acc * 100, 2), "%")
print(classification_report(y_test, pred))

MODEL.parent.mkdir(exist_ok=True)
joblib.dump({"model": model, "features": features}, MODEL)
print("Modelo salvo em:", MODEL)
