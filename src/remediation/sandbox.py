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


    def validate_ast(self, code_str: str) -> None:
        """Performs static analysis on synthesized AST tree to prevent dangerous calls."""
        tree = ast.parse(code_str)
        forbidden_modules = {"os", "sys", "subprocess", "socket", "shutil", "__import__"}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden_modules:
                        raise SecurityViolationError(f"Unauthorized import detected: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in forbidden_modules:
                    raise SecurityViolationError(f"Unauthorized from-import detected: {node.module}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec", "__import__", "open"):
                    raise SecurityViolationError(f"Dangerous built-in function invocation: {node.func.id}")
        logger.info("AST Static Security Verification Passed.")


    def execute(self, code_str: str, client: Any) -> RemediationResult:
        """Executes the validated AST script with restricted globals and locals."""
        start_time = time.perf_counter()
        audit_log = []
        
        try:
            self.validate_ast(code_str)
            audit_log.append("Static AST validation passed.")
            
            # Isolated execution scope
            restricted_globals = {
                "__builtins__": {k: __builtins__[k] for k in self.allowed_builtins if k in __builtins__}
            }
            local_scope = {}
            
            # Compile and exec function definition
            compiled_code = compile(code_str, filename="<ast_remediation>", mode="exec")
            exec(compiled_code, restricted_globals, local_scope)
            audit_log.append("Remediation function compiled and registered into isolated scope.")
            
            # Execute remediation function
            remediate_fn = local_scope.get("remediate_unauthorized_ingress")
            if not callable(remediate_fn):
                raise ValueError("Remediation function not found in compiled scope.")
                
            response = remediate_fn(client)
            audit_log.append(f"Function executed successfully. AWS API Response: {response}")
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RemediationResult(
                success=True,
                action="revoke_security_group_ingress",
                generated_code=code_str,
                execution_time_ms=elapsed_ms,
                audit_log=audit_log
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Sandbox execution failed: {str(e)}")
            audit_log.append(f"Execution Error: {str(e)}")
            return RemediationResult(
                success=False,
                action="revoke_security_group_ingress",
                generated_code=code_str,
                execution_time_ms=elapsed_ms,
                error_message=str(e),
                audit_log=audit_log
            )


    def get_sandbox_capabilities(self) -> Dict[str, Any]:
        return {
            "sandbox_type": "Restricted-AST-Exec",
            "isolation_level": "Restricted Builtins & Lexical Scope",
            "allowed_builtins": list(self.allowed_builtins)
        }

