from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Relationships
# Venue - Show: one to Many, bidirectional
# Artist - Show: one to Many, bidirectional

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    shows = db.relationship("Show", back_populates='venue', lazy=True)

    #Prints an object as a string
    def __repr__(self):
      return str({
        'id':self.id,
        'name':self.name,
        'city':self.city,
        'state':self.state,
        'address':self.address,
        'phone':self.phone,
        'image_link':self.image_link,
        'facebook_link':self.facebook_link,
        'genres':self.genres,
        'website':self.website,
        'seeking_talent':self.seeking_talent,
        'seeking_description':self.seeking_description
      })

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    website = db.Column(db.String)

    shows = db.relationship("Show", back_populates ='artist')

    # Prints the object as a string 
    def __repr__(self):
      return str({
        'id':self.id,
        'name':self.name,
        'city':self.city,
        'state':self.state,
        'phone':self.phone,
        'image_link':self.image_link,
        'facebook_link':self.facebook_link,
        'genres':self.genres,
        'website':self.website,
        'seeking_venue':self.seeking_venue,
        'seeking_description':self.seeking_description
      })
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  start_time = db.Column(db.DateTime(), nullable=False)
  
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

  artist = db.relationship("Artist", back_populates="shows")
  venue = db.relationship("Venue", back_populates="shows")
