import numpy as np
import pandas as pd
import tensorflow as tf

comments_table = pd.read_csv("comments.csv")
testing_comments_table = pd.read_csv("test_data.csv")
train_comments_list_raw, train_roles_list_raw = comments_table["Content"].tolist(
), comments_table["Person's Role"].tolist()
test_comments_list_raw, test_roles_list_raw = testing_comments_table["comment"].tolist(
), testing_comments_table["role"].tolist()


# --- 1. Data Preparation Function (from previous response, no change needed here) ---
def prepare_comment_role_tensors_pre_split(
        train_comments_list, train_roles_list,
        test_comments_list, test_roles_list,
        max_length=200, vocab_size=10000
):
    """
    Convert comments and roles to TensorFlow tensors, assuming data is already split.
    """
    tokenizer = tf.keras.preprocessing.text.Tokenizer(
        num_words=vocab_size,
        oov_token="<OOV>",
        filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'
    )
    role_lookup = tf.keras.layers.StringLookup(mask_token=None)

    tokenizer.fit_on_texts(train_comments_list)
    role_lookup.adapt(train_roles_list)

    train_comment_sequences = tokenizer.texts_to_sequences(train_comments_list)
    X_train = tf.keras.preprocessing.sequence.pad_sequences(
        train_comment_sequences,
        maxlen=max_length,
        padding='post',
        truncating='post'
    )
    X_train = tf.constant(X_train, dtype=tf.int32)
    y_train = role_lookup(train_roles_list)

    test_comment_sequences = tokenizer.texts_to_sequences(test_comments_list)
    X_test = tf.keras.preprocessing.sequence.pad_sequences(
        test_comment_sequences,
        maxlen=max_length,
        padding='post',
        truncating='post'
    )
    X_test = tf.constant(X_test, dtype=tf.int32)
    y_test = role_lookup(test_roles_list)

    return X_train, y_train, X_test, y_test, tokenizer, role_lookup


print("--- Original Raw Lists (might contain non-strings) ---")
print("Train Comments Raw (first 2):", train_comments_list_raw[:2])
print("Test Comments Raw:", test_comments_list_raw)
print("-" * 20)


# --- NEW CLEANING STEP ---
def clean_string_list(string_list):
    """
    Ensures all elements in a list are strings, converting non-strings to empty strings.
    """
    cleaned_list = []
    for item in string_list:
        if isinstance(item, str):
            cleaned_list.append(item)
        elif item is None:  # Handle explicit None if present
            cleaned_list.append("")
        elif isinstance(item, (int, float)):  # Handle numbers, including NaN
            # Convert to string or empty string if NaN
            cleaned_list.append(str(item) if not np.isnan(item) else "")
        else:  # Catch-all for other unexpected types
            cleaned_list.append("")
    return cleaned_list


train_comments_list = clean_string_list(train_comments_list_raw)
test_comments_list = clean_string_list(test_comments_list_raw)

# It's good practice to ensure roles are also strings, though less likely to be floats
train_roles_list = [str(r) for r in train_roles_list_raw]
test_roles_list = [str(r) for r in test_roles_list_raw]

print("--- Cleaned Lists (all strings) ---")
print("Train Comments Cleaned (first 2):", train_comments_list[:2])
# Will show '' instead of nan
print("Test Comments Cleaned:", test_comments_list)
print("-" * 20)

# Set parameters for the data preparation
MAX_LENGTH = 100  # Max number of words/tokens per comment
VOCAB_SIZE = 5000  # Max number of unique words in the vocabulary

# Call the data preparation function with the CLEANED lists
X_train, y_train, X_test, y_test, tokenizer, role_lookup = \
    prepare_comment_role_tensors_pre_split(
        train_comments_list, train_roles_list,
        test_comments_list, test_roles_list,
        MAX_LENGTH, VOCAB_SIZE
    )

num_roles = len(role_lookup.get_vocabulary())

print(f"X_train shape: {X_train.shape}")
print(f"y_train shape: {y_train.shape}")
print(f"X_test shape: {X_test.shape}")
print(f"y_test shape: {y_test.shape}")
print(f"Role vocabulary (from training data): {role_lookup.get_vocabulary()}")
print(f"Number of unique roles (including UNK if present): {num_roles}")

# --- Remaining Model Training, Evaluation, and Prediction Code (No Change) ---

# 2. Define the Model Architecture
EMBEDDING_DIM = 128

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(
        input_dim=VOCAB_SIZE,
        output_dim=EMBEDDING_DIM,
        input_length=MAX_LENGTH
    ),
    tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(64, return_sequences=True)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(
        num_roles,
        activation='softmax'
    )
])
model.summary()

# 3. Compile the Model
model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy']
)

# 4. Train the Model
EPOCHS = 20
BATCH_SIZE = 32

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=3,
        restore_best_weights=True
    )
]

print("\n--- Training Model ---")
history = model.fit(
    X_train,
    y_train,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_data=(X_test, y_test),
    callbacks=callbacks,
    verbose=1
)

# 5. Evaluate the Model
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"\n--- Model Evaluation ---")
print(f"Test Loss: {loss:.4f}")
print(f"Test Accuracy: {accuracy:.4f}")


# 6. Make Predictions
def predict_role(comment_text):
    # Ensure the input comment is a string before tokenizing
    if not isinstance(comment_text, str):
        # Convert any non-string input to string
        comment_text = str(comment_text)

    sequence = tokenizer.texts_to_sequences([comment_text])
    padded_sequence = tf.keras.preprocessing.sequence.pad_sequences(
        sequence,
        maxlen=MAX_LENGTH,
        padding='post',
        truncating='post'
    )
    input_tensor = tf.constant(padded_sequence, dtype=tf.int32)

    predictions = model.predict(input_tensor)

    predicted_role_index = np.argmax(predictions, axis=1)[0]

    predicted_role_string = role_lookup.get_vocabulary()[predicted_role_index]

    confidence = predictions[0][predicted_role_index]

    return predicted_role_string, confidence


# Test with new comments
new_comment_1 = "I need to pick up my children from school early today."
role, confidence = predict_role(new_comment_1)
print(f"\n--- Prediction Example 1 ---")
print(f"Comment: '{new_comment_1}'")
print(f"Predicted Role: '{role}' with confidence: {confidence:.2f}")

new_comment_2 = "Is there a scholarship available for next semester?"
role, confidence = predict_role(new_comment_2)
print(f"\n--- Prediction Example 2 ---")
print(f"Comment: '{new_comment_2}'")
print(f"Predicted Role: '{role}' with confidence: {confidence:.2f}")

new_comment_3 = "The students in my class are doing great on this project!"
role, confidence = predict_role(new_comment_3)
print(f"\n--- Prediction Example 3 ---")
print(f"Comment: '{new_comment_3}'")
print(f"Predicted Role: '{role}' with confidence: {confidence:.2f}")

# Example with a potentially problematic input (after cleaning for predictions)
new_comment_4 = None  # Or np.nan
role, confidence = predict_role(new_comment_4)
print(f"\n--- Prediction Example 4 (Problematic Input) ---")
print(f"Comment: '{new_comment_4}'")  # Will print 'None' as a string
print(f"Predicted Role: '{role}' with confidence: {confidence:.2f}")
