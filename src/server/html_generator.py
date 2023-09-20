import sqlite3

from flask import url_for

from src.server.utilities import DBAgent


class HTMLGenerator:
    def __init__(self, dbagent: DBAgent):
        self.dbagent = dbagent

    def get_table_data_list(self) -> dict:
        conn = sqlite3.connect(self.dbagent.get_db_path())
        c = conn.cursor()

        # Query to get all table names in the database
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()

        # Create a dictionary to store data from all tables
        all_data = {}

        # Loop through all tables and fetch data
        for table in tables:
            table_name = table[0]
            if not (table_name == "sqlite_sequence") and not (table_name == "Reviews"):
                c.execute(f"SELECT * FROM {table_name}")
                all_data[table_name] = c.fetchall()

        # Close connection
        conn.close()

        return all_data

    def get_column_names_for_all_tables(self) -> dict:
        conn = sqlite3.connect(self.dbagent.get_db_path())

        column_names_dict = {}
        cursor = conn.cursor()

        # First, let's get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table_name in tables:
            table_name = table_name[0]  # The query returns a tuple, so we unpack it
            print("table_name: " + table_name)
            cursor.execute(f"PRAGMA table_info({table_name});")

            # This will return a list of tuples with various information about each column.
            # The second element in each tuple is the column's name.
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]

            column_names_dict[table_name] = column_names

        column_names_dict.pop('sqlite_sequence', None)  # Remove sqlite_sequence; do nothing if the key does not exist
        column_names_dict.pop('Reviews', None)  # Remove Reviews; do nothing if the key does not exist

        return column_names_dict

    def generate_table_html(self, table_data_list) -> str:
        column_names_dict = self.get_column_names_for_all_tables()
        html_output = ""
        html_output += "<link rel=\"stylesheet\" type=\"text/css\" href=\"{{ url_for('static', filename='style.css') }}\""
        html_output += "<script src=\"https://code.jquery.com/jquery-3.6.0.min.js\"></script>"
        html_output += "<script src=\"{{ url_for('static', filename='scripts.js') }}\" ></script>"

        for table_name, table_data in table_data_list.items():
            html_output += f"<h2>{table_name}</h2>\n"

            create_url = url_for("create", table_name=table_name)

            html_output += f"<td>"
            html_output += f'<form action="{create_url}" method="post" class="form-inline" style="display: inline-block;">'
            html_output += f'<button type="submit">Create</button>'
            html_output += '</form>'

            html_output += "<table border='1'>\n"

            column_names = column_names_dict.get(table_name, [])

            if table_data:
                html_output += "<tr>\n"

                for column_name in column_names:
                    html_output += f"<th>{column_name}</th>\n"

                html_output += "<th>Actions</th>\n"
                html_output += "</tr>\n"

                for row in table_data:
                    html_output += "<tr>\n"

                    for cell in row:
                        html_output += f"<td>{cell}</td>\n"
                    try:
                        id_value = int(row[0])
                    except:
                        continue

                    # Generate URLs
                    update_url = url_for("update", table_name=table_name, object_id=id_value)
                    delete_url = url_for("delete", table_name=table_name, column_name=column_names[0],
                                         object_id=id_value)

                    # Adding buttons next to each entry

                    html_output += f"<td>"
                    html_output += f'<form action="{update_url}" method="post" class="form-inline" style="display: inline-block;">'
                    html_output += f'<button type="submit">Update</button>'
                    html_output += '</form>'

                    html_output += f'<form action="{delete_url}" method="post" class="form-inline" style="display: inline-block;">'
                    html_output += f'<button type="submit">Delete</button>'
                    html_output += '</form>'
                    html_output += "</td>\n"

                    html_output += "</tr>\n"

            html_output += "</table>\n\n"

        return html_output