
from jinja2 import Template
import os
import datetime

def generate_html_report(data, filename, template_html):
    """
    辞書データとテンプレートHTMLを使ってレポートを生成する
    """
    
    # 日付を追加
    data["generated_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    try:
        template = Template(template_html)
        html_content = template.render(data)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return True
    except Exception as e:
        print(f"Report Generation Error: {e}")
        return False
