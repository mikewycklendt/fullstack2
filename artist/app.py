#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import config
from forms import VenueForm, ShowForm, ArtistForm
from datetime import datetime
import db

app = Flask(__name__)
moment = Moment(app)
#app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@3.134.26.61:5432/artistapp'
db = SQLAlchemy(app)

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
  today = datetime.now()
  areas = db.session.query(Venue.city,Venue.state).distinct(Venue.city, Venue.state)

  data = []
  for area in areas:
    venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in venues:
      show_count = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time>today).count()
      venue_data.append({'id':venue.id, 'name':venue.name, 'shows':show_count})
    data.append({'city':area.city, 'state': area.state, 'venues': venue_data})

  print(data)
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  today = datetime.now()
  search_term=request.form['search_term']
  search = '%' + search_term + '%'
  data = db.session.query(Venue).filter(Venue.name.ilike(search)).all()
  count = db.session.query(Venue).filter(Venue.name.ilike(search)).count()
  for result in data:
    print(result.name)

  venues = []
  for result in data:
    shows = db.session.query(Show).filter(Show.venue_id==result.id, Show.start_time>today).count()
    venues.append({'id':result.id, 'name':result.name, 'num_upcoming_shows':shows})
  results = {'count': count, 'data':venues}
  print(results)
  
  response=results

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  today = datetime.now()
  venue = db.session.query(Venue).filter_by(id=venue_id).one()
  upcoming_shows_count = db.session.query(Show).filter(Show.venue_id == venue_id, Show.start_time>today).count()
  past_shows_count = db.session.query(Show).filter(Show.venue_id == venue_id, Show.start_time<today).count()
  pastshows = db.session.query(Show).filter(Show.venue_id == venue_id, Show.start_time<today).all()
  upcomingshows = db.session.query(Show).filter(Show.venue_id == venue_id, Show.start_time>today).all()

  past_shows = []
  upcoming_shows = []

  for show in pastshows:
    artist = db.session.query(Artist).filter_by(id=show.artist_id).one()
    past_shows.append({'artist_id': artist.id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': str(show.start_time)})

  for show in upcomingshows:
    artist = db.session.query(Artist).filter_by(id=show.artist_id).one()
    upcoming_shows.append({'artist_id': artist.id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': str(show.start_time)})

  print(past_shows)
  print(upcoming_shows)
  
  return render_template('pages/show_venue.html', venue=venue, upcoming_shows_count=upcoming_shows_count, past_shows_count=past_shows_count, upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #form = VenueForm(request.form)
  error = False
  name = request.form['name']
  city = request.form['city']
  venueState = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image = request.form['image_link']
  facebook = request.form['facebook_link']
  seeking = request.form['seeking_talent']
  seekingDesc = request.form['seeking_description']
  genres = request.form.getlist('genres')
  website = request.form['website']
  print(genres)
  if seeking == 'True':
    seeking = True
  else:
    seeking = False
  try:
    newEntry = Venue(name=name, city=city, state=venueState, address=address, phone=phone, image_link=image, facebook_link=facebook, seeking_talent=seeking, seeking_description=seekingDesc, genres=genres, website=website)
    db.session.add(newEntry)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. Venue ' + name + ' could not be listed.')
    return redirect(url_for('index'))
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).one()
  form = VenueForm()
  form.state.data = venue.state
  form.genres.data = venue.genres
  form.seeking_talent.data = venue.seeking_talent

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter_by(id=venue_id).one()
  error = False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image = request.form['image_link']
  genres = request.form.getlist('genres')
  facebook = request.form['facebook_link']
  seeking = request.form['seeking_talent']
  seekingDesc = request.form['seeking_description']
  website = request.form['website']
  if seeking == 'True':
    seeking = True
  else:
    seeking = False
    
  try:
    venue.name = name
    venue.city = city
    venue.state = state
    venue.phone = phone
    venue.image_link = image
    venue.genres = genres
    venue.facebook_link = facebook
    venue.seeking_talent = seeking
    venue.seeking_description = seekingDesc
    venue.website = website
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured.  Venue ' + name + ' could not be edited.')
    return redirect(url_for('show_venue', venue_id=venue.id))
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue.id))

@app.route('/deletevenue/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  venue = db.session.query(Venue).filter_by(id=venue_id).one()
  shows = db.session.query(Show).filter_by(venue_id=venue_id).all()
  name = venue.name
  try:
    for show in shows:
      db.session.delete(show)
      db.session.commit()
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An Error occured.  The venue ' + name + ' could not be deleted.')
    return jsonify({'success': True})
  else:
    flash('Success.  Venue ' + name + ' was deleted.')
    return jsonify({'success': True})
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST','GET'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  today = datetime.now()
  search_term=request.form['search_term']
  search = '%' + search_term + '%'
  data = db.session.query(Artist).filter(Artist.name.ilike(search)).all()
  count = db.session.query(Artist).filter(Artist.name.ilike(search)).count()
  for result in data:
    print(result.name)

  artists = []
  for result in data:
    shows = db.session.query(Show).filter(Show.artist_id==result.id, Show.start_time>today).count()
    artists.append({'id':result.id, 'name':result.name, 'num_upcoming_shows':shows})
  results = {'count': count, 'data':artists}
  print(results)

  response=results
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  today = datetime.now()

  artist = Artist.query.filter_by(id=artist_id).first()
  upcoming_shows = Show.query.filter(Show.artist_id==artist.id, Show.start_time>today).all()
  for show in upcoming_shows:
    print(show.venue_name)
  past_shows = Show.query.filter(Show.artist_id==artist.id, Show.start_time<today).all()

  upcoming_count = Show.query.filter(Show.artist_id==artist.id, Show.start_time>today).count()
  past_count = Show.query.filter(Show.artist_id==artist.id, Show.start_time<today).count()

  print(upcoming_count)
  print(past_count)

  return render_template('pages/show_artist.html', artist=artist, upcoming_shows=upcoming_shows, upcoming_count=upcoming_count, past_shows=past_shows, past_count=past_count)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm()
  form.state.data = artist.state
  form.genres.data = artist.genres
  form.seeking_venue.data = artist.seeking_venue

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).one()
  error = False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image = request.form['image_link']
  genres = request.form.getlist('genres')
  facebook = request.form['facebook_link']
  seeking = request.form['seeking_venue']
  seekingDesc = request.form['seeking_description']
  website = request.form['website']
  if seeking == 'True':
    seeking = True
  else:
    seeking = False
    
  try:
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.image_link = image
    artist.genres = genres
    artist.facebook_link = facebook
    artist.seeking_venue = seeking
    artist.seeking_description = seekingDesc
    artist.website = website
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured.  Artist ' + name + ' could not be edited.')
    return redirect(url_for('show_artist', artist_id=artist.id))
  else:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist.id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image = request.form['image_link']
  genres = request.form.getlist('genres')
  facebook = request.form['facebook_link']
  seeking = request.form['seeking_venue']
  seekingDesc = request.form['seeking_description']
  website = request.form['website']
  if seeking == 'True':
    seeking = True
  else:
    seeking = False
    
  try:
    newEntry = Artist(name=name,
                      city=city,
                      state=state,
                      phone=phone,
                      genres=genres,
                      image_link=image,
                      facebook_link=facebook,
                      seeking_venue=seeking,
                      seeking_description=seekingDesc,
                      website=website)
    db.session.add(newEntry)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured.  Artist ' + name + ' could not be listed.')
    return redirect(url_for('index'))
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = db.session.query(Show).all()

  data = []

  for show in shows:
    artist = db.session.query(Artist).filter_by(id=show.artist_id).one()
    data.append({'venue_id': show.venue_id, 'venue_name': show.venue_name, 'artist_id': show.artist_id, 'artist_name': show.artist_name, 'artist_image_link': artist.image_link, 'start_time': str(show.start_time)})

  print(data)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()

  artists = Artist.query.all()
  artistsSelect = [(artist.id, artist.name) for artist in artists]

  venues = Venue.query.all()
  venuesSelect = [(venue.id, venue.name) for venue in venues]
  
  form.artists.choices = artistsSelect
  form.venue_id.choices = venueSelect

  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  venue_id = request.form['venue_id']
  artist_id = request.form['artists']
  start_time = request.form['start_time']
  venue = Venue.query.filter_by(id=venue_id).first()
  artist = Artist.query.filter_by(id=artist_id).first()
  artist_name = artist.name
  venue_name = venue.name
  venue_image = venue.image_link

  try:
    newEntry = Show(venue_id=venue_id,
                    artist_id=artist_id,
                    start_time=start_time,
                    artist_name=artist_name,
                    venue_name=venue_name,
                    venue_image=venue_image)
    db.session.add(newEntry)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured.  Show could not be listed.')
    return redirect(url_for('index'))
  else:
    flash('Show was successfully listed!')
    return redirect(url_for('index'))

@app.route('/show/delete', methods=['GET', 'DELETE'])
def delete_show():
  Show.query.filter_by(id=1).delete()
  db.session.commit()
  Show.query.filter_by(id=1).delete()
  db.session.commit()
  db.session.close()
  flash('Shows Deleted')
  return redirect(url_for('index'))

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

if __name__ == '__main__':
    app.debug = True
    app.secret_key = config.SECRET_KEY
    app.run(host='0.0.0.0', port=80)
