from fast_json_server.json_server import start_server

if __name__ == "__main__":
    start_server(host="0.0.0.0", port=3000, log_level='debug',
                 server_type="rest_api")