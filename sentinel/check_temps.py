import sqlite3
import json

conn = sqlite3.connect('data/system_stats.db')
cursor = conn.cursor()

# Get latest snapshot
cursor.execute("""
    SELECT id, timestamp 
    FROM system_snapshots 
    ORDER BY timestamp DESC 
    LIMIT 1
""")

row = cursor.fetchone()
if row:
    snapshot_id, timestamp = row
    print(f"Latest snapshot: ID={snapshot_id}, Time={timestamp}")
    print()
    
    # Check CPU metrics
    cursor.execute("""
        SELECT temperature_celsius 
        FROM cpu_metrics 
        WHERE snapshot_id = ?
    """, (snapshot_id,))
    
    cpu_temp = cursor.fetchone()
    if cpu_temp:
        print(f"CPU Temperature: {cpu_temp[0]}°C" if cpu_temp[0] else "CPU Temperature: NULL (not available)")
    
    # Check GPU metrics
    cursor.execute("""
        SELECT temperature_celsius 
        FROM gpu_metrics 
        WHERE snapshot_id = ?
    """, (snapshot_id,))
    
    gpu_temps = cursor.fetchall()
    if gpu_temps:
        for i, temp in enumerate(gpu_temps):
            print(f"GPU {i} Temperature: {temp[0]}°C" if temp[0] else f"GPU {i} Temperature: NULL")
    
    print()
    print("Temperature collectors status:")
    print("- Standard temperature collector: Implemented (returns NULL on Windows)")
    print("- AIDA64 collector: Implemented, not enabled (set ENABLE_AIDA64=true)")
    print("- HWiNFO collector: Implemented, not enabled (set ENABLE_HWINFO=true)")
    print()
    print("To enable temperature monitoring:")
    print("1. Install AIDA64 ($39.95) or HWiNFO64 (FREE)")
    print("2. Run: .\\setup_aida64.ps1")
    print("3. Or manually edit .env and set ENABLE_AIDA64=true or ENABLE_HWINFO=true")

conn.close()
