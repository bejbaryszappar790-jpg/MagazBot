from enum import Enum
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric, BigInteger
from sqlalchemy import Enum as SAENUM
from bot.database import Base



class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class Users(Base):
    __tablename__ = "Users"
    

    user_id : Mapped[int] = mapped_column(BigInteger, primary_key = True, index = True)
    user_role : Mapped[UserRole] = mapped_column(SAENUM(UserRole), nullable = False)

class Parent_Products(Base):
    __tablename__ = "Parent_Products"

    parent_id : Mapped[int] = mapped_column(primary_key = True, index = True)
    parent_name : Mapped[str] = mapped_column(nullable = False, unique = True)
    variants : Mapped[list["Variants"]] = relationship(
        "Variants", 
        back_populates = "parent",
        cascade = "all, delete-orphan"
        )

class Variants(Base):
    __tablename__ = "Variants"

    var_id : Mapped[int] = mapped_column(primary_key = True, index = True)
    var_name : Mapped[str] = mapped_column(nullable = False, unique = True)
    parent_id : Mapped[int] = mapped_column(ForeignKey("Parent_Products.parent_id"), nullable = True, index = True)
    var_price : Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable = True)
    parent : Mapped["Parent_Products"] = relationship("Parent_Products", back_populates = "variants")
    
    stocks : Mapped[list["Stocks"]] = relationship(
        "Stocks", 
        back_populates = "variant",
        cascade = "all, delete-orphan")



class Stocks(Base):
    __tablename__ = "Stocks"
    stock_id : Mapped[int] = mapped_column(primary_key = True, index = True)
    var_id : Mapped[int] = mapped_column(ForeignKey("Variants.var_id"), nullable = False, index = True)
    stock_quantity : Mapped[int] = mapped_column(nullable = False)
    variant : Mapped["Variants"] = relationship("Variants", back_populates = "stocks")