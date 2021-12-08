import click
from .rest_api import start_api
from .graph_ql import start_graphql


@click.command()
@click.option('--data_path', '-dp',
              help='Data Source Path', default="")
@click.option('--host', '-h',
              help='Host', default='0.0.0.0"')
@click.option('--port', '-p',
              help='Port', default=3000)
@click.option('--log_level', '-l',
              help='Log Level', default="debug")
@click.option('--server_type', '-st',
              help='Server Type', default="rest_api")
def __start_cli_server(data_path: str, host: str,
                       port: int,
                       log_level: str, server_type: str):
    if data_path != "":
        if server_type == "rest_api":
            print("REST API Server Started....")
            start_api(data_path=data_path, host=host, port=port,
                      log_level=log_level)
        elif server_type == "graph_ql":
            print("GraphQL Server Started....")
            start_graphql(data_path=data_path, host=host, port=port,
                          log_level=log_level)
        else:
            print("rest_api or graph_ql are allowed")
    else:
        print("Please provide json data")


def start_server(data_path: str = "", host: str = "0.0.0.0",
                 port: int = 3000,
                 log_level: str = "debug", server_type: str = "rest_api"):
    """
    Start Fast JSON Server
    :param data_path:
    :param host:
    :param port:
    :param log_level:
    :param server_type:
    :return:
    """
    if data_path != "":
        if server_type == "rest_api":
            print("REST API Server Started....")
            start_api(data_path=data_path, host=host, port=port,
                      log_level=log_level)
        elif server_type == "graph_ql":
            print("GraphQL Server Started....")
            start_graphql(data_path=data_path, host=host, port=port,
                          log_level=log_level)
        else:
            print("rest_api or graph_ql are allowed")
    else:
        print("Please provide json data")


if __name__ == "__main__":
    __start_cli_server()
