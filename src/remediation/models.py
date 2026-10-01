"""Data models for remediation payloads and actions."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class DriftPayload:
    group_id: str
    protocol: str = "tcp"
    from_port: int = 5432
    to_port: int = 5432
    cidr_ip: str = "0.0.0.0/0"
    target_resource: str = "Database-Server-1"

@dataclass
class RemediationResult:
    success: bool
    action: str
    generated_code: str
    execution_time_ms: float
    error_message: Optional[str] = None
    audit_log: List[str] = field(default_factory=list)

