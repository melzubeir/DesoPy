import jwt
import binascii
from ecdsa import (
    SECP256k1,
    VerifyingKey,
    SigningKey
)
from deso.Sign import Sign_Transaction
from base58 import b58decode_check


class Identity:
    def __init__(
        self,
        publicKey,
        seedHex=None,
        nodeURL="https://node.deso.org/api/v0/",
        derivedPublicKey=None,
        derivedSeedHex=None,
        minFee=1000,
        derivedKeyFee=1700,
    ):
        self.SEED_HEX = seedHex
        self.PUBLIC_KEY = publicKey
        self.NODE_URL = nodeURL
        self.DERIVED_PUBLIC_KEY = derivedPublicKey
        self.DERIVED_SEED_HEX = derivedSeedHex
        self.MIN_FEE = minFee if seedHex else derivedKeyFee

    def getJWT(self):
        # returns JWT token of user that helps in public key validation
        # in backend
        private_key = bytes(self.SEED_HEX, "utf-8")
        private_key = binascii.unhexlify(private_key)
        key = SigningKey.from_string(private_key, curve=SECP256k1)
        key = key.to_pem()
        encoded_jwt = jwt.encode({}, key, algorithm="ES256")
        return encoded_jwt

    def validateJWT(self, JWT, publicKey):
        # Validates the JWT token generated by DeSo Identity for a publicKey
        try:
            rawPublicKeyHex = b58decode_check(publicKey)[3:].hex()
            public_key = bytes(rawPublicKeyHex, "utf-8")
            public_key = binascii.unhexlify(public_key)
            key = VerifyingKey.from_string(public_key, curve=SECP256k1)
            key = key.to_pem()
            decoded = jwt.decode(JWT, key, algorithms=["ES256"])
            return {"isValid": True, "decodedJWT": decoded}
        except Exception as e:
            return {"isValid": False, "error": str(e)}

    def signTransaction(self, seedHex, transactionHex):
        """Signs Transaction thorugh seedHex.
        Supports derived key signing as well"""
        try:
            signedTransactionHex = Sign_Transaction(seedHex, transactionHex)
        except Exception as e:
            raise Exception(str(e))
        return signedTransactionHex

    def __repr__(self):
        return f"Identity(publicKey={self.PUBLIC_KEY}, nodeURL={self.NODE_URL})"

    def __str__(self):
        return f"Identity object on {self.NODE_URL}"
