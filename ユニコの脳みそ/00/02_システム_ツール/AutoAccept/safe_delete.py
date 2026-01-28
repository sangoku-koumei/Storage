import os
import sys
from send2trash import send2trash

def safe_delete(paths):
    """
    Moves files or directories to the Recycle Bin.
    """
    success_count = 0
    fail_count = 0
    
    for path in paths:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"Skipping: {abs_path} (File not found)")
            continue
            
        try:
            send2trash(abs_path)
            print(f"Moved to Recycle Bin: {abs_path}")
            success_count += 1
        except Exception as e:
            print(f"Failed to move to Recycle Bin: {abs_path}. Error: {e}")
            fail_count += 1
            
    print(f"\nSummary: {success_count} moved, {fail_count} failed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python safe_delete.py <path1> <path2> ...")
        sys.exit(1)
        
    safe_delete(sys.argv[1:])
