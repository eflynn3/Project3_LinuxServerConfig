#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class CatalogUser(Base):
    __tablename__ = 'catalog_user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('catalog_user.id'))
    user = relationship(CatalogUser)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id
        }


class Book(Base):
    __tablename__ = 'book'

    title = Column(String(80), nullable=False)
    author = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(400))
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)
    user_id = Column(Integer, ForeignKey('catalog_user.id'))
    user = relationship(CatalogUser)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'id': self.id,
            'genre_id': self.genre_id
        }


engine = create_engine('postgresql://catalog:catalog@localhost/catalog')


Base.metadata.create_all(engine)
