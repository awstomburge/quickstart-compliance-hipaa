from aws_cdk import core
import aws_cdk.aws_config as aws_config
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_assets as s3_assets

class ConfigStack(core.NestedStack):

    def __init__(self, scope: core.Construct, id: str, main_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create S3 Bucket for AWS Config

        self.config_bucket = s3.CfnBucket(self,
            id='AWS Config Logging Bucket',
            bucket_encryption=s3.CfnBucket.BucketEncryptionProperty(
                server_side_encryption_configuration=[
                    s3.CfnBucket.ServerSideEncryptionRuleProperty(
                        server_side_encryption_by_default=s3.CfnBucket.ServerSideEncryptionByDefaultProperty(
                                sse_algorithm="AES256"
                        )
                    )
                ]
            ),
            tags=[{"key": "Name", "value": "AWS Config Logging Bucket"}, {"key": "Purpose", "value": "Security"}]
        )

        config_bucket_policy = {
            "Version": "2012-10-17",
            "Id": "AWSConfigAccessToBucket",
            "Statement": [
                {
                    "Sid": "AWSConfigBucketPermissionsCheck",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "config.amazonaws.com"
                    },
                    "Action": "s3:GetBucketAcl",
                    "Resource": self.config_bucket.attr_arn
                },
                {
                    "Sid": "AWSConfigBucketDelivery",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "config.amazonaws.com"
                    },
                    "Action": "s3:PutObject",
                    "Resource": self.config_bucket.attr_arn + "/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                }
            ]
        }

        aws_config_policy = s3.CfnBucketPolicy(self,
            id='AWS Config Bucket Policy',
            bucket=self.config_bucket.ref,
            policy_document=config_bucket_policy
        )

        # Upload Conformance Pack to Bucket

        self.hipaa_pack = s3_assets.Asset(self,
            id='HIPAA Conformance Pack',
            path='./quickstart_compliance_hipaa_cdk/Operational-Best-Practices-for-HIPAA-Security.yaml'
        )

        # Create AWS Config Delivery Channel
        self.config_dc = aws_config.CfnDeliveryChannel(self,
            id='AWS Config Delivery Channel',
            name='default',
            s3_bucket_name=self.config_bucket.ref
        )

        # Create AWS Config Configuration Recorder
        self.config_recorder = aws_config.CfnConfigurationRecorder(self,
            id='AWS Config Configuration Recorder',
            name='default',
            role_arn=main_stack.aws_config_arn.value_as_string
        )

        # Add HIPAA Conformance Pack
        self.config_hipaa_pack = aws_config.CfnConformancePack(self,
            id='AWS Config HIPAA Conformance Pack',
            conformance_pack_name='aws-config-hipaa-conformance-pack',
            template_s3_uri=self.hipaa_pack.s3_object_url
        )
