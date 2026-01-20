
import os
# import markdown (Removed)
import re

base_path = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\03"
html_base_path = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\04"
report_file = os.path.join(base_path, "2025-12-29_AutonomousAgents_Report.md")
part_final_file = os.path.join(base_path, "part_final_push.md")
html_file = os.path.join(html_base_path, "2025-12-29.index.html")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# 1. Append Volume X
report_content = read_file(report_file)
part_final_content = read_file(part_final_file)
# Insert Volume X before Appendix (or at the end if simpler, but structure matters)
# Let's insert before Volume 13 or Appendix.
# Structure: Vol 0 ... Vol 12 ... Vol 13 ... Appendix
# Let's put Volume X before Volume 13.
vol13_marker = "# Volume 13:"
if vol13_marker in report_content:
    report_content = report_content.replace(vol13_marker, part_final_content + "\n\n" + vol13_marker)
else:
    # Fallback: append at end
    report_content += "\n\n" + part_final_content

# Write back revised markdown
with open(report_file, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"Updated Markdown length: {len(report_content)}")

# 2. Convert to HTML
# We need a proper HTML template.
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
        Verified & Expanded by Unico's Brain v4.2<br>
        2025-12-29
    </div>
</body>
</html>
"""

# Simple Markdown to HTML conversion
# We'll use a loop to process headers for TOC
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
        # Paragraphs
        html_body += f'<p>{line}</p>'

toc_html += "</ul>"

final_html = html_template.replace("[CONTENT_PLACEHOLDER]", html_body)
final_html = final_html.replace("[TOC_PLACEHOLDER]", toc_html)

with open(html_file, "w", encoding="utf-8") as f:
    f.write(final_html)

print("HTML generated successfully.")
