#   How to run:
#   1. Ensure python is installed:      python --version
#   2. Start virtual environment:       python3 -m venv venv
#   3. Activate virtual environment:    .\venv\Scripts\activate
#   4. Install dependencies:            pip install -r requirements.txt
#   5. Run server:                      python3 main.py
#
#   How to test server:
#   1. Ensure pytest is installed:      pip install pytest pytest-cov requests
#   2. Run pytest with test_main.py:
#      -> pytest test_main.py --cov=main --cov-report=term-missing

# PROVIDED CODE #
from http.server import BaseHTTPRequestHandler, HTTPServer
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from urllib.parse import urlparse, parse_qs
import base64
import json
import jwt
import datetime

# --- My Code ---
# Library for SQLite
import sqlite3
# Importing deserialization for later
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# Creating database if not already created
conn = sqlite3.connect("totally_not_my_privateKeys.db")
# Creating a cursor to execute SQLite functions
cursor = conn.cursor()

# Table Schema provided by Canvas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS keys(
        kid INTEGER PRIMARY KEY AUTOINCREMENT,
        key BLOB NOT NULL,
        exp INTEGER NOT NULL
    )
""")
# Saving the changes and closing the connection
# come later to reduce reopening and reclosing
# --- End of my code ---

hostName = "localhost"
serverPort = 8080

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
expired_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)
expired_pem = expired_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

numbers = private_key.private_numbers()

# --- My Code ---
timePlusOneHour = int((datetime.datetime.utcnow()
                       + datetime.timedelta(hours=1)).timestamp())
timeMinusOneHour = int((datetime.datetime.utcnow()
                        - datetime.timedelta(hours=1)).timestamp())

# Clearing old keys to keep table from growing exponentially
cursor.execute("DELETE FROM keys")

# Using SQLite INSERT command to add entries
cursor.execute("INSERT INTO keys (key, exp) VALUES (?, ?)",
               # This is the serialized key using the pem above
               (pem.decode('utf-8'),
                # This is the time now + 1 hour = expiry time
                timePlusOneHour))

# Using SQLITE INSERT again for same reason
cursor.execute("INSERT INTO keys (key, exp) VALUES (?, ?)",
               # This time using the expired_pem from above for expired key
               (expired_pem.decode('utf-8'),
                # Rather than have time + 1 hour = expiry,
                # we have time - 1 = expired
                timeMinusOneHour))

conn.commit()       # Saving changes
conn.close()        # Closing connection
# --- End of my code ---


def int_to_base64(value):
    """Convert an integer to a Base64URL-encoded string"""
    value_hex = format(value, 'x')
    # Ensure even length
    if len(value_hex) % 2 == 1:
        value_hex = '0' + value_hex
    value_bytes = bytes.fromhex(value_hex)
    encoded = base64.urlsafe_b64encode(value_bytes).rstrip(b'=')
    return encoded.decode('utf-8')


class MyServer(BaseHTTPRequestHandler):
    def do_PUT(self):
        self.send_response(405)
        self.end_headers()
        return

    def do_PATCH(self):
        self.send_response(405)
        self.end_headers()
        return

    def do_DELETE(self):
        self.send_response(405)
        self.end_headers()
        return

    def do_HEAD(self):
        self.send_response(405)
        self.end_headers()
        return

    def do_POST(self):
        # --- My Code ---
        # Handling request body
        content_length = int(self.headers.get('Content-Length', 0))
        _ = self.rfile.read(content_length)

        # Parsing path
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        if parsed_path.path == "/auth":
            # Opening our connection again
            conn = sqlite3.connect("totally_not_my_privateKeys.db")
            # Getting our executor
            cursor = conn.cursor()
            # Making a variable to make code cleaner
            timeNow = int(datetime.datetime.utcnow().timestamp())

            if 'expired' in params:
                # Query for expired key
                cursor.execute("SELECT kid, key FROM keys WHERE exp <= ? LIMIT 1", (timeNow,))
            else:
                # Query for valid key
                cursor.execute("SELECT kid, key FROM keys WHERE exp > ? LIMIT 1", (timeNow,))

            # Fetch for result with error handling if nothing is found
            row = cursor.fetchone()
            conn.close()

            if row is None:
                self.send_response(404)
                self.end_headers()
                return

            # Deserialize the key from startup
            kid = row[0]
            key_pem = row[1].encode('utf-8')
            private_key = load_pem_private_key(key_pem, password=None)

            # Build JWT from database
            token_payload = {
                "user": "username",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }

            # Checking if expired
            if 'expired' in params:
                token_payload["exp"] = datetime.datetime.utcnow() - datetime.timedelta(hours=1)

            encoded_jwt = jwt.encode(token_payload, private_key, algorithm="RS256", headers={"kid": str(kid)})

            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(encoded_jwt, "utf-8"))
            return

        self.send_response(405)
        self.end_headers()
        return
        # --- End of my code ---

    def do_GET(self):
        # --- My Code ---
        if self.path == "/.well-known/jwks.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            # Opening our connection again
            conn = sqlite3.connect("totally_not_my_privateKeys.db")
            # Getting our executor
            cursor = conn.cursor()
            # Making a variable to make code cleaner
            timeNow = int(datetime.datetime.utcnow().timestamp())

            cursor.execute("SELECT kid, key FROM keys WHERE exp > ?", (timeNow,))

            rows = cursor.fetchall()    # Querying all
            conn.close()                # Closing connection

            # Deserializing to read and build keys
            key_list = []
            for row in rows:
                kid = row[0]
                key_pem = row[1].encode('utf-8')
                private_key = load_pem_private_key(key_pem, password=None)
                pub_numbers = private_key.private_numbers().public_numbers
                key_list.append({
                    "alg": "RS256",
                    "kty": "RSA",
                    "use": "sig",
                    "kid": str(kid),
                    "n": int_to_base64(pub_numbers.n),
                    "e": int_to_base64(pub_numbers.e)
                })

            keys = {"keys": key_list}
            self.wfile.write(bytes(json.dumps(keys), "utf-8"))
            return

        self.send_response(405)
        self.end_headers()
        return
        # --- End of my code ---


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
# PROVIDED CODE #
