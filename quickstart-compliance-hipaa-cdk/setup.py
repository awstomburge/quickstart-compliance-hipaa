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
