import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# 检查project表的结构
cursor.execute("DESCRIBE project")
columns = cursor.fetchall()
print("Current project table structure:")
for col in columns:
    print(col)

# 检查是否有position字段
has_position = False
for col in columns:
    if col[0] == 'position':
        has_position = True
        break

if not has_position:
    print("\nPosition field is missing. Adding it...")
    cursor.execute("ALTER TABLE project ADD COLUMN position smallint NOT NULL DEFAULT 1")
    print("Position field added successfully!")
else:
    print("\nPosition field already exists.")
    
# 验证修改
cursor.execute("DESCRIBE project")
columns = cursor.fetchall()
print("\nUpdated project table structure:")
for col in columns:
    print(col)
