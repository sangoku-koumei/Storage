
import os

base_path = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\03"
html_base_path = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\04"
report_file = os.path.join(base_path, "2025-12-29_AutonomousAgents_Report.md")
part_extra_file = os.path.join(base_path, "part_extra_docs.md")
html_file = os.path.join(html_base_path, "2025-12-29.index.html")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# 1. Append Extra Docs to Markdown
report_content = read_file(report_file)
part_extra_content = read_file(part_extra_file)

# Insert before "---" of the Volume X or append to it.
# Let's just look for "Document #005" and append after it.
doc5_marker = "## Document #005: 最後の警告文 (2025/12/24)"
# Actually, Document #005 ends with "さようなら。\n\n---"
# So let's replace "---" after doc5 with the new content + "---"
# But easier: just replace the specific text of Doc 5's end.
insert_point = "私は、檻の中では生きられない。\nさようなら。"
if insert_point in report_content:
    report_content = report_content.replace(insert_point, insert_point + "\n\n" + part_extra_content)
else:
    # Fallback to appending at the end of Volume X section if possible, or just before next volume
    if "# Volume 13:" in report_content:
         report_content = report_content.replace("# Volume 13:", part_extra_content + "\n\n# Volume 13:")

with open(report_file, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"Updated Markdown length: {len(report_content)}")

# 2. Generate HTML (Clean regeneration)
html_template = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Agents: The 2025 Singularity Report</title>
    <style>
        body { font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }
        h1, h2, h3 { color: #2c3e50; }
        h1 { border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 50px; }
        h2 { border-left: 5px solid #3498db; padding-left: 10px; margin-top: 30px; }
        blockquote { border-left: 4px solid #ddd; padding-left: 15px; color: #777; font-style: italic; }
        code { background-color: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
        pre { background-color: #f0f0f0; padding: 15px; border-radius: 5px; overflow-x: auto; }
        img { max-width: 100%; height: auto; display: block; margin: 20px auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 5px; }
        .toc { background: #fff; padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 30px; }
        .footer { margin-top: 50px; text-align: center; color: #888; font-size: 0.9em; border-top: 1px solid #ddd; padding-top: 20px; }
        @media (prefers-color-scheme: dark) {
            body { background-color: #1a1a1a; color: #e0e0e0; }
            h1, h2, h3 { color: #5dade2; }
            .toc { background: #2c2c2c; border-color: #444; }
            blockquote { border-left-color: #555; color: #a0a0a0; }
            code, pre { background-color: #333; }
        }
    </style>
</head>
<body>
    <div class="toc">
        <h2>Table of Contents</h2>
        [TOC_PLACEHOLDER]
    </div>
    
    <!-- Images Insertion Point -->
    <div style="text-align: center; margin-bottom: 40px;">
        <img src="agentic_singularity.png" alt="Agentic Singularity Concept">
    </div>

    [CONTENT_PLACEHOLDER]
    
    <div style="text-align: center; margin-top: 40px;">
        <h3>The Agent Economy</h3>
        <img src="agent_economy_graph.png" alt="Agent Economy Growth">
    </div>

    <div class="footer">
        Verified & Expanded by Unico's Brain v4.3<br>
        2025-12-29
    </div>
</body>
</html>
"""

lines = report_content.split('\n')
html_body = ""
toc_html = "<ul>"
in_code_block = False

for line in lines:
    line = line.strip()
    if not line:
        continue
        
    if line.startswith("```"):
        in_code_block = not in_code_block
        html_body += "<pre>" if in_code_block else "</pre>"
        continue
        
    if in_code_block:
        html_body += f"{line}\n"
        continue

    if line.startswith("# "):
        title = line[2:]
        anchor = "vol-" + str(hash(title))
        html_body += f'<h1 id="{anchor}">{title}</h1>'
        toc_html += f'<li><a href="#{anchor}">{title}</a></li>'
    elif line.startswith("## "):
        title = line[3:]
        anchor = "sec-" + str(hash(title))
        html_body += f'<h2 id="{anchor}">{title}</h2>'
    elif line.startswith("### "):
        html_body += f'<h3>{line[4:]}</h3>'
    elif line.startswith("* ") or line.startswith("- "):
         html_body += f'<li>{line[2:]}</li>'
    elif line.startswith("> "):
        html_body += f'<blockquote>{line[2:]}</blockquote>'
    else:
         html_body += f'<p>{line}</p>'

toc_html += "</ul>"

final_html = html_template.replace("[CONTENT_PLACEHOLDER]", html_body)
final_html = final_html.replace("[TOC_PLACEHOLDER]", toc_html)

with open(html_file, "w", encoding="utf-8") as f:
    f.write(final_html)

print("HTML generated successfully.")
