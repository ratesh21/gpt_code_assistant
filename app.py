import gradio as gr
from groq import Groq
from dotenv import load_dotenv
import os, datetime, re

# === Load API key ===
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# === Helper Functions ===
def sanitize_filename(name):
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)

def save_code(code, language):
    os.makedirs("outputs", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/{sanitize_filename(language)}_{ts}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    return f" Code saved to `{filename}`"

# === Simple Heuristic Language Detector ===
def detect_language(prompt_or_code):
    text = prompt_or_code.lower()
    if "python" in text or "def " in text or "import " in text:
        return "python"
    elif "#include" in text or "printf" in text:
        return "c"
    elif "iostream" in text or "cout" in text:
        return "cpp"
    elif "public static void main" in text or "System.out.println" in text:
        return "java"
    elif "console.log" in text or "function(" in text:
        return "javascript"
    else:
        return "python"  # default fallback

# === Code Generation ===
def generate_code(prompt, language, history):
    try:
        # Auto-detect language if none selected
        if language == "auto" or not language:
            language = detect_language(prompt)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert software engineer."},
                {"role": "user", "content": f"Write a {language} program for: {prompt}"}
            ],
            temperature=0.4
        )
        text = response.choices[0].message.content.strip()
        text = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "").strip()

        history.append({"action": "Generated", "prompt": prompt, "language": language, "code": text})
        return text, history, language
    except Exception as e:
        return f"Error: {e}", history, language

# === Debugging & Explanation ===
def debug_code(code, error_message, language, history):
    try:
        # Auto-detect language from code
        if language == "auto" or not language:
            language = detect_language(code)

        debug_prompt = f"""
You are a professional {language} developer and debugger.
Here is the user's code that produced an error:

CODE:
{code}

ERROR MESSAGE / OUTPUT:
{error_message}

Please identify and fix the issue. Return only the corrected code.
"""
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert code debugger."},
                {"role": "user", "content": debug_prompt}
            ],
            temperature=0.3
        )
        fixed_code = response.choices[0].message.content.strip()
        fixed_code = re.sub(r"```[a-zA-Z]*", "", fixed_code).replace("```", "").strip()

        # Explain fix
        exp_prompt = f"Explain briefly (under 100 words) what was wrong in this {language} code and how it was fixed."
        exp_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert software explainer."},
                {"role": "user", "content": f"{exp_prompt}\n\nOriginal Code:\n{code}\n\nFixed Code:\n{fixed_code}"}
            ],
            temperature=0.4
        )
        explanation = exp_response.choices[0].message.content.strip()

        history.append({
            "action": "Debugged",
            "language": language,
            "error": error_message,
            "fixed_code": fixed_code,
            "explanation": explanation
        })
        return fixed_code, explanation, history, language
    except Exception as e:
        return f"Error: {e}", "Could not generate explanation.", history, language

# === GUI ===
with gr.Blocks(theme=gr.themes.Soft(primary_hue="violet", neutral_hue="gray"), title="LLaMA 3.1 Code Assistant") as demo:
    gr.HTML("<h1 style='text-align:center;'>🧠 LLaMA 3.1 Code Assistant + Debugger + Explainer</h1>")
    gr.Markdown("An intelligent, debugging-friendly AI tool built with **Groq API (LLaMA 3.1)** — generate, debug, and learn code effortlessly.")

    history = gr.State([])

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Code Generation")
            prompt = gr.Textbox(label="Enter your programming request", placeholder="e.g., Write a Python program to check palindrome", lines=3)
            language = gr.Dropdown(
                ["auto", "python", "c", "cpp", "java", "javascript"],
                label="Select Language (auto-detect default)",
                value="auto"
            )
            run_btn = gr.Button("Generate Code", variant="primary")
            output = gr.Code(label="Generated Code", language="python", interactive=False)
            save_btn = gr.Button("Save Code")
            save_status = gr.Markdown("")
        with gr.Column(scale=2):
            gr.Markdown("### Debugging & Explanation")
            error_box = gr.Textbox(label="Paste Error Message / Output", lines=3, placeholder="e.g., segmentation fault, syntax error...")
            debug_btn = gr.Button("Debug Code")
            debugged_output = gr.Code(label="Fixed Code", language="python", interactive=False)
            explanation_box = gr.Textbox(label="Explanation", interactive=False, lines=4)

    # Event Bindings
    run_btn.click(fn=generate_code, inputs=[prompt, language, history], outputs=[output, history, language])
    save_btn.click(fn=save_code, inputs=[output, language], outputs=save_status)
    debug_btn.click(fn=debug_code, inputs=[output, error_box, language, history], outputs=[debugged_output, explanation_box, history, language])

    with gr.Accordion("Session Memory (History)", open=False):
        gr.JSON(history)

# === Launch ===
if __name__ == "__main__":
    demo.launch()
