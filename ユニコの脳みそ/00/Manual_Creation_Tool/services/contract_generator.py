from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

class ContractGenerator:
    def __init__(self):
        self._register_font()

    def _register_font(self):
        self.font_name = "Helvetica"
        try:
            # Try MS Gothic for Japanese support on Windows
            font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Gothic', font_path))
                self.font_name = 'Gothic'
            else:
                # Fallback to Meiryo or others if needed
                pass
        except:
            pass

    def generate_contract(self, client_name, client_address, rep_name, portfolio_option, output_path="Contract.pdf"):
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        c.setFont(self.font_name, 11)
        
        # Simple rendering of the contract text
        # (For a real tool, we might want a flowable document, but canvas is fine for fixed structure)
        
        y = height - 50
        
        # Title
        c.setFont(self.font_name, 16)
        c.drawString(width/2 - 60, y, "業務委託契約書")
        y -= 40
        
        c.setFont(self.font_name, 10)
        text_lines = [
            f"委託者 {client_name}（以下「甲」）と 受託者 株式会社Unico Brain（以下「乙」）は、",
            "マニュアル作成業務に関し、以下の通り契約を締結する。",
            "",
            "第1条（目的）",
            "甲は乙に対し、本業務を委託し、乙はこれを受託する。",
            "",
            "第2条（成果物の権利）",
            "1. 成果物の著作権は乙に帰属する。",
            "2. 甲は成果物を社内業務等の範囲で自由に使用できる。",
            "",
            "第3条（ポートフォリオ掲載）",
            "1. 乙は成果物を実績として公開できるものとする。",
            f"2. 特約: {portfolio_option}",
            "   (掲載不可の場合は社名・ロゴを伏せる等の対応を行う)",
            "",
            "第4条（免責）",
            "乙は成果物の完全性を保証しない。AI利用に同意するものとする。",
            "",
            "--------------------------------------------------------------------------------",
            f"契約日: {datetime.now().strftime('%Y年%m月%d日')}",
            "",
            "【甲】",
            f"住所: {client_address}",
            f"氏名: {client_name}",
            f"代表: {rep_name}  (印)",
            "",
            "【乙】",
            "住所: 東京都...",
            "氏名: 株式会社Unico Brain",
        ]

        for line in text_lines:
            c.drawString(50, y, line)
            y -= 15
            if y < 50: # Page break logic simplified
                c.showPage()
                y = height - 50
                c.setFont(self.font_name, 10)

        c.save()
        return output_path

    def generate_receipt(self, client_name, amount, output_path="Receipt.pdf"):
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        c.setFont(self.font_name, 12)
        
        y = height - 100
        
        # Header
        c.setFont(self.font_name, 20)
        c.drawString(width/2 - 40, y, "領収書")
        y -= 60
        
        # Recipient
        c.setFont(self.font_name, 14)
        c.drawString(50, y, f"{client_name} 様")
        y -= 50
        
        # Amount
        c.setFont(self.font_name, 24)
        # Add comma formatting
        amount_str = "{:,}".format(int(amount))
        c.drawString(100, y, f"¥{amount_str} -")
        c.line(100, y-5, 300, y-5)
        y -= 40
        
        # Detail
        c.setFont(self.font_name, 12)
        c.drawString(100, y, "但 マニュアル作成代金として")
        y -= 100
        
        # Issuer
        c.setFont(self.font_name, 12)
        c.drawString(350, y, "株式会社Unico Brain")
        c.drawString(350, y-20, "東京都...")
        c.drawString(350, y-40, "発行日: " + datetime.now().strftime('%Y年%m月%d日'))
        
        c.save()
        return output_path
