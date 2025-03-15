from dataclasses import dataclass, field


@dataclass(frozen=True)
class AttackOptions:
    half_range: bool
    cover: bool
    anti_active: bool
