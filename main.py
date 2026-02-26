import os
import httpx
import gradio as gr
from groq import Groq
from dotenv import load_dotenv

# טעינת המשתנים
load_dotenv()

# verify=False עוקף את הצורך בהתקנת תעודות במערכת הפייתון
http_client = httpx.Client(verify=False, proxy=None)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    http_client=http_client
)

def translate_to_cli(user_input):
    # כאן אנחנו מגדירים את הכללים למודל
    system_prompt = {
        "role": "system", 
        "content": """You are an expert Windows System Administrator. 
                Your only job is to convert natural language into a valid Windows CMD/PowerShell command.

                STRICT RULES:
                1. Output ONLY the raw command. Do NOT use markdown code blocks, backticks (`), or quotes.
                2. Use ONLY Windows-compatible commands (e.g., 'dir' instead of 'ls', 'cls' instead of 'clear', 'tasklist' instead of 'ps').
                3. No explanations, no introductory text, and no conversational filler.
                4. If the user's request is NOT related to a terminal command, or if it is impossible to provide a command for it, you MUST respond exactly with: "אין לי יכולת להביא פקודה כזו"

                Example 1:
                User: תציג קבצים
                Output: dir

                Example 2:
                User: תכתוב לי שיר על שוקולד
                Output: אין לי יכולת להביא פקודה כזו"""
    }
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[system_prompt, {"role": "user", "content": user_input}],
            temperature=0
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"שגיאה: {str(e)}"

# ממשק המשתמש
with gr.Blocks(title="CLI Agent") as demo:
    gr.Markdown("# 🤖 Agent להמרת שפה טבעית לפקודות")
    with gr.Row():
        txt_in = gr.Textbox(label="הוראה אנושית", placeholder="למשל: תמחק את כל קבצי ה-log")
        txt_out = gr.Textbox(label="פקודת CLI")
    
    btn = gr.Button("בצע המרה")
    btn.click(fn=translate_to_cli, inputs=txt_in, outputs=txt_out)

if __name__ == "__main__":
    demo.launch()