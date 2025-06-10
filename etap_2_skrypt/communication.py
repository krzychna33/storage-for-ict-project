import socket, struct, threading, pickle, os, time, datetime
from minio import Minio
from minio.error import S3Error
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from crypto_auth_utils import (
    generate_hmac, verify_hmac,
    generate_ecdh_key_pair, compute_shared_secret,
    derive_session_keys, hash
)
from database import get_key_for_satellite, init_db

CHUNK_SIZE   = 1024
SATELLITE_ID = "SAT-001"


# ───────── pomocnicze ─────────
def compare_files(f1, f2) -> bool:
    with open(f1, "rb") as a, open(f2, "rb") as b:
        while True:
            ba, bb = a.read(4096), b.read(4096)
            if ba != bb: return False
            if not ba:   return True                        # EOF

def send_msg(sock, obj):
    data = pickle.dumps(obj)
    sock.sendall(struct.pack(">I", len(data)))
    sock.sendall(data)

def recv_msg(sock):
    raw = recvall(sock, 4)
    if not raw: return None
    length = struct.unpack(">I", raw)[0]
    return pickle.loads(recvall(sock, length))

def recvall(sock, n):
    data = b""
    while len(data) < n:
        part = sock.recv(n - len(data))
        if not part: return None
        data += part
    return data


# ───────── upload do MinIO ─────────
def upload_to_minio(file_path: str) -> bool:
    client = Minio(
        "127.0.0.1:9000",        # dopasuj host/port
        access_key="uploader", # dopasuj do terraform.tfvars
        secret_key="uploader_secure_password123",
        secure=False
    )
    bucket = "raw-data"
    obj    = os.path.basename(file_path)

    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        client.fput_object(bucket, obj, file_path)
        print(f"Odebrany plik '{obj}' został wysłany do MinIO (bucket: {bucket}).")
        return True
    except S3Error as err:
        print(f"Nie udało się wysłać '{obj}' do MinIO: {err}")
        return False


# ───────── SERVER ─────────
def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 12345)); s.listen()
        conn, _ = s.accept()

        sat_id = conn.recv(1024).decode().strip()
        nonce  = os.urandom(16)
        conn.send(nonce)
        if not verify_hmac(sat_id, nonce, conn.recv(32)):
            conn.send(b"AUTH_FAILED"); return
        conn.send(b"AUTH_OK")

        priv, pub = generate_ecdh_key_pair()
        conn.send(pub.public_bytes_raw())
        peer_pub  = x25519.X25519PublicKey.from_public_bytes(conn.recv(32))

        chacha_key, _ = derive_session_keys(
            compute_shared_secret(priv, peer_pub)
        )
        cipher = ChaCha20Poly1305(chacha_key)

        with open("random_data.bin", "rb") as f:
            i = 0
            while (chunk := f.read(512 * 1024)):
                i += 1
                nonce_enc = os.urandom(12)
                enc       = cipher.encrypt(nonce_enc, chunk, None)
                send_msg(conn, (nonce_enc, enc, hash(enc)))
                print(f"{datetime.datetime.now()} ▶ Pakiet {i} ({len(chunk)} B)")
                time.sleep(2)
        send_msg(conn, (b"END", b"END", b"END"))


# ───────── CLIENT ─────────
def client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 12345))
        s.send(SATELLITE_ID.encode())

        nonce = s.recv(16)
        s.send(generate_hmac(nonce, get_key_for_satellite(SATELLITE_ID)))
        if s.recv(1024) != b"AUTH_OK": return

        priv, pub = generate_ecdh_key_pair()
        peer_pub  = x25519.X25519PublicKey.from_public_bytes(s.recv(32))
        s.send(pub.public_bytes_raw())

        chacha_key, _ = derive_session_keys(
            compute_shared_secret(priv, peer_pub)
        )
        cipher = ChaCha20Poly1305(chacha_key)

        with open("received_random_data.bin", "wb") as f:
            while True:
                msg = recv_msg(s)
                if msg is None: break
                nonce_enc, enc, sha = msg
                if nonce_enc == b"END": break
                if hash(enc) != sha:
                    send_msg(s, ("SHA_MISMATCH",)); continue
                f.write(cipher.decrypt(nonce_enc, enc, None))


# ───────── MAIN ─────────
if __name__ == "__main__":
    init_db()
    ts, tc = threading.Thread(target=server), threading.Thread(target=client)
    ts.start(); tc.start(); ts.join(); tc.join()

    src, dst = "random_data.bin", "received_random_data.bin"
    if os.path.exists(src) and os.path.exists(dst):
        if compare_files(src, dst):
            print("Pliki są identyczne – wysyłam odebrany do MinIO…")
            upload_to_minio(dst)
        else:
            print("Pliki się różnią – pomijam wysyłkę do MinIO.")
    else:
        print("Brakuje plików do porównania – brak uploadu.")
