from openai import OpenAI
import json
import os
from services.manual_generator import openai as shared_client

class ContentArchitect:
    USER_PRESETS_FILE = "user_presets.json"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        # Ensure client is initialized even if api_key is None, it will raise an error later if used without a key.
        # The original code had a check for shared_client, but the new instruction removes it.
        # If self.api_key is None, OpenAI() will likely fail or require an env var.
        # For faithfulness, I'll follow the instruction's client initialization.
        self.client = OpenAI(api_key=self.api_key)
        
        self.model_fast = "gpt-4o-mini"
                "required_sections": ["Communication Policy (Tone & Manner)", "Standard Talk Flows", "Scenario: Complaints", "Scenario: Inquiries", "Escalation Rules", "NG Phrases"],
                "instruction": "Focus on 'Talk Scripts'. Provide concrete 'Good Examples' and 'Bad Examples'. Emphasize the 'Tone of Voice' and empathy."
            },
            "StoreOps": {
                "name": "Store / Franchise Operations",
                "focus": "Brand Consistency, Daily Routine, Customer Service",
                "required_sections": ["Brand Concept", "Opening/Closing Procedures", "Service Standards", "Daily Routine", "Emergency Procedures", "QA Standards"],
                "instruction": "Balance 'Brand Rules' (Must-dos) with 'Local Discretion' (Can-dos). detailed checklists for Opening/Closing."
            }
        }

        self.VOLUME_PRESETS = {
            "Short": {
                "name": "Short (5-10 pages)",
                "section_count": "5-7 sections",
                "depth": "Concise. Focus on key actions only. No fluff."
            },
            "Standard": {
                "name": "Standard (15-20 pages)",
                "section_count": "10-15 sections",
                "depth": "Standard depth. Include sufficient examples and explanations."
            },
            "Deep": {
                "name": "Agency/Pro (30-50 pages)",
                "section_count": "20+ sections",
                "depth": "Extremely detailed. Exhaustive coverage. Multiple examples per step. Comprehensive formatting."
            }
        }
        
    def generate_outline(self, input_text, mode="Manual", manual_type="SOP", volume="Standard"):
        """
        Step 1: 骨子策定 (Skeleton)
        論理構成(MECE)を意識した目次を作成
        """
        preset = self.MANUAL_PRESETS.get(manual_type, self.MANUAL_PRESETS["SOP"])
        vol_preset = self.VOLUME_PRESETS.get(volume, self.VOLUME_PRESETS["Standard"])
        
        system_prompt = f"あなたはプロのコンテンツ・アーキテクトです。与えられた情報の構造を整理し、論理的な目次構成を作成してください。Mode: {mode}, Type: {preset['name']}"
        user_prompt = f"""
        以下の情報を元に、{mode}形式の実用的な構成案（目次と各節の要点）を3パターン作成してください。
        
        【マニュアル定義】
        タイプ: {preset['name']}
        重点: {preset['focus']}
        必須セクション: {', '.join(preset['required_sections'])}
        指示: {preset['instruction']}

        【ボリューム要件 (Strict)】
        ターゲット: {vol_preset['name']}
        必須セクション数: {vol_preset['section_count']}
        詳細度: {vol_preset['depth']}
        ※必ずこのセクション数を満たすように、内容を適切に分割・詳細化してください。不足する場合は具体的なサブセクションを追加すること。
        
        【入力情報】
        {input_text}
        
        【出力ルール】
        - 読者が迷わず行動できる「アクション指向」の構成にすること。
        - 各パターンはそれぞれ異なるアプローチ（例：初心者向け、網羅的、緊急対応用）をとること。
        - 出力はMarkdown形式で、見出し(#)と箇条書き(-)を使うこと。
        """
        return self._call_ai(system_prompt, user_prompt, self.model_fast)

    def generate_draft(self, outline, input_text):
        """
        Step 2: ドラフト執筆 (Drafting)
        具体例とフレームワークを強制注入して執筆
        """
        system_prompt = "あなたは熟練のビジネスライターです。骨子に従って具体的な本文を執筆してください。"
        user_prompt = f"""
        以下の構成案（Outline）に基づき、入力情報（Source）を肉付けして、詳細な原稿を執筆してください。
        
        【構成案】
        {outline}
        
        【入力情報】
        {input_text}
        
        【執筆ルール: Agency Quality】
        1. **具体性の注入**: 抽象的な表現（例：「適切に行う」）は禁止。「具体的にどうするか（例：〜を3回確認する）」を書くこと。
        2. **フレームワーク**: 手順書なら「ナンバリング(1,2,3)」、解説なら「PREP法(結論→理由→具体例→結論)」を意識すること。
        3. **Tone**: プロフェッショナルかつ読み手が安心できるトーン。
        """
        return self._call_ai(system_prompt, user_prompt, self.model_fast)

    def critique_draft(self, draft):
        """
        Step 3: 鬼の編集長レビュー (Critique)
        """
        system_prompt = "あなたは厳しい編集長です。原稿の「曖昧さ」「論理飛躍」「読みにくさ」を指摘してください。"
        user_prompt = f"""
        以下の原稿を厳しくレビューし、修正すべき点を3〜5つ挙げてください。
        具体的な修正案は不要です。「ここがダメ」という指摘だけを行ってください。
        
        【原稿】
        {draft}
        """
        return self._call_ai(system_prompt, user_prompt, self.model_fast)

    def polish_content(self, draft, critique, mode, manual_type="SOP", volume="Standard", human_critique=None):
        """
        Step 4: プロフェッショナル・リライト (Polishing)
        指摘事項を反映し、Markdown/Mermaidで整形
        """
        preset = self.MANUAL_PRESETS.get(manual_type, self.MANUAL_PRESETS["SOP"])
        vol_preset = self.VOLUME_PRESETS.get(volume, self.VOLUME_PRESETS["Standard"])

        system_prompt = f"""
        あなたはTop 1%のコピーライター兼テクニカルライターです。
        以下の「{preset['name']}」の基準を厳密に遵守し、最高品質のドキュメントに仕上げてください。
        
        【厳守事項 (Strict Rules)】
        1. **Focus**: {preset['focus']}
        2. **Volume/Depth**: {vol_preset['depth']} (Target: {vol_preset['section_count']})
        3. **Instruction**: {preset['instruction']}
        """

        # Append Human Critique if exists
        combined_critique = f"【編集長(AI)の指摘】\n{critique}"
        if human_critique:
            combined_critique += f"\n\n【監修者(人間)の追加指示】\n{human_critique}\n※この「追加指示」は編集長の指摘より優先してください。"

        user_prompt = f"""
        以下の「原稿」を、指摘を踏まえてリライトし、最終稿を作成してください。
        また、内容に応じて **Mermaid記法** の図解（フローチャートやシーケンス図）を適切な場所に挿入してください。
        
        【原稿】
        {draft}
        
        {combined_critique}
        
        【最終出力要件】
        - フォーマット: 美しいMarkdown
        - 図解: 業務フローや手順がある場合は、必ず ```mermaid ... ``` ブロックを入れること。
        - デザイン: 重要なポイントは**太字**や> コールアウト(引用表示)を使って強調すること。
        
        【Self-Check (書き出し前に確認すること)】
        - 必須セクション ({', '.join(preset['required_sections'])}) は全て網羅されていますか？
        - "{vol_preset['name']}" のボリューム感に達していますか？肉付けは十分ですか？
        YESなら出力してください。
        """
        # Using a smarter model here if possible, but sticking to mini for speed/stability unless config changes.
        return self._call_ai(system_prompt, user_prompt, self.model_fast) # Keep fast for now
        # Using a smarter model here if possible, but sticking to mini for speed/stability unless config changes.
        return self._call_ai(system_prompt, user_prompt, self.model_fast) # Keep fast for now

    def _call_ai(self, system, user, model):
        if not self.client: return "Error: API Key not set"
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Generation Error: {e}"
