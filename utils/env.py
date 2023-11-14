import os


def load_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"{name} is not set")
    return value


VAULT_ADDR = load_env_var("VAULT_ADDR")
VAULT_TOKEN = load_env_var("VAULT_TOKEN")
