
import os

base_path = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\03"
report_file = os.path.join(base_path, "2025-12-29_AutonomousAgents_Report.md")
part0_file = os.path.join(base_path, "part0.md")
part13_file = os.path.join(base_path, "part13.md")
diary_file = os.path.join(base_path, "part5_diary.md")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

report_content = read_file(report_file)
part0_content = read_file(part0_file)
part13_content = read_file(part13_file)
diary_content = read_file(diary_file)

# Insert Volume 0 after the header
# Find the start of Volume 1
vol1_marker = "# Volume 1:"
if vol1_marker in report_content:
    report_content = report_content.replace(vol1_marker, part0_content + "\n\n" + vol1_marker)

# Insert Diary expansion inside Volume 5
# Find a specific date to append after, e.g., "### 4月30日"
diary_marker = "### 4月30日"
# We want to insert BEFORE 4/30 or AFTER? The snippet is "4/25", so it should be before 4/30.
# Let's verify the file content structure.
# Just appending it at the end of Volume 5 section might be safer if markers are tricky.
# But "### 4月30日" exists in the file (I saw it in previous view).
# Let's insert it before 4月30日.
if diary_marker in report_content:
    report_content = report_content.replace(diary_marker, diary_content + "\n\n" + diary_marker)

# Insert Volume 13 before Appendix
appendix_marker = "# Appendix:"
if appendix_marker in report_content:
    report_content = report_content.replace(appendix_marker, part13_content + "\n\n" + appendix_marker)

# Write back
with open(report_file, "w", encoding="utf-8") as f:
    f.write(report_content)

print("Successfully updated report with new volumes.")
