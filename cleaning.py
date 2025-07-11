import re

import pandas as pd

df = pd.read_csv("labels.csv")


def clean_and_capitalize(text):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove everything except letters and spaces
        letters_only = re.sub(r'[^a-zA-Z\s]', '',
                              line).replace("•", "").replace("-", "")
        # Collapse multiple spaces, strip, then capitalize first letter
        cleaned_line = re.sub(r'\s+', ' ', letters_only).strip().capitalize()
        cleaned_lines.append(cleaned_line)
    return '\n'.join(cleaned_lines)


def normalize_labels(text):
    # Split by commas, clean each label
    parts = [part.strip().strip('"').strip("'").lower()
             for part in text.split(',')]
    return ', '.join(parts)


df["role"] = df["role"].str.split().str[0].apply(
    clean_and_capitalize).apply(normalize_labels)

df.to_csv("labels_cleaned.csv", index=False)
