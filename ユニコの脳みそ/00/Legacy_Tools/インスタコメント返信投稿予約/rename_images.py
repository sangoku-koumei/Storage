
import os
import sys

def batch_rename_images(directory):
    """
    Renames all images in the directory to image_001.jpg, image_002.jpg...
    Sorted by Creation Date (Oldest first) -> Assuming you create them in order of the sheet rows.
    """
    # Supported extensions
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    
    # Get all files
    files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in extensions]
    
    if not files:
        print(f"No images found in {directory}")
        return

    # Sort by creation time (Older is first = Row 1)
    # This matches the user workflow: "Create image for row 1, then row 2..."
    files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)))
    
    print(f"Found {len(files)} images. Renaming...")
    
    for i, filename in enumerate(files):
        ext = os.path.splitext(filename)[1].lower()
        new_name = f"image_{str(i+1).zfill(3)}{ext}" # image_001.jpg
        
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        
        if old_path != new_path:
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_name}")
            
    print("Done! All images are ready for the robot.")

if __name__ == "__main__":
    print("--- Image Batch Renamer ---")
    print("This tool renames all images in a folder to image_001.jpg, image_002.jpg...")
    print("based on the order they were created.")
    
    target_dir = input("Enter the folder path containing your images: ").strip()
    
    if os.path.isdir(target_dir):
        batch_rename_images(target_dir)
    else:
        print("Invalid directory.")
