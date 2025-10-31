import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)

def generate_code(prompt, language="python"):
    full_prompt = f"Write a {language} program for the following task:\n{prompt}"
    try:
        response = client.chat.completions.create(
            #Updated model (recommended)
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert software engineer."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print(" LLaMA 3.1 Code Assistant (Groq API)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Enter your programming request: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        language = input("Enter language (default: python): ") or "python"
        print("\nGenerating code...\n")

        result = generate_code(user_input, language)
        print("Generated Code:\n")
        print(result)
        print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    main()
