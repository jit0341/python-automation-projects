import os
import shutil

# ==============================
# CONFIGURATION
# ==============================

BASE_PATH = os.getcwd()

DRY_RUN = False     # True = preview only (no files moved)
OVERWRITE = False    # True = overwrite existing files

FILE_TYPES = {
    "Images": [".jpg", ".png", ".jpeg"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Videos": [".mp4", ".mkv"],
    "Audio": [".mp3"]
}

# ==============================
# COUNTERS
# ==============================

total_files = 0
moved_files = 0
skipped_files = 0

# ==============================
# MAIN PROCESS
# ==============================

for item in os.listdir(BASE_PATH):
    item_path = os.path.join(BASE_PATH, item)

    # --- Validation ---
    if not os.path.isfile(item_path):
        continue

    total_files += 1

    # Skip the script itself
    if item == "organizer.py":
        skipped_files += 1
        continue

    # Skip hidden files
    if item.startswith("."):
        skipped_files += 1
        continue

    name, ext = os.path.splitext(item)
    moved = False

    # --- Business Rules ---
    for folder_name, extensions in FILE_TYPES.items():
        if ext.lower() in extensions:
            folder_path = os.path.join(BASE_PATH, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            destination = os.path.join(folder_path, item)

            # Overwrite protection
            if os.path.exists(destination) and not OVERWRITE:
                skipped_files += 1
                moved = True
                break

            if DRY_RUN:
                print(f"[DRY-RUN] Would move: {item} → {folder_name}")
                moved_files += 1
            else:
                shutil.move(item_path, destination)
                moved_files += 1

            moved = True
            break

    # --- Others category ---
    if not moved:
        others_path = os.path.join(BASE_PATH, "Others")
        os.makedirs(others_path, exist_ok=True)

        destination = os.path.join(others_path, item)

        if os.path.exists(destination) and not OVERWRITE:
            skipped_files += 1
            continue

        if DRY_RUN:
            print(f"[DRY-RUN] Would move: {item} → Others")
            moved_files += 1
        else:
            shutil.move(item_path, destination)
            moved_files += 1

# ==============================
# SUMMARY REPORT
# ==============================

print("\n📊 Folder Organizer Summary")
print("---------------------------")
print(f"Total files found : {total_files}")
print(f"Files moved       : {moved_files}")
print(f"Files skipped     : {skipped_files}")
print("Status            : Completed")


