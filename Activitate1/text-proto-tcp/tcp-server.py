import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024

class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    # adaugare in dictionar
    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return f"{key} added"

    #citire in dictionar
    def get(self, key):
        with self.lock:
            return self.data.get(key, "Key not found")
    #stergere in dictionar
    def remove(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return f"{key} removed"
            return "Key not found"

    def list_items(self):
        with self.lock:
            if not self.data:
                return "DATA|"
            return "DATA|" + ','.join([f'{k}={v}' for k, v in self.data.items()])

    def count(self):
        with self.lock:
            return f"DATA {len(self.data)}"

    def clear(self):
        with self.lock:
            self.data.clear()
        return "all data deleted"

    def update(self, key, value):
        with self.lock:
            if key in self.data:
                self.data[key] = value
                return "Data updated"
            return "ERROR invalid key"

    def pop(self, key):
        with self.lock:
            if key in self.data:
                value = self.data.pop(key)
                return f"Data {value}"
            return "ERROR invalid key"

state = State()

def process_command(command):
    parts = command.strip().split()
    if not parts:
        return "ERROR unknown command"

    cmd = parts[0].upper()

    if cmd == "ADD" and len(parts) >= 3:
        key = parts[1]
        value = ' '.join(parts[2:])
        return state.add(key, value)
    elif cmd == "GET" and len(parts) == 2:
        key = parts[1]
        val = state.get(key)
        if val == "Key not found":
            return "ERROR invalid key"
        return f"DATA {val}"
    elif cmd == "REMOVE" and len(parts) == 2:
        key = parts[1]
        val = state.remove(key)
        if val == "Key not found":
            return "ERROR invalid key"
        return "OK value deleted"
    elif cmd == "LIST" and len(parts) == 1:
        return state.list_items()
    elif cmd == "COUNT" and len(parts) == 1:
        return state.count()
    elif cmd == "CLEAR" and len(parts) == 1:
        return state.clear()
    elif cmd == "UPDATE" and len(parts) >= 3:
        key = parts[1]
        value = ' '.join(parts[2:])
        return state.update(key, value)
    elif cmd == "POP" and len(parts) == 2:
        key = parts[1]
        return state.pop(key)
    elif cmd == "QUIT" and len(parts) == 1:
        return "QUIT"
    else:
        return "ERROR unknown command"

def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode('utf-8').strip()
                response = process_command(command)

                if response == "QUIT":
                    client_socket.sendall(f"{len('Bye!')} Bye!".encode('utf-8'))
                    break

                response_data = f"{len(response)} {response}".encode('utf-8')
                client_socket.sendall(response_data)

            except Exception as e:
                client_socket.sendall(f"Error: {str(e)}".encode('utf-8'))
                break

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[SERVER] Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()