import ast
import time
import logging
from typing import Dict, Any
from src.remediation.models import RemediationResult

logger = logging.getLogger(__name__)

class SecurityViolationError(Exception):
    """Raised when dynamically generated code attempts unsafe operations."""
    pass

class ExecutionSandbox:
    """Executes synthesized AST code within a strictly controlled, isolated scope."""
    def __init__(self):
        self.allowed_builtins = {"range", "len", "print", "dict", "list", "True", "False", "None"}

