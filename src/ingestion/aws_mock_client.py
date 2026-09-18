import asyncio
import logging

logger = logging.getLogger(__name__)

class AsyncMockAWSClient:
    def __init__(self):
        pass

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
        return [
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

