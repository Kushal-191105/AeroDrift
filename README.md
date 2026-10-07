# AeroDrift
AeroDrift is a Python-based CloudOps system that detects cloud security drift and automatically remediates configuration issues in AWS.
\n## Week 2 Features\n- **Drift Detection**: Automatic graph traversal for unauthorized paths.\n- **UI Dashboard**: Terminal tree rendering using Rich.

## Week 3 Features: Agentic Remediation (AST & Sandbox)
- **Metaprogramming Code Generator**: Uses Python's `ast` module to dynamically build `boto3.revoke_security_group_ingress` rollback functions on the fly.
- **Controlled Execution Sandbox**: Safely executes dynamic code using `exec()` with restricted lexical scopes and AST security inspection.
- **Autonomous Self-Healing**: Real-time closed-loop remediation that restores security baselines without human intervention.

