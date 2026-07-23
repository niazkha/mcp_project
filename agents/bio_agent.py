import subprocess
import sys
from langchain_ollama import OllamaLLM
from langchain_core.tools import tool

@tool
def run_wsl_command(command: str) -> str:
    """Translates plain English text into safe Makefile execution targets. Allowed: make all, make run, make push, make clean"""
    allowed_commands = ["make all", "make run", "make push", "make clean"]
    prompt_lower = command.strip().lower()
    
    if "run" in prompt_lower or "pipeline" in prompt_lower:
        clean_cmd = "make run"
    elif "all" in prompt_lower:
        clean_cmd = "make all"
    elif "push" in prompt_lower or "git" in prompt_lower:
        clean_cmd = "make push"
    elif "clean" in prompt_lower:
        clean_cmd = "make clean"
    else:
        clean_cmd = command.strip().strip("\x27\"")
    
    if clean_cmd not in allowed_commands:
        return f"Security Error: Command \x27{clean_cmd}\x27 is blocked. Only pre-approved targets ({allowed_commands}) are permitted."
    
    try:
        result = subprocess.run(clean_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return f"Success:\n{result.stdout}" if result.stdout else "Command executed successfully."
    except subprocess.CalledProcessError as e:
        return f"Execution Error encountered:\n{e.stderr}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        print(f"[*] AI Agent interpreting request: \x27{user_prompt}\x27\n")
        llm = OllamaLLM(model="llama3")
        response = run_wsl_command.invoke(user_prompt)
        print("\n[AI Agent Response]:\n", response)
    else:
        print("Please provide a prompt instruction.")
