import os
import sys
from send2trash import send2trash

DRY_RUN_FILE = "DELETION_DRY_RUN.txt"

def dry_run_delete(paths, confirmed=False):
    """
    If not confirmed, lists files to be deleted in DELETION_DRY_RUN.txt.
    If confirmed, moves them to the Recycle Bin.
    """
    abs_paths = [os.path.abspath(p) for p in paths]
    existing_paths = [p for p in abs_paths if os.path.exists(p)]
    
    if not confirmed:
        with open(DRY_RUN_FILE, "w", encoding="utf-8") as f:
            f.write("# DELETION DRY-RUN LIST\n")
            f.write("# To confirm, run with --confirm flag\n\n")
            for p in existing_paths:
                f.write(f"{p}\n")
        print(f"Dry-run list created: {DRY_RUN_FILE}")
        print("Please review the list and run with --confirm to proceed.")
    else:
        success_count = 0
        fail_count = 0
        for p in existing_paths:
            try:
                send2trash(p)
                print(f"Moved to Recycle Bin: {p}")
                success_count += 1
            except Exception as e:
                print(f"Failed: {p}. Error: {e}")
                fail_count += 1
        
        # Clean up dry-run file if it exists
        if os.path.exists(DRY_RUN_FILE):
            os.remove(DRY_RUN_FILE)
            
        print(f"\nSummary: {success_count} moved, {fail_count} failed.")

if __name__ == "__main__":
    confirm = "--confirm" in sys.argv
    targets = [a for a in sys.argv[1:] if a != "--confirm"]
    
    if not targets and not os.path.exists(DRY_RUN_FILE):
        print("Usage: python dry_run_delete.py <paths...> [--confirm]")
        sys.exit(1)
        
    if confirm and not targets and os.path.exists(DRY_RUN_FILE):
        # Read from dry-run file
        with open(DRY_RUN_FILE, "r", encoding="utf-8") as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
    dry_run_delete(targets, confirmed=confirm)
