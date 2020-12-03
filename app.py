#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)
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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues_city = Venue.query.all()
  data=[]
  # Filling data[] with cities and states, venues is set as an empty array
  # to fill later
  for venue in venues_city:
    d = {
      'city': venue.city,
      'state': venue.state,
      'venues':[]
    }
    # If d isn't in data, add d to data
    if d not in data:
      data.append(d)
  
  # Go through all the cities of data[] and add the venues
  for d in data:
    # Getting all venues of a d.city
    venues_add = Venue.query.filter_by(city=d.get('city')).all()
    # Adding the venues_add to d['venues].
    for v in venues_add:
      d['venues'].append({
        "id":v.id,
        "name":v.name,
        "num_upcoming_shows":count_upcoming_shows_venue(v.id)
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  # search: pattern matching to search
  search = "%{}%".format(search_term)
  # Searching all venues with case-insensitive
  venues = Venue.query.filter(Venue.name.ilike(search)).all()
  
  response = {
    "count":len(venues),
    "data":[]
  }
  # Filling response['data'] 
  for venue in venues:
    response['data'].append({
      'id':venue.id,
      'name':venue.name,
      'num_upcoming_shows':count_upcoming_shows_venue(venue.id)
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": get_past_shows_venue(venue.id),
    "upcoming_shows": get_upcoming_shows_venue(venue.id),
    "past_shows_count": count_past_shows_venue(venue.id),
    "upcoming_shows_count": count_upcoming_shows_venue(venue.id)
  }
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form['name']
  city = request.form['city']
  state = request.form['state'] 
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']

  # Getting the max_id of the venue to avoid IntegrityError duplicate key id value violates unique constraint
  # Verifying if there aren't venues, set max_id = 1, to avoid send None type to Venue(id=None).
  if len(Venue.query.all()) == 0 :
    max_id=1
  else:
    max_id = Venue.query.order_by(Venue.id.desc()).first().id
    max_id = max_id+1

  venue = Venue(id=max_id, name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)

  # Adding a new row to table "Venue" with postgresql
  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name+ ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  
  return venue_id

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data=[]
  # Filling data with artists.
  for artist in artists:
    data.append({
      'id':artist.id,
      "name":artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  search_term = search_term.lower()
  # search: pattern matching to search
  search = "%{}%".format(search_term)
  # Searching all Artist with case-insensitive

  artists = Artist.query.filter(Artist.name.ilike(search)).all()
  
  response = {
    "count":len(artists),
    "data":[]
  }
  # filling response['data'] with all artist obtained
  for artist in artists:
    response['data'].append({
      'id':artist.id,
      'name':artist.name, 
      'num_upcoming_shows':count_upcoming_shows_artist(artist.id)
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": get_past_shows_artist(artist.id),
    "upcoming_shows": get_upcoming_shows_artist(artist.id),
    "past_shows_count": count_past_shows_artist(artist.id),
    "upcoming_shows_count": count_upcoming_shows_artist(artist.id)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # Populating form with artist data
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  print(artist.genres)
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
 
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # Populating form with venue data
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  print(venue.genres)
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.address = request.form['address']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state'] 
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    # Getting the max_id of the Artist to avoid IntegrityError duplicate key id value violates unique constraint
    # Verifying if there aren't Artist, set max_id = 1, to avoid send None type to Artist(id=None)
    if len(Artist.query.all()) == 0:
      max_id=1
    else:
      max_id = Artist.query.order_by(Artist.id.desc()).first().id
      max_id = max_id+1
    artist = Artist(id=max_id,name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = getall_upcoming_shows()
  data=[]
  for show in shows:
    artist = show.artist
    venue = show.venue
    data.append({
      'venue_id':venue.id,
      'venue_name':venue.name,
      'artist_id':artist.id,
      'artist_name':artist.name,
      'artist_image_link':artist.image_link,
      'start_time':show.start_time.isoformat()
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
    artist_id=request.form['artist_id']
    venue_id=request.form['venue_id']
    start_time =request.form['start_time']
    # Getting the max_id of the Show to avoid IntegrityError duplicate key id value violates unique constraint
    # Verifying if there aren't Shows, set max_id = 1 to avoid send None type to Show(id=None) 
    if len(Show.query.all())==0:
      max_id=1
    else:
      max_id = Show.query.order_by(Show.id.desc()).first().id
      max_id = max_id+1
    show = Show(id=max_id,artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    print(show)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.') 
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
# Get all the upcoming shows of a venue, and return data[] with dictionaries, with all the information needed it
def get_upcoming_shows_venue(id):
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter_by(venue_id=id).filter(Show.start_time>=todays_datetime).all()
  data = []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    data.append({
      "artist_id":artist.id,
      "artist_name":artist.name,
      "artist_image_link":artist.image_link,
      "start_time": show.start_time.isoformat()
    })
  return data

# Get all the past shows of a venue, and return data[] with dictionaries with all the information needed it. 
def get_past_shows_venue(id):
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter_by(venue_id=id).filter(Show.start_time<=todays_datetime).all()
  data = []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    data.append({
      "artist_id":artist.id,
      "artist_name":artist.name,
      "artist_image_link":artist.image_link,
      "start_time": show.start_time.isoformat()
    })
  return data
# Get all the past shows of an artist, and return data[] with dictionaries, with all the information needed it. 
def get_past_shows_artist(id):
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter_by(artist_id=id).filter(Show.start_time<=todays_datetime).all()
  data = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    data.append({
      "venue_id":venue.id,
      "venue_name":venue.name,
      "venue_image_link":venue.image_link,
      "start_time": show.start_time.isoformat()
    })
  return data
# Get all the upcoming shows of the database
def getall_upcoming_shows():
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter(Show.start_time>=todays_datetime).all()
  return shows
# Get all the upcoming shows of an artist, and return data[] with dictionaries, with all the information needed it
def get_upcoming_shows_artist(id):
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter_by(artist_id=id).filter(Show.start_time>=todays_datetime).all()
  data = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    data.append({
      "venue_id":venue.id,
      "venue_name":venue.name,
      "venue_image_link":venue.image_link,
      "start_time": show.start_time.isoformat()
    })
  return data
# Count all the past shows of a venue
def count_past_shows_venue(id):
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter_by(venue_id=id).filter(Show.start_time<=todays_datetime).count()
  return shows
# Count all the past shows of an artist
def count_past_shows_artist(id):
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter_by(artist_id=id).filter(Show.start_time<=todays_datetime).count()
  return shows

# Count all the upcoming shows of a venue
def count_upcoming_shows_venue(id):
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter_by(venue_id=id).filter(Show.start_time>=todays_datetime).count()
  return shows
# Count all the upcoming shows of a artist
def count_upcoming_shows_artist(id):
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter_by(artist_id=id).filter(Show.start_time>=todays_datetime).count()
  return shows


