import sqlite3
from flask import Flask, render_template, g, request, redirect, url_for, jsonify
import os
import bcrypt
from apscheduler.schedulers.background import BackgroundScheduler
import random
import uuid

# Database paths
DATABASE_PATH_FLIGHTS = 'database/flights.db'
DATABASE_PATH_JOBS = 'database/jobs.db'
DATABASE_PATH_AIRPORTS = 'database/airport.db'
DATABASE_PATH_JOBMARKET = 'database/jobmarket.db'
DATABASE_PATH_PILOTS = 'database/pilots.db'
DATABASE_PATH_FLEET = 'database/fleet.db'
DATABASE_PATH_AIRCRAFT = 'database/aircraft.db'  # <-- Add this line

# Flask app setup
app = Flask(__name__)
app.config['DATABASE_PATH_FLIGHTS'] = DATABASE_PATH_FLIGHTS
app.config['DATABASE_PATH_JOBS'] = DATABASE_PATH_JOBS
app.config['DATABASE_PATH_AIRCRAFT'] = DATABASE_PATH_AIRCRAFT  # <-- Add this line

# CPL Ranks Configuration
CPL_RANKS = [
    {"rank": "CPL 1",  "min_hours": 0},
    {"rank": "CPL 2",  "min_hours": 10},
    {"rank": "CPL 3",  "min_hours": 20},
    {"rank": "CPL 4",  "min_hours": 35},
    {"rank": "CPL 5",  "min_hours": 50},
    {"rank": "CPL 6",  "min_hours": 70},
    {"rank": "CPL 7",  "min_hours": 90},
    {"rank": "CPL 8",  "min_hours": 120},
    {"rank": "CPL 9",  "min_hours": 150},
    {"rank": "CPL 10", "min_hours": 200},
    {"rank": "CPL 11", "min_hours": 300},
    {"rank": "CPL 12", "min_hours": 500},
]

def get_cpl_rank(total_hours):
    for rank in reversed(CPL_RANKS):
        if total_hours >= rank["min_hours"]:
            return rank["rank"]
    return "CPL 1"

def get_rank_multiplier(rank):
    rank_map = {
        "CPL 1": 0.7, "CPL 2": 0.75, "CPL 3": 0.8, "CPL 4": 0.85,
        "CPL 5": 0.9, "CPL 6": 1.0, "CPL 7": 1.05, "CPL 8": 1.1,
        "CPL 9": 1.15, "CPL 10": 1.2, "CPL 11": 1.3, "CPL 12": 1.5
    }
    return rank_map.get(rank, 1.0)

# Database connection functions
def get_db_pilots():
    database_path = os.path.abspath(DATABASE_PATH_PILOTS)  # 🔹 Get absolute path
    print(f"Connecting to database at: {database_path}")  # 🔹 Debugging log

    db = getattr(g, '_database_pilots', None)
    if db is None:
        db = g._database_pilots = sqlite3.connect(database_path)
        db.row_factory = sqlite3.Row
    return db

def get_db_flights():
    db = getattr(g, '_database_flights', None)
    if db is None:
        db = g._database_flights = sqlite3.connect(app.config['DATABASE_PATH_FLIGHTS'])
        db.row_factory = sqlite3.Row
    return db

def get_db_jobs():
    db = getattr(g, '_database_jobs', None)
    if db is None:
        db = g._database_jobs = sqlite3.connect(app.config['DATABASE_PATH_JOBS'])
        db.row_factory = sqlite3.Row
    return db

def get_db_jobmarket():
    db = getattr(g, '_database_jobmarket', None)
    if db is None:
        db = g._database_jobmarket = sqlite3.connect(DATABASE_PATH_JOBMARKET)
        db.row_factory = sqlite3.Row
    return db

def get_db_airports():
    db = getattr(g, '_database_airports', None)
    if db is None:
        db = g._database_airports = sqlite3.connect(DATABASE_PATH_AIRPORTS)
        db.row_factory = sqlite3.Row
    return db

def get_db_fleet():
    db = getattr(g, '_database_fleet', None)
    if db is None:
        db = g._database_fleet = sqlite3.connect(DATABASE_PATH_FLEET)
        db.row_factory = sqlite3.Row
    return db

def get_db_aircraft():
    db = getattr(g, '_database_aircraft', None)
    if db is None:
        db = g._database_aircraft = sqlite3.connect(app.config['DATABASE_PATH_AIRCRAFT'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(error):
    db_flights = getattr(g, '_database_flights', None)
    if db_flights is not None:
        db_flights.close()

    db_jobs = getattr(g, '_database_jobs', None)
    if db_jobs is not None:
        db_jobs.close()

    db_fleet = getattr(g, '_database_fleet', None)  # Add fleet.db
    if db_fleet is not None:
        db_fleet.close()

def query_db(database_path, query, args=()):
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    conn.close()
    return rows

# Define all routes **before** app.run()
@app.route('/')
def main_menu():
    print("Main menu route accessed")
    return render_template('index.html')

@app.route('/submit-flight-log', methods=['POST'])
def submit_flight_log():
    if request.method == 'POST':
        try:
            departure = request.form['departure']
            destination = request.form['destination']
            date = request.form['date']
            hours = float(request.form['hours'])
            pilotId = request.form['pilotId']
            aircraftType = request.form['aircraftType']
            aircraftIdent = request.form['aircraftIdent']
            flightNumber = request.form['flightNumber']
            takeoffsDay = int(request.form['takeoffsDay'])
            takeoffsNight = int(request.form['takeoffsNight'])
            landingsDay = int(request.form['landingsDay'])
            landingsNight = int(request.form['landingsNight'])
            instrumentApproach = int(request.form['instrumentApproach'])
            job_market_id = request.form.get('jobMarketId')  # Get job ID from form

            # Connect to databases
            conn_flights = get_db_flights()
            conn_pilots = get_db_pilots()
            conn_jobmarket = get_db_jobmarket()
            
            cursor_flights = conn_flights.cursor()
            cursor_pilots = conn_pilots.cursor()
            cursor_jobmarket = conn_jobmarket.cursor()

            # Insert flight log into flights.db
            cursor_flights.execute('''
                INSERT INTO flights (departure, destination, flight_date, flight_hours, pilot_id, aircraft_type, aircraft_ident, flight_number, takeoffs_day, takeoffs_night, landings_day, landings_night, instrument_approaches)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (departure, destination, date, hours, pilotId, aircraftType, aircraftIdent, flightNumber, takeoffsDay, takeoffsNight, landingsDay, landingsNight, instrumentApproach))
            conn_flights.commit()

            # Fetch pilot data
            cursor_pilots.execute("SELECT * FROM pilots WHERE identifier = ?", (pilotId,))
            pilot = cursor_pilots.fetchone()
            if not pilot:
                print("Pilot not found.")
                return jsonify({'success': False, 'message': 'Pilot not found'}), 404

            # Find the completed job from the job market
            completed_job = None
            if job_market_id:
                cursor_jobmarket.execute("SELECT * FROM job_market WHERE jm_id = ?", (job_market_id,))
                completed_job = cursor_jobmarket.fetchone()
            
            # Update pilot's balance, hours, and location
            current_balance = pilot['balance']
            current_hours = pilot['total_hours']
            new_hours = current_hours + hours
            new_rank = get_cpl_rank(new_hours)
            
            # Calculate payment
            payment_amount = 0
            if completed_job:
                payment_amount = completed_job['reward']
            
            # Apply rank multiplier to the payment
            multiplier = get_rank_multiplier(new_rank)
            final_payment = payment_amount * multiplier

            new_balance = current_balance + final_payment

            cursor_pilots.execute('''
                UPDATE pilots SET balance = ?, total_hours = ?, current_location = ?, rank = ? WHERE identifier = ?
            ''', (new_balance, new_hours, destination, new_rank, pilotId))
            conn_pilots.commit()

            # Record ledger entry
            record_ledger_entry('Flight Income', pilotId, final_payment, 0, f"Flight from {departure} to {destination}")

            # Delete completed job from job market
            if completed_job:
                cursor_jobmarket.execute("DELETE FROM job_market WHERE jm_id = ?", (job_market_id,))
                conn_jobmarket.commit()

            return jsonify({'success': True, 'message': 'Flight log submitted successfully.'})

        except Exception as e:
            print(f"Error submitting flight log: {e}")
            return jsonify({'success': False, 'message': f'Error: {e}'})

@app.route('/logbook')
def logbook():
    flights = query_db(DATABASE_PATH_FLIGHTS, "SELECT * FROM flights")
    return render_template('logbook.html', flights=flights)

@app.route('/api/job-market')
def job_market():
    jobs = query_db(DATABASE_PATH_JOBMARKET, "SELECT * FROM job_market")
    job_list = []
    if jobs:
        for job in jobs:
            job_list.append(dict(job))
        return jsonify(job_list)
    else:
        return jsonify({"error": "Could not fetch jobs from the database."})

@app.route('/api/create-pilot', methods=['POST'])
def create_pilot():
    try:
        data = request.json
        print(f"Received request data: {data}")

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({'message': 'All fields are required!'}), 400

        conn = get_db_pilots()
        cursor = conn.cursor()

        # Check if the pilot already exists by email
        cursor.execute("SELECT id FROM pilots WHERE email = ?", (email,))
        existing_pilot = cursor.fetchone()
        if existing_pilot:
            conn.close()
            return jsonify({'success': False, 'message': 'A pilot with that email already exists.'}), 409

        # Encrypt password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Get the highest current AEP number
        cursor.execute("SELECT identifier FROM pilots ORDER BY id DESC LIMIT 1;")
        last_identifier = cursor.fetchone()
        print(f"last_identifier: {last_identifier}")

        if last_identifier and isinstance(last_identifier[0], str) and last_identifier[0].startswith("AEP") and last_identifier[0][3:].isdigit():
            last_number = int(last_identifier[0][3:])
            next_number = last_number + 1
        else:
            next_number = 1

        identifier = f"AEP{str(next_number).zfill(2)}"

        print(f"Generated pilot ID: {identifier}")

        # ❗ CORRECTED INSERT STATEMENT ❗
        # Insert the new pilot with initial values for all columns
        cursor.execute(
            "INSERT INTO pilots (identifier, name, email, password, total_hours, balance, rank, current_location) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (identifier, name, email, hashed_password, 0.0, 50000.0, 'CPL 1', 'LECU')
        )

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Pilot profile created successfully!', 'pilot_id': identifier}), 201
    except Exception as e:
        print(f"Error creating pilot: {e}")
        # A 500 status code indicates a server error, which is appropriate here.
        return jsonify({'success': False, 'message': 'An error occurred while creating the pilot.'}), 500

@app.route('/api/login-pilot', methods=['POST'])
def login_pilot():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Both fields are required!'}), 400

    conn = get_db_pilots()
    cursor = conn.cursor()
    cursor.execute("SELECT identifier, name, rank, email, password, total_hours, balance, current_location FROM pilots WHERE email = ?", (email,))
    pilot = cursor.fetchone()
    conn.close()

    if pilot and bcrypt.checkpw(password.encode('utf-8'), pilot[4]):
        # Always calculate rank from total_hours
        total_hours = pilot[5] or 0
        cpl_rank = get_cpl_rank(total_hours)
        pilot_info = {
            "identifier": pilot[0],
            "name": pilot[1],
            "rank": cpl_rank,
            "email": pilot[3],
            "total_hours": total_hours,
            "balance": pilot[6],
            "current_location": pilot[7]
        }
        return jsonify({'success': True, 'pilot': pilot_info}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401

@app.route('/api/submit-flight-log', methods=['POST'])
def submit_flight_log_api():
    data = request.json
    pilot_id = data['pilot_id']
    departure = data['departure']
    destination = data['destination']
    date = data['date']
    hours = data['hours']
    aircraft_type = data['aircraftType']
    aircraft_ident = data['aircraftIdent']
    flight_number = data['flightNumber']
    takeoffs_day = data['takeoffsDay']
    takeoffs_night = data['takeoffsNight']
    landings_day = data['landingsDay']
    landings_night = data['landingsNight']
    instrument_approach = data['instrumentApproach']
    reward = data.get('reward', 0)

    # Insert flight log into the database
    conn = get_db_flights()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO flights (departure, destination, flight_date, flight_hours, pilot_id, aircraft_type, aircraft_ident, flight_number, takeoffs_day, takeoffs_night, landings_day, landings_night, instrument_approaches)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (departure, destination, date, hours, pilot_id, aircraft_type, aircraft_ident, flight_number, takeoffs_day, takeoffs_night, landings_day, landings_night, instrument_approach))
    conn.commit()

    # Calculate total hours for this pilot
    cursor.execute('SELECT SUM(flight_hours) FROM flights WHERE pilot_id = ?', (pilot_id,))
    total_hours = cursor.fetchone()[0] or 0

    # Update pilot's current_location and total_hours, and balance if reward
    pilots_conn = get_db_pilots()
    pilots_cursor = pilots_conn.cursor()
    pilots_cursor.execute(
        "UPDATE pilots SET current_location = ?, total_hours = ? WHERE identifier = ?",
        (destination, total_hours, pilot_id)
    )

    # Get current balance and rank
    pilots_cursor.execute("SELECT balance, rank FROM pilots WHERE identifier = ?", (pilot_id,))
    pilot_row = pilots_cursor.fetchone()
    current_balance = pilot_row[0] if pilot_row else 0
    current_rank = pilot_row[1] if pilot_row else "Pilot"

    # Add reward if present
    if reward:
        try:
            reward = float(reward)
            # Get pilot's current rank
            pilots_cursor.execute("SELECT rank FROM pilots WHERE identifier = ?", (pilot_id,))
            rank_row = pilots_cursor.fetchone()
            current_rank = rank_row[0] if rank_row else "CPL 1"
            multiplier = get_rank_multiplier(current_rank)

            # Calculate final reward
            final_reward = float(reward) * multiplier
            new_balance = current_balance + final_reward
            pilots_cursor.execute(
                "UPDATE pilots SET balance = ? WHERE identifier = ?",
                (new_balance, pilot_id)
            )
            # --- RECORD LEDGER ENTRY HERE ---
            record_ledger_entry(
                entry_type="Job Reward",
                pilot=pilot_id,
                income=final_reward,
                outgoing=0,
                description=f"Flight log reward for job. From {departure} to {destination}."
            )
        except Exception as e:
            print(f"Error updating balance: {e}")
            new_balance = current_balance
    else:
        new_balance = current_balance

    # Optionally, update rank based on total_hours (example logic)
    new_rank = get_cpl_rank(total_hours)
    pilots_cursor.execute("UPDATE pilots SET rank = ? WHERE identifier = ?", (new_rank, pilot_id))

    pilots_conn.commit()
    pilots_conn.close()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Flight logged and pilot updated.',
        'balance': new_balance,
        'total_hours': total_hours,
        'rank': new_rank,
        'current_location': destination
    }, 200)

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return jsonify({'success': False, 'message': 'Email and new password are required.'}), 400

    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_pilots()
    cursor = conn.cursor()
    cursor.execute("UPDATE pilots SET password = ? WHERE email = ?", (hashed_password, email))
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        return jsonify({'success': True, 'message': 'Password reset successful.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Pilot not found.'}), 404

@app.route('/api/get-pilot-profile')
def get_pilot_profile():
    pilot_id = request.args.get('id')
    conn = get_db_pilots()
    cursor = conn.cursor()
    cursor.execute("SELECT identifier, name, rank, email, password, total_hours, balance, current_location FROM pilots WHERE identifier = ?", (pilot_id,))
    pilot = cursor.fetchone()
    conn.close()
    if pilot:
        total_hours = pilot[5] or 0
        cpl_rank = get_cpl_rank(total_hours)
        return jsonify({
            "identifier": pilot[0],
            "name": pilot[1],
            "rank": cpl_rank,
            "email": pilot[3],
            "total_hours": total_hours,
            "balance": pilot[6],
            "current_location": pilot[7]
        })
    else:
        return jsonify({"error": "Pilot not found"}), 404

@app.route('/api/pilot/<pilot_id>')
def get_pilot_info(pilot_id):
    conn = get_db_pilots()
    cursor = conn.cursor()
    cursor.execute('SELECT identifier, name, rank, email, total_hours, balance, current_location FROM pilots WHERE identifier = ?', (pilot_id,))
    row = cursor.fetchone()
    if row:
        pilot = dict(row)
        return jsonify(pilot)
    else:
        return jsonify({'error': 'Pilot not found'}), 404

# Job scheduler function
def refresh_jobs():
    # Your logic to remove completed jobs and generate new ones
    print("Refreshing jobs...")

def refresh_job_market():
    conn = sqlite3.connect("G:\\MSFSWebApp\\database\\jobmarket.db")
    cursor = conn.cursor()

    # Clear old job market listings
    cursor.execute("DELETE FROM job_market")

    # Fetch random jobs from jobs.db
    jobs_conn = sqlite3.connect("G:\\MSFSWebApp\\database\\jobs.db")
    jobs_cursor = jobs_conn.cursor()
    jobs_cursor.execute("SELECT job_type, description FROM jobs ORDER BY RANDOM() LIMIT 20")
    job_templates = jobs_cursor.fetchall()
    jobs_conn.close()

    # Fetch random airports
    airports_conn = sqlite3.connect("G:\\MSFSWebApp\\database\\airports.db")
    airports_cursor = airports_conn.cursor()
    airports_cursor.execute("SELECT code FROM airports")
    airports = [row[0] for row in airports_cursor.fetchall()]
    airports_conn.close()

    new_jobs = []
    for job_type, description in job_templates:
        departure = random.choice(airports)
        destination = random.choice([a for a in airports if a != departure])
        reward = round(random.uniform(250.0, 750.0), 2)  # Random reward range

        job_id = f"JM{random.randint(1000, 9999)}"
        if job_type == 'Air Taxi':
            passengers = random.randint(1, 5)
            cargo_weight = None
            description = f"{passengers} passengers"
        else:
            passengers = None
            cargo_weight = random.randint(1, 500)
            description = None  # Or a cargo description if needed

        new_jobs.append((
            job_id,
            job_type,
            description,
            cargo_weight,
            departure,
            destination,
            reward,
            "Available"
        ))

    cursor.executemany(
        "INSERT INTO job_market (job_id, job_type, passengers, cargo_weight, departure_airport, destination_airport, reward, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        new_jobs
    )

    conn.commit()
    conn.close()
    print("Daily Job Market refreshed!")

scheduler = BackgroundScheduler()
scheduler.add_job(refresh_jobs, 'interval', hours=24)
scheduler.add_job(refresh_job_market, 'interval', hours=24)
scheduler.start()

import math
import sqlite3
import random

# Haversine formula to calculate distance between two points on the Earth
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance_km = R * c
    return distance_km

def get_airport_coords(icao):
    conn = sqlite3.connect(DATABASE_PATH_AIRPORTS)
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude FROM airports WHERE icao_code = ?", (icao,))
    coords = cursor.fetchone()
    conn.close()
    return coords

def generate_daily_jobs():
    print("Generating daily jobs...")

    # Connect to all databases
    pilots_conn = sqlite3.connect('database/pilots.db')
    pilots_cursor = pilots_conn.cursor()
    jobs_conn = sqlite3.connect('database/jobs.db')
    jobs_cursor = jobs_conn.cursor()
    airports_conn = sqlite3.connect('database/airport.db')
    airports_cursor = airports_conn.cursor()
    jobmarket_conn = sqlite3.connect('database/jobmarket.db')
    jobmarket_cursor = jobmarket_conn.cursor()

    # Clear old jobs
    jobmarket_cursor.execute("DELETE FROM job_market")

    # Fetch all airports with coordinates
    airports_cursor.execute("SELECT icao_code, latitude, longitude FROM airports")
    airports_data = {row[0]: (row[1], row[2]) for row in airports_cursor.fetchall()}
    airports = list(airports_data.keys())

    # Fetch all jobs including their descriptions
    jobs_cursor.execute("SELECT job_id, job_type, description FROM jobs")
    jobs_templates = jobs_cursor.fetchall()
    
    # Fetch all pilots and their locations
    pilots_cursor.execute("SELECT identifier, current_location FROM pilots")
    pilots = pilots_cursor.fetchall()

    new_jobs = []
    
    for pilot_id, current_location in pilots:
        job_template = random.choice(jobs_templates)
        job_id, job_type, job_description = job_template # Unpack the description here
        
        departure = current_location
        possible_destinations = [a for a in airports if a != departure]
        if not possible_destinations:
            continue
        destination = random.choice(possible_destinations)

        dep_coords = airports_data.get(departure)
        dest_coords = airports_data.get(destination)

        if not dep_coords or not dest_coords:
            print(f"Skipping job from {departure} to {destination} due to missing coordinates.")
            continue
            
        distance_km = calculate_distance(dep_coords[0], dep_coords[1], dest_coords[0], dest_coords[1])
        
        passengers = None
        cargo_weight = None

        if job_type == 'Air Taxi':
            passengers = random.randint(1, 5)
            reward = round(500 + (1.5 * distance_km) + (200 * passengers), 2)
            # Use the description from the database as a base
            final_description = f"{passengers} passengers - {job_description}"
        else: # Cargo
            cargo_weight = random.randint(1, 500)
            reward = round(400 + (1.0 * distance_km) + (1.0 * cargo_weight), 2)
            # Use the database description
            final_description = job_description

        jm_id = f"JM{random.randint(1000, 9999)}"

        new_jobs.append((
            jm_id, job_id, job_type, final_description, cargo_weight,
            departure, destination, reward, "Available", None
        ))
    
    # Add the farm produce jobs
    farm_produce_jobs = [
        ('LESL', 'LECU'), 
        ('LEMU', 'LEMG'),
        ('LEJU', 'LELL'),
        ('LERE', 'LEVC'),
        ('LECS', 'LECU')
    ]
    
    # Use a fixed job_id for farm jobs
    farm_job_id = "AE0025" 
    jobs_cursor.execute("SELECT description FROM jobs WHERE job_id = ?", (farm_job_id,))
    farm_description = jobs_cursor.fetchone()[0]

    for dep, dest in farm_produce_jobs:
        dep_coords = airports_data.get(dep)
        dest_coords = airports_data.get(dest)

        if not dep_coords or not dest_coords:
            continue
            
        distance_km = calculate_distance(dep_coords[0], dep_coords[1], dest_coords[0], dest_coords[1])
        
        # ❗ UPDATED CODE: Generate a random weight ❗
        # Random weight between 100 kg and the max payload of the Piper 34T (523 kg)
        weight = random.randint(100, 523)
        reward = round(600 + (1.2 * distance_km) + (1.5 * weight), 2)
        
        # Now, the description is simply pulled from the database
        jm_id = f"FARM{random.randint(1000, 9999)}"
        new_jobs.append((
            jm_id, farm_job_id, 'Cargo', farm_description, weight,
            dep, dest, reward, "Available", None
        ))

    jobmarket_cursor.executemany('''
        INSERT INTO job_market (
            jm_id, job_id, job_type, job_description, cargo_weight,
            departure_airport, destination_airport, reward, status, assigned_pilot
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', new_jobs)

    jobmarket_conn.commit()
    pilots_conn.close()
    jobs_conn.close()
    airports_conn.close()
    jobmarket_conn.close()
    print(f"Generated {len(new_jobs)} jobs in job_market.")

# Schedule the job generator every 24 hours
scheduler = BackgroundScheduler()
scheduler.add_job(generate_daily_jobs, 'interval', hours=24)
scheduler.start()

# Optionally, run once at startup
generate_daily_jobs()

# Flask app execution (RUN THIS LAST)

@app.route('/dashboard')
def dashboard():
    # For now, use dummy data. Later, fetch from DB or session.
    pilot = {
        "identifier": "AEP01",
        "name": "Mark Jones",
        "rank": "First Officer",
        "email": "mjones@email.com"
    }
    return render_template('dashboard.html', pilot=pilot)


# Fleet Routes (Must be Above `app.run(debug=True)`)
@app.route('/api/fleet', methods=['GET'])
def get_fleet():
    conn = sqlite3.connect(DATABASE_PATH_FLEET)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fleet")
    fleet_data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(fleet_data)

@app.route('/api/fleet/add', methods=['POST'])
def add_aircraft():
    data = request.json
    aircraft_ident = data['aircraft_ident']
    # Fetch the type and description from the aircraft table
    conn_aircraft = sqlite3.connect(DATABASE_PATH_AIRCRAFT)
    cursor_aircraft = conn_aircraft.cursor()
    cursor_aircraft.execute("SELECT type, description FROM aircraft WHERE aircraft_ident = ? OR id = ?", (aircraft_ident, aircraft_ident))
    row = cursor_aircraft.fetchone()
    aircraft_type = row[0] if row else None
    aircraft_description = row[1] if row else None
    conn_aircraft.close()

    conn = sqlite3.connect(DATABASE_PATH_FLEET)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO fleet (aircraft_ident, aircraft_model, status, type, description) VALUES (?, ?, 'Free', ?, ?)",
        (aircraft_ident, aircraft_description, aircraft_type, aircraft_description)
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/fleet/book', methods=['POST'])
def book_aircraft():
    data = request.json
    aircraft_ident = data['aircraft_ident']
    owner_id = data['owner_id']
    conn = sqlite3.connect(DATABASE_PATH_FLEET)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE fleet SET status='Booked', owner_id=? WHERE aircraft_ident=? AND status='Free'",
        (owner_id, aircraft_ident)
    )
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return jsonify({'success': updated > 0})

@app.route('/api/fleet/sell', methods=['POST'])
def sell_aircraft():
    data = request.json
    aircraft_ident = data['aircraft_ident']
    pilot_id = data['pilot_id']

    conn = sqlite3.connect(DATABASE_PATH_FLEET)
    cursor = conn.cursor()
    cursor.execute("SELECT hours_flown, condition FROM fleet WHERE aircraft_ident=? AND owner_id=?", (aircraft_ident, pilot_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'Aircraft not found or not owned by pilot.'}), 404

    total_hours, condition = row
    # Calculate sale price: higher for low hours and high condition
    base_price = 200000  # Example base price, adjust as needed
    hours_factor = max(0.5, 1 - (total_hours / 10000))  # 0.5 at 10,000 hours, 1 at 0 hours
    condition_factor = condition / 100.0
    sale_price = int(base_price * hours_factor * condition_factor)

    # Remove aircraft from fleet
    cursor.execute("DELETE FROM fleet WHERE aircraft_ident=? AND owner_id=?", (aircraft_ident, pilot_id))
    conn.commit()
    conn.close()

    # Update pilot balance
    conn_pilot = get_db_pilots()
    cursor_pilot = conn_pilot.cursor()
    cursor_pilot.execute("UPDATE pilots SET balance = balance + ? WHERE identifier = ?", (sale_price, pilot_id))
    conn_pilot.commit()
    conn_pilot.close()

    # Record ledger entry
    record_ledger_entry(
        entry_type="Aircraft Sale",
        pilot=pilot_id,
        income=sale_price,
        outgoing=0,
        description=f"Sold aircraft {aircraft_ident} for {sale_price}€"
    )

    return jsonify({'success': True, 'sale_price': sale_price})

@app.route('/marketplace')
def marketplace():
    # You can later fetch real data from DB
    return render_template('marketplace.html')

@app.route('/api/marketplace/new', methods=['GET'])
def get_new_aircraft():
    conn = get_db_aircraft()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, description, manufacturer, type, cost_new, lease_price, mtow
        FROM aircraft
        WHERE for_sale = 1 AND is_new = 1
    """)
    aircraft = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(aircraft)

@app.route('/api/marketplace/private', methods=['GET'])
def get_private_sale_aircraft():
    conn = get_db_aircraft()
    cursor = conn.cursor()
    # Select 10 random aircraft that are for sale (regardless of is_new)
    cursor.execute("""
        SELECT id, description, manufacturer, type, cost_new, mtow
        FROM aircraft
        WHERE for_sale = 1
        ORDER BY RANDOM() LIMIT 10
    """)
    aircraft = []
    for row in cursor.fetchall():
        base_price = row['cost_new']
        condition = random.randint(60, 99)  # Random condition between 60% and 99%
        used_price = round(base_price * (condition / 100), 0) # Used price based on condition
        hours_flown = random.randint(500, 8000)  # Random hours flown
        aircraft.append({
            'id': row['id'],
            'description': row['description'],
            'manufacturer': row['manufacturer'],
            'type': row['type'],
            'cost_new': base_price,
            'mtow': row['mtow'],
            'used_price': used_price,
            'condition': condition,
            'hours_flown': hours_flown
        })
    conn.close()
    return jsonify(aircraft)

@app.route('/api/aircraft/<int:aircraft_id>', methods=['GET'])
def get_aircraft_by_id(aircraft_id):
    conn = get_db_aircraft()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aircraft WHERE id = ?", (aircraft_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        ac = dict(row)
        # For private sale, generate used_price, condition, hours_flown if needed
        return jsonify(ac)
    else:
        return jsonify({'error': 'Aircraft not found'}), 404


@app.route('/api/marketplace/buy', methods=['POST'])
def buy_aircraft():
    data = request.json
    pilot_id = data['pilot_id']
    aircraft_id = data['aircraft_id']
    ac_type = data['type']
    model = data.get('model')
    condition = data.get('condition')
    hours_flown = data.get('hours_flown')

    # Fetch pilot info
    conn_pilot = get_db_pilots()
    cursor_pilot = conn_pilot.cursor()
    cursor_pilot.execute("SELECT rank, balance FROM pilots WHERE identifier = ?", (pilot_id,))
    pilot = cursor_pilot.fetchone()
    if not pilot:
        return jsonify({'success': False, 'message': 'Pilot not found.'}), 404

    # Fetch aircraft info (get MTOW, cost_new)
    conn_ac = get_db_aircraft()
    cursor_ac = conn_ac.cursor()
    cursor_ac.execute("SELECT mtow, cost_new, type FROM aircraft WHERE id = ?", (aircraft_id,))
    ac = cursor_ac.fetchone()
    if not ac:
        return jsonify({'success': False, 'message': 'Aircraft not found.'}), 404

    mtow, cost_new, db_type = ac

    # Check rank unlock using MTOW
    if not can_pilot_access_aircraft_by_mtow(pilot[0], mtow):
        return jsonify({'success': False, 'message': 'Rank too low for this aircraft.'}), 403

    # Calculate price
    if ac_type == 'private':
        price = data.get('price') or cost_new
    else:
        price = cost_new

    # Check balance
    if pilot[1] < price:
        return jsonify({'success': False, 'message': 'Insufficient balance.'}), 403

    # Deduct balance and record purchase (add to fleet, etc.)
    new_balance = pilot[1] - price
    cursor_pilot.execute("UPDATE pilots SET balance = ? WHERE identifier = ?", (new_balance, pilot_id))
    conn_pilot.commit()

    # --- RECORD LEDGER ENTRY HERE ---
    record_ledger_entry(
        entry_type="Aircraft Purchase",
        pilot=pilot_id,
        income=0,
        outgoing=price,
        description=f"Purchased aircraft ID {aircraft_id} ({ac_type} sale)"
    )

    # --- ADD AIRCRAFT TO FLEET ---
    conn_fleet = sqlite3.connect(DATABASE_PATH_FLEET)
    cursor_fleet = conn_fleet.cursor()
    cursor_fleet.execute(
    "INSERT INTO fleet (aircraft_ident, aircraft_model, status, owner_id, Hours_Flown, last_a_check, last_b_check, last_c_check, maintenance_required, type, Condition) VALUES (?, ?, 'Free', ?, ?, 0, 0, 0, 0, ?, ?)",
    (aircraft_id, model, pilot_id, hours_flown, db_type, condition)
)
    conn_fleet.commit()
    conn_fleet.close()

    conn_pilot.close()
    conn_ac.close()
    return jsonify({'success': True})

# Utility function for fleet insert (to avoid code duplication)
def insert_into_fleet(aircraft_id, pilot_id):
    conn_ac = get_db_aircraft()
    cursor_ac = conn_ac.cursor()
    cursor_ac.execute("SELECT description, type FROM aircraft WHERE id = ?", (aircraft_id,))
    row = cursor_ac.fetchone()
    description = row['description'] if row else ''
    ac_type = row['type'] if row else ''
    conn_ac.close()

    conn_fleet = sqlite3.connect(DATABASE_PATH_FLEET)
    cursor_fleet = conn_fleet.cursor()
    cursor_fleet.execute(
    "INSERT INTO fleet (aircraft_ident, aircraft_model, status, owner_id, Hours_Flown, last_a_check, last_b_check, last_c_check, maintenance_required, description, type) VALUES (?, ?, 'Free', ?, 0, 0, 0, 0, 0, ?, ?)",
    (aircraft_id, pilot_id, ac_type)
    )
    conn_fleet.commit()
    conn_fleet.close()

def record_ledger_entry(entry_type, pilot, income, outgoing, description):
    import sqlite3
    from datetime import datetime
    conn = sqlite3.connect('database/ledger.db')
    cursor = conn.cursor()
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    cursor.execute(
        "INSERT INTO ledger (type, datetime, pilot, income, outgoing, description) VALUES (?, ?, ?, ?, ?, ?)",
        (entry_type, now, pilot, income, outgoing, description)
    )
    conn.commit()
    conn.close()

def get_required_cpl_rank_for_mtow(mtow):
    if mtow <= 5500:
        return 4
    elif mtow <= 75000:
        return 8
    else:
        return 12

def can_pilot_access_aircraft_by_mtow(pilot_rank, mtow):
    try:
        rank_num = int(str(pilot_rank).replace('CPL ', ''))
    except Exception:
        return False
    required_rank = get_required_cpl_rank_for_mtow(mtow)
    return rank_num <= required_rank

# Only ONE app.run block at the very end!
if __name__ == "__main__":
    app.run(debug=True)
    print(app.url_map)



