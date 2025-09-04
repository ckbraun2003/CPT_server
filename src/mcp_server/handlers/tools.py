from typing import Dict


def send_message(message: str) -> Dict[str, str]:
    return {"response": message}