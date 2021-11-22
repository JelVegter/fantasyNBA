from typing import List
import psycopg2
import os
import pandas as pd


# conn = psycopg2.connect(
#     database="postgres",
#     user="user",
#     password="pass",
#     port=5432,
#     host="localhost",
# )
#
# command = """
#         CREATE TABLE schedule (
#             Test1 SERIAL PRIMARY KEY,
#             Test2 VARCHAR(255) NOT NULL
#         )
#         """
#
# cur = conn.cursor()
# cur.execute(command)
# cur.close()
# conn.commit()
# print("success")


def create_tables():
    """create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE vendors (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE parts (
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
                )
        """,
        """
        CREATE TABLE part_drawings (
                part_id INTEGER PRIMARY KEY,
                file_extension VARCHAR(5) NOT NULL,
                drawing_data BYTEA NOT NULL,
                FOREIGN KEY (part_id)
                REFERENCES parts (part_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE vendor_parts (
                vendor_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                PRIMARY KEY (vendor_id , part_id),
                FOREIGN KEY (vendor_id)
                    REFERENCES vendors (vendor_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (part_id)
                    REFERENCES parts (part_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
    )


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
        query = base_query + ",".join([col for col in cols_to_add]) + ")"
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
