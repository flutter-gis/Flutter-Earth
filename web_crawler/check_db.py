import sqlite3
import os

def check_database():
    db_path = 'exported_data/crawler_data.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {tables}")
        
        # Check each table
        for table_name, in tables:
            if table_name == 'sqlite_sequence':
                continue
                
            print(f"\n📊 Table: {table_name}")
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Records: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                samples = cursor.fetchall()
                print(f"   Sample data:")
                for i, row in enumerate(samples, 1):
                    print(f"     {i}. {row}")
        
        conn.close()
        print("\n✅ Database check completed")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database() 