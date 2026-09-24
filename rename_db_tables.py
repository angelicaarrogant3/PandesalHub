import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pandesalhub.settings')
django.setup()

def rename_tables():
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cursor.fetchall()]
        except Exception:
            tables = []
            
        if not tables:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
        print("Existing tables:", tables)
        
        for table in tables:
            if table.startswith('pandesal_'):
                new_name = 'pandesal_' + table[len('pandesal_'):]
                
                if new_name in tables:
                    print(f"Dropping existing {new_name} to replace with {table}")
                    try:
                        cursor.execute(f"DROP TABLE {new_name} CASCADE;") 
                    except Exception:
                        cursor.execute(f"DROP TABLE {new_name};") 
                
                print(f"Renaming {table} to {new_name}")
                cursor.execute(f"ALTER TABLE {table} RENAME TO {new_name}")
                
    
        cursor.execute("UPDATE django_content_type SET app_label = 'pandesal' WHERE app_label = 'pandesal'")
        
   
        cursor.execute("UPDATE django_migrations SET app = 'pandesal' WHERE app = 'pandesal'")
        
        print("Done renaming tables and updating django metadata.")

if __name__ == "__main__":
    try:
        rename_tables()
    except Exception as e:
        print("Error:", e)
        
        import traceback
        traceback.print_exc()
