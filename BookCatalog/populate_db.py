#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Book, CatalogUser

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

User1 = CatalogUser(name="Erin Flynn", email="eflynn55@gmail.com")
session.add(User1)
session.commit()

genre1 = Genre(user_id=1, name="General Fiction")
session.add(genre1)
session.commit()

User2 = CatalogUser(name="Jane Doe", email="janedoe@test.com")
session.add(User2)
session.commit()

book1 = Book(user_id=1, title="East of Eden", author="John Steinbeck", description="Often described as Steinbeck's most ambitious novel, East of Eden brings to life the intricate details of two families, the Trasks and the Hamiltons, and their interwoven stories.",
                     genre=genre1)

session.add(book1)
session.commit()

book2 = Book(user_id=2, title="Oliver Twist", author="Charles Dickens", description=" The story centres on orphan Oliver Twist, born in a workhouse and sold into apprenticeship with an undertaker. After escaping, Oliver travels to London, where he meets 'The Artful Dodger', a member of a gang of juvenile pickpockets led by the elderly criminal, Fagin.",
                     genre=genre1)

session.add(book2)
session.commit()

genre2 = Genre(user_id=1, name="Memoir")

session.add(genre2)
session.commit()


book3 = Book(user_id=1, title="The Glass Castle", author="Jeannette Walls", description="The book recounts the unconventional, poverty-stricken upbringing Walls and her siblings had at the hands of their deeply dysfunctional parents. The title refers to her father’s long held intention of building his dream house, a glass castle.",
                     genre=genre2)

session.add(book3)
session.commit()

genre3 = Genre(user_id=1, name="Mystery")

session.add(genre3)
session.commit()

book4 = Book(user_id=1, title="In Cold Blood", author="Truman Capote", description="In Cold Blood details the 1959 murders of four members of the Herbert Clutter family in the small farming community of Holcomb, Kansas.",
                     genre=genre3)

session.add(book4)
session.commit()

book5 = Book(user_id=1, title="Faithful Place", author="Tana French", description="Back in 1985, Frank Mackey was nineteen, growing up poor in Dublin's inner city and living crammed into a small flat with his family on Faithful Place. But he had his sights set on a lot more. He and his girl, Rosie Daly, were all set to run away to London together, get married, get good jobs, break away from factory work and poverty and their old lives.",
                     genre=genre3)

session.add(book5)
session.commit()

genre4 = Genre(user_id=1, name="Fantasy")

session.add(genre4)
session.commit()

book6 = Book(user_id=1, title="A Game of Thrones", author="George R. R. Martin", description="In the novel, recounting events from various points of view, Martin introduces the plot-lines of the noble houses of Westeros, the Wall, and the Targaryens.",
                     genre=genre4)

session.add(book6)
session.commit()
