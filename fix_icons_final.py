import shutil
import os

source_dir = r"C:\Users\User\.gemini\antigravity\brain\47828f34-179f-40f2-90a3-5b3f40ef87ad"
dest_dir = r"C:\Users\User\.gemini\antigravity\scratch\nucleo-digital-trello-dash\assets"

# Mapping based on visual deduction:
# uploaded_media_0 -> USER
# uploaded_media_1 -> TARGET
# uploaded_media_2 -> EDIT
# uploaded_media_3 -> GEAR
# uploaded_media_4 -> SIREN

files_map = [
    ("uploaded_media_0_1769779364895.png", "user.png"),
    ("uploaded_media_1_1769779364895.png", "target.png"),
    ("uploaded_media_2_1769779364895.png", "edit.png"),
    ("uploaded_media_3_1769779364895.png", "gear.png"),
    ("uploaded_media_4_1769779364895.png", "siren.png")
]

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

print("Starting Definitive Copy...")
for src_name, dest_name in files_map:
    src_path = os.path.join(source_dir, src_name)
    dest_path = os.path.join(dest_dir, dest_name)
    try:
        shutil.copy2(src_path, dest_path)
        print(f"Mapped {src_name} -> {dest_name}")
    except Exception as e:
        print(f"Error copying {src_name}: {e}")

print("Done.")
