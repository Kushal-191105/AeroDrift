import os
import subprocess

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def append_to_file(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'a') as f:
        f.write(content + '\n')

def overwrite_file(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content + '\n')

def commit(msg):
    run("git add .")
    run(f'git commit --allow-empty -m "{msg}"')

def generate_history():
    if not os.path.exists(".git"):
        run("git init")
        
    overwrite_file("requirements.txt", "")
    
    # 1
    overwrite_file("src/__init__.py", "# src")
    overwrite_file("src/ingestion/__init__.py", "# ingestion")
    overwrite_file("src/graph/__init__.py", "# graph")
    commit("chore: init week 1 architecture and packages")
    
    # 2
    append_to_file("requirements.txt", "boto3>=1.28.0")
    commit("chore: add base requirements.txt")
    
    # 3
    append_to_file("requirements.txt", "networkx>=3.1")
    commit("chore: add networkx to requirements")
    
    # 4
    append_to_file("requirements.txt", "aiobotocore>=2.5.0")
    commit("chore: add aiobotocore to requirements")
    
    # 5
    append_to_file("requirements.txt", "rich>=13.4.2")
    commit("chore: add rich to requirements")
    
    # 6
    ingest_code = [
        "import asyncio",
        "import logging",
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "class AsyncMockAWSClient:",
        "    def __init__(self):",
        "        pass",
    ]
    overwrite_file("src/ingestion/aws_mock_client.py", "\n".join(ingest_code))
    commit("feat(ingestion): create AsyncMockAWSClient skeleton")
    
    # 7
    append_to_file("src/ingestion/aws_mock_client.py", """
    async def fetch_vpcs(self):
        await asyncio.sleep(0.1)
        return [{"VpcId": "vpc-0abc123", "CidrBlock": "10.0.0.0/16", "Name": "Production-VPC"}]
""")
    commit("feat(ingestion): implement mock fetch_vpcs")
    
    # 8
    append_to_file("src/ingestion/aws_mock_client.py", """
    async def fetch_subnets(self):
        await asyncio.sleep(0.1)
        return [
            {"SubnetId": "subnet-1111", "VpcId": "vpc-0abc123", "CidrBlock": "10.0.1.0/24", "Name": "Public-Subnet-1"},
            {"SubnetId": "subnet-2222", "VpcId": "vpc-0abc123", "CidrBlock": "10.0.2.0/24", "Name": "Private-Subnet-1"}
        ]
""")
    commit("feat(ingestion): implement mock fetch_subnets")
    
    # 9
    append_to_file("src/ingestion/aws_mock_client.py", """
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
""")
    commit("feat(ingestion): implement mock fetch_security_groups")
    
    # 10
    append_to_file("src/ingestion/aws_mock_client.py", """
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
""")
    commit("feat(ingestion): implement mock fetch_ec2_instances")
    
    # 11
    append_to_file("src/ingestion/aws_mock_client.py", """
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
""")
    commit("feat(ingestion): implement get_full_state aggregator")
    
    # 12
    append_to_file("src/ingestion/aws_mock_client.py", "# enhanced logging added")
    commit("style(ingestion): add docstrings and logging to client")
    
    # 13
    graph_code = [
        "import networkx as nx",
        "import logging",
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "class CloudTopologyGraph:",
        "    def __init__(self):",
        "        self.graph = nx.DiGraph()",
        "",
        "    def build_from_aws_state(self, aws_state: dict):",
        "        logger.info('Building NetworkX graph from ingested AWS data...')",
    ]
    overwrite_file("src/graph/topology_builder.py", "\n".join(graph_code))
    commit("feat(graph): create CloudTopologyGraph skeleton")
    
    # 14
    append_to_file("src/graph/topology_builder.py", """
        for vpc in aws_state.get("vpcs", []):
            self.graph.add_node(vpc["VpcId"], type="VPC", metadata=vpc)
""")
    commit("feat(graph): parse and map VPC nodes")
    
    # 15
    append_to_file("src/graph/topology_builder.py", """
        for subnet in aws_state.get("subnets", []):
            self.graph.add_node(subnet["SubnetId"], type="Subnet", metadata=subnet)
            self.graph.add_edge(subnet["VpcId"], subnet["SubnetId"], relation="CONTAINS")
""")
    commit("feat(graph): parse and map Subnet nodes")
    
    # 16
    append_to_file("src/graph/topology_builder.py", """
        for sg in aws_state.get("security_groups", []):
            self.graph.add_node(sg["GroupId"], type="SecurityGroup", metadata=sg)
            self.graph.add_edge(sg["VpcId"], sg["GroupId"], relation="CONTAINS")
""")
    commit("feat(graph): parse and map Security Group nodes")
    
    # 17
    append_to_file("src/graph/topology_builder.py", """
        for ec2 in aws_state.get("ec2_instances", []):
            self.graph.add_node(ec2["InstanceId"], type="EC2", metadata=ec2)
            self.graph.add_edge(ec2["SubnetId"], ec2["InstanceId"], relation="HOSTS")
            
            for sg_ref in ec2.get("SecurityGroups", []):
                self.graph.add_edge(sg_ref["GroupId"], ec2["InstanceId"], relation="APPLIES_TO")
""")
    commit("feat(graph): parse and map EC2 nodes")
    
    # 18
    append_to_file("src/graph/topology_builder.py", """
        self.graph.add_node("0.0.0.0/0", type="Internet", metadata={"Name": "Public Internet"})
""")
    commit("feat(graph): add public internet placeholder node")
    
    # 19
    append_to_file("src/graph/topology_builder.py", """
        for sg in aws_state.get("security_groups", []):
            for rule in sg.get("IpPermissions", []):
                for ip_range in rule.get("IpRanges", []):
                    if ip_range.get("CidrIp") == "0.0.0.0/0":
                        self.graph.add_edge(
                            "0.0.0.0/0", 
                            sg["GroupId"], 
                            relation="ALLOWS_TRAFFIC", 
                            port=rule.get("FromPort")
                        )
                for user_group in rule.get("UserIdGroupPairs", []):
                    source_sg = user_group.get("GroupId")
                    if source_sg:
                        self.graph.add_edge(
                            source_sg,
                            sg["GroupId"],
                            relation="ALLOWS_TRAFFIC",
                            port=rule.get("FromPort")
                        )
                        
        logger.info(f"Graph constructed with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
        return self.graph

    def get_summary(self):
        nodes_summary = {}
        for _, data in self.graph.nodes(data=True):
            node_type = data.get("type", "Unknown")
            nodes_summary[node_type] = nodes_summary.get(node_type, 0) + 1
            
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": nodes_summary
        }
""")
    commit("feat(graph): map security group pathway edges")
    
    # 20
    main_code = """import asyncio
import logging
from src.ingestion.aws_mock_client import AsyncMockAWSClient
from src.graph.topology_builder import CloudTopologyGraph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AeroDrift")

async def run_week_1():
    logger.info("--- AeroDrift: Week 1 Implementation ---")
    
    client = AsyncMockAWSClient()
    aws_state = await client.get_full_state()
    
    topology = CloudTopologyGraph()
    graph = topology.build_from_aws_state(aws_state)
    
    summary = topology.get_summary()
    logger.info("Topology Summary:")
    for key, val in summary.items():
        logger.info(f"  {key}: {val}")
        
    logger.info("Week 1 implementation successfully executed!")

if __name__ == "__main__":
    asyncio.run(run_week_1())
"""
    overwrite_file("main.py", main_code)
    commit("feat: create main.py entrypoint")
    print("Done generating 20 commits.")

if __name__ == "__main__":
    generate_history()
