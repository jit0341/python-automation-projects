import os
import shutil
# Base directory where files will be organised.
base_path = os.getcwd()

# Mapping of folder names to file extensions
file_types = {
    'Images': ['.jpg','.png','.jpeg'],
    'Documents': ['.pdf','.docx','.txt'],
    'Videos': ['.mp4','.mkv']
    }
# Loop through all items in the directory
for item in os.listdir(base_path):
    item_path = os.path.join(base_path,item)
# check if item is a file.
    if os.path.isfile(item_path):
# Skip the script file(organizer.py) itself.
        if item == 'organizer.py':
            continue
# Extract file extension.
        name,ext = os.path.splitext(item)
        moved = False
# Match extension with folder.
        for folder_name, extensions in file_types.items():
            if ext.lower() in extensions:
                folder_path = os.path.join(base_path,folder_name)
                os.makedirs(folder_path, exist_ok = True)
                shutil.move(item_path,os.path.join(folder_path,item))
                moved = True
                break
            # If no match found ,move to others
        if not moved:
            others_path = os.path.join(base_path, "others")
            os.makedirs(others_path, exist_ok = True)

            shutil.move(item_path, os.path.join(others_path, item))


