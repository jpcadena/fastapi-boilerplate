"""
A module for init settings in the app.core.config package.
"""
import base64
import time
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from authlib.jose import jwt
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.models import Example
from pydantic import PositiveInt
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.infrastructure.gender import Gender


def get_image_b64(image_path: str) -> str:
    """
    Converts an image to base64 format
    :param image_path: Path to the image file
    :type image_path: str
    :return: The image file in base64 format
    :rtype: str
    """
    return base64.b64encode(Path(image_path).read_bytes()).decode("utf")


img_b64: str = get_image_b64("assets/images/project.png")
users_b64: str = get_image_b64("assets/images/users.png")
auth_b64: str = get_image_b64("assets/images/auth.png")


class InitSettings(BaseSettings):
    """
    Init Settings class based on Pydantic Base Settings
    """

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="allow",
    )

    ITERATIONS: PositiveInt = 100000
    KEY_BYTES_LENGTH: PositiveInt = 32
    SALT_BYTES: PositiveInt = 16
    IV_BYTES: PositiveInt = 12
    PUBLIC_EXPONENT: PositiveInt = 65537
    RSA_KEY_BITS: PositiveInt = 2048
    SALUTE: str = "Salute!"
    ROOT_MSG: str = "Hello, World!"
    SERVER_NAME: str = "FastAPI Boilerplate"
    PROJECT_NAME: str = "fastapi-boilerplate"
    VERSION: str = "1.0"
    ENCODING: str = "UTF-8"
    DEFAULT_REGION: str = "Guayas"
    DEFAULT_COUNTRY: str = "Ecuador"
    OPENAPI_FILE_PATH: str = "/openapi.json"
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    FILE_DATE_FORMAT: str = "%d-%b-%Y-%H-%M-%S"
    IMAGES_APP: str = "images"
    IMAGES_PATH: str = "/assets/images"
    IMAGES_DIRECTORY: str = "assets/images"
    EMAIL_TEMPLATES_DIR: str = "templates"
    PASSWORD_RECOVERY_SUBJECT: str = "Password recovery for user"
    NEW_ACCOUNT_SUBJECT: str = "New account for user"
    WELCOME_SUBJECT: str = "Welcome to "
    PASSWORD_CHANGED_CONFIRMATION_SUBJECT: str = (
        "Successfully password " "changed for "
    )
    DELETE_ACCOUNT_SUBJECT: str = "Account deleted for "
    LOG_FORMAT: str = (
        "[%(name)s][%(asctime)s][%(levelname)s][%(module)s]"
        "[%(funcName)s][%(lineno)d]: %(message)s"
    )
    PASSWORD_REGEX: str = (
        "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?" "[#?!@$%^&*-]).{8,14}$"
    )

    SUMMARY: str = """This backend project is FastAPI template.
     This project serves as the backend, which aims to provide a robust and
     reliable system to its users.
       This backend application plays a crucial role in providing the
     functionality for user authentication, real-time monitoring,
      data processing, and advanced alerting system. It is designed to ensure
       the scalability and maintainability of the mobile app,
        making it a vital part of the overall solution.
    """
    DESCRIPTION: str = f"""**FastAPI**, **SQLAlchemy** and **Redis** helps you
    do awesome stuff. 🚀
    \n\n<img src="data:image/png;base64,{img_b64}"/>"""
    LICENSE_INFO: dict[str, str] = {
        "name": "MIT",
        "identifier": "MIT",
    }
    TAGS_METADATA: list[dict[str, str]] = [
        {
            "name": "user",
            "description": f"""Operations with users, such as register, get,
             update and delete.\n\n<img src="data:image/png;base64,
             {users_b64}" width="150" height="100"/>""",
        },
        {
            "name": "auth",
            "description": f"""The authentication logic is here as well as
             password recovery and reset.
             \n\n<img src="data:image/png;base64,{auth_b64}" width="75"
             height="75"/>""",
        },
    ]
    USER_CREATE_EXAMPLES: dict[str, Example] = {
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** user create object that works "
            "correctly.",
            "value": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "middle_name": "One",
                "last_name": "Example",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 12, 31),
                "phone_number": PhoneNumber("+593987654321"),
                "address": {
                    "street_address": "Urdesa Norte mz A1 v 99",
                    "locality": "Guayaquil",
                    "region": "Guayas",
                    "country": "Ecuador",
                    "postal_code": "090505",
                },
            },
        },
        "converted": {
            "summary": "An example with converted data",
            "description": "FastAPI can convert phone number `strings` to "
            "actual `numbers` automatically",
            "value": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "middle_name": "One",
                "last_name": "Example",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 12, 31),
                "phone_number": PhoneNumber(593987654321),
                "address": {
                    "street_address": "Urdesa Norte mz A1 v 99",
                    "locality": "Guayaquil",
                    "region": "Guayas",
                    "country": "Ecuador",
                    "postal_code": "090505",
                },
            },
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": {
                "username": "username",
                "email": "username",
                "first_name": "Some",
                "middle_name": "One",
                "last_name": "Example",
                "password": "miclave123",
                "gender": Gender.MALE,
                "birthdate": date(95, 12, 31),
                "phone_number": PhoneNumber("5939876a4321"),
                "address": {
                    "street_address": "True",
                    "locality": "123",
                    "region": "Andes",
                    "country": "New York",
                    "postal_code": "999999",
                },
            },
        },
    }
    USER_UPDATE_EXAMPLES: dict[str, Example] = {
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** user update object that works "
            "correctly.",
            "value": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "middle_name": "One",
                "last_name": "Example",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 12, 31),
                "phone_number": PhoneNumber(593987654321),
                "address": {
                    "street_address": "Urdesa Norte mz A1 v 99",
                    "locality": "Guayaquil",
                },
            },
        },
        "converted": {
            "summary": "An example with converted data",
            "description": "FastAPI can convert phone numbers `strings` to "
            "actual `numbers` automatically",
            "value": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "middle_name": "One",
                "last_name": "Example",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 12, 31),
                "phone_number": PhoneNumber("593987654321"),
                "address": {
                    "street_address": "Urdesa Norte mz A1 v 99",
                    "locality": "Guayaquil",
                },
            },
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": {
                "username": "username",
                "email": "username",
                "first_name": "Some",
                "middle_name": "One",
                "last_name": "Example",
                "password": "miclave123",
                "gender": Gender.MALE,
                "birthdate": date(95, 12, 31),
                "phone_number": PhoneNumber("59398x54321"),
                "address": {
                    "street_address": "True",
                    "locality": "123",
                },
            },
        },
    }
    EMAIL_BODY_EXAMPLES: dict[str, Example] = {
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** email object that works correctly.",
            "value": "example@mail.com",
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": 123,
        },
    }
    TOKEN_PAYLOAD_EXAMPLES: dict[str, Example] = {
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** token payload object that works "
            "correctly.",
            "value": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "password": "Hk7pH9*35Fu&3U",
            },
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": {
                "token": "123",
                "password": "abc123",
            },
        },
    }
    AUTHORIZATION_HEADER_EXAMPLES: dict[str, Example] = {
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** authorization token object that works "
            "correctly.",
            "value": jwt.encode(
                header={"alg": "HS256"},
                payload=jsonable_encoder(
                    {
                        "sub": f"username:{str(uuid4())}",
                        "nationalities": ["ECU"],
                        "email": "example@mail.com",
                        "nickname": "example",
                        "preferred_username": "example",
                        "given_name": "Some",
                        "family_name": "Example",
                        "middle_name": "One",
                        "gender": Gender.MALE,
                        "birthdate": date(2004, 12, 31),
                        "updated_at": datetime.now(),
                        "phone_number": PhoneNumber("+593987654321"),
                        "address": {
                            "street_address": "Urdesa Norte mz A1 v 99",
                            "locality": "Guayaquil",
                            "region": "Guayas",
                            "country": "Ecuador",
                            "postal_code": "090505",
                        },
                        "exp": int(time.time()) + 1800,
                        "nbf": int(time.time()) - 1,
                        "iat": int(time.time()),
                    }
                ),
                key="f52e826e62cdd364c86f129cb18db2fe2be93859c5104cac9585f"
                "305378dce65",
            ),
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": "123",
        },
    }
    LIMIT_EXAMPLES: dict[str, Example] = {
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** limit query parameter that works "
            "correctly.",
            "value": 1,
        },
        "converted": {
            "summary": "An example with converted data",
            "description": "FastAPI can convert limit `strings` to actual"
            " `numbers` automatically",
            "value": "5",
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": -1,
        },
    }
    SKIP_EXAMPLES: dict[str, Example] = {
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** skip query parameter that works "
            "correctly.",
            "value": 0,
        },
        "converted": {
            "summary": "An example with converted data",
            "description": "FastAPI can convert skip `strings` to actual"
            " `numbers` automatically",
            "value": "20",
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": -1,
        },
    }
