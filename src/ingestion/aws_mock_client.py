import asyncio
import logging

logger = logging.getLogger(__name__)

class AsyncMockAWSClient:
    def __init__(self):
        pass

    async def fetch_vpcs(self):
        await asyncio.sleep(0.1)
        return [{"VpcId": "vpc-0abc123", "CidrBlock": "10.0.0.0/16", "Name": "Production-VPC"}]

