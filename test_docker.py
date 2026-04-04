#!/usr/bin/env python3
import socket, json, os

sock_path = '/var/run/docker.sock'
print(f'Testing Docker socket at: {sock_path}')
print(f'Socket exists: {os.path.exists(sock_path)}')

try:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(sock_path)
    print('Connected to socket successfully')

    req = 'GET /containers/json?all=true HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n'
    sock.sendall(req.encode())

    response = b''
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        response += chunk

    response_str = response.decode('utf-8', errors='ignore')
    if '\r\n\r\n' in response_str:
        headers, body = response_str.split('\r\n\r\n', 1)
        data = json.loads(body)
        print(f'Received {len(data)} containers')
        for c in data[:5]:
            name = c.get('Names', ['?'])[0]
            state = c.get('State', '?')
            print(f'  - {name}: {state}')
    else:
        print('Invalid response format')
        print(f'Response length: {len(response_str)}')

    sock.close()
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
