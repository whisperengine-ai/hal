"""
Simple headless CLI runner for Hal.

Use this when Tkinter isn't available on your system. It uses the same
Cortex → Thalamus → Hippocampus pipeline but runs in the terminal.
"""
import os
import time
import json

import config  # loads .env if present
from cortex import Cortex
from hippocampus import Hippocampus
from thalamus import Thalamus


def main():
    print("Hal (CLI) — type 'exit' to quit")

    # Initialize core components
    cortex = Cortex()
    hippo = Hippocampus(cortex)
    thal = Thalamus(cortex, hippo)

    while True:
        try:
            user_query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye")
            break

        if not user_query:
            continue
        if user_query.lower() in {"exit", "quit", ":q"}:
            print("Bye")
            break

        turn_id = int(time.time())
        try:
            state, reflection, raw_response = thal.process_turn(
                user_query=user_query,
                turn_id=turn_id,
                task_id=f"CLI_{turn_id}",
            )

            # Extract RESPONSE section if present
            response = raw_response
            try:
                import re
                m_resp = re.search(r"RESPONSE\s*:\s*(.+?)(?:\n[A-Z ]{3,}?:|\Z)", raw_response, flags=re.S | re.I)
                if m_resp:
                    response = m_resp.group(1).strip()
            except Exception:
                pass

            print("\n[Reflection]\n" + (reflection or "(none)"))
            print("\n[Response]\n" + (response or "(none)"))
            print()

        except Exception as e:
            print(f"[Error] {e}")


if __name__ == "__main__":
    main()
