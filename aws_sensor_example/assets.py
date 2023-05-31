from dagster import (
    asset,
    Config,
    define_asset_job,
    OpExecutionContext,
    DynamicPartitionsDefinition,
    AssetSelection,
)
from aws_sensor_example.resources import ClickHouseResource
import os

raw_files = DynamicPartitionsDefinition(name="raw_files")


class RawDataAssetLoadConfig(Config):
    asset_config: str


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET = os.getenv("AWS_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")


@asset(partitions_def=raw_files)
def raw_data(
    context: OpExecutionContext,
    config: RawDataAssetLoadConfig,
    database: ClickHouseResource,
):
    """Raw data loaded from s3 to the ClickHouse table dagster_demo"""
    s3_file_to_process = context.partition_key
    s3_url = f"https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_file_to_process}"

    query = f"""
        INSERT INTO dagster_demo
        SELECT * FROM s3(
            '{s3_url}',
            '{AWS_ACCESS_KEY_ID}', '{AWS_SECRET_ACCESS_KEY}',
            'CSVWithNames'
        )
        SETTINGS input_format_with_names_use_header=1;
    """

    other_parameters = config.asset_config

    context.log.info(
        f"Attempting to load {s3_file_to_process}. Other potential config is: {other_parameters}"
    )

    database.execute_query(query)

    context.add_output_metadata(
        metadata={
            "clickhouse_destination": "dagster_demo",
            "loaded_from": s3_url,
            "owner": "data@example.com",
        }
    )


load_raw_data = define_asset_job(
    name="load_raw_data",
    selection=AssetSelection.assets(raw_data),
    partitions_def=raw_files,
    description="loads raw files from s3 to clickhouse",
    tags={"owner": "data team"},
)
