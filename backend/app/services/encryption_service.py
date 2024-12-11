from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
import json
from app.core.config import settings

class EncryptionService:
    def __init__(self):
        self.master_key = base64.b64decode(settings.ENCRYPTION_MASTER_KEY)
        self.fernet = Fernet(self.master_key)
        
    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt sensitive data using Fernet (symmetric encryption).
        Used for data that needs to be decrypted later.
        """
        json_data = json.dumps(data)
        encrypted_data = self.fernet.encrypt(json_data.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt sensitive data using Fernet.
        """
        try:
            decoded_data = base64.b64decode(encrypted_data)
            decrypted_data = self.fernet.decrypt(decoded_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")

    def hash_sensitive_data(self, data: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """
        One-way hash sensitive data using PBKDF2.
        Used for data that doesn't need to be decrypted (e.g., passwords).
        """
        if not salt:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = base64.b64encode(kdf.derive(data.encode())).decode()
        return {
            "hash": key,
            "salt": base64.b64encode(salt).decode()
        }

    def verify_hashed_data(self, data: str, stored_hash: str, salt: str) -> bool:
        """
        Verify hashed data against stored hash.
        """
        salt_bytes = base64.b64decode(salt)
        new_hash = self.hash_sensitive_data(data, salt_bytes)
        return new_hash["hash"] == stored_hash

    def generate_key_pair(self) -> Dict[str, str]:
        """
        Generate RSA key pair for asymmetric encryption.
        Used for secure key exchange and digital signatures.
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            "private_key": private_pem.decode(),
            "public_key": public_pem.decode()
        }

    def asymmetric_encrypt(self, data: str, public_key_pem: str) -> str:
        """
        Encrypt data using RSA public key.
        Used for secure data exchange between parties.
        """
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        
        encrypted_data = public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(encrypted_data).decode()

    def asymmetric_decrypt(self, encrypted_data: str, private_key_pem: str) -> str:
        """
        Decrypt data using RSA private key.
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        decrypted_data = private_key.decrypt(
            base64.b64decode(encrypted_data),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted_data.decode()

    def encrypt_file(self, file_path: str, output_path: str) -> None:
        """
        Encrypt a file using AES-256-GCM.
        Used for secure file storage.
        """
        key = os.urandom(32)
        iv = os.urandom(12)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
        )
        
        encryptor = cipher.encryptor()
        
        with open(file_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            # Write IV at the beginning of the file
            f_out.write(iv)
            
            # Encrypt and write the file content
            while True:
                chunk = f_in.read(64 * 1024)
                if not chunk:
                    break
                f_out.write(encryptor.update(chunk))
            
            # Write the tag at the end
            f_out.write(encryptor.finalize())
            f_out.write(encryptor.tag)
        
        # Return the key for safe storage
        return base64.b64encode(key).decode()

    def decrypt_file(self, encrypted_file: str, output_path: str, key: str) -> None:
        """
        Decrypt a file using AES-256-GCM.
        """
        key_bytes = base64.b64decode(key)
        
        with open(encrypted_file, 'rb') as f_in:
            # Read the IV from the beginning of the file
            iv = f_in.read(12)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key_bytes),
                modes.GCM(iv),
            )
            
            decryptor = cipher.decryptor()
            
            # Get file size and calculate tag position
            f_in.seek(0, 2)
            file_size = f_in.tell()
            tag_position = file_size - 16
            
            # Read encrypted data
            f_in.seek(12)
            encrypted_data = f_in.read(tag_position - 12)
            
            # Read tag
            tag = f_in.read(16)
            
            # Set tag
            decryptor.authenticate_additional_data(b"")
            
            # Decrypt and write to output file
            with open(output_path, 'wb') as f_out:
                decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize_with_tag(tag)
                f_out.write(decrypted_data)

    def secure_random_string(self, length: int = 32) -> str:
        """
        Generate a secure random string.
        Used for generating secure tokens, keys, etc.
        """
        return base64.b64encode(os.urandom(length)).decode()[:length]
