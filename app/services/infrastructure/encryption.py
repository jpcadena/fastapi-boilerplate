"""
A module for encryption in the app.services.infrastructure package.
"""

import base64
import logging
from os import urandom
from typing import Any

import aiofiles
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends.openssl.backend import Backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    RSAPublicKey,
)
from cryptography.hazmat.primitives.asymmetric.types import (
    PrivateKeyTypes,
    PublicKeyTypes,
)
from cryptography.hazmat.primitives.ciphers import (
    AEADDecryptionContext,
    AEADEncryptionContext,
    Cipher,
    algorithms,
    modes,
)
from pydantic import FilePath, PositiveInt

from app.config.config import init_setting, setting

logger: logging.Logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Encryption service implementation for the E2EE backend.
    """

    def __init__(self, backend: Backend = default_backend()) -> None:
        self._backend: Backend = backend
        self._iterations: PositiveInt = init_setting.ITERATIONS

    def _load_public_key(self, public_key_pem: str) -> PublicKeyTypes:
        """
        Load a public key from a PEM-formatted string.
        :param public_key_pem: The public key in PEM format.
        :type public_key_pem: str
        :return: The loaded public key.
        :rtype: PublicKeyTypes
        """
        try:
            return serialization.load_pem_public_key(
                public_key_pem.encode(), backend=self._backend
            )
        except Exception as e:
            logger.error(f"Error loading public key: {e}")
            raise

    def _load_private_key(self, private_key_pem: str) -> PrivateKeyTypes:
        """
        Load a private key from a PEM-formatted string.
        :param private_key_pem: The private key in PEM format.
        :type private_key_pem: str
        :return: The loaded private key.
        :rtype: PrivateKeyTypes
        """
        try:
            return serialization.load_pem_private_key(
                private_key_pem.encode(), None, backend=self._backend
            )
        except Exception as e:
            logger.error(f"Error loading private key: {e}")
            raise

    @staticmethod
    def _get_padding_scheme() -> padding.OAEP:
        """
        Get the padding scheme used for RSA encryption and decryption.
        :return: The padding scheme.
        :rtype: padding.OAEP
        """
        return padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )

    def encrypt_aes_key_with_rsa(
        self, public_key_pem: str, aes_key: bytes
    ) -> bytes:
        """
        Encrypt an AES key using a public RSA key.
        :param public_key_pem: The public RSA key in PEM format.
        :type public_key_pem: str
        :param aes_key: The AES key to encrypt.
        :type aes_key: bytes
        :return: The encrypted AES key.
        :rtype: bytes
        """
        public_key: PublicKeyTypes = self._load_public_key(public_key_pem)
        try:
            return public_key.encrypt(  # type: ignore
                aes_key, self._get_padding_scheme()
            )
        except Exception as e:
            logger.error(f"Error encrypting AES key: {e}")
            raise

    def decrypt_aes_key_with_rsa(
        self, private_key_pem: str, encrypted_aes_key: bytes
    ) -> bytes:
        """
        Decrypt an AES key using a private RSA key.
        :param private_key_pem: The private RSA key in PEM format.
        :type private_key_pem: str
        :param encrypted_aes_key: The encrypted AES key.
        :type encrypted_aes_key: bytes
        :return: The decrypted AES key.
        :rtype: bytes
        """
        private_key: PrivateKeyTypes = self._load_private_key(private_key_pem)
        try:
            return private_key.decrypt(  # type: ignore
                encrypted_aes_key, self._get_padding_scheme()
            )
        except Exception as e:
            logger.error(f"Error decrypting AES key: {e}")
            raise

    def encrypt_data(self, data: str, public_key_pem: str) -> dict[str, bytes]:
        """
        Encrypt data with a public key (PEM).
        :param data: The data to encrypt
        :type data: str
        :param public_key_pem: The public key to encrypt
        :type public_key_pem: str
        :return: The encrypted data
        :rtype: dict[str, bytes]
        """
        aes_key: bytes = urandom(init_setting.KEY_BYTES_LENGTH)
        encrypted_aes_key: bytes = self.encrypt_aes_key_with_rsa(
            public_key_pem, aes_key
        )
        iv: bytes = urandom(init_setting.IV_BYTES)
        cipher: Cipher[modes.GCM] = Cipher(
            algorithms.AES(aes_key), modes.GCM(iv), backend=self._backend
        )
        encryptor: AEADEncryptionContext = cipher.encryptor()
        encrypted_data_bytes: bytes = (
            encryptor.update(data.encode()) + encryptor.finalize()
        )
        return {
            "encrypted_data": encrypted_data_bytes,
            "encrypted_aes_key": encrypted_aes_key,
            "iv": iv,
            "tag": encryptor.tag,
        }

    def decrypt_data(
        self,
        encrypted_data: bytes,
        private_key_pem: str,
        encrypted_aes_key: bytes,
        iv: bytes,
        tag: bytes,
    ) -> str:
        """
        Decrypt data with a password.
        :param encrypted_data: The encrypted data
        :type encrypted_data: bytes
        :param private_key_pem: The private key
        :type private_key_pem: str
        :param encrypted_aes_key: The encrypted AES key
        :type encrypted_aes_key: bytes
        :param iv: The initialization vector
        :type iv: bytes
        :param tag: The decryption tag
        :type tag: bytes
        :return: The decrypted data
        :rtype: str
        """
        aes_key: bytes = self.decrypt_aes_key_with_rsa(
            private_key_pem, encrypted_aes_key
        )
        cipher: Cipher[modes.GCM] = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, tag),
            backend=self._backend,
        )
        decryptor: AEADDecryptionContext = cipher.decryptor()
        decrypted_data_bytes: bytes = (
            decryptor.update(encrypted_data) + decryptor.finalize()
        )
        return decrypted_data_bytes.decode()

    def generate_key_pair(self) -> tuple[str, str]:
        """
        Generate a pair of RSA keys.
        :return: Tuple containing public and private RSA keys in PEM format.
        :rtype: tuple[str, str]
        """
        # Used ONLY ONCE to generate the local keys on disk
        private_key: RSAPrivateKey = rsa.generate_private_key(
            public_exponent=init_setting.PUBLIC_EXPONENT,
            key_size=init_setting.RSA_KEY_BITS,
            backend=self._backend,
        )
        public_key: RSAPublicKey = private_key.public_key()
        private_pem: str = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode(init_setting.ENCODING)
        public_pem: str = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode(init_setting.ENCODING)
        return public_pem, private_pem

    def save_key_pair(
        self, public_key_path: str, private_key_path: str
    ) -> None:
        """
        Save RSA keys to files.
        :param public_key_path: Path to save the public key.
        :type public_key_path: str
        :param private_key_path: Path to save the private key.
        :type private_key_path: str
        :return: None
        :rtype: NoneType
        """
        public_pem, private_pem = self.generate_key_pair()
        with open(public_key_path, 'w') as public_file:
            public_file.write(public_pem)
        with open(private_key_path, 'w') as private_file:
            private_file.write(private_pem)
        print("Public and Private keys have been generated and saved.")

    @staticmethod
    def serialize_encrypted_info(encrypted_info: dict[str, bytes]) -> str:
        """
        Serialize the encrypted information
        :param encrypted_info: The encrypted information
        :type encrypted_info: dict[str, bytes]
        :return: The combined data
        :rtype: str
        """
        combined: bytes = (
            encrypted_info["encrypted_aes_key"]
            + encrypted_info["iv"]
            + encrypted_info["encrypted_data"]
            + encrypted_info["tag"]
        )
        return base64.b64encode(combined).decode()

    @staticmethod
    def deserialize_encrypted_info(serialized_info: str) -> dict[str, bytes]:
        """
        Deserialize the encrypted information
        :param serialized_info: The serialized info
        :type serialized_info: str
        :return: The dictionary with encrypted data as bytes
        :rtype: dict[str, bytes]
        """
        decoded: bytes = base64.b64decode(serialized_info)
        rsa_key_size_bytes: PositiveInt = init_setting.RSA_KEY_BITS // 8
        iv_size_bytes: PositiveInt = init_setting.IV_BYTES
        tag_size_bytes: PositiveInt = init_setting.SALT_BYTES
        encrypted_aes_key: bytes = decoded[:rsa_key_size_bytes]
        iv: bytes = decoded[
            rsa_key_size_bytes : rsa_key_size_bytes + iv_size_bytes
        ]
        tag: bytes = decoded[-tag_size_bytes:]
        encrypted_data: bytes = decoded[
            rsa_key_size_bytes + iv_size_bytes : -tag_size_bytes
        ]
        return {
            "encrypted_aes_key": encrypted_aes_key,
            "iv": iv,
            "encrypted_data": encrypted_data,
            "tag": tag,
        }

    async def encrypt_and_serialize(
        self,
        data: Any,
        key_path: FilePath = setting.PUBLIC_KEY_PATH,
    ) -> tuple[bytes, str]:
        """
        Encrypts and serializes the given data
        :param data: The data to encrypt
        :type data: Any
        :param key_path: The path for the key
        :type key_path: FilePath
        :return: The encrypted data and the serialized data
        :rtype:
        """
        async with aiofiles.open(key_path, mode="r") as key_file:
            public_key: str = await key_file.read()
        encrypted_info: dict[str, bytes] = self.encrypt_data(
            str(data), public_key
        )
        serialized_info: str = self.serialize_encrypted_info(encrypted_info)
        return encrypted_info["encrypted_data"], serialized_info


def get_encryption_service() -> EncryptionService:
    """
    Get the encryption service instance
    :return: The encryption service instance
    :rtype: EncryptionService
    """
    return EncryptionService()


encryption_service: EncryptionService = get_encryption_service()
encryption_service.save_key_pair("public_key.pem", "private_key.pem")
