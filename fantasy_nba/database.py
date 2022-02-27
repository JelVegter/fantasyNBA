import os
from typing import List

import psycopg2


class Connection:
    """servers: "postgres"""

    def __init__(
        self,
        database: str,
        server: str = "postgres",
    ):
        self.server = server
        self.database = database
        self.username = os.environ.get("USER")
        servers = {
            "postgres": "vstdsprd01.database.windows.net",
        }
        self.server_url = servers[server]
        params = {
            "database": "postgres",
            "user": "user",
            "password": "pass",
            "port": 5432,
            "host": "localhost",
        }
        self.cnxn = psycopg2.connect(**params)
        self.cursor = self.cnxn.cursor()

    def create_table(self, table_name: str, columns: List[tuple], schema: str = ""):
        """(col_name, data_type, null)"""
        data_types = {
            "int": "INT",
            "float": "DECIMAL(18,6)",
            "str": "VARCHAR(200)",
            "date": "DATE",
            "datetime": "DATETIME",
        }
        cols_to_add = []
        for column in columns:
            col_name, data_type, null = column
            cols_to_add.append(f"{col_name} {data_types[data_type]} {null}")
        base_query = f"CREATE TABLE IF NOT EXISTS {schema}{table_name} ("
        query = base_query + ",".join(cols_to_add) + ")"
        self.cursor.execute(query)
        self.cursor.close()
        self.cnxn.commit()

    def insert_in_table(self, table: str, nr_cols: int, data: List[tuple]):
        nr_cols_text = "?" + ",?" * (nr_cols - 1)
        row_count = 0
        for row in data:
            query = f"INSERT INTO {table} VALUES ({nr_cols_text})"
            self.cursor.execute(query, row)
            row_count += self.cursor.rowcount
        self.cnxn.commit()
        print("Rows inserted:", row_count)


def main():
    conn = Connection(server="postgres", database="postgres")
    conn.create_table(
        table_name="testing",
        columns=[
            ("test1", "int", "not null"),
            ("test2", "float", "not null"),
            ("test3", "str", "not null"),
            ("test4", "date", "not null"),
        ],
    )


if __name__ == "__main__":
    main()
