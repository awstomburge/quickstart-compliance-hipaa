from aws_cdk import core
import aws_cdk.aws_cloudformation as cf

class MainStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        # cf.CfnStack(self,
        #     id='ConfigStack',
        #     template_url='https://bucket.s3.region.amazonaws.com/mainstackconfigstack8791BFD3.nested.template.json'
        # )

        # cf.CfnStack(self,
        #     id='LogStack',
        #     template_url='https://bucket.s3.region.amazonaws.com/mainstackconfigstack8791BFD3.nested.template.json'
        # )

        # cf.CfnStack(self,
        #     id='DevStack',
        #     template_url='https://bucket.s3.region.amazonaws.com/mainstackconfigstack8791BFD3.nested.template.json'
        # )

        # cf.CfnStack(self,
        #     id='ProdStack',
        #     template_url='https://bucket.s3.region.amazonaws.com/mainstackconfigstack8791BFD3.nested.template.json'
        # )

        # cf.CfnStack(self,
        #     id='MgmtStack',
        #     template_url='https://bucket.s3.region.amazonaws.com/mainstackconfigstack8791BFD3.nested.template.json'
        # )

        # cf.CfnStack(self,
        #     id='TgwStack',
        #     template_url='https://bucket.s3.region.amazonaws.com/mainstackconfigstack8791BFD3.nested.template.json'
        # )

        # Config Parameters
        self.aws_config_arn = core.CfnParameter(self,
            id='AWS Config ARN',
            default='arn:aws:iam::501353236270:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig',
            description='AWS Config Service Linked Role ARN',
            type='String'
        )

        self.aws_config_hipaa = core.CfnParameter(self,
            id='AWS Config HIPAA Pack',
            default='Operational-Best-Practices-for-HIPAA-Security.yaml',
            description='AWS Config HIPAA Pack Location',
            type='String'
        )

        # Log Parameters
        self.lc_expire_days = core.CfnParameter(self,
            id='Lifecycle Expiration Days',
            default=2555,
            description='Lifecycle Expiration Days',
            type='Number'
        )

        self.lc_trans_std = core.CfnParameter(self,
            id='Lifecycle Transition StandardIA Days',
            default=90,
            description='Lifecycle Transition Standard-IA Days',
            type='Number'
        )

        self.lc_trans_gla = core.CfnParameter(self,
            id='Lifecycle Transition Glacier Days',
            default=180,
            description='Lifecycle Transition Glacier Days',
            type='Number'
        )

        self.sns_alarm_email = core.CfnParameter(self,
            id='SNS Alarm Email',
            default='change@me.com',
            description='SNS Security Alarm Email',
            type='String'
        )

        self.ct_log_ret = core.CfnParameter(self,
            id='CloudTrail Log Retention Days',
            default=90,
            description='CloudTrail Log Group Retention Days',
            type='Number'
        )

        # Development Parameters
        self.dev_cidr = core.CfnParameter(self,
            id='Dev VPC CIDR Block',
            default='172.18.0.0/16',
            description='Development VPC CIDR Block',
            type='String'
        )

        self.dev_subnet_1 = core.CfnParameter(self,
            id='Dev VPC Subnet 1',
            default='172.18.11.0/24',
            description='Development VPC Subnet 1',
            type='String'
        )

        self.dev_subnet_2 = core.CfnParameter(self,
            id='Dev VPC Subnet 2',
            default='172.18.12.0/24',
            description='Development VPC Subnet 2',
            type='String'
        )

        self.dev_log_group = core.CfnParameter(self,
            id='Dev VPC Flow Log Log Group',
            default='dev-flow-logs-group',
            description='Development VPC Flow Logs Log Group',
            type='String'
        )

        self.dev_log_group_ret = core.CfnParameter(self,
            id='Dev VPC Flow Log Log Group Retention',
            default=90,
            description='Development VPC Flow Logs Log Group Retention Days',
            type='Number'
        )

        # Production Parameters
        self.prod_cidr = core.CfnParameter(self,
            id='Prod VPC CIDR Block',
            default='172.17.0.0/16',
            description='Production VPC CIDR Block',
            type='String'
        )

        self.prod_subnet_1 = core.CfnParameter(self,
            id='Prod VPC Subnet 1',
            default='172.17.11.0/24',
            description='Production VPC Subnet 1',
            type='String'
        )

        self.prod_subnet_2 = core.CfnParameter(self,
            id='Prod VPC Subnet 2',
            default='172.17.12.0/24',
            description='Production VPC Subnet 2',
            type='String'
        )

        self.prod_log_group = core.CfnParameter(self,
            id='Prod VPC Flow Log Log Group',
            default='prod-flow-logs-group',
            description='Production VPC Flow Logs Log Group',
            type='String'
        )

        self.prod_log_group_ret = core.CfnParameter(self,
            id='Prod VPC Flow Log Log Group Retention',
            default=90,
            description='Production VPC Flow Logs Log Group Retention Days',
            type='Number'
        )

        # Management Parameters
        self.mgmt_cidr = core.CfnParameter(self,
            id='Mgmt VPC CIDR Block',
            default='172.16.0.0/16',
            description='Management VPC CIDR Block',
            type='String'
        )

        self.mgmt_pub_subnet_1 = core.CfnParameter(self,
            id='Mgmt VPC Public Subnet 1',
            default='172.16.1.0/24',
            description='Management VPC Subnet 1',
            type='String'
        )

        self.mgmt_pub_subnet_2 = core.CfnParameter(self,
            id='Mgmt VPC Public Subnet 2',
            default='172.16.2.0/24',
            description='Management VPC Subnet 2',
            type='String'
        )

        self.mgmt_pri_subnet_1 = core.CfnParameter(self,
            id='Mgmt VPC Private Subnet 1',
            default='172.16.11.0/24',
            description='Management VPC Subnet 1',
            type='String'
        )

        self.mgmt_pri_subnet_2 = core.CfnParameter(self,
            id='Mgmt VPC Private Subnet 2',
            default='172.16.12.0/24',
            description='Management VPC Subnet 2',
            type='String'
        )

        self.mgmt_log_group = core.CfnParameter(self,
            id='Mgmt VPC Flow Log Log Group',
            default='mgmt-flow-logs-group',
            description='Management VPC Flow Logs Log Group',
            type='String'
        )

        self.mgmt_log_group_ret = core.CfnParameter(self,
            id='Mgmt VPC Flow Log Log Group Retention',
            default=90,
            description='Management VPC Flow Logs Log Group Retention Days',
            type='Number'
        )