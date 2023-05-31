from dagster import ConfigurableResource
import clickhouse_connect


class ClickHouseResource(ConfigurableResource):
    """This is a demo resource that shows how you could load data to ClickHouse"""

    # add necessary connection parameters
    host: str
    port: int

    def execute_query(self, query):
        """Execute a ClickHouse query"""
        client = clickhouse_connect.get_client(host=self.host, port=self.port)
        # A real resource should do error handling here
        client.raw_query(query=query)
