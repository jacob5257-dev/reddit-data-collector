import pandas as pd

df = pd.read_csv("labels_formatted.csv")

def normalize_labels(text):
    # Split by commas, clean each label
    parts = [part.strip().strip('"').strip("'").lower() for part in text.split(',')]
    return ', '.join(parts)

df['Labels'] = df['Labels'].apply(normalize_labels)
df_grouped = df.groupby('Labels', as_index=False).sum(numeric_only=True)

df_grouped.to_csv("labels_formatted.csv", index=False)