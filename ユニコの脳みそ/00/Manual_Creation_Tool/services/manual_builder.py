import json
import os
from datetime import datetime
from services.generator import set_api_key, openai

class ManualBuilder:
    MANUAL_PRESETS = {
        "SOP": {
            "name": "Standard Operating Procedure (SOP)",
            "focus": "Consistency, Quality Control, Safety",
            "required_sections": ["Objective", "Scope", "Prerequisites", "Step-by-Step Instructions", "Quality Standards", "Exception Handling", "Checklist"],
            "instruction": "Focus on clarity and reproducibility. Use numbered lists for steps. Clearly define 'Success Critera' for each task."
        },
        "System": {
            "name": "System Operation (Scenario-based)",
            "focus": "Efficiency, Screen Navigation, Troubleshooting",
            "required_sections": ["System Overview", "Use Case Scenarios", "Screen-by-Screen Guide", "Troubleshooting", "FAQ"],
            "instruction": "Do not just explain buttons. Explain 'Business Scenarios' (e.g., How to issue an invoice). Map screen actions to business outcomes."
        },
        "Training": {
            "name": "Training / Onboarding",
            "focus": "Learning Retention, Engagement, Evaluation",
            "required_sections": ["Learning Objectives", "Curriculum Overview", "Module 1: Basic", "Module 2: Advanced", "Exercises/Drills", "Evaluation/Test"],
            "instruction": "Structure this as a course. Define clear 'Learning Objectives' for each section. Include 'Practice Exercises' and 'Quizzes'."
        },
        "CallCenter": {
            "name": "Call Center / Customer Support",
            "focus": "Empathy, Speed, Accuracy, Toneality",
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

    def __init__(self, api_key=None):
        if api_key:
            set_api_key(api_key)

    def get_presets(self):
        return self.MANUAL_PRESETS

    def create_draft(self, input_text, mode, manual_type="SOP", hearing_data=None):
        """
        Step 1: Create a Skeleton Draft (JSON Structure) using GPT-4o-mini
        """
        if not openai: return {"error": "API Key missing"}

        # Load Preset Logic
        preset = self.MANUAL_PRESETS.get(manual_type, self.MANUAL_PRESETS["SOP"])
        
        # Combine Input + Hearing Data
        context = f"Input: {input_text}\n"
        if hearing_data:
            context += f"Hearing Info: {json.dumps(hearing_data, ensure_ascii=False)}\n"

        prompt = f"""
        You are an expert Document Architect. Create a detailed structural draft for a '{mode}' manual.
        
        【Manual Type】
        Type: {preset['name']}
        Focus: {preset['focus']}
        Required Sections: {', '.join(preset['required_sections'])}
        Instruction: {preset['instruction']}

        【Input Context】
        {context}

        【Output Requirement】
        Return a JSON structure representing the manual sections.
        Format:
        {{
            "title": "Manual Title",
            "target_audience": "Target Reader",
            "sections": [
                {{
                    "heading": "Section Title",
                    "intent": "What is this section for?",
                    "key_points": ["Point 1", "Point 2", "Point 3"],
                    "draft_content": "Rough draft text describing the content..."
                }}
            ]
        }}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}

    def finalize_manual(self, draft_json, mode, feedback=None, cast_key="Standard"):
        """
        Step 3: Polish and Finalize (GPT-4o)
        """
        if not openai: return "Error: API Key"

        draft_str = json.dumps(draft_json, ensure_ascii=False)
        
        system_prompt = "You are a professional top-tier copywriter."
        if mode == "Manga":
            system_prompt = """
            You are a Manga Scriptwriter. Output pure HTML/Markdown structure.
            
            【CRITICAL VISUAL STRATEGY: Empty Bubble】
            - We will overlay text using HTML/CSS.
            - The image prompts you generate MUST specify: "Speech bubble is empty" or "Character pointing to blank space".
            - NO text inside the generated image itself.
            - Ensure ONE key message per panel.
            """
        
        feedback_context = ""
        if feedback:
            feedback_context = f"\n【Editor Feedback (CRITICAL)】\nThe editor has reviewed the draft and requested these changes:\n{feedback}\nPlease strictly implement these corrections."

        prompt = f"""
        Refine the following Draft Manual into a Final High-Quality Document.
        
        【Draft Data】
        {draft_str}

        【Mode】
        {mode} (Cast: {cast_key})
        {feedback_context}

        【Requirements】
        - Expand 'draft_content' into professional prose.
        - Add 'Specific Examples' where abstract.
        - Format as Markdown.
        - **Manga Mode**:
            - Divide content into "Scenes" (Panels).
            - For each panel, provide:
              1. `Narrative`: Context description.
              2. `Img Prompt`: DALL-E 3 prompt. (Always include "Manga style, wide aspect ratio").
              3. `Dialogue`: Who says what (Rookie/Mentor).
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o", # Using High Quality Model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def save_state(self, filepath, state_data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)

    def load_state(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
