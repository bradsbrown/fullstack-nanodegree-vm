from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Users, Base, Rooms, Items

engine = create_engine('sqlite:///householdinventory.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# first, some users
brad = Users(name='Brad',
             email="brad@bradsbrown.com",
             picture='http://zoocat.com/bear.JPG')

session.add(brad)
session.commit()

jenn = Users(name='Jenn',
             email="jenniferlbrown@me.com",
             picture='http://zoocat.com/bearcut.JPG')

session.add(jenn)
session.commit()

living = Rooms(name="Living Room")

session.add(living)
session.commit()

bedroom = Rooms(name="Bedroom")

session.add(bedroom)
session.commit()

guest = Rooms(name="Guest Room")

session.add(guest)
session.commit()

couch = Items(name="Couch",
              description="Beige cloth 3-seat couch",
              value="$300.00",
              users=brad,
              rooms=living)

session.add(couch)
session.commit()

bed = Items(name="Bed",
            description="Sleigh bed in cherry wood",
            value="$600.00",
            users=jenn,
            rooms=bedroom)

session.add(bed)
session.commit()

file_cab = Items(name="File Cabinet",
                 description="Rolling file cabinet and printer stand",
                 value="$50.00",
                 users=brad,
                 rooms=guest)

session.add(file_cab)
session.commit()
