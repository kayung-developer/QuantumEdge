import socket
import time
import os
import sys

def wait_for_postgres():
    """
    Waits for the PostgreSQL database to become available.
    Reads connection details from environment variables.
    """
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")

    if not host or not port:
        print("Error: POSTGRES_HOST and POSTGRES_PORT environment variables not set.", file=sys.stderr)
        sys.exit(1)

    print(f"Waiting for PostgreSQL at {host}:{port}...")
    
    while True:
        try:
            with socket.create_connection((host, int(port)), timeout=2):
                print("PostgreSQL is available!")
                break
        except (socket.timeout, ConnectionRefusedError):
            print("PostgreSQL not available yet, sleeping for 2 seconds...")
            time.sleep(2)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    wait_for_postgres()
