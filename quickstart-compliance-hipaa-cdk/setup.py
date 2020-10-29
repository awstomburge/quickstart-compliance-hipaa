import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="quickstart_compliance_hipaa_cdk",
    version="1.0.0",

    description="Quickstart Compliance HIPAA CDK Version",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Amazon Web Services",

    package_dir={"": "quickstart_compliance_hipaa_cdk"},
    packages=setuptools.find_packages(where="quickstart_compliance_hipaa_cdk"),

    install_requires=[
        "aws-cdk.core==1.69.0",
        "attrs==20.2.0",
        "aws-cdk.assets==1.69.0",
        "aws-cdk.aws-applicationautoscaling==1.69.0",
        "aws-cdk.aws-autoscaling-common==1.69.0",
        "aws-cdk.aws-cloudformation==1.69.0",
        "aws-cdk.aws-cloudtrail==1.69.0",
        "aws-cdk.aws-cloudwatch==1.69.0",
        "aws-cdk.aws-codeguruprofiler==1.69.0",
        "aws-cdk.aws-config==1.69.0",
        "aws-cdk.aws-ec2==1.69.0",
        "aws-cdk.aws-efs==1.69.0",
        "aws-cdk.aws-events==1.69.0",
        "aws-cdk.aws-iam==1.69.0",
        "aws-cdk.aws-kms==1.69.0",
        "aws-cdk.aws-lambda==1.69.0",
        "aws-cdk.aws-logs==1.69.0",
        "aws-cdk.aws-s3==1.69.0",
        "aws-cdk.aws-s3-assets==1.69.0",
        "aws-cdk.aws-sns==1.69.0",
        "aws-cdk.aws-sqs==1.69.0",
        "aws-cdk.aws-ssm==1.69.0",
        "aws-cdk.cloud-assembly-schema==1.69.0",
        "aws-cdk.core==1.69.0",
        "aws-cdk.cx-api==1.69.0",
        "aws-cdk.region-info==1.69.0",
        "cattrs==1.0.0",
        "constructs==3.2.0",
        "jsii==1.13.0",
        "publication==0.0.3",
        "python-dateutil==2.8.1",
        "six==1.15.0",
        "typing-extensions==3.7.4.3",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
