import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

#Print to check if key is loaded (for debugging)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file location and format.")

#Initialize the OpenAI client
client = OpenAI(api_key=api_key)

def generate_code(prompt, language="python"):
    full_prompt = f"Write a {language} program for the following request:\n{prompt}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert programmer."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print("GPT Code Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Enter your programming request: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        language = input("Enter language (default: python): ") or "python"
        print("\n⏳ Generating code...\n")

        result = generate_code(user_input, language)
        print("Generated Code:\n")
        print(result)
        print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    main()
