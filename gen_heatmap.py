import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter, defaultdict

# Example input: list of strings with newline-separated labels (possibly with extra whitespace)
data = pd.read_csv("cleaned_file.csv")["labels"]

cleaned_entries = []
for entry in data:
    if pd.isna(entry):
        continue
    # Replace both newlines and commas with a common separator (e.g. newline), then split
    raw_labels = entry.replace(',', '\n').split('\n')
    labels = [label.strip() for label in raw_labels if label.strip()]
    if len(labels) > 1:
        cleaned_entries.append(labels)

# Count co-occurrences
co_counts = defaultdict(int)
all_labels = set()

for labels in cleaned_entries:
    unique_labels = sorted(set(labels))  # sort for consistent pair order
    all_labels.update(unique_labels)
    for a, b in combinations(unique_labels, 2):
        co_counts[(a, b)] += 1
        co_counts[(b, a)] += 1  # make it symmetric

# Initialize co-occurrence matrix
all_labels = sorted(all_labels)
co_matrix = pd.DataFrame(0, index=all_labels, columns=all_labels)

for (a, b), count in co_counts.items():
    co_matrix.at[a, b] = count

# Plot heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(co_matrix, annot=True, fmt='d', cmap='YlGnBu', square=True, cbar_kws={'label': 'Co-occurrence'})
plt.title("Label Co-occurrence Heatmap")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("cooccurrence_heatmap.png", dpi=300)
plt.show()
