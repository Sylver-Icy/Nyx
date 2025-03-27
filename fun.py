import random
import os

# File paths
MSG_FILE = "messages.txt"
USED_FILE = "used_messages.txt"

# Ensure both files exist
if not os.path.exists(MSG_FILE):
    with open(MSG_FILE, "w") as f:
        f.write("Message 1\nMessage 2\nMessage 3\nMessage 4\nMessage 5")  # Add initial messages

if not os.path.exists(USED_FILE):
    open(USED_FILE, "w").close()  # Create empty file if not exists

def load_messages(file):
    """Load messages from a file into a list."""
    with open(file, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_messages(file, messages):
    """Save a list of messages to a file."""
    with open(file, "w") as f:
        f.write("\n".join(messages) + "\n")

def get_new_message():
    """Returns a new message each time it's called."""
    l1 = load_messages(MSG_FILE)
    l2 = load_messages(USED_FILE)

    if not l1:  # If l1 is empty, refill from l2 and reset
        l1, l2 = l2, []
        save_messages(MSG_FILE, l1)
        save_messages(USED_FILE, l2)

    if not l1:  # In case both lists are empty (shouldn't happen)
        return "No messages available."

    # Pick a random message
    msg = random.choice(l1)
    l1.remove(msg)
    l2.append(msg)

    # Save updated lists
    save_messages(MSG_FILE, l1)
    save_messages(USED_FILE, l2)

    return msg  # Return the message instead of printing

# Example usage:
# print(get_new_message())  # Call this whenever you want a new message