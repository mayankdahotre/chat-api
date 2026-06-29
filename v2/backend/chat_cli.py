"""Interactive terminal client for the Analytics Copilot."""

import json
import sys

import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000/api/v1"


def check_server() -> bool:
    try:
        r = httpx.get(f"{BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except httpx.ConnectError:
        return False


def stream_message(message: str) -> list[str]:
    nodes: list[str] = []

    with httpx.Client(timeout=60) as client:
        with client.stream(
            "POST", f"{BASE_URL}/chat/stream", json={"message": message}
        ) as response:
            for line in response.iter_lines():
                if not line.startswith("data: "):
                    continue
                event = json.loads(line[6:])
                if event["type"] == "token":
                    print(event["content"], end="", flush=True)
                elif event["type"] == "error":
                    print(f"\n[Error] {event['content']}")
                elif event["type"] == "metadata":
                    nodes = event.get("nodes", [])

    print()
    return nodes


def show_history() -> None:
    r = httpx.get(f"{BASE_URL}/chat/sessions")
    data = r.json()
    if not data.get("exists"):
        print("No messages yet.")
        return
    print("\n--- Conversation History ---")
    for msg in data.get("messages", []):
        role = msg["role"].upper()
        preview = msg["content"][:120].replace("\n", " ")
        print(f"  [{role}] {preview}...")
    print("---\n")


def reset_conversation() -> None:
    httpx.post(f"{BASE_URL}/chat/reset")


def main() -> None:
    print("=" * 55)
    print("  Analytics Copilot — Terminal Chat")
    print("=" * 55)

    if not check_server():
        print("\nServer not running. Start it first:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload --port 8000")
        sys.exit(1)

    print("\nConnected. Type your questions below (multi-turn chat).\n")
    print("Commands:  /help  /history  /new  /quit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print("Goodbye!")
            break

        if user_input.lower() == "/new":
            reset_conversation()
            print("[Conversation cleared — ready for a new chat]\n")
            continue

        if user_input.lower() == "/help":
            print("  /history  — show saved messages")
            print("  /new      — start a fresh conversation")
            print("  /quit     — exit\n")
            continue

        if user_input.lower() == "/history":
            show_history()
            continue

        print("Copilot: ", end="", flush=True)
        nodes = stream_message(user_input)
        if nodes:
            print(f"  [route: {' -> '.join(nodes)}]\n")


if __name__ == "__main__":
    main()
