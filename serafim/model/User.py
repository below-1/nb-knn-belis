from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import  String
from sqlalchemy.orm import relationship
from serafim.model.base import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    nama = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    email = Column(String, nullable=True)
    records = relationship("DsetRow", back_populates="user")

    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nama': self.nama
        }