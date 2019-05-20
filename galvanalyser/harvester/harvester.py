import sys
import json
import psutil
import psycopg2


def has_handle(fpath):
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if fpath == item.path:
                    return True
        except Exception:
            pass

    return False


def load_config(config_file_path):
    with open(config_file_path, "r") as json_file:
        return json.load(json_file)


def write_config_template(config_template_path):
    template = {
        "database_username": "harvester_user",
        "database_password": "password",
        "database_host": "127.0.0.1",
        "database_port": 5432,
        "database_name": "galvanalyser",
        "machine_id": "my_machine_01",
    }
    with open(config_template_path, "w") as json_file:
        json.dump(template, json_file, indent=4)


def main(argv):
    config = load_config("harvester-config.json")
    try:
        conn = psycopg2.connect(
            host=config.database_host,
            port=config.database_port,
            database=config.database_name,
            user=config.database_username,
            password=config.database_password,
        )
        conn.autocommit = True

    finally:
        conn.close()


if __name__ == "__main__":
    main(sys.argv)
