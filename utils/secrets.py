from typing import Dict

import hvac


def create_client(url: str, token: str) -> hvac.Client:
    return hvac.Client(url=url, token=token)


def read_secret(client: hvac.Client, path: str) -> Dict[str, str]:
    try:
        data_response = client.secrets.kv.v2.read_secret_version(
            path=path, raise_on_deleted_version=True
        )

        return data_response["data"]["data"]
    except hvac.exceptions.InvalidPath:
        raise ValueError(f"Path {path} does not exist")
    except Exception as e:
        print(f"read_secret: {e}")
        raise e
