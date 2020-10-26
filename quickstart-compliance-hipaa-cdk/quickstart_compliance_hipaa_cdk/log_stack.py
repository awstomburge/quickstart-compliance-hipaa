from aws_cdk import core
import aws_cdk.aws_cloudtrail as cloudtrail
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_iam as iam
import aws_cdk.aws_logs as logs
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_sns as sns

class LogStack(core.NestedStack):

    def __init__(self, scope: core.Construct, id: str, main_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        # Create S3 Buckets and Bucket Policies

        # AWS Logging Bucket
        self.logging_bucket = s3.CfnBucket(self,
            id='AWS Logging Bucket',
            bucket_encryption=s3.CfnBucket.BucketEncryptionProperty(
                server_side_encryption_configuration=[
                    s3.CfnBucket.ServerSideEncryptionRuleProperty(
                        server_side_encryption_by_default=s3.CfnBucket.ServerSideEncryptionByDefaultProperty(
                                sse_algorithm="AES256"
                        )
                    )
                ]
            ),
            access_control='LogDeliveryWrite',
            lifecycle_configuration=s3.CfnBucket.LifecycleConfigurationProperty(
                rules=[
                    s3.CfnBucket.RuleProperty(
                        id='Transition90daysRetain7yrs',
                        status='Enabled',
                        expiration_in_days=main_stack.lc_expire_days.value_as_number,
                        transitions=[
                            s3.CfnBucket.TransitionProperty(
                                storage_class='STANDARD_IA',
                                transition_in_days=main_stack.lc_trans_std.value_as_number
                            ),
                            s3.CfnBucket.TransitionProperty(
                                storage_class='GLACIER',
                                transition_in_days=main_stack.lc_trans_gla.value_as_number
                            )
                        ]
                    )
                ]
            ),
            versioning_configuration=s3.CfnBucket.VersioningConfigurationProperty(status='Enabled'),
            tags=[{"key": "Name", "value": "AWS Logging Bucket"}, {"key": "Purpose", "value": "Security"}]
        )

        logging_bucket_policy = {
            "Version": "2012-10-17",
            "Id": "AWSLoggingAccessToBucket",
            "Statement": [
                {
                    "Sid": "DenyUnEncryptedObjectUploads",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": self.logging_bucket.attr_arn + "/*",
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                },
                {
                    "Sid": "Restrict Delete* Actions",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:Delete*",
                    "Resource": self.logging_bucket.attr_arn + "/*"
                },
                {
                    "Sid": "DenyUnEncryptedObjectUploads",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:PutObject",
                    "Resource": self.logging_bucket.attr_arn + "/*",
                    "Condition": {
                        "StringNotEquals": {
                            "s3:x-amz-server-side-encryption": "AES256"
                        }
                    }
                }
            ]
        }

        self.aws_config_policy = s3.CfnBucketPolicy(self,
            id='AWS Logging Bucket Policy',
            bucket=self.logging_bucket.ref,
            policy_document=logging_bucket_policy
        )
        self.aws_config_policy.add_depends_on(self.logging_bucket)

        # AWS CloudTrail Bucket
        self.cloudtrail_bucket = s3.CfnBucket(self,
            id='AWS CloudTrail Bucket',
            bucket_encryption=s3.CfnBucket.BucketEncryptionProperty(
                server_side_encryption_configuration=[
                    s3.CfnBucket.ServerSideEncryptionRuleProperty(
                        server_side_encryption_by_default=s3.CfnBucket.ServerSideEncryptionByDefaultProperty(
                                sse_algorithm="AES256"
                        )
                    )
                ],
            ),
            access_control='LogDeliveryWrite',
            versioning_configuration=s3.CfnBucket.VersioningConfigurationProperty(status='Enabled'),
            logging_configuration=s3.CfnBucket.LoggingConfigurationProperty(
                destination_bucket_name=self.logging_bucket.bucket_name,
                log_file_prefix='cloudtraillogs-'
            ),
            tags=[{"key": "Name", "value": "AWS CloudTrail Bucket"}, {"key": "Purpose", "value": "Security"}]
        )

        cloudtrail_bucket_policy = {
            "Version": "2012-10-17",
            "Id": "AWSCloudTrailAccessToBucket",
            "Statement": [
                {
                    "Sid": "AWSCloudTrailAclCheck20150319",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:GetBucketAcl",
                    "Resource": self.cloudtrail_bucket.attr_arn
                },
                {
                    "Sid": "AWSCloudTrailWrite20150319",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudtrail.amazonaws.com"
                    },
                    "Action": "s3:PutObject",
                    "Resource": self.cloudtrail_bucket.attr_arn + "/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                },
                {
                    "Sid": "DenyUnEncryptedObjectUploads",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": self.cloudtrail_bucket.attr_arn + "/*",
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                },
                {
                    "Sid": "Restrict Delete* Actions",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:Delete*",
                    "Resource": self.cloudtrail_bucket.attr_arn + "/*"
                },
                {
                    "Sid": "DenyUnEncryptedObjectUploads",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:PutObject",
                    "Resource": self.cloudtrail_bucket.attr_arn + "/*",
                    "Condition": {
                        "StringNotEquals": {
                            "s3:x-amz-server-side-encryption": "AES256"
                        }
                    }
                }
            ]
        }

        self.aws_cloudtrail_policy = s3.CfnBucketPolicy(self,
            id='AWS CloudTrail Bucket Policy',
            bucket=self.cloudtrail_bucket.ref,
            policy_document=cloudtrail_bucket_policy
        )
        self.aws_cloudtrail_policy.add_depends_on(self.cloudtrail_bucket)

        # Create SNS Topic
        self.security_alarm_topic = sns.CfnTopic(self,
            id='SNS Security Alarm Topic',
            subscription=[ 
                sns.CfnTopic.SubscriptionProperty(
                    endpoint=main_stack.sns_alarm_email.value_as_string,
                    protocol='email'
                )
            ]
        )

        # Log Groups
        self.cloudtrail_log_group = logs.CfnLogGroup(self, 
            id='CloudTrail Log Group',
            log_group_name='cloudtrail-log-group',
            retention_in_days=main_stack.ct_log_ret.value_as_number
        )
        self.cloudtrail_log_group.add_depends_on(self.security_alarm_topic)

        # IAM Policies
        cloudtrail_assume_role = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowFlowLogs",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        cloudtrail_actions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:ListBucket",
                    "Resource": self.logging_bucket.attr_arn
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:GetObject"
                    ],
                    "Resource": self.logging_bucket.attr_arn + "/*"
                }
            ]    
        }

        cloudwatch_assume_role = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowFlowLogs",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudtrail.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        cloudwatch_actions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AWSCloudTrailCreateLogStream20141101",
                    "Effect": "Allow",
                    "Action": "logs:CreateLogStream",
                    "Resource": self.cloudtrail_log_group.attr_arn
                },
                {
                    "Sid": "AWSCloudTrailPutLogEvents20141101",
                    "Effect": "Allow",
                    "Action": "logs:PutLogEvents",
                    "Resource": self.cloudtrail_log_group.attr_arn
                }
            ]    
        }

        self.cloudtrail_role = iam.CfnRole(self, 
            id='CloudTrail Role',
            description='CloudTrail Role',
            path='/',
            assume_role_policy_document=cloudtrail_assume_role,
            policies=[
                {
                    "policyName": "cloudtrail-limited-actions",
                    "policyDocument": cloudtrail_actions_policy
                }
            ]
        )

        self.cloudwatch_role = iam.CfnRole(self, 
            id='CloudWatch Role',
            description='CloudWatch Role',
            path='/',
            assume_role_policy_document=cloudwatch_assume_role,
            policies=[
                {
                    "policyName": "cloudwatch-limited-actions",
                    "policyDocument": cloudwatch_actions_policy
                }
            ]
        )

        # Create Instance Profile
        self.cloudtrail_ip = iam.CfnInstanceProfile(self,
            id='Cloud Trail Instance Profile',
            path='/',
            roles=[self.cloudtrail_role.ref]
        )

        # CloudTrail Trails
        self.cloudtrail_trail = cloudtrail.CfnTrail(self,
            id='CloudTrail Trail',
            is_logging=True,
            s3_bucket_name=self.cloudtrail_bucket.ref,
            cloud_watch_logs_log_group_arn=self.cloudtrail_log_group.attr_arn,
            cloud_watch_logs_role_arn=self.cloudwatch_role.attr_arn,
            enable_log_file_validation=True,
            include_global_service_events=True,
            # sns_topic_name=self.security_alarm_topic.ref, # TODO FIX TOPIC POLICY
            trail_name='cloudtrail-trail'
        )
        self.cloudtrail_trail.add_depends_on(self.aws_cloudtrail_policy)
        self.cloudtrail_trail.add_depends_on(self.security_alarm_topic)

        # Create Metric Filters
        self.mf_cloudtrail_change = logs.CfnMetricFilter(self,
            id='Metric Filter CloudTrail Change',
            log_group_name=self.cloudtrail_log_group.ref,
            filter_pattern='{($.eventSource = cloudtrail.amazonaws.com) && (($.eventName != Describe*) && ($.eventName != Get*) && ($.eventName != Lookup*) && ($.eventName != List*))}',
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_namespace='CloudTrailMetrics',
                    metric_name='CloudTrailChangeCount',
                    metric_value='1'
                )
            ]
        )
        self.mf_cloudtrail_change.add_depends_on(self.cloudtrail_log_group)

        self.mf_iam_create_access_key = logs.CfnMetricFilter(self,
            id='Metric Filter IAM Create Access Key',
            log_group_name=self.cloudtrail_log_group.ref,
            filter_pattern='{($.eventName=CreateAccessKey)}',
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_namespace='CloudTrailMetrics',
                    metric_name='NewAccessKeyCreated',
                    metric_value='1'
                )
            ]
        )
        self.mf_iam_create_access_key.add_depends_on(self.cloudtrail_log_group)

        self.mf_iam_policy_changes = logs.CfnMetricFilter(self,
            id='Metric Filter IAM Policy Changes',
            log_group_name=self.cloudtrail_log_group.log_group_name,
            filter_pattern='{($.eventName=DeleteGroupPolicy) || ($.eventName=DeleteRolePolicy) || ($.eventName=DeleteUserPolicy) ||  ($.eventName=PutGroupPolicy) || ($.eventName=PutRolePolicy) || ($.eventName=PutUserPolicy) || ($.eventName=CreatePolicy) || ($.eventName=DeletePolicy) || ($.eventName=CreatePolicyVersion) ||  ($.eventName=DeletePolicyVersion) || ($.eventName=AttachRolePolicy) || ($.eventName=DetachRolePolicy) || ($.eventName=AttachUserPolicy) || ($.eventName=DetachUserPolicy) || ($.eventName=AttachGroupPolicy) || ($.eventName=DetachGroupPolicy)}',
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_namespace='CloudTrailMetrics',
                    metric_name='IAMPolicyEventCount',
                    metric_value='1'
                )
            ]
        )
        self.mf_iam_policy_changes.add_depends_on(self.cloudtrail_log_group)

        self.mf_iam_root_activity = logs.CfnMetricFilter(self,
            id='Metric Filter IAM Root Activity',
            log_group_name=self.cloudtrail_log_group.ref,
            filter_pattern='{($.userIdentity.type = "Root") && ($.userIdentity.invokedBy NOT EXISTS) && ($.eventType != "AwsServiceEvent")}',
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_namespace='CloudTrailMetrics',
                    metric_name='RootUserPolicyEventCount',
                    metric_value='1'
                )
            ]
        )
        self.mf_iam_root_activity.add_depends_on(self.cloudtrail_log_group)

        self.mf_network_acl_changes = logs.CfnMetricFilter(self,
            id='Metric Filter Network ACL Changes',
            log_group_name=self.cloudtrail_log_group.ref,
            filter_pattern='{($.eventName = CreateNetworkAcl) || ($.eventName = CreateNetworkAclEntry) || ($.eventName = DeleteNetworkAcl) || ($.eventName = DeleteNetworkAclEntry) || ($.eventName = ReplaceNetworkAclEntry) || ($.eventName = ReplaceNetworkAclAssociation)}',
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_namespace='CloudTrailMetrics',
                    metric_name='NetworkAclEventCount',
                    metric_value='1'
                )
            ]
        )
        self.mf_network_acl_changes.add_depends_on(self.cloudtrail_log_group)

        self.mf_security_group_changes = logs.CfnMetricFilter(self,
            id='Metric Filter Security Group Changes',
            log_group_name=self.cloudtrail_log_group.ref,
            filter_pattern='{($.eventName = AuthorizeSecurityGroupIngress) || ($.eventName = AuthorizeSecurityGroupEgress) || ($.eventName = RevokeSecurityGroupIngress) || ($.eventName = RevokeSecurityGroupEgress) || ($.eventName = CreateSecurityGroup) || ($.eventName = DeleteSecurityGroup)}',
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_namespace='CloudTrailMetrics',
                    metric_name='SecurityGroupEventCount',
                    metric_value='1'
                )
            ]
        )
        self.mf_security_group_changes.add_depends_on(self.cloudtrail_log_group)

        self.mf_unauthorized_attempts = logs.CfnMetricFilter(self,
            id='Metric Filter Unauthorized Attempts',
            log_group_name=self.cloudtrail_log_group.ref,
            filter_pattern='{($.errorCode=AccessDenied) || ($.errorCode=UnauthorizedOperation)}',
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_namespace='CloudTrailMetrics',
                    metric_name='UnauthorizedAttemptCount',
                    metric_value='1'
                )
            ]
        )
        self.mf_unauthorized_attempts.add_depends_on(self.cloudtrail_log_group)

        # Create Alarms
        self.cw_alarm_cloudtrail_change = cloudwatch.CfnAlarm(self,
            id='CloudWatch Alarm CloudTrail Change',
            alarm_name='cloudtrail-change-alarm',
            alarm_description='Warning: Changes to CloudTrail log configuration detected in this account.',
            actions_enabled=True,
            alarm_actions=[self.security_alarm_topic.ref],
            namespace='CloudTrailMetrics',
            metric_name='CloudTrailChangeCount',
            comparison_operator='GreaterThanOrEqualToThreshold',
            evaluation_periods=1,
            period=300,
            statistic='Sum',
            threshold=1
        )
        self.cw_alarm_cloudtrail_change.add_depends_on(self.mf_cloudtrail_change)

        self.cw_alarm_iam_create_access_key = cloudwatch.CfnAlarm(self,
            id='CloudWatch Alarm IAM Create Access Key',
            alarm_name='iam-create-access-key-alarm',
            alarm_description='Warning: New IAM access key was created. Please be sure this action was neccessary.',
            actions_enabled=True,
            alarm_actions=[self.security_alarm_topic.ref],
            namespace='CloudTrailMetrics',
            metric_name='NewAccessKeyCreated',
            comparison_operator='GreaterThanOrEqualToThreshold',
            evaluation_periods=1,
            period=300,
            statistic='Sum',
            threshold=1
        )
        self.cw_alarm_iam_create_access_key.add_depends_on(self.mf_iam_create_access_key)

        self.cw_alarm_iam_policy_change = cloudwatch.CfnAlarm(self,
            id='CloudWatch Alarm IAM Policy Change',
            alarm_name='iam-policy-change-alarm',
            alarm_description='Warning: IAM Configuration changes detected!',
            actions_enabled=True,
            alarm_actions=[self.security_alarm_topic.ref],
            namespace='CloudTrailMetrics',
            metric_name='IAMPolicyEventCount',
            comparison_operator='GreaterThanOrEqualToThreshold',
            evaluation_periods=1,
            period=300,
            statistic='Sum',
            threshold=1
        )
        self.cw_alarm_iam_policy_change.add_depends_on(self.mf_iam_policy_changes)

        self.cw_alarm_iam_root_activity = cloudwatch.CfnAlarm(self,
            id='CloudWatch Alarm IAM Root Activity',
            alarm_name='iam-root-activity-alarm',
            alarm_description='Warning: Root user activity detected!',
            actions_enabled=True,
            alarm_actions=[self.security_alarm_topic.ref],
            namespace='CloudTrailMetrics',
            metric_name='RootUserPolicyEventCount',
            comparison_operator='GreaterThanOrEqualToThreshold',
            evaluation_periods=1,
            period=300,
            statistic='Sum',
            threshold=1
        )
        self.cw_alarm_iam_root_activity.add_depends_on(self.mf_iam_root_activity)

        self.cw_alarm_network_acl_changes = cloudwatch.CfnAlarm(self,
            id='CloudWatch Alarm Network ACL Changes',
            alarm_name='network-acl-changes-alarm',
            alarm_description='Warning: Network ACLs have changed!',
            actions_enabled=True,
            alarm_actions=[self.security_alarm_topic.ref],
            namespace='CloudTrailMetrics',
            metric_name='NetworkAclEventCount',
            comparison_operator='GreaterThanOrEqualToThreshold',
            evaluation_periods=1,
            period=300,
            statistic='Sum',
            threshold=1
        )
        self.cw_alarm_network_acl_changes.add_depends_on(self.mf_network_acl_changes)

        self.cw_alarm_security_group_changes = cloudwatch.CfnAlarm(self,
            id='CloudWatch Alarm Security Group Changes',
            alarm_name='security-group-changes-alarm',
            alarm_description='Warning: Security Groups have changed!',
            actions_enabled=True,
            alarm_actions=[self.security_alarm_topic.ref],
            namespace='CloudTrailMetrics',
            metric_name='SecurityGroupEventCount',
            comparison_operator='GreaterThanOrEqualToThreshold',
            evaluation_periods=1,
            period=300,
            statistic='Sum',
            threshold=1
        )
        self.cw_alarm_security_group_changes.add_depends_on(self.mf_security_group_changes)

        self.cw_alarm_unauthorized_attemps = cloudwatch.CfnAlarm(self,
            id='CloudWatch Alarm Unauthorized Attempts',
            alarm_name='unauthorized-attempts-alarm',
            alarm_description='Warning: Unauthorized Attempts have been detected!',
            actions_enabled=True,
            alarm_actions=[self.security_alarm_topic.ref],
            namespace='CloudTrailMetrics',
            metric_name='UnauthorizedAttemptCount',
            comparison_operator='GreaterThanOrEqualToThreshold',
            evaluation_periods=1,
            period=300,
            statistic='Sum',
            threshold=1
        )
        self.cw_alarm_unauthorized_attemps.add_depends_on(self.mf_unauthorized_attempts)