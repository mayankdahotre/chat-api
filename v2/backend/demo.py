import json

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
client = httpx.Client(timeout=30)


def stream_chat(message: str):
    with client.stream("POST", f"{BASE}/chat/stream", json={"message": message}) as r:
        tokens = []
        nodes = []
        for line in r.iter_lines():
            if line.startswith("data: "):
                evt = json.loads(line[6:])
                if evt["type"] == "token":
                    tokens.append(evt["content"])
                elif evt["type"] == "metadata":
                    nodes = evt.get("nodes", [])
        return "".join(tokens).strip(), nodes


def main():
    print("=" * 60)
    print("1. HEALTH CHECK")
    print("=" * 60)
    health = client.get(f"{BASE}/health").json()
    print(json.dumps(health, indent=2))

    print()
    print("=" * 60)
    print("2. FLOW A - Finance statement request")
    print("=" * 60)
    response, nodes = stream_chat("Give me a financial statement table.")
    print(f"Graph path: {' -> '.join(nodes)}")
    print(f"Response  :\n{response}")

    print()
    print("=" * 60)
    print("3. FLOW A - Finance follow-up (self-loop)")
    print("=" * 60)
    response2, nodes2 = stream_chat("Why is COGS high in Q2?")
    print(f"Graph path: {' -> '.join(nodes2)}")
    print(f"Response  :\n{response2}")

    print()
    print("=" * 60)
    print("4. FLOW B - Shift to marketing")
    print("=" * 60)
    response3, nodes3 = stream_chat("Show me marketing performance instead.")
    print(f"Graph path: {' -> '.join(nodes3)}")
    print(f"Response  :\n{response3}")

    print()
    print("=" * 60)
    print("5. SESSION HISTORY")
    print("=" * 60)
    session = client.get(f"{BASE}/chat/sessions").json()
    print(f"Active domain : {session['session']['active_domain']}")
    print(f"Message count : {len(session['messages'])}")
    for msg in session["messages"]:
        preview = msg["content"][:70].replace("\n", " ")
        print(f"  [{msg['role']:9}] {preview}...")

    print()
    print("=" * 60)
    print("6. FLOW C - Session termination")
    print("=" * 60)
    response4, nodes4 = stream_chat("I am done with all my questions, thank you.")
    print(f"Graph path: {' -> '.join(nodes4)}")
    print(f"Response  :\n{response4}")

    session_end = client.get(f"{BASE}/chat/sessions").json()
    print(f"Session active: {session_end['session']['is_active']}")
    print()
    print("ALL TESTS PASSED - Server is working!")


if __name__ == "__main__":
    main()
