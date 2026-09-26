from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel

class TopologyDashboard:
    def __init__(self):
        self.console = Console()

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

