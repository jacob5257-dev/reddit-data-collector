import pandas as pd
import re

# Load the CSV file
df = pd.read_csv("labels.csv")  # Replace with your filename

# Choose the column to clean
column_name = "labels"  # Replace with your column name

# Function to clean each value
def clean_text(text):
    if pd.isna(text):
        return text
    return re.sub(r'[^a-zA-Z,\n ]', '', str(text))

# Apply the cleaning function to the column
df[column_name] = df[column_name].apply(clean_text)

# Optional: save to a new CSV
df.to_csv("cleaned_file.csv", index=False)
