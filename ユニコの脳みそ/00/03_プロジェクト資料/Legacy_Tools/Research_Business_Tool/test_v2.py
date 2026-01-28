
from search_engine import search_web
from report_generator import generate_html_report
from data import HTML_REPORT_TEMPLATE
import os

print("Testing Search Engine...")
results = search_web("Python programming trends 2025", num_results=3)
if results:
    print(f"Success! Found {len(results)} results.")
    print(f"Sample: {results[0]['title']}")
else:
    print("Search failed or returned no results.")

print("\nTesting Report Generator...")
dummy_data = {
    "title": "Test Report",
    "ai_analysis": "This is a <b>test</b> analysis.",
    "search_results": results
}

if generate_html_report(dummy_data, "test_report.html", HTML_REPORT_TEMPLATE):
    print("Success! HTML report generated.")
    if os.path.exists("test_report.html"):
        print("File exists.")
else:
    print("Report generation failed.")
