from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel

import sys

class TopologyDashboard:
    def __init__(self):
        if sys.platform == "win32":
            try:
                sys.stdout.reconfigure(encoding="utf-8")
                sys.stderr.reconfigure(encoding="utf-8")
            except Exception:
                pass
        self.console = Console(force_terminal=True)

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


    def render_drift_alert(self, exposures):
        if not exposures:
            self.console.print(Panel("[bold green]✅ No configuration drift detected. Infrastructure is secure.[/bold green]", title="Status", style="green"))
            return
        
        alert_text = "[bold red]CRITICAL: Unapproved public exposure detected![/bold red]\n\n"
        for exp in exposures:
            alert_text += f"Target: [bold]{exp['target']}[/bold]\n"
            alert_text += f"Path: {' ➡️  '.join(exp['path'])}\n"
            
        self.console.print(Panel(alert_text, title="⚠️ DRIFT DETECTED ⚠️", border_style="red"))
        self.console.print()


    def render_remediation_preview(self, code: str):
        from rich.syntax import Syntax
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title="🤖 Agentic AST Code Generation (Python)", border_style="cyan"))
        self.console.print()


    def render_remediation_result(self, result):
        if result.success:
            content = f"[bold green]✨ Autonomous Remediation Succeeded![/bold green]\n\n"
            content += f"Action: [cyan]{result.action}[/cyan]\n"
            content += f"Execution Latency: [yellow]{result.execution_time_ms:.2f} ms[/yellow]\n"
            content += "\n[bold]Audit Log:[/bold]\n"
            for log_entry in result.audit_log:
                content += f" • {log_entry}\n"
            self.console.print(Panel(content, title="🛡️ Self-Healing Status: SECURE", border_style="green"))
        else:
            self.console.print(Panel(f"[bold red]Remediation Failed:[/bold red] {result.error_message}", title="Error", border_style="red"))
        self.console.print()


    def render_topology_diff(self, diff_result):
        from rich.table import Table
        
        title = f"🔄 Topology Diff: [{diff_result.snapshot_a_id}] {diff_result.label_a} ➡️  [{diff_result.snapshot_b_id}] {diff_result.label_b}"
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Change Type", style="bold", width=14)
        table.add_column("Resource / Edge", width=40)
        table.add_column("Details", justify="left")
        
        for n in diff_result.added_nodes:
            table.add_row("[green]+ NODE ADDED[/green]", str(n.get("id")), f"Type: {n.get('type')}")
        for n in diff_result.removed_nodes:
            table.add_row("[red]- NODE REMOVED[/red]", str(n.get("id")), f"Type: {n.get('type')}")
        for e in diff_result.added_edges:
            table.add_row("[bold yellow]+ EDGE DRIFT[/bold yellow]", f"{e.get('source')} ➡️  {e.get('target')}", f"Rel: {e.get('relation')}, Port: {e.get('port')}")
        for e in diff_result.removed_edges:
            table.add_row("[bold cyan]- EDGE REVERTED[/bold cyan]", f"{e.get('source')} ➡️  {e.get('target')}", f"Rel: {e.get('relation')}, Port: {e.get('port')}")
            
        if diff_result.total_changes == 0:
            table.add_row("[dim]NO CHANGES[/dim]", "Identical topologies", "Zero drift detected")
            
        self.console.print(table)
        self.console.print()

