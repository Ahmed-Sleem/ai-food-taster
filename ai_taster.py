# -*- coding: utf-8 -*-
"""ai_taster.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ml3k6z0GuX5u-tegn0b4JFmrIEHiiILl

#preprocessing(taster)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as pn

df = pd.read_csv("dataset_recipe.csv")

df

from itertools import combinations
from collections import Counter

def ingredient_combinations(df, num_ingredients):
    # Flatten the list of ingredients from all recipes
    all_combinations = []
    for ingredients in df['ingredients']:

        ingredients = str(ingredients).replace("[","")
        ingredients = str(ingredients).replace("]","")
        ingredients = str(ingredients).split(",")


        # Generate combinations of the specified number of ingredients
        all_combinations.extend(combinations(ingredients, num_ingredients))

    # Count occurrences of each combination
    combination_counts = Counter(all_combinations)

    # Convert the Counter to a DataFrame
    combo_df = pd.DataFrame([
        (*combo, count) for combo, count in combination_counts.items()
    ], columns=[f'ingredient_{i+1}' for i in range(num_ingredients)] + ['matching_score'])

    return combo_df

ing_2 = ingredient_combinations(df, 2)

ing_2

def normalize_matching_score(df_matching, df_recipes):
    # Function to count recipes containing at least one of the ingredients
    def count_recipes_with_ingredients(ingredient_1, ingredient_2):
        count = 0
        for ingredients in df_recipes['ingredients']:
            ingredients = str(ingredients)

            if ingredient_1 in ingredients or ingredient_2 in ingredients:
                count += 1
        return count

    # Normalize the matching scores
    normalized_scores = []
    for index, row in df_matching.iterrows():
        ingredient_1 = row['ingredient_1']
        ingredient_2 = row['ingredient_2']
        matching_score = row['matching_score']

        # Count the number of recipes containing at least one of the ingredients
        num_recipes = count_recipes_with_ingredients(ingredient_1, ingredient_2)

        # Normalize the matching score
        if num_recipes > 0:
            normalized_score = matching_score / num_recipes
        else:
            normalized_score = 0

        normalized_scores.append(normalized_score)

    # Add the normalized score to the DataFrame
    df_matching['normalized_matching_score'] = normalized_scores
    df_matching.drop(columns=['matching_score'], inplace=True)

    return df_matching

df_matching = ing_2.copy()
df_matching = df_matching[0:5000]

df_recipes = df
# Normalize the matching scores
normalized_df = normalize_matching_score(df_matching, df_recipes)

normalized_df

"""#model train (taster)"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


df = normalized_df.copy()

# Combine ingredient columns for encoding
df['ingredient_pair'] = df['ingredient_1'] + '_' + df['ingredient_2']

# Use OneHotEncoder to convert categorical data to numerical data
encoder = OneHotEncoder(sparse=False)
encoded_ingredients = encoder.fit_transform(df[['ingredient_pair']])

# Prepare the features (X) and target (y)
X = encoded_ingredients
y = df['normalized_matching_score']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')

# Function to predict matching score for new ingredient pairs
def predict_matching_score(ingredient_1, ingredient_2):
    ingredient_pair = f"'{ingredient_1}'_ '{ingredient_2}'"  # Ensure spaces around underscore

    # Get the categories used during training
    categories = encoder.categories_[0]

    # Ensure the new ingredient pair is in the same format as during training
    if ingredient_pair in categories:
        # If the ingredient pair exists in the training data, transform it
        encoded_pair = encoder.transform([[ingredient_pair]])
        return model.predict(encoded_pair)[0]


# Example prediction
new_score = predict_matching_score('winter squash', 'mexican seasoning')
print(f'Predicted normalized matching score: {new_score}')

def total_matching_score(ingredients_array):
    # Initialize variables to store total matching score and number of combinations
    total_score = 0.0
    num_combinations = 0

    # Iterate over all combinations of ingredients
    for i in range(len(ingredients_array)):
        for j in range(i + 1, len(ingredients_array)):
            # Get the normalized matching score for the ingredient pair
            score = predict_matching_score(ingredients_array[i], ingredients_array[j])
            # the pairs that doesnt exist in the dataset will be skipped
            if score :
              # Print the score for debugging
              print(f"Matching score for {ingredients_array[i]} and {ingredients_array[j]}: {score}")

            # Skip non-numeric scores
            if not isinstance(score, (int, float)):
                continue

            # If the score is not None, add it to the total score
            total_score += score
            num_combinations += 1

    # Calculate the average matching score
    if num_combinations > 0:
        average_score = total_score / num_combinations
    else:
        average_score = 0

    return average_score

# Example usage
ingredients = ['winter squash', 'mexican seasoning', 'mixed spice', 'honey', 'butter', 'olive oil']
total_score = total_matching_score(ingredients)
print(f'Total matching score: {total_score}')

"""#for saving"""

!pip install nbconvert
!apt-get install texlive texlive-xetex texlive-latex-extra pandoc

from google.colab import drive
drive.mount("/content/drive")

!jupyter nbconvert --to pdf "/content/drive/MyDrive/Colab Notebooks/ai_taster.ipynb"