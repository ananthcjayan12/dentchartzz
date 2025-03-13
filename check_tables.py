import os
import django
import sys
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    # Get the cursor
    cursor = connection.cursor()
    
    # Execute a query to get all tables that start with 'app_'
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name LIKE 'app_%'
        ORDER BY table_name;
    """)
    
    # Fetch all results
    tables = cursor.fetchall()
    
    # Print the table names
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1) 