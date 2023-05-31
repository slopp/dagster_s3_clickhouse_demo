from setuptools import find_packages, setup

setup(
    name="aws_sensor_example",
    packages=find_packages(exclude=["aws_sensor_example_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "clickhouse-connect",
        "dagster-aws"
    ],
    extras_require={"dev": ["dagit", "pytest"]},
)
