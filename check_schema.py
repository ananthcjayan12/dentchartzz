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
    
    # Execute a query to get column information for the app_payment table
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'app_payment'
        ORDER BY ordinal_position;
    """)
    
    # Fetch all results
    columns = cursor.fetchall()
    
    # Print the column information
    print("Columns in app_payment table:")
    for column in columns:
        col_name = column[0]
        data_type = column[1]
        max_length = column[2]
        precision = column[3]
        scale = column[4]
        nullable = column[5]
        
        type_info = data_type
        if max_length:
            type_info += f"({max_length})"
        elif precision and scale:
            type_info += f"({precision},{scale})"
            
        print(f"{col_name}: {type_info} {'NULL' if nullable == 'YES' else 'NOT NULL'}")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1) 