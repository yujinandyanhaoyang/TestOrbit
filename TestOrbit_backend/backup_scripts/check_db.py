import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SHOW TABLES LIKE 'project'")
tables = cursor.fetchall()
print('Tables:', tables)

if tables:
    cursor.execute('DESCRIBE project')
    columns = cursor.fetchall()
    print('Project table structure:')
    for col in columns:
        print(col)
else:
    print('No project table found')
