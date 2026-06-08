import json
import sys
import urllib.request


def is_ollama_authenticated():
    """
    Pings the local Ollama API to verify if it can authenticate
    requests for the specified cloud model.
    """
    url = "http://localhost:11434/api/generate"
    # Sending an empty prompt to the cloud model to evaluate server authentication status
    data = json.dumps(
        {"model": "gemma4:31b-cloud", "prompt": "", "stream": False}
    ).encode("utf-8")

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            # If it responds successfully (even with an empty output), auth is valid
            if response.status == 200:
                return True
    except urllib.error.HTTPError as e:
        # A 401 status explicitly flags an unauthenticated machine state
        if e.code == 401:
            return False
    except Exception:
        # Fallback to safety if the daemon hasn't completed initializing
        return False
    return False


if __name__ == "__main__":
    print("[+] Running strict cloud model authorization handshake...")
    if not is_ollama_authenticated():
        print("[!] AUTH_REQUIRED")
        sys.exit(1)
    else:
        print("[✓] Machine authorized for Ollama Cloud.")
        sys.exit(0)
