import unittest
from src.remediation.models import DriftPayload
from src.remediation.ast_generator import ASTCodeGenerator
from src.remediation.sandbox import ExecutionSandbox, SecurityViolationError
from src.ingestion.aws_mock_client import AsyncMockAWSClient

class TestAgenticRemediation(unittest.TestCase):
    def setUp(self):
        self.generator = ASTCodeGenerator()
        self.sandbox = ExecutionSandbox()
        self.client = AsyncMockAWSClient()

    def test_ast_code_generation(self):
        payload = DriftPayload(group_id="sg-0002")
        code = self.generator.generate_code(payload)
        self.assertIn("def remediate_unauthorized_ingress", code)
        self.assertIn("revoke_security_group_ingress", code)
        self.assertIn("sg-0002", code)

    def test_sandbox_execution(self):
        self.client.inject_drift()
        payload = DriftPayload(group_id="sg-0002")
        code = self.generator.generate_code(payload)
        res = self.sandbox.execute(code, self.client)
        self.assertTrue(res.success)
        self.assertEqual(res.action, "revoke_security_group_ingress")

    def test_security_violation(self):
        malicious_code = "import os\nos.system('echo hacked')"
        with self.assertRaises(SecurityViolationError):
            self.sandbox.validate_ast(malicious_code)

if __name__ == "__main__":
    unittest.main()

