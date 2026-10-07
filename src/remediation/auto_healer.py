import logging
from typing import List, Dict, Any, Optional
from src.remediation.models import DriftPayload, RemediationResult
from src.remediation.ast_generator import ASTCodeGenerator
from src.remediation.sandbox import ExecutionSandbox

logger = logging.getLogger(__name__)

class AutoHealer:
    """Coordinates drift analysis, AST code generation, and sandboxed rollback execution."""
    def __init__(self, aws_client: Any):
        self.client = aws_client
        self.generator = ASTCodeGenerator()
        self.sandbox = ExecutionSandbox()

    def resolve_drift(self, exposures: List[Dict[str, Any]]) -> List[RemediationResult]:
        results = []
        for exp in exposures:
            path = exp.get("path", [])
            target = exp.get("target")
            
            # Locate compromised security group
            compromised_sg = exp.get("sg")
            if not compromised_sg:
                for node in path:
                    if str(node).startswith("sg-"):
                        compromised_sg = node
            
            port = exp.get("port", 5432)
            payload = DriftPayload(
                group_id=compromised_sg,
                protocol="tcp",
                from_port=port,
                to_port=port,
                cidr_ip="0.0.0.0/0",
                target_resource=target
            )
            
            # Generate AST Code
            generated_code = self.generator.generate_code(payload)
            
            # Execute in sandbox
            res = self.sandbox.execute(generated_code, self.client)
            results.append(res)
            
        return results

