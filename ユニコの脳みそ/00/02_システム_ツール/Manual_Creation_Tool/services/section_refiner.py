import re
from services.manual_generator import openai as shared_client
from openai import OpenAI
import os

class SectionRefiner:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"

    def parse_markdown_to_sections(self, markdown_text):
        """
        Parse markdown into a dict of {header: content}
        Supports H1 (#) and H2 (##) as main dividers.
        """
        # Split by ## headers (Assuming H1 is Title)
        # Using regex to find ## Heading
        sections = []
        
        # 1. Split into H2 chunks
        parts = re.split(r'\n(## .+)\n', markdown_text)
        
        if len(parts) < 2:
            return [{"heading": "Full Document", "content": markdown_text}]

        # parts[0] is usually Intro (before first ##)
        if parts[0].strip():
            sections.append({"heading": "Introduction", "content": parts[0]})

        # Iterate 
        for i in range(1, len(parts), 2):
            heading = parts[i].strip().replace("## ", "")
            content = parts[i+1] if i+1 < len(parts) else ""
            sections.append({"heading": heading, "content": "## " + heading + "\n" + content})

        return sections

    def reconstruct_markdown(self, sections):
        """Join sections back to full text"""
        full_text = ""
        for sec in sections:
            full_text += sec["content"] + "\n"
        return full_text

    def refine_section_content(self, section_content, instruction):
        """
        Rewrite specific section based on instruction.
        """
        system_prompt = """
        あなたは熟練の編集者です。
        提供された「マニュアルの特定の章（セクション）」を、ユーザーの指示に従ってリライトしてください。
        
        【ルール】
        1. 入力されたセクションの範囲のみを出力すること。前後の挨拶は不要。
        2. Markdown形式（見出しレベルなど）を崩さないこと。
        """
        
        user_prompt = f"""
        【対象セクション】
        {section_content}
        
        【修正指示】
        {instruction}
        
        【リライト後のセクション出力】
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
