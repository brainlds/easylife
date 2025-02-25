import socket

def test_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 设置超时时间
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"Port {port} is open on {ip}")
        else:
            print(f"Port {port} is closed or filtered on {ip}")
        sock.close()
    except Exception as e:
        print(f"Error: {e}")

test_port("139.196.160.165", 5000)