"""
Package app.models.sql initialization.
"""

from app.models.sql.address import Address
from app.models.sql.locality import Locality
from app.models.sql.region import Region
from app.models.sql.user import User

from ...db.base_class import Base

# Export a list of models in the order you want them created.
__all__: list[Base] = [Address, User, Region, Locality]  # type: ignore
