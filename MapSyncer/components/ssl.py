import os
import subprocess


def ssl_create():
    directory_path = os.path.expanduser(f'~/.config/mapilio/configs/MapSyncer/')

    cert_file = f'{directory_path}cert.pem'
    key_file = f'{directory_path}key.pem'

    openssl_command = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-nodes',
        '-out', cert_file,
        '-keyout', key_file,
        '-days', '365', '-subj', '/C=GB/ST=England/L=Andover/O=Mapilio/CN=127.0.0.1', '-batch'
    ]

    if not (os.path.exists(cert_file) and os.path.exists(key_file)):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        subprocess.run(openssl_command)
    else:
        print("Cert.pem and key.pem already exist.")
