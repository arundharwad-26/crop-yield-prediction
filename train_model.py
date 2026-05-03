"""
train_model.py
--------------
Loads crop_data.csv, trains a RandomForestRegressor,
evaluates it, and saves the model as model/model.pkl

Usage:
    python train_model.py
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ─────────────────────────────────────────────
# Step 1: Load Dataset
# ─────────────────────────────────────────────
print("📂 Loading dataset...")
df = pd.read_csv("dataset/crop_data.csv")

print(f"   Rows    : {len(df)}")
print(f"   Columns : {list(df.columns)}")
print(df.head(3))

# ─────────────────────────────────────────────
# Step 2: Preprocess Data
# ─────────────────────────────────────────────
print("\n⚙️  Preprocessing...")

# Encode crop names (text → numbers) so the model can understand them
le = LabelEncoder()
df["crop_encoded"] = le.fit_transform(df["crop"])

print(f"   Crops found : {list(le.classes_)}")

# Features (inputs) and Target (output)
X = df[["crop_encoded", "rainfall", "temperature", "area"]]
y = df["yield"]

# Split into training (80%) and testing (20%) sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"   Training samples : {len(X_train)}")
print(f"   Testing samples  : {len(X_test)}")

# ─────────────────────────────────────────────
# Step 3: Train the Model
# ─────────────────────────────────────────────
print("\n🌲 Training RandomForestRegressor...")

model = RandomForestRegressor(
    n_estimators=100,    # 100 decision trees in the forest
    max_depth=10,        # max depth of each tree
    random_state=42      # for reproducibility
)

model.fit(X_train, y_train)
print("   Training complete!")

# ─────────────────────────────────────────────
# Step 4: Evaluate the Model
# ─────────────────────────────────────────────
print("\n📊 Evaluating model...")

y_pred = model.predict(X_test)

mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print(f"   MAE  (Mean Absolute Error)  : {mae:.4f}")
print(f"   RMSE (Root Mean Sq. Error)  : {rmse:.4f}")
print(f"   R²   (Accuracy Score)       : {r2:.4f}  ({r2*100:.1f}%)")

# ─────────────────────────────────────────────
# Step 5: Save Model + Label Encoder
# ─────────────────────────────────────────────
print("\n💾 Saving model...")

os.makedirs("model", exist_ok=True)

# Save both model and label encoder together
model_data = {
    "model":         model,
    "label_encoder": le,
    "features":      ["crop_encoded", "rainfall", "temperature", "area"],
    "crops":         list(le.classes_)
}

with open("model/model.pkl", "wb") as f:
    pickle.dump(model_data, f)

print("   ✅ model/model.pkl saved successfully!")
print(f"   Crops supported : {list(le.classes_)}")
print("\n🎉 Done! You can now run app.py")