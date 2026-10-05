from dataclasses import dataclass


@dataclass
class Decision:
    decision: str   # ALLOW / DENY / STEP_UP
    reason: str


def evaluate(user, application, device, mfa_ok, risk_score) -> Decision:
    return Decision("DENY", "policy engine not implemented")   # STUB: Komal replaces on her Day 3