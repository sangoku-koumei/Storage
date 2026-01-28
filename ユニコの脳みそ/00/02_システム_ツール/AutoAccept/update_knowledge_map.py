import os
import re

KNOWLEDGE_MAP_PATH = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\00_知識マップ.md"
BIBLES_DIR = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Deep_Knowledge_Bibles"
MEMOS_DIR = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\作業メモ"

def extract_metadata(file_path):
    tags = []
    summary = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(2000)  # Read more for summary
            # Extract tags
            tag_match = re.search(r"tags:\s*\[(.*?)\]", content)
            if tag_match:
                tags = [t.strip() for t in tag_match.group(1).split(",")]
            
            # Extract summary (first paragraph after # Title or ## 序章)
            lines = content.split("\n")
            found_start = False
            for line in lines:
                l = line.strip()
                if l.startswith("# ") or "## 序章" in l:
                    found_start = True
                    continue
                if found_start and l:
                    if l.startswith("---") or l.startswith("date:") or l.startswith("tags:") or l.startswith("source:"):
                        continue
                    # Skip lines that are just a list of links
                    if re.match(r"^(\[\[.*?\]\]\s*\|*\s*)+$", l):
                        continue
                    summary = l
                    if len(summary) > 150:
                        summary = summary[:147] + "..."
                    break
            
            date_match = re.search(r"date:\s*(\d{4}-\d{2}-\d{2})", content)
            date = date_match.group(1) if date_match else None
            return date, tags, summary
    except: pass
    return None, [], ""

def get_bible_list():
    bibles_dict = {}
    for root, dirs, files in os.walk(BIBLES_DIR):
        for file in files:
            if file.endswith(".md") and "Vol." in file:
                match = re.search(r"Vol\.(\d+)([^_]*)", file)
                if match:
                    vol_num = int(match.group(1))
                    full_path = os.path.join(root, file)
                    date, tags, summary = extract_metadata(full_path)
                    title = file.replace(".md", "")
                    display_title = title.split("_")[1] if "_" in title else title
                    
                    memo_file = f"{date}_作業メモ.md" if date else None
                    memo_exists = os.path.exists(os.path.join(MEMOS_DIR, memo_file)) if memo_file else False
                    
                    item = {
                        "vol": vol_num,
                        "file": title,
                        "display": f"Vol.{vol_num}: {display_title}",
                        "date": date,
                        "tags": tags,
                        "summary": summary,
                        "memo": memo_file.replace(".md", "") if memo_exists else None
                    }
                    if vol_num not in bibles_dict or (date and not bibles_dict[vol_num]["date"]):
                        bibles_dict[vol_num] = item
    return sorted(bibles_dict.values(), key=lambda x: x["vol"])

def update_map():
    bibles = get_bible_list()
    if not bibles: return

    with open(KNOWLEDGE_MAP_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    max_vol = 0
    found_vols = set()

    # Pre-process headers and items
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        updated_any_group = False
        for start, end in [(30, 59), (60, 89), (90, 120)]:
            header = f"### Vol. {start} - {end}"
            if header in line:
                group = [b for b in bibles if start <= b["vol"] <= end]
                for b in group:
                    date_prefix = f"[{b['date']}] " if b['date'] else ""
                    memo_suffix = f" (関連: [[{b['memo']}|メモ]])" if b['memo'] else ""
                    new_lines.append(f"- {date_prefix}**[[{b['file']}|{b['display']}]]**{memo_suffix}\n")
                    if b['tags']:
                        new_lines.append(f"    - 🏷️ Tags: {' '.join(['#'+t for t in b['tags']])}\n")
                    if b['summary']:
                        new_lines.append(f"    - 📝 Summary: {b['summary']}\n")
                    
                    found_vols.add(b['vol'])
                    max_vol = max(max_vol, b['vol'])
                
                updated_any_group = True
                i += 1
                while i < len(lines) and not lines[i].startswith("###") and not lines[i].startswith("## "):
                    i += 1
                break
        
        if not updated_any_group:
            if "## 🚨 欠落・未作成バイブル (Gaps)" in line:
                # Skip old gaps section if it exists
                i += 1
                while i < len(lines) and not lines[i].startswith("## "):
                    i += 1
                continue
            i += 1

    # Add Gap Finder at the bottom
    new_lines.append("\n## 🚨 欠落・未作成バイブル (Gaps)\n")
    gaps = []
    for v in range(30, max_vol + 1):
        if v not in found_vols:
            gaps.append(str(v))
    
    if gaps:
        new_lines.append(f"- 未作成・欠番: {', '.join(gaps)}\n")
    else:
        new_lines.append("- 現在、重大な欠番はありません。\n")

    with open(KNOWLEDGE_MAP_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Knowledge Map integrated with Tags, Summaries, and Gap Finder.")

if __name__ == "__main__":
    update_map()
