from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_logs as logs

class MgmtStack(core.NestedStack):

    def __init__(self, scope: core.Construct, id: str, main_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        # self.add_dependency(prod_stack)

        region = 'us-east-1'

        # VPC Flow Logs Log Group
        self.mgmt_vpc_flow_log_group = logs.CfnLogGroup(self, 'Management VPC Flow Log Group',
            log_group_name=main_stack.mgmt_log_group.value_as_string,
            retention_in_days=main_stack.mgmt_log_group_ret.value_as_number
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

        self.mgmt_flow_logs_role = iam.CfnRole(self, 
            id='Management Flow Logs Role',
            description='Management Flow Logs Role',
            path='/',
            assume_role_policy_document=flow_logs_assume_role,
            policies=[
                {
                    "policyName": "Management-Flow-Logs-Role",
                    "policyDocument": flow_logs_policy
                }
            ]
        )

        # Creates Initial Empty VPC
        self.vpc = ec2.CfnVPC(self, "Management VPC",
            cidr_block=main_stack.mgmt_cidr.value_as_string,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags=[{"key":"Name", "value":"Management VPC"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.vpc.add_depends_on(self.mgmt_vpc_flow_log_group)

        # VPC Flow Logs
        self.mgmt_vpc_flow_logs = ec2.CfnFlowLog(self, 'Management VPC Flow Logs',
            resource_id=self.vpc.ref,
            resource_type="VPC",
            traffic_type="ALL",
            deliver_logs_permission_arn=self.mgmt_flow_logs_role.attr_arn,
            log_group_name=self.mgmt_vpc_flow_log_group.log_group_name,
            log_destination_type='cloud-watch-logs',
            tags=[{"key":"Name", "value":"Management VPC Flow Logs"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.mgmt_vpc_flow_logs.add_depends_on(self.mgmt_vpc_flow_log_group)

        # Creates Subnets
        self.mgmt_dmz_1 = ec2.CfnSubnet(self, 
            id="Management DMZ Subnet 1",
            cidr_block=main_stack.mgmt_pub_subnet_1.value_as_string,
            vpc_id=self.vpc.ref,
            availability_zone=region + "a",
            map_public_ip_on_launch=True,
            tags=[{"key":"Name", "value":"Management DMZ Subnet 1"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.mgmt_dmz_2 = ec2.CfnSubnet(self, 
            id="Management DMZ Subnet 2",
            cidr_block=main_stack.mgmt_pub_subnet_2.value_as_string,
            vpc_id=self.vpc.ref,
            availability_zone=region + "b",
            map_public_ip_on_launch=True,
            tags=[{"key":"Name", "value":"Management DMZ Subnet 2"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.mgmt_core_1 = ec2.CfnSubnet(self, 
            id="Management Core Subnet 1",
            cidr_block=main_stack.mgmt_pri_subnet_1.value_as_string,
            vpc_id=self.vpc.ref,
            availability_zone=region + "a",
            map_public_ip_on_launch=False,
            tags=[{"key":"Name", "value":"Management Core Subnet 1"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.mgmt_core_2 = ec2.CfnSubnet(self, 
            id="Management Core Subnet 2",
            cidr_block=main_stack.mgmt_pri_subnet_2.value_as_string,
            vpc_id=self.vpc.ref,
            availability_zone=region + "b",
            map_public_ip_on_launch=False,
            tags=[{"key":"Name", "value":"Management Core Subnet 2"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Create Route Tables
        self.pub_rt_1 = ec2.CfnRouteTable(self,
            id="Management Public Route Table 1",
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Management VPC Public Route Table 1"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.pri_rt_1 = ec2.CfnRouteTable(self,
            id="Management Private Route Table 1",
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Management VPC Private Route Table 1"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.pub_rt_2 = ec2.CfnRouteTable(self,
            id="Management Public Route Table 2",
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Management VPC Public Route Table 2"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.pri_rt_2 = ec2.CfnRouteTable(self,
            id="Management Private Route Table 2",
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Management VPC Private Route Table 2"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Associate Subnets to Route Tables
        self.mgmt_dmz_1_ass = ec2.CfnSubnetRouteTableAssociation(self,
            id="Management DMZ 1 Route Association",
            route_table_id=self.pub_rt_1.ref,
            subnet_id=self.mgmt_dmz_1.ref
        )
        self.mgmt_dmz_2_ass = ec2.CfnSubnetRouteTableAssociation(self,
            id="Management DMZ 2 Route Association",
            route_table_id=self.pub_rt_2.ref,
            subnet_id=self.mgmt_dmz_2.ref
        )

        self.mgmt_core_1_ass = ec2.CfnSubnetRouteTableAssociation(self,
            id="Management Core 1 Route Association",
            route_table_id=self.pri_rt_1.ref,
            subnet_id=self.mgmt_core_1.ref
        )
        self.mgmt_core_2_ass = ec2.CfnSubnetRouteTableAssociation(self,
            id="Management Core 2 Route Association",
            route_table_id=self.pri_rt_2.ref,
            subnet_id=self.mgmt_core_2.ref
        )

        # Create Internet Gateway
        self.mgmt_vpc_igw = ec2.CfnInternetGateway(self,
            id="Management VPC IGW",
            tags=[{"key":"Name", "value":"Management VPC IGW"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.mgmt_igw_attach = ec2.CfnVPCGatewayAttachment(self,
            id="Management VPC IGW Attach",
            vpc_id=self.vpc.ref,
            internet_gateway_id=self.mgmt_vpc_igw.ref
        )

        # Create Elastic IPs for NAT Gateways
        self.nat_gw_eip_1 = ec2.CfnEIP(self,
            id="Management EIP for NAT Gateway 1",
            domain=self.vpc.ref,
            tags=[{"key":"Name", "value":"Management EIP for NAT Gateway 1"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.nat_gw_eip_1.add_depends_on(self.mgmt_vpc_igw)

        self.nat_gw_eip_2 = ec2.CfnEIP(self,
            id="Management EIP for NAT Gateway 2",
            domain=self.vpc.ref,
            tags=[{"key":"Name", "value":"Management EIP for NAT Gateway 2"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.nat_gw_eip_2.add_depends_on(self.mgmt_vpc_igw)

        # Create NAT Gateways
        self.mgmt_nat_1 = ec2.CfnNatGateway(self,
            id="Management NAT Gateway 1",
            allocation_id=self.nat_gw_eip_1.attr_allocation_id,
            subnet_id=self.mgmt_dmz_1.ref,
            tags=[{"key":"Name", "value":"Management NAT Gateway 1"}, {"key": "Purpose", "value": "Networking"}]
        )
        self.mgmt_nat_2 = ec2.CfnNatGateway(self,
            id="Management NAT Gateway 2",
            allocation_id=self.nat_gw_eip_2.attr_allocation_id,
            subnet_id=self.mgmt_dmz_2.ref,
            tags=[{"key":"Name", "value":"Management NAT Gateway 2"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Add Default Routes to Route Tables
        self.mgmt_igw_route_1 = ec2.CfnRoute(self,
            id="Management IGW Default Route 1",
            route_table_id=self.pub_rt_1.ref,
            gateway_id=self.mgmt_vpc_igw.ref,
            destination_cidr_block="0.0.0.0/0"
        )
        self.mgmt_nat_route_1 = ec2.CfnRoute(self,
            id="Management NAT Default Route 1",
            route_table_id=self.pri_rt_1.ref,
            nat_gateway_id=self.mgmt_nat_1.ref,
            destination_cidr_block="0.0.0.0/0"
        )
        self.mgmt_igw_route_2 = ec2.CfnRoute(self,
            id="Management IGW Default Route 2",
            route_table_id=self.pub_rt_2.ref,
            gateway_id=self.mgmt_vpc_igw.ref,
            destination_cidr_block="0.0.0.0/0"
        )
        self.mgmt_nat_route_2 = ec2.CfnRoute(self,
            id="Management NAT Default Route 2",
            route_table_id=self.pri_rt_2.ref,
            nat_gateway_id=self.mgmt_nat_2.ref,
            destination_cidr_block="0.0.0.0/0"
        )
        