from aws_cdk import core
import aws_cdk.aws_ec2 as ec2

class TgwStack(core.NestedStack):

    def __init__(self, scope: core.Construct, id: str, main_stack, dev_stack, prod_stack, mgmt_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.add_dependency(mgmt_stack)
        self.add_dependency(prod_stack)
        self.add_dependency(dev_stack)

        # Create Transit Gateway
        self.tgw = ec2.CfnTransitGateway(self,
            id='HIPAA Transit Gateway',
            auto_accept_shared_attachments='enable',
            default_route_table_association='disable',
            default_route_table_propagation='disable',
            description='HIPAA Transit Gateway',
            dns_support='enable',
            vpn_ecmp_support='enable',
            tags=[{"key":"Name", "value":"HIPAA Transit Gateway"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Create Transit Gateway Attachments
        self.mgmt_tgw_attach_1 = ec2.CfnTransitGatewayAttachment(self,
            id='Management VPC to Transit Gateway',
            subnet_ids=[mgmt_stack.mgmt_core_1.ref, mgmt_stack.mgmt_core_2.ref],
            transit_gateway_id=self.tgw.ref,
            vpc_id=mgmt_stack.vpc.ref,
            tags=[{"key":"Name", "value":"Management Transit Gateway Attachment"}, {"key": "Purpose", "value": "Networking"}]
        )

        self.prod_tgw_attach_1 = ec2.CfnTransitGatewayAttachment(self,
            id='Production VPC to Transit Gateway',
            subnet_ids=[prod_stack.prod_core_1.ref, prod_stack.prod_core_2.ref],
            transit_gateway_id=self.tgw.ref,
            vpc_id=prod_stack.vpc.ref,
            tags=[{"key":"Name", "value":"Production Transit Gateway Attachment"}, {"key": "Purpose", "value": "Networking"}]
        )

        self.dev_tgw_attach_1 = ec2.CfnTransitGatewayAttachment(self,
            id='Dev VPC to Transit Gateway',
            subnet_ids=[dev_stack.dev_core_1.ref, dev_stack.dev_core_2.ref],
            transit_gateway_id=self.tgw.ref,
            vpc_id=dev_stack.vpc.ref,
            tags=[{"key":"Name", "value":"Development Transit Gateway Attachment"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Create Transit Gateway Route Tables
        self.ext_route_table = ec2.CfnTransitGatewayRouteTable(self,
            id='Transit Gateway External Route Table',
            transit_gateway_id=self.tgw.ref,
            tags=[{"key":"Name", "value":"External Transit Gateway Route Table"}, {"key": "Purpose", "value": "Networking"}]
        )

        self.int_route_table = ec2.CfnTransitGatewayRouteTable(self,
            id='Transit Gateway Internal Route Table',
            transit_gateway_id=self.tgw.ref,
            tags=[{"key":"Name", "value":"Internal Transit Gateway Route Table"}, {"key": "Purpose", "value": "Networking"}]
        )

        # Create Transit Gateway Route Table Associations
        self.ext_route_table_ass = ec2.CfnTransitGatewayRouteTableAssociation(self,
            id='Transit Gateway External Route Table Association',
            transit_gateway_attachment_id=self.mgmt_tgw_attach_1.ref,
            transit_gateway_route_table_id=self.ext_route_table.ref
        )

        self.int_route_table_ass_1 = ec2.CfnTransitGatewayRouteTableAssociation(self,
            id='Transit Gateway Production VPC Route Table Association',
            transit_gateway_attachment_id=self.prod_tgw_attach_1.ref,
            transit_gateway_route_table_id=self.int_route_table.ref
        )

        self.int_route_table_ass_2 = ec2.CfnTransitGatewayRouteTableAssociation(self,
            id='Transit Gateway Development VPC Route Table Association',
            transit_gateway_attachment_id=self.dev_tgw_attach_1.ref,
            transit_gateway_route_table_id=self.int_route_table.ref
        )

        # Create Transit Gateway Internal Route Propagations
        self.int_route_prop_1 = ec2.CfnTransitGatewayRouteTablePropagation(self,
            id='Transit Gateway Internal Route Prop 1',
            transit_gateway_attachment_id=self.prod_tgw_attach_1.ref,
            transit_gateway_route_table_id=self.int_route_table.ref
        )

        self.int_route_prop_2 = ec2.CfnTransitGatewayRouteTablePropagation(self,
            id='Transit Gateway Internal Route Prop 2',
            transit_gateway_attachment_id=self.dev_tgw_attach_1.ref,
            transit_gateway_route_table_id=self.int_route_table.ref
        )

        # Create Transit Gateway External Route Propagations
        self.ext_route_prop_1 = ec2.CfnTransitGatewayRouteTablePropagation(self,
            id='Transit Gateway External Route Prop 1',
            transit_gateway_attachment_id=self.mgmt_tgw_attach_1.ref,
            transit_gateway_route_table_id=self.ext_route_table.ref
        )

        # Create Transit Gateway Internal Route Table Routes
        self.int_route_1 = ec2.CfnTransitGatewayRoute(self,
            id='Transit Gateway Internal Route 1',
            transit_gateway_route_table_id=self.int_route_table.ref,
            destination_cidr_block='0.0.0.0/0',
            transit_gateway_attachment_id=self.mgmt_tgw_attach_1.ref
        )

        # Create Transit Gateway External Route Table Routes
        self.ext_route_1 = ec2.CfnTransitGatewayRoute(self,
            id='Transit Gateway External Route 1',
            transit_gateway_route_table_id=self.ext_route_table.ref,
            destination_cidr_block=main_stack.prod_cidr.value_as_string,
            transit_gateway_attachment_id=self.prod_tgw_attach_1.ref
        )

        self.ext_route_2 = ec2.CfnTransitGatewayRoute(self,
            id='Transit Gateway External Route 2',
            transit_gateway_route_table_id=self.ext_route_table.ref,
            destination_cidr_block=main_stack.dev_cidr.value_as_string,
            transit_gateway_attachment_id=self.dev_tgw_attach_1.ref
        )

        # Create VPC Routes to Transit Gateway
        self.mgmt_private_subnet1_route1 = ec2.CfnRoute(self,
            id='Management Private Subnet 1 Route 1',
            destination_cidr_block=main_stack.prod_cidr.value_as_string,
            route_table_id=mgmt_stack.pri_rt_1.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.mgmt_private_subnet1_route1.add_depends_on(self.tgw)
        self.mgmt_private_subnet1_route1.add_depends_on(self.mgmt_tgw_attach_1)

        self.mgmt_private_subnet1_route2 = ec2.CfnRoute(self,
            id='Management Private Subnet 1 Route 2',
            destination_cidr_block=main_stack.dev_cidr.value_as_string,
            route_table_id=mgmt_stack.pri_rt_1.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.mgmt_private_subnet1_route2.add_depends_on(self.tgw)
        self.mgmt_private_subnet1_route2.add_depends_on(self.mgmt_tgw_attach_1)

        self.mgmt_private_subnet2_route1 = ec2.CfnRoute(self,
            id='Management Private Subnet 2 Route 1',
            destination_cidr_block=main_stack.prod_cidr.value_as_string,
            route_table_id=mgmt_stack.pri_rt_2.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.mgmt_private_subnet2_route1.add_depends_on(self.tgw)
        self.mgmt_private_subnet2_route1.add_depends_on(self.mgmt_tgw_attach_1)

        self.mgmt_private_subnet2_route2 = ec2.CfnRoute(self,
            id='Management Private Subnet 2 Route 2',
            destination_cidr_block=main_stack.dev_cidr.value_as_string,
            route_table_id=mgmt_stack.pri_rt_2.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.mgmt_private_subnet2_route2.add_depends_on(self.tgw)
        self.mgmt_private_subnet2_route2.add_depends_on(self.mgmt_tgw_attach_1)

        self.mgmt_public_subnet1_route1 = ec2.CfnRoute(self,
            id='Management Public Subnet 1 Route 1',
            destination_cidr_block=main_stack.prod_cidr.value_as_string,
            route_table_id=mgmt_stack.pub_rt_1.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.mgmt_public_subnet1_route1.add_depends_on(self.tgw)
        self.mgmt_public_subnet1_route1.add_depends_on(self.mgmt_tgw_attach_1)

        self.mgmt_public_subnet1_route2 = ec2.CfnRoute(self,
            id='Management Public Subnet 1 Route 2',
            destination_cidr_block=main_stack.dev_cidr.value_as_string,
            route_table_id=mgmt_stack.pub_rt_1.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.mgmt_public_subnet1_route2.add_depends_on(self.tgw)
        self.mgmt_public_subnet1_route2.add_depends_on(self.mgmt_tgw_attach_1)

        self.mgmt_public_subnet2_route1 = ec2.CfnRoute(self,
            id='Management Public Subnet 2 Route 1',
            destination_cidr_block=main_stack.prod_cidr.value_as_string,
            route_table_id=mgmt_stack.pub_rt_2.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.mgmt_public_subnet2_route1.add_depends_on(self.tgw)
        self.mgmt_public_subnet2_route1.add_depends_on(self.mgmt_tgw_attach_1)

        self.mgmt_public_subnet2_route2 = ec2.CfnRoute(self,
            id='Management Public Subnet 2 Route 2',
            destination_cidr_block=main_stack.dev_cidr.value_as_string,
            route_table_id=mgmt_stack.pub_rt_2.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.mgmt_public_subnet2_route2.add_depends_on(self.tgw)
        self.mgmt_public_subnet2_route2.add_depends_on(self.mgmt_tgw_attach_1)

        self.dev_default_route = ec2.CfnRoute(self,
            id='Development VPC Default Route',
            destination_cidr_block='0.0.0.0/0',
            route_table_id=dev_stack.pri_rt_1.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.dev_default_route.add_depends_on(self.tgw)
        self.dev_default_route.add_depends_on(self.dev_tgw_attach_1)

        self.prod_default_route = ec2.CfnRoute(self,
            id='Production VPC Default Route',
            destination_cidr_block='0.0.0.0/0',
            route_table_id=prod_stack.pri_rt_1.ref,
            transit_gateway_id=self.tgw.ref
        )
        self.prod_default_route.add_depends_on(self.tgw)
        self.prod_default_route.add_depends_on(self.prod_tgw_attach_1)
