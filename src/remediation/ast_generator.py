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


    def _build_call_node(self, payload: DriftPayload) -> ast.Call:
        """Constructs ast.Call node for client.revoke_security_group_ingress(...)."""
        perm_dict = self._build_ip_permission_dict_node(payload)
        
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="client", ctx=ast.Load()),
                attr="revoke_security_group_ingress",
                ctx=ast.Load()
            ),
            args=[],
            keywords=[
                ast.keyword(
                    arg="GroupId",
                    value=ast.Constant(value=payload.group_id)
                ),
                ast.keyword(
                    arg="IpPermissions",
                    value=ast.List(elts=[perm_dict], ctx=ast.Load())
                )
            ]
        )

