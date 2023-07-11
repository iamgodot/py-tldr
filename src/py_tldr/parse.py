from typing import List


def parse_command(commands: List[str]) -> str:
    return "-".join(commands).lower()
