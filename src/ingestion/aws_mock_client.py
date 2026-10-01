import asyncio
import logging

logger = logging.getLogger(__name__)

class AsyncMockAWSClient:
    def __init__(self):
        self.sgs = [
            {
                "GroupId": "sg-0001",
                "VpcId": "vpc-0abc123",
                "GroupName": "web-sg",
                "IpPermissions": [
                    {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
                ]
            },
            {
                "GroupId": "sg-0002",
                "VpcId": "vpc-0abc123",
                "GroupName": "db-sg",
                "IpPermissions": [
                    {"IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432, "UserIdGroupPairs": [{"GroupId": "sg-0001"}]}
                ]
            }
        ]

    async def fetch_vpcs(self):
        await asyncio.sleep(0.1)
        return [{"VpcId": "vpc-0abc123", "CidrBlock": "10.0.0.0/16", "Name": "Production-VPC"}]

    async def fetch_subnets(self):
        await asyncio.sleep(0.1)
        return [
            {"SubnetId": "subnet-1111", "VpcId": "vpc-0abc123", "CidrBlock": "10.0.1.0/24", "Name": "Public-Subnet-1"},
            {"SubnetId": "subnet-2222", "VpcId": "vpc-0abc123", "CidrBlock": "10.0.2.0/24", "Name": "Private-Subnet-1"}
        ]

    async def fetch_security_groups(self):
        await asyncio.sleep(0.1)
        return self.sgs

    async def fetch_ec2_instances(self):
        await asyncio.sleep(0.1)
        return [
            {
                "InstanceId": "i-0123456789abcdef0",
                "SubnetId": "subnet-1111",
                "VpcId": "vpc-0abc123",
                "SecurityGroups": [{"GroupId": "sg-0001"}],
                "State": {"Name": "running"},
                "Tags": [{"Key": "Name", "Value": "Web-Server-1"}]
            },
            {
                "InstanceId": "i-0987654321fedcba0",
                "SubnetId": "subnet-2222",
                "VpcId": "vpc-0abc123",
                "SecurityGroups": [{"GroupId": "sg-0002"}],
                "State": {"Name": "running"},
                "Tags": [{"Key": "Name", "Value": "Database-Server-1"}]
            }
        ]

    async def get_full_state(self):
        logger.info("Starting asynchronous AWS state ingestion...")
        vpcs, subnets, sgs, ec2s = await asyncio.gather(
            self.fetch_vpcs(),
            self.fetch_subnets(),
            self.fetch_security_groups(),
            self.fetch_ec2_instances()
        )
        logger.info("Successfully ingested AWS state.")
        return {
            "vpcs": vpcs,
            "subnets": subnets,
            "security_groups": sgs,
            "ec2_instances": ec2s
        }

    def inject_drift(self):
        logger.warning("INJECTING DRIFT: Opening Database Security Group to 0.0.0.0/0...")
        for sg in self.sgs:
            if sg["GroupId"] == "sg-0002":
                sg["IpPermissions"].append(
                    {"IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
                )


    def revoke_security_group_ingress(self, GroupId: str, IpPermissions: list):
        """Mock implementation of boto3.revoke_security_group_ingress."""
        logger.info(f"REVOKING INGRESS: Revoking permissions on {GroupId}...")
        for sg in self.sgs:
            if sg["GroupId"] == GroupId:
                for rule_to_remove in IpPermissions:
                    protocol = rule_to_remove.get("IpProtocol")
                    from_port = rule_to_remove.get("FromPort")
                    to_port = rule_to_remove.get("ToPort")
                    ranges = [r.get("CidrIp") for r in rule_to_remove.get("IpRanges", [])]
                    
                    # Filter out matching permission
                    updated_perms = []
                    for existing_rule in sg.get("IpPermissions", []):
                        if (existing_rule.get("IpProtocol") == protocol and
                            existing_rule.get("FromPort") == from_port and
                            existing_rule.get("ToPort") == to_port):
                            
                            remaining_ranges = [
                                r for r in existing_rule.get("IpRanges", [])
                                if r.get("CidrIp") not in ranges
                            ]
                            if remaining_ranges or existing_rule.get("UserIdGroupPairs"):
                                existing_rule["IpRanges"] = remaining_ranges
                                updated_perms.append(existing_rule)
                        else:
                            updated_perms.append(existing_rule)
                    sg["IpPermissions"] = updated_perms
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

