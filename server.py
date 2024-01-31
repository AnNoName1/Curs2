from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import mysql.connector
from datetime import datetime,date

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def authenticate_user(self, username, password):
        # For simplicity, let's assume there are two hardcoded users: admin and user
        users = {
            'admin': {'password': 'adminpass', 'role': 'admin'},
            'user': {'password': 'userpass', 'role': 'user'},
        }

        if username in users and users[username]['password'] == password:
            print("login successfull")
            return {'result': {'role': users[username]['role']}}
        else:
            print("login failed")
            return {'error': 'Invalid username or password'}

    def execute_procedure(self, procedure_name, input_values):
        try:
            
            logging.basicConfig(level=logging.DEBUG)
            # Replace the connection details with your MySQL database information
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='1234',
                database='manufactorum'
            )

            cursor = connection.cursor()
            logging.debug("Input values: %s",input_values)
            # Get the argument count for the specified procedure
            cursor.execute("SELECT COUNT(*) FROM information_schema.parameters WHERE specific_name = %s", (procedure_name,))
            argument_count = cursor.fetchone()[0]
            if(input_values!=''):
                input_values_tuple = tuple(input_values.split(','))
            else:
                input_values_tuple = ()
            # Check if the number of provided arguments matches the expected count
            if len(input_values_tuple) != argument_count:
                return {"error": f"Invalid number of arguments for {procedure_name}"}

            # Build the CALL statement dynamically
            call_statement = f"CALL manufactorum.{procedure_name}("
            call_statement += ', '.join(['%s' for _ in range(argument_count)])
            call_statement += ");"
            print(call_statement,input_values_tuple)
            # Execute the procedure with the provided input values
            cursor.execute(call_statement, input_values_tuple)
            column_names = [description[0] for description in cursor.description]
            rows = list(cursor.fetchall())

            cursor.close()
            connection.close()

            # Send only column names in the first row
            result_data = {"result": [column_names] + rows}
            logging.debug("Result Data: %s", result_data)
            return result_data

        except mysql.connector.Error as e:
            error_message = f"MySQL Error {e.errno}: {e.msg}"
            logging.error("Error executing procedure: %s", error_message)
            return {"error": error_message}

        except Exception as e:
            logging.error("Unexpected error executing procedure: %s", str(e))
            return {"error": "Unexpected error executing procedure"}


    def execute_select(self, select_statement):
        try:
            # Replace the connection details with your MySQL database information
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='1234',
                database='manufactorum'
            )
            
            
            cursor = connection.cursor()
            # Validate that the statement is a SELECT query
            if not select_statement.strip().lower().startswith('select'):
                raise ValueError("Invalid query. Only SELECT statements are allowed.")

            # Execute the SELECT statement
            cursor.execute(select_statement)
            column_names = [description[0] for description in cursor.description]
            rows = list(cursor.fetchall())

            cursor.close()
            connection.close()

            # Send only column names in the first row
            return {"result": [column_names] + rows}

        except ValueError as ve:
            logging.error("Invalid SELECT statement: %s", str(ve))
            return {"error": str(ve)}

        except Exception as e:
            logging.error("Error executing SELECT statement: %s", str(e))
            return {"error": "Error executing SELECT statement"}

        finally:
            cursor.close()
            connection.close()
    # Add a new method to execute functions with parameters
    def execute_function(self, function_name, input_values):
        try:
            logging.basicConfig(level=logging.DEBUG)
            # Replace the connection details with your MySQL database information
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='1234',
                database='manufactorum'
            )

            cursor = connection.cursor()

            # Get the argument count for the specified function
            cursor.execute("SELECT COUNT(*) FROM information_schema.parameters WHERE specific_name = %s", (function_name,))
            argument_count = cursor.fetchone()[0]-1
            if input_values != '':
                input_values_tuple = tuple(input_values.split(','))
            else:
                input_values_tuple = ()

            print(argument_count,input_values_tuple)
            # Check if the number of provided arguments matches the expected count
            if len(input_values_tuple) != argument_count:
                return {"error": f"Invalid number of arguments for {function_name}"}

            # Build the CALL statement dynamically for functions
            call_statement = f"SELECT manufactorum.{function_name}("
            call_statement += ', '.join(['%s' for _ in range(argument_count)])
            call_statement += ");"
            print(call_statement, input_values_tuple)

            # Execute the function with the provided input values
            cursor.execute(call_statement, input_values_tuple)
            column_names = ["result"]
            rows = list(cursor.fetchall())

            cursor.close()
            connection.close()

            # Send only column names in the first row
            result_data = {"result": [column_names] + rows}
            logging.debug("Result Data: %s", result_data)
            return result_data

        except mysql.connector.Error as e:
            error_message = f"MySQL Error {e.errno}: {e.msg}"
            logging.error("Error executing function: %s", error_message)
            return {"error": error_message}

        except Exception as e:
            logging.error("Unexpected error executing function: %s", str(e))
            return {"error": "Unexpected error executing function"}


    def get_procedure_names(self):
        try:
            # Replace the connection details with your MySQL database information
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='1234',
                database='manufactorum'
            )

            cursor = connection.cursor()

            # Fetch all procedure names
            cursor.execute("SHOW PROCEDURE STATUS WHERE Db = 'manufactorum';")
            procedure_names = [row[1] for row in cursor.fetchall()]

            cursor.close()
            connection.close()
            print(procedure_names)
            return {"procedureNames": procedure_names}

        except Exception as e:
            logging.error("Error fetching procedure names: %s", str(e))
            return {"error": "Error fetching procedure names"}
    def get_function_names(self):
        try:
            # Replace the connection details with your MySQL database information
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='1234',
                database='manufactorum'
            )

            cursor = connection.cursor()

            # Fetch all function names
            cursor.execute("SHOW FUNCTION STATUS WHERE Db = 'manufactorum';")
            function_names = [row[1] for row in cursor.fetchall()]

            cursor.close()
            connection.close()

            print(function_names)
            return {"functionNames": function_names}

        except Exception as e:
            logging.error("Error fetching function names: %s", str(e))
            return {"error": "Error fetching function names"}
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            with open(self.path[1:], 'rb') as file:
                content = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, 'File Not Found: {}'.format(self.path))
        except Exception as e:
            self.send_error(500, 'Internal Server Error: {}'.format(str(e)))
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        

        try:
            data = json.loads(post_data)
            action = data.get('action', '')

            if action == 'login':
                username = data.get('username', '')
                password = data.get('password', '')
                result = self.authenticate_user(username, password)

            elif action == 'executeProcedure':
                procedure_name = data.get('procedureName', '')
                input_value = data.get('inputValue', '')
                result = self.execute_procedure(procedure_name, input_value)
            elif action == 'executeFunction':
                function_name = data.get('functionName', '')
                input_value = data.get('inputValues', '')
                result = self.execute_function(function_name, input_value)
            elif action == 'executeSelect':
                select_statement = data.get('selectStatement', '')
                result = self.execute_select(select_statement)
            elif action == 'getProcedureNames':
                result = self.get_procedure_names()
            elif action == 'getFunctionNames':
                result = self.get_function_names()
            else:
                result = {"error": "Invalid action"}

        except Exception as e:
            logging.error("Error processing request: %s", str(e))
            result = {"error": "Internal Server Error"}

        self._set_response()
        self.wfile.write(json.dumps({"result": result}, cls=DateTimeEncoder).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
def run(server_class=HTTPServer, handler_class=S, port=8080):

    logging.basicConfig(level=logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd on port %s...\n', port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
