from dagster import Definitions, load_assets_from_modules, EnvVar

from aws_sensor_example import assets
from aws_sensor_example.sensors import my_s3_sensor, my_mac_notify_on_run_success
from aws_sensor_example.resources import ClickHouseResource
from dagster_aws.s3 import S3Resource

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    sensors=[my_s3_sensor, my_mac_notify_on_run_success],
    jobs=[assets.load_raw_data],
    resources={
        "s3": S3Resource(
            aws_access_key_id=EnvVar("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=EnvVar("AWS_SECRET_ACCESS_KEY"),
            region_name=EnvVar("AWS_REGION"),
            profile_name=EnvVar("AWS_PROFILE_NAME"),
        ),
        "database": ClickHouseResource(host="localhost", port=8123),
    },
)
