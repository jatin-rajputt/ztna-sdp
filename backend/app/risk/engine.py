from dataclasses import dataclass


@dataclass
class RiskResult:
    score: int      # 0-100
    level: str      # LOW / MEDIUM / HIGH / CRITICAL
    factors: dict


def assess(user, device, mfa_ok) -> RiskResult:
    return RiskResult(100, "CRITICAL", {"stub": 100})   # STUB: Komal replaces on her Day 4