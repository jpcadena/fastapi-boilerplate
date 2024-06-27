"""
A module for encryption in the app.services.infrastructure package.
"""

import logging
from functools import lru_cache

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends.openssl.backend import Backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    RSAPublicKey,
)

from app.config.config import init_setting

logger: logging.Logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Encryption service implementation for the E2EE backend.
    """

    def __init__(self, backend: Backend = default_backend()) -> None:
        self._backend: Backend = backend
        self._padding_scheme = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
        self.__public_exponent = init_setting.PUBLIC_EXPONENT
        self.__rsa_key_bits = init_setting.RSA_KEY_BITS
        self.__encoding = init_setting.ENCODING

    def _generate_key_pair(self) -> tuple[str, str]:
        """
        Generate a pair of RSA keys.
        :return: Tuple containing public and private RSA keys in PEM format.
        :rtype: tuple[str, str]
        """
        # Used ONLY ONCE to generate the local keys on disk
        private_key: RSAPrivateKey = rsa.generate_private_key(
            public_exponent=self.__public_exponent,
            key_size=self.__rsa_key_bits,
            backend=self._backend,
        )
        public_key: RSAPublicKey = private_key.public_key()
        private_pem: str = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode(self.__encoding)
        public_pem: str = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode(self.__encoding)
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
        public_pem, private_pem = self._generate_key_pair()
        with open(public_key_path, "w") as public_file:
            public_file.write(public_pem)
        with open(private_key_path, "w") as private_file:
            private_file.write(private_pem)
        print("Public and Private keys have been generated and saved.")


@lru_cache
def get_encryption_service() -> EncryptionService:
    """
    Get the encryption service instance
    :return: The encryption service instance
    :rtype: EncryptionService
    """
    return EncryptionService()


encryption_service: EncryptionService = get_encryption_service()
encryption_service.save_key_pair("public_key.pem", "private_key.pem")
