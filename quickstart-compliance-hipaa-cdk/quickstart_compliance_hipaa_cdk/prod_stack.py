from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_logs as logs

class ProdStack(core.NestedStack):

    def __init__(self, scope: core.Construct, id: str, main_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        region = 'us-east-1'

        # VPC Flow Logs Log Group
        self.prod_vpc_flow_log_group = logs.CfnLogGroup(self, 'Production VPC Flow Log Group',
            log_group_name=main_stack.prod_log_group.value_as_string,
            retention_in_days=main_stack.prod_log_group_ret.value_as_number
        )

        # Flow Logs IAM Roles and Policies
        flow_logs_assume_role = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowFlowLogs",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "vpc-flow-logs.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        flow_logs_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:DescribeLogGroups",
                        "logs:DescribeLogStreams"
                    ],
                    "Resource": "*"
                }
            ]
        }

        self.prod_flow_logs_role = iam.CfnRole(self,
            id='Production Flow Logs Role',
            description='Production Flow Logs Role',
            path='/',
            assume_role_policy_document=flow_logs_assume_role,
            policies=[
                {
                    "policyName": "Production-Flow-Logs-Role",
                    "policyDocument": flow_logs_policy
                }
            ],
            tags=[{"key":"Name", "value":"Production VPC Flow Logs Role"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Creates Initial Empty VPC
        self.vpc = ec2.CfnVPC(self, "Production VPC",
            cidr_block=main_stack.prod_cidr.value_as_string,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags=[{"key":"Name", "value":"Production VPC"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.vpc.add_depends_on(self.prod_vpc_flow_log_group)

        # VPC Flow Logs
        self.prod_vpc_flow_logs = ec2.CfnFlowLog(self, 'Production VPC Flow Logs',
            resource_id=self.vpc.ref,
            resource_type="VPC",
            traffic_type="ALL",
            deliver_logs_permission_arn=self.prod_flow_logs_role.attr_arn,
            log_group_name=self.prod_vpc_flow_log_group.log_group_name,
            log_destination_type='cloud-watch-logs',
            tags=[{"key":"Name", "value":"Production VPC Flow Logs"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.prod_vpc_flow_logs.add_depends_on(self.prod_vpc_flow_log_group)

        # Creates Subnets
        self.prod_core_1 = ec2.CfnSubnet(self,
            id="Production Core Subnet 1",
            cidr_block=main_stack.prod_subnet_1.value_as_string,
            vpc_id=self.vpc.ref,
            availability_zone=region + "a",
            map_public_ip_on_launch=False,
            tags=[{"key":"Name", "value":"Production Core Subnet 1"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.prod_core_2 = ec2.CfnSubnet(self,
            id="Production Core Subnet 2",
            cidr_block=main_stack.prod_subnet_2.value_as_string,
            vpc_id=self.vpc.ref,
            availability_zone=region + "b",
            map_public_ip_on_launch=False,
            tags=[{"key":"Name", "value":"Production Core Subnet 2"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Create Route Tables
        self.pri_rt_1 = ec2.CfnRouteTable(self,
            id="Production Private Route Table 1",
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Production VPC Private Route Table 1"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Associate Subnets to Route Tables
        self.prod_core_1_ass = ec2.CfnSubnetRouteTableAssociation(self,
            id="Production Core 1 Route Association",
            route_table_id=self.pri_rt_1.ref,
            subnet_id=self.prod_core_1.ref
        )
        self.prod_core_2_ass = ec2.CfnSubnetRouteTableAssociation(self,
            id="Production Core 2 Route Association",
            route_table_id=self.pri_rt_1.ref,
            subnet_id=self.prod_core_2.ref
        )
