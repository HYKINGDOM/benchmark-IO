#!/usr/bin/env python3
import socket, json

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect('/var/run/docker.sock')
sock.sendall(b'GET /containers/json?all=true HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')

response = b''
while True:
    chunk = sock.recv(8192)
    if not chunk:
        break
    response += chunk

resp_str = response.decode()
print(f'Full response length: {len(resp_str)}')
if '\r\n\r\n' in resp_str:
    headers, body = resp_str.split('\r\n\r\n', 1)
    print(f'Headers:\n{headers[:200]}')
    print(f'\nBody type: {type(body)}')
    print(f'Body starts with: {repr(body[:100])}')
    print(f'Body length: {len(body)}')

    # Try to parse as JSON array
    try:
        data = json.loads(body)
        print(f'\nParsed as JSON: type={type(data).__name__}')
        if isinstance(data, list):
            print(f'List length: {len(data)}')
            if data and isinstance(data[0], dict):
                print(f'First item keys: {list(data[0].keys())}')
                print(f'First item: {json.dumps(data[0], indent=2)[:300]}')
        else:
            print(f'Value: {str(data)[:200]}')
    except json.JSONDecodeError as e:
        print(f'\nJSON parse error: {e}')
        # Show raw body for debugging
        print(f'Raw body (first 500 chars):\n{body[:500]}')

sock.close()
