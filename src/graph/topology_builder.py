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

