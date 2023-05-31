from dagster import (
    sensor,
    SkipReason,
    RunRequest,
    SensorResult,
    RunConfig,
    run_status_sensor,
    RunStatusSensorContext,
    DagsterRunStatus,
)
from dagster_aws.s3.sensor import get_s3_keys
from dagster_aws.s3 import S3Resource
from aws_sensor_example.assets import load_raw_data, raw_files, RawDataAssetLoadConfig
from datetime import datetime

import os


@sensor(job=load_raw_data)
def my_s3_sensor(context, s3: S3Resource):
    """Watches for files to land in s3 and loads them to ClickHouse"""
    s3_bucket = os.getenv("AWS_BUCKET")
    s3_prefix = "sensor_demo"
    since_key = context.cursor or None
    new_s3_keys = get_s3_keys(
        s3_bucket, since_key=since_key, prefix=s3_prefix, s3_session=s3
    )

    if f"{s3_prefix}/" in new_s3_keys:
        new_s3_keys.remove(f"{s3_prefix}/")

    if not new_s3_keys:
        return SkipReason("No new s3 files found for bucket.")

    last_key = new_s3_keys[-1]

    # an example of how to pass additional run time parameters as asset configuration
    additional_config = RunConfig(
        {
            "raw_data": RawDataAssetLoadConfig(
                asset_config=f" ran from sensor config at {datetime.now()}"
            )
        }
    )

    return SensorResult(
        # for each new file, register the file key as a dagster partition
        dynamic_partitions_requests=[raw_files.build_add_request(new_s3_keys)],
        # for each new file, submit a run, using newly registered dagster partition key and optional config
        run_requests=[
            RunRequest(partition_key=key, run_config=additional_config)
            for key in new_s3_keys
        ],
        cursor=last_key,
    )


@run_status_sensor(run_status=DagsterRunStatus.SUCCESS)
def my_mac_notify_on_run_success(context: RunStatusSensorContext):
    """An example sensor that notifies us on success, use Dagster Cloud alerts for common cases"""
    _mac_notify(
        "ClickHouse Update", f'Dagster Job {context.dagster_run.job_name} succeeded.'
    )


def _mac_notify(title, text):
    """Notifications for mac"""
    os.system(
        """
              osascript -e 'display notification "{}" with title "{}"'
              """.format(
            text, title
        )
    )
