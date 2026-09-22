import networkx as nx
import logging

logger = logging.getLogger(__name__)

class CloudTopologyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_from_aws_state(self, aws_state: dict):
        logger.info('Building NetworkX graph from ingested AWS data...')

        for vpc in aws_state.get("vpcs", []):
            self.graph.add_node(vpc["VpcId"], type="VPC", metadata=vpc)


        for subnet in aws_state.get("subnets", []):
            self.graph.add_node(subnet["SubnetId"], type="Subnet", metadata=subnet)
            self.graph.add_edge(subnet["VpcId"], subnet["SubnetId"], relation="CONTAINS")


        for sg in aws_state.get("security_groups", []):
            self.graph.add_node(sg["GroupId"], type="SecurityGroup", metadata=sg)
            self.graph.add_edge(sg["VpcId"], sg["GroupId"], relation="CONTAINS")


        for ec2 in aws_state.get("ec2_instances", []):
            self.graph.add_node(ec2["InstanceId"], type="EC2", metadata=ec2)
            self.graph.add_edge(ec2["SubnetId"], ec2["InstanceId"], relation="HOSTS")
            
            for sg_ref in ec2.get("SecurityGroups", []):
                self.graph.add_edge(sg_ref["GroupId"], ec2["InstanceId"], relation="APPLIES_TO")


        self.graph.add_node("0.0.0.0/0", type="Internet", metadata={"Name": "Public Internet"})


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

