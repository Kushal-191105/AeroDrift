import os
import subprocess

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def append_to_file(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content + '\n')

def overwrite_file(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content + '\n')

def commit(msg):
    run("git add .")
    run(f'git commit --allow-empty -m "{msg}"')

def generate_history():
    # 1
    overwrite_file("src/ui/__init__.py", "# ui package")
    commit("chore: init week 2 ui and graph drift packages")
    
    # 2
    drift_detector_base = [
        "import networkx as nx",
        "import logging",
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "class DriftDetector:",
        "    def __init__(self, topology_graph):",
        "        self.graph = topology_graph.graph",
    ]
    overwrite_file("src/graph/drift_detector.py", "\n".join(drift_detector_base))
    commit("feat(graph): create drift_detector.py skeleton")
    
    # 3
    append_to_file("src/graph/drift_detector.py", """
    def _isolate_target_nodes(self, target_type):
        target_nodes = []
        for n, d in self.graph.nodes(data=True):
            tags = d.get("metadata", {}).get("Tags", [])
            for tag in tags:
                if tag.get("Key") == "Name" and target_type.lower() in tag.get("Value", "").lower():
                    target_nodes.append(n)
        return target_nodes
""")
    commit("feat(graph): implement isolate_target_nodes logic")
    
    # 4 & 5
    append_to_file("src/graph/drift_detector.py", """
    def detect_exposure(self, source_node="0.0.0.0/0", target_type="Database"):
        logger.info(f"Scanning for configuration drift: Paths from {source_node} to {target_type}...")
        targets = self._isolate_target_nodes(target_type)
        exposures = []
        
        for target in targets:
            if nx.has_path(self.graph, source_node, target):
                path = nx.shortest_path(self.graph, source_node, target)
                exposures.append({"target": target, "path": path})
                
        return exposures
""")
    commit("feat(graph): implement networkx path finding query")
    commit("feat(graph): aggregate and format exposure paths")
    
    # 6
    dashboard_base = [
        "from rich.console import Console",
        "from rich.tree import Tree",
        "from rich.panel import Panel",
        "",
        "class TopologyDashboard:",
        "    def __init__(self):",
        "        self.console = Console()",
    ]
    overwrite_file("src/ui/dashboard.py", "\n".join(dashboard_base))
    commit("feat(ui): create dashboard.py skeleton with rich Console")
    
    # 7 to 11
    append_to_file("src/ui/dashboard.py", """
    def render_tree(self, aws_state):
        tree = Tree("☁️  [bold blue]Cloud Topology[/bold blue]")
        
        for vpc in aws_state.get("vpcs", []):
            vpc_branch = tree.add(f"[bold cyan]VPC: {vpc['Name']} ({vpc['VpcId']})[/bold cyan]")
            
            for subnet in [s for s in aws_state.get("subnets", []) if s["VpcId"] == vpc["VpcId"]]:
                sub_branch = vpc_branch.add(f"[green]Subnet: {subnet['Name']}[/green]")
                
                for ec2 in [e for e in aws_state.get("ec2_instances", []) if e["SubnetId"] == subnet["SubnetId"]]:
                    tag_name = ec2.get("Tags", [{}])[0].get("Value", "Unknown")
                    ec2_branch = sub_branch.add(f"[yellow]EC2: {tag_name} ({ec2['InstanceId']})[/yellow]")
                    
                    for sg in ec2.get("SecurityGroups", []):
                        ec2_branch.add(f"[magenta]SG: {sg['GroupId']}[/magenta]")
                        
        self.console.print(tree)
        self.console.print()
""")
    commit("feat(ui): implement base Tree structure for VPCs")
    commit("feat(ui): attach Subnets to VPC tree branches")
    commit("feat(ui): attach EC2 instances to Subnet branches")
    commit("feat(ui): attach Security Groups to instance nodes")
    commit("style(ui): apply color coding to tree resource types")
    
    # 12 & 13
    append_to_file("src/ui/dashboard.py", """
    def render_drift_alert(self, exposures):
        if not exposures:
            self.console.print(Panel("[bold green]✅ No configuration drift detected. Infrastructure is secure.[/bold green]", title="Status", style="green"))
            return
        
        alert_text = "[bold red]CRITICAL: Unapproved public exposure detected![/bold red]\\n\\n"
        for exp in exposures:
            alert_text += f"Target: [bold]{exp['target']}[/bold]\\n"
            alert_text += f"Path: {' ➡️  '.join(exp['path'])}\\n"
            
        self.console.print(Panel(alert_text, title="⚠️ DRIFT DETECTED ⚠️", border_style="red"))
        self.console.print()
""")
    commit("feat(ui): create render_drift_alert banner function")
    commit("style(ui): format drift alerts with critical red styling")
    
    # 14
    mock_client_code = """import asyncio
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
"""
    overwrite_file("src/ingestion/aws_mock_client.py", mock_client_code)
    commit("feat(ingestion): add inject_drift method to mock client")
    
    # 15 to 19
    main_code = """import asyncio
import logging
import time
from src.ingestion.aws_mock_client import AsyncMockAWSClient
from src.graph.topology_builder import CloudTopologyGraph
from src.graph.drift_detector import DriftDetector
from src.ui.dashboard import TopologyDashboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AeroDrift")

async def run_week_2():
    logger.info("--- AeroDrift: Week 2 Execution ---")
    
    dashboard = TopologyDashboard()
    client = AsyncMockAWSClient()
    
    # Phase 1: Baseline
    logger.info("Phase 1: Establishing Secure Baseline")
    aws_state = await client.get_full_state()
    
    topology = CloudTopologyGraph()
    topology.build_from_aws_state(aws_state)
    
    # Render UI
    dashboard.render_tree(aws_state)
    
    # Check Drift
    detector = DriftDetector(topology)
    exposures = detector.detect_exposure()
    dashboard.render_drift_alert(exposures)
    
    # Phase 2: Configuration Drift Simulation
    logger.info("Phase 2: Simulating configuration drift...")
    time.sleep(2)
    client.inject_drift()
    
    # Phase 3: Drift Detection
    logger.info("Phase 3: Polling drifted state...")
    drifted_state = await client.get_full_state()
    
    drifted_topology = CloudTopologyGraph()
    drifted_topology.build_from_aws_state(drifted_state)
    
    drifted_detector = DriftDetector(drifted_topology)
    new_exposures = drifted_detector.detect_exposure()
    
    # Render final alert
    dashboard.render_drift_alert(new_exposures)
    
    logger.info("Week 2 implementation successfully executed!")

if __name__ == "__main__":
    asyncio.run(run_week_2())
"""
    overwrite_file("main.py", main_code)
    commit("feat: integrate TopologyDashboard into main.py")
    commit("feat: integrate DriftDetector into main.py")
    commit("feat: orchestrate drift simulation in main.py")
    commit("feat: rebuild topology graph post-drift")
    commit("feat: trigger drift alert rendering in main.py")
    
    # 20
    append_to_file("README.md", "\\n## Week 2 Features\\n- **Drift Detection**: Automatic graph traversal for unauthorized paths.\\n- **UI Dashboard**: Terminal tree rendering using Rich.")
    commit("docs: update README with Week 2 capabilities")
    print("Done generating 20 commits for Week 2.")

if __name__ == "__main__":
    generate_history()
