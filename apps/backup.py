import os
import shutil
from datetime import datetime

# Define paths relative to the script location
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_file = os.path.join(base_dir, 'db.sqlite3')
backup_dir = os.path.join(base_dir, 'backups')

# Ensure the backup directory exists
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)
    print(f"Created backup directory: {backup_dir}")

# Create a backup file name with the current date and time
backup_file = os.path.join(backup_dir, f'db_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3')

# Copy the database file and log the operation
try:
    shutil.copy2(db_file, backup_file)
    print(f"{datetime.now()} - Backup created: {backup_file}")
except Exception as e:
    print(f"{datetime.now()} - Backup failed: {str(e)}")

# Remove old backups
files = os.listdir(backup_dir)
files = [os.path.join(backup_dir, f) for f in files if f.startswith('db_backup_')]
files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
for f in files[1:]:
    os.remove(f)
    print(f"Deleted old backup: {f}")