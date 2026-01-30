import os
import shutil

assets_dir = r"C:\Users\User\.gemini\antigravity\scratch\nucleo-digital-trello-dash\assets"
os.chdir(assets_dir)

# Current State (Hypothesis: Alphabetical Upload vs Target Mapping)
# target.png -> has Edit content
# edit.png   -> has Gear content
# gear.png   -> has Siren content
# siren.png  -> has Target content
# user.png   -> Correct

# Step 1: Rename to temp based on CONTENT
try:
    os.rename("target.png", "temp_edit.png")
    os.rename("edit.png", "temp_gear.png")
    os.rename("gear.png", "temp_siren.png")
    os.rename("siren.png", "temp_target.png")

    # Step 2: Rename temp to CORRECT filenames
    os.rename("temp_target.png", "target.png")
    os.rename("temp_edit.png", "edit.png")
    os.rename("temp_gear.png", "gear.png")
    os.rename("temp_siren.png", "siren.png")
    
    print("Icons rotated successfully.")
except Exception as e:
    print(f"Error rotating icons: {e}")
