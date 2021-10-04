import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="iac",
    version="0.0.1",

    description="CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="info@SteelHeadHQ.com",

    package_dir={"": "stacks"},
    packages=setuptools.find_packages(where="stacks"),

    install_requires=[
        "aws-cdk.core==1.98.0",
        "aws-cdk.pipelines",
        "aws-cdk.aws-s3",
        "aws-cdk.aws-s3-deployment",
        "aws-cdk.aws-glue",
        "aws-cdk.aws-redshift",
        "aws-cdk.aws-ec2",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-s3-notifications",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-lambda-event-sources",
        "aws-cdk.aws-dynamodb",
        "aws-cdk.aws-events",
        "aws-cdk.aws-events-targets",
        "aws-cdk.aws-apigateway",
        "aws-cdk.aws_appflow",
        "aws-cdk.aws_secretsmanager",
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