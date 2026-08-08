from decimal import Decimal
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric, BigInteger
from sqlalchemy import Enum as SAENUM
from bot.database import Base
from bot.enums import UserRole




class Users(Base):
    __tablename__ = "Users"
    

    user_id : Mapped[int] = mapped_column(BigInteger, primary_key = True)
    user_role : Mapped[UserRole] = mapped_column(SAENUM(UserRole), nullable = False)

class Parent_Products(Base):
    __tablename__ = "Parent_Products"

    parent_id : Mapped[int] = mapped_column(primary_key = True)
    parent_name : Mapped[str] = mapped_column(nullable = False, unique = True)
    variants : Mapped[list["Variants"]] = relationship(
        "Variants", 
        back_populates = "parent",
        cascade = "all, delete-orphan"
        )

    __table_args__ = (
        Index(
            'ix_product_parent_name',
            "parent_name",
            postgresql_using = 'gin',
            postgresql_ops = {"parent_name" : "gin_trgm_ops"}
        ),
    )

class Variants(Base):
    __tablename__ = "Variants"

    var_id : Mapped[int] = mapped_column(primary_key = True)
    var_name : Mapped[str] = mapped_column(nullable = False)
    parent_id : Mapped[int] = mapped_column(ForeignKey("Parent_Products.parent_id"), nullable = False, index = True)
    var_price : Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable = False)
    var_quantity : Mapped[int] = mapped_column(nullable = False)
    parent : Mapped["Parent_Products"] = relationship("Parent_Products", back_populates = "variants")
    
    __table_args__ = (
        UniqueConstraint("parent_id", "var_name", name = "var_name_parent_id"),
    )