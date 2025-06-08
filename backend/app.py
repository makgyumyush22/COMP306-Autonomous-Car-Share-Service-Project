from flask import Flask, request, jsonify
from flask_cors import CORS
from db import conn, cursor

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Flask backend is running."

@app.route("/cars/list", methods=["GET"])
def list_all_available_cars():
    query = """
        SELECT c.car_id, c.model, c.capacity, c.price_rate, c.photo_URL, 
               l.name AS location_name, l.latitude, l.longitude
        FROM Car c
        JOIN Location l ON c.current_location_id = l.location_id
        WHERE c.is_available = TRUE
    """
    cursor.execute(query)
    return jsonify(cursor.fetchall())

@app.route("/user/<int:user_id>", methods=["GET"])
def get_user_info(user_id):
    query = "SELECT user_id, name, email, phone, license_number, registration_date FROM User WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    return jsonify(cursor.fetchone())

@app.route("/user/<int:user_id>/payment_methods", methods=["GET"])
def get_user_payment_methods(user_id):
    query = """
        SELECT method_id, card_number, card_type 
        FROM PaymentMethod 
        WHERE user_id = %s
    """
    cursor.execute(query, (user_id,))
    return jsonify(cursor.fetchall())

@app.route("/user/<int:user_id>/reservations", methods=["GET"])
def get_past_reservations(user_id):
    query = """
        SELECT r.reservation_id, r.start_time, r.end_time, r.trip_cost,
               c.model AS car_model, l1.name AS pickup, l2.name AS dropoff,
               rp.method_id, pm.card_type, pm.card_number
        FROM Reservation r
        JOIN Car c ON r.car_id = c.car_id
        JOIN Location l1 ON r.pickup_location_id = l1.location_id
        JOIN Location l2 ON r.dropoff_location_id = l2.location_id
        JOIN ReservationPayment rp ON r.reservation_id = rp.reservation_id
        JOIN PaymentMethod pm ON rp.method_id = pm.method_id
        WHERE r.user_id = %s
        ORDER BY r.start_time DESC
    """
    cursor.execute(query, (user_id,))
    return jsonify(cursor.fetchall())

@app.route("/user/<int:user_id>/active_reservation", methods=["GET"])
def get_active_reservation(user_id):
    query = """
        SELECT r.reservation_id, r.start_time, r.end_time, r.trip_cost,
               c.model AS car_model, l1.name AS pickup, l2.name AS dropoff
        FROM Reservation r
        JOIN Car c ON r.car_id = c.car_id
        JOIN Location l1 ON r.pickup_location_id = l1.location_id
        JOIN Location l2 ON r.dropoff_location_id = l2.location_id
        WHERE r.user_id = %s AND NOW() BETWEEN r.start_time AND r.end_time
        LIMIT 1
    """
    cursor.execute(query, (user_id,))
    return jsonify(cursor.fetchone())

@app.route("/available_cars", methods=["GET"])
def available_cars():
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)

    query = """
        SELECT c.*, l.latitude, l.longitude,
               (111.111 * SQRT(POW(l.latitude - %s, 2) + POW(l.longitude - %s, 2))) AS distance_km
        FROM Car c
        JOIN Location l ON c.current_location_id = l.location_id
        WHERE c.is_available = TRUE
        ORDER BY distance_km ASC
    """
    cursor.execute(query, (user_lat, user_lon))
    return jsonify(cursor.fetchall())

@app.route("/available_cars/city_distance", methods=["GET"])
def cars_by_city_distance():
    city_name = request.args.get("city")
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)

    if not city_name or user_lat is None or user_lon is None:
        return jsonify({"error": "Missing required parameters"}), 400

    query = """
        SELECT c.*, l.city_name,
               (111.111 * SQRT(POW(l.latitude - %s, 2) + POW(l.longitude - %s, 2))) AS distance_km
        FROM Car c
        JOIN Location l ON c.current_location_id = l.location_id
        WHERE l.city_name = %s AND c.is_available = TRUE
        ORDER BY distance_km ASC;
    """
    cursor.execute(query, (user_lat, user_lon, city_name))
    return jsonify(cursor.fetchall())

@app.route("/available_cars/price_distance", methods=["GET"])
def cars_by_price_distance():
    min_price = request.args.get("min", type=float)
    max_price = request.args.get("max", type=float)
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)

    if min_price is None or max_price is None or user_lat is None or user_lon is None:
        return jsonify({"error": "Missing required parameters"}), 400

    query = """
        SELECT c.*, 
               (111.111 * SQRT(POW(l.latitude - %s, 2) + POW(l.longitude - %s, 2))) AS distance_km
        FROM Car c
        JOIN Location l ON c.current_location_id = l.location_id
        WHERE c.price_rate BETWEEN %s AND %s AND c.is_available = TRUE
        ORDER BY distance_km ASC;
    """
    cursor.execute(query, (user_lat, user_lon, min_price, max_price))
    return jsonify(cursor.fetchall())
  
@app.route("/reserve", methods=["POST"])
def create_reservation():
    data = request.get_json()

    required_fields = [
        "user_id", "car_id", "start_time", "end_time",
        "pickup_location_id", "dropoff_location_id",
        "trip_cost", "trip_distance_km"
    ]

    # Check all required fields are present
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required reservation fields"}), 400

    try:
        query = """
            INSERT INTO Reservation (
                user_id, car_id, start_time, end_time,
                pickup_location_id, dropoff_location_id,
                trip_cost, trip_distance_km
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data["user_id"],
            data["car_id"],
            data["start_time"],
            data["end_time"],
            data["pickup_location_id"],
            data["dropoff_location_id"],
            data["trip_cost"],
            data["trip_distance_km"]
        )

        cursor.execute(query, values)
        conn.commit()

        return jsonify({"message": "Reservation created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reservations/<int:user_id>", methods=["GET"])
def get_user_reservations(user_id):
    query = """
        SELECT
            r.reservation_id,
            r.start_time,
            r.end_time,
            r.trip_cost,
            r.trip_distance_km,
            c.model AS car_model,
            c.make AS car_make,
            pl.name AS pickup_location,
            dl.name AS dropoff_location
        FROM Reservation r
        JOIN Car c ON r.car_id = c.car_id
        JOIN Location pl ON r.pickup_location_id = pl.location_id
        JOIN Location dl ON r.dropoff_location_id = dl.location_id
        WHERE r.user_id = %s
        ORDER BY r.start_time DESC
    """
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    return jsonify(results)

@app.route("/stations", methods=["GET"])
def get_charging_stations():
    query = """
        SELECT
            cs.station_id,
            l.name AS location_name,
            l.latitude,
            l.longitude,
            cs.num_ports,
            cs.power_output_kw,
            cs.status
        FROM Charging_Station cs
        JOIN Location l ON cs.location_id = l.location_id
    """
    cursor.execute(query)
    stations = cursor.fetchall()
    return jsonify(stations)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
