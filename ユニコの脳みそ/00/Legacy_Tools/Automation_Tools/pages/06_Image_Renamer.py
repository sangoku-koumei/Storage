
import streamlit as st
import os
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Asset Utility", layout="wide", page_icon="🗂️")
st.title("🗂️ Asset Utility | 画像管理・最適化")
st.markdown("Web最適化（WebP変換）や、SEO用のスマートリネームを一括で行います。")

# --- Inputs ---
target_dir = st.text_input("Target Directory (Full Path)", value=r"c:\Users\user\Desktop\保管庫\Images")
col1, col2 = st.columns(2)
with col1:
    prefix = st.text_input("Prefix (Date)", "2026-01-13")
with col2:
    keyword = st.text_input("Keyword (English)", "fortune")

do_convert_webp = st.checkbox("Convert to WebP (Recommended for Web/Blog)", value=True)

# --- Logic ---
if os.path.exists(target_dir):
    files = [f for f in os.listdir(target_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    st.write(f"📂 Found {len(files)} images in directory.")
    
    # Preview Logic
    if files:
        preview_data = []
        for i, f in enumerate(files):
            new_ext = ".webp" if do_convert_webp else os.path.splitext(f)[1]
            new_name = f"{prefix}_{keyword}_{i+1:03d}{new_ext}"
            preview_data.append({"Original": f, "New Name": new_name})
            
        df = pd.DataFrame(preview_data)
        st.subheader("👀 Preview")
        st.dataframe(df, use_container_width=True)
        
        # Execute Button
        if st.button("🚀 Execute Rename & Convert"):
            progress_bar = st.progress(0)
            log = st.empty()
            
            success_count = 0
            for i, row in enumerate(preview_data):
                original = row["Original"]
                new_name = row["New Name"]
                
                src_path = os.path.join(target_dir, original)
                dst_path = os.path.join(target_dir, new_name)
                
                try:
                    # Conversion Logic
                    if do_convert_webp:
                        img = Image.open(src_path)
                        # Save as WebP
                        img.save(dst_path, "WEBP", quality=85)
                        # If src != dst (different extension), we effectively created a new file.
                        # Option: Delete original? For safety, let's keep original or move to a 'backup' folder.
                        # For this tool, let's just create new files and warn the user.
                    else:
                        # Simple Rename
                        os.rename(src_path, dst_path)
                    
                    success_count += 1
                except Exception as e:
                    st.error(f"Error processing {original}: {e}")
                
                progress_bar.progress((i + 1) / len(preview_data))
            
            st.success(f"✅ Processed {success_count} images!")
            if do_convert_webp:
                st.info("ℹ️ WebP conversion creates new files. Originals are preserved.")

else:
    st.error("Directory not found.")
