import ast
import logging
from typing import Dict, Any
from src.remediation.models import DriftPayload

logger = logging.getLogger(__name__)

class ASTCodeGenerator:
    """Generates Python remediation code dynamically using Python's ast module."""
    def __init__(self):
        pass


    def _build_ip_permission_dict_node(self, payload: DriftPayload) -> ast.Dict:
        """Constructs an AST Dict node representing AWS IpPermissions structure."""
        keys = [
            ast.Constant(value="IpProtocol"),
            ast.Constant(value="FromPort"),
            ast.Constant(value="ToPort"),
            ast.Constant(value="IpRanges"),
        ]
        values = [
            ast.Constant(value=payload.protocol),
            ast.Constant(value=payload.from_port),
            ast.Constant(value=payload.to_port),
            ast.List(
                elts=[
                    ast.Dict(
                        keys=[ast.Constant(value="CidrIp")],
                        values=[ast.Constant(value=payload.cidr_ip)]
                    )
                ],
                ctx=ast.Load()
            )
        ]
        return ast.Dict(keys=keys, values=values)

