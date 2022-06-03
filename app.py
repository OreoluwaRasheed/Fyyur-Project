#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import config
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues = Venue.query.all()
  for venue in venues:
    data.append({
      'city': venue.city,
      'state': venue.state,
      'venues':[{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(venue.shows)
      }]
    })
  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(db.func.lower(Venue.name).ilike(f'%{search_term.lower()}%')).all()
  response = {
    "count": len(venues),
    "data": []
  }
  for venue in venues:
    response['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(venue.shows)
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  for show in venue.shows:
    if show.start_time < datetime.now():
      data['past_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
      data['past_shows_count'] += 1
    else:
      data['upcoming_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
      data['upcoming_shows_count'] += 1
  return render_template('pages/show_venue.html', venue=data)
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  try:
    seeking_talent = False
    if 'seeking_talent' in request.form:
      seeking_talent = True
      
    venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'],
                  phone=request.form['phone'], image_link=request.form['image_link'], genres=request.form.getlist('genres'),
                  facebook_link=request.form['facebook_link'], website_link=request.form['website_link'],  seeking_talent=seeking_talent, seeking_description=request.form['seeking_description'])
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('There was an error in adding your venue. Venue '+ request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue_name + ' was deleted')
  except:
    flash(' There was an error and ' + venue_name + ' could not be deleted')
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(db.func.lower(Artist.name).ilike(f'%{search_term.lower()}%')).all()
  response = {
    "count": len(artists),
    "data": []
  }
  for artist in artists:
    response['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(artist.shows)
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "phone": artist.phone,
    "website": artist.website_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  for show in artist.shows:
    if show.start_time < datetime.now():
      data['past_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
      data['past_shows_count'] += 1
    else:
      data['upcoming_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
      data['upcoming_shows_count'] += 1
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
   # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.city.data = artist.city
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.facebook_link.data = artist.facebook_link
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.city = request.form['city']
    artist.genres = request.form.getlist('genres')
    artist.website_link = request.form['website_link']
    artist.seeking_venue = request.form['seeking_venue']
    artist.seeking_description = request.form['seeking_description']
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    db.session.commit()
    flash('Success! The artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('There was an error. The artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.city.data = venue.city
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.genres.data = venue.genres
  form.state.data = venue.state
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  seeking_talent = False
  if 'seeking_talent' in request.form:
      seeking_talent = True
  
  venue = Venue.query.get(venue_id)  
  try:
    venue.name = request.form['name']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.website_link = request.form['website_link']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = seeking_talent
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash('Success! The venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('There was an error. The venue ' + request.form['name'] + ' could not be updated.')
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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  try:
    seeking_venue = False
    if 'seeking_venue' in request.form:
      seeking_venue = True

    artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      website_link = request.form['website_link'],
      facebook_link = request.form['facebook_link'],
      seeking_venue = seeking_venue,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
    flash('Success! The artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('There was an error. The artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.order_by(db.desc(Show.start_time))
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
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
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  try:
    show = Show(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      start_time = request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()
    flash('Success! Show was successfully listed!')
  except:
    db.session.rollback()
    flash('There was an error. Show could not be listed.')
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
