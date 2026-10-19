# Manages Ollama model initialization and prompt/chat request helpers.

# Standard library
import os
import re
import time

# Third-party
import ollama

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# See https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx#valid-parameters-and-values
OLLAMA_DEFAULT_OPTIONS = {
    "seed": 42,
    "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "16384")),
    "temperature": 0.6,  # recommended for DeepSeek-R1
}

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)


def strip_reasoning(text):
    """Remove DeepSeek-R1 <think>...</think> reasoning from a response."""
    if not text:
        return text
    text = _THINK_BLOCK.sub("", text)
    if "</think>" in text:  # opening tag missing
        text = text.split("</think>")[-1]
    text = re.sub(r"<think>.*\Z", "", text, flags=re.DOTALL)  # cut off mid-thought
    return text.strip()

_ollama_initialized = False

def check_ollama_ready(max_retries: int = 5, retry_delay: int = 2) -> bool:
    """Check whether Ollama is responsive."""
    for attempt in range(max_retries):
        try:
            print(f"Checking Ollama at {OLLAMA_HOST} (attempt {attempt + 1}/{max_retries})...")
            response = ollama.generate(
                model=OLLAMA_MODEL,
                prompt='Say "ready"',
                options={"num_predict": 5, "temperature": 0.0},
            )
            if response and "response" in response:
                print("Ollama is ready!")
                return True
        except Exception as exc:
            print(f"Ollama not ready yet: {exc}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

    print("Ollama readiness check failed after all retries")
    return False


def initialize_ollama() -> None:
    """Warm up the Ollama model once per process."""
    global _ollama_initialized

    if _ollama_initialized:
        return

    try:
        print("Initializing ollama...")
        print(f"Preloading Ollama model: {OLLAMA_MODEL}")
        print(f"Connecting to Ollama at: {OLLAMA_HOST}")

        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt="Say 'ready' if you are ready.",
            options={"num_predict": 10, "temperature": 0.0},
        )

        if response and "response" in response:
            print("Ollama model preloaded successfully")
        else:
            print("Warning: Ollama responded with an unexpected response structure")
            print(f"Full Response: {response}")

        _ollama_initialized = True
    except ConnectionError as exc:
        print(f"Warning: Could not connect to Ollama: {exc}")
        print("Ollama may not be running. Grading requests will fail.")
    except Exception as exc:
        print(f"Warning: Failed to preload Ollama model: {exc}")
        print("Grading requests may be slow on first use.")


def prompt_ollama(prompt, model = OLLAMA_MODEL, options = OLLAMA_DEFAULT_OPTIONS):
    """Send a single prompt to Ollama and return the generated text."""
    if not _ollama_initialized:
        try:
            initialize_ollama()
        except Exception as exc:
            print(f"Failed to initialize Ollama.")
            raise RuntimeError("Ollama initialization failed.")
        
    try:
        response = ollama.generate(
            model=model,
            prompt=str(prompt),
            options=options,
        )
        if response:
            return strip_reasoning(response["response"])
        else:
            print("No response detected")
            return None
    except Exception as exc:
        print(f"Error encountered when prompting ollama: {exc}")
        return None


def chat_ollama(messages, model=OLLAMA_MODEL, options=OLLAMA_DEFAULT_OPTIONS):
    """Send chat messages to Ollama and return the assistant content."""
    if not _ollama_initialized:
        try:
            initialize_ollama()
        except Exception as exc:
            print("Failed to initialize Ollama.")
            raise RuntimeError("Ollama initialization failed.")

    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options=options,
        )
        if response and "message" in response and "content" in response["message"]:
            return strip_reasoning(response["message"]["content"])
        print("No chat response detected")
        return None
    except Exception as exc:
        print(f"Error encountered when chatting with ollama: {exc}")
        return None
