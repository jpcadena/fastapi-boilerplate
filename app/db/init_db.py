"""
Initialization of the database (PostgreSQL) script
"""
import logging

from app.config.db.auth_settings import AuthSettings
from app.config.init_settings import InitSettings
from app.config.settings import Settings
from app.crud.specification import EmailSpecification
from app.crud.user import UserRepository
from app.db.base_class import Base
from app.db.session import async_engine
from app.models.sql import __all__ as tables
from app.models.sql.user import User
from app.schemas.external.address import Address
from app.schemas.external.user import UserSuperCreate
from app.schemas.infrastructure.gender import Gender
from app.tasks.email_tasks.email_tasks import (
    send_new_account_email,
    send_welcome_email,
)
from app.utils.utils import hide_email

logger: logging.Logger = logging.getLogger(__name__)


async def create_db_and_tables() -> None:
    """
    Create the database and tables if they don't exist
    :return: None
    :rtype: NoneType
    """
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        for table in tables:
            await connection.run_sync(table.__table__.create)  # type: ignore


async def create_superuser(
    user_repo: UserRepository,
    settings: Settings,
    init_settings: InitSettings,
    auth_settings: AuthSettings,
) -> None:
    """
    Create the superuser if it doesn't exist already in the database
    :param user_repo: The user repository dependency.
    :type user_repo: UserRepository
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: None
    :rtype: NoneType
    """
    user = await user_repo.read_by_email(
        EmailSpecification(settings.SUPERUSER_EMAIL)
    )
    if user:
        logger.warning("Superuser already exists.")
        return
    address: Address = Address(
        street_address=settings.SUPERUSER_STREET_ADDRESS,
        locality=settings.SUPERUSER_LOCALITY,
        region=init_settings.DEFAULT_REGION,
        country=init_settings.DEFAULT_COUNTRY,
        postal_code=settings.SUPERUSER_POSTAL_CODE,
    )
    superuser_created: UserSuperCreate = UserSuperCreate(
        username=settings.SUPERUSER_EMAIL.split("@")[0],
        email=settings.SUPERUSER_EMAIL,
        first_name=settings.SUPERUSER_FIRST_NAME,
        last_name=settings.SUPERUSER_LAST_NAME,
        password=settings.SUPERUSER_PASSWORD,
        address=address,
        gender=Gender.MALE,
    )
    superuser: User = await user_repo.create_user(superuser_created)
    await send_new_account_email(
        superuser.email,
        superuser.username,
        settings,
        auth_settings,
        init_settings,
    )
    hidden_email: str = hide_email(superuser.email)
    logger.info(
        "Superuser created with email %s from %s",
        hidden_email,
        address.locality,
    )
    await send_welcome_email(
        superuser.email,
        superuser.username,
        init_settings,
        settings,
        auth_settings,
    )


async def init_db(
    user_repo: UserRepository,
    settings: Settings,
    init_settings: InitSettings,
    auth_settings: AuthSettings,
) -> None:
    """
    Initialize the database connection and create the necessary tables.
    :param user_repo: The user repository dependency.
    :type user_repo: UserRepository
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: None
    :rtype: NoneType
    """
    await create_db_and_tables()
    await create_superuser(user_repo, settings, init_settings, auth_settings)
