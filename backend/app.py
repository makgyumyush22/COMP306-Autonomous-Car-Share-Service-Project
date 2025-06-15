from flask import Flask, request, jsonify
from flask_cors import CORS
from db import conn, cursor

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Flask backend is running."

@app.route("/user/<int:user_id>", methods=["GET"])
def get_user_info(user_id):
    query = "SELECT * FROM User WHERE user_id = %s"
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
        SELECT r.reservation_id, r.start_time, r.end_time,
               c.model AS car_model,
               l1.city_name AS pickup_city, l2.city_name AS dropoff_city,
               l1.name AS pickup_location, l2.name AS dropoff_location,
               rp.trip_cost, pm.card_type, pm.card_number
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
        SELECT r.reservation_id, r.start_time, r.end_time,
               c.model AS car_model,
               l1.city_name AS pickup_city, l2.city_name AS dropoff_city,
               l1.name AS pickup_location, l2.name AS dropoff_location,
               rp.trip_cost, pm.card_type, pm.card_number
        FROM Reservation r
        JOIN Car c ON r.car_id = c.car_id
        JOIN Location l1 ON r.pickup_location_id = l1.location_id
        JOIN Location l2 ON r.dropoff_location_id = l2.location_id
        JOIN ReservationPayment rp ON r.reservation_id = rp.reservation_id
        JOIN PaymentMethod pm ON rp.method_id = pm.method_id
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
        SELECT c.*, l.city_name, l.name AS location_name,
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
        SELECT c.*, l.city_name, l.name AS location_name,
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
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)

    if min_price is None or max_price is None or user_lat is None or user_lon is None:
        return jsonify({"error": "Missing required parameters"}), 400

    query = """
        SELECT c.*, l.city_name, l.name AS location_name,
               (111.111 * SQRT(POW(l.latitude - %s, 2) + POW(l.longitude - %s, 2))) AS distance_km
        FROM Car c
        JOIN Location l ON c.current_location_id = l.location_id
        WHERE c.price_rate BETWEEN %s AND %s AND c.is_available = TRUE
        ORDER BY distance_km ASC;
    """
    cursor.execute(query, (user_lat, user_lon, min_price, max_price))
    return jsonify(cursor.fetchall())

@app.route("/available_cars/capacity_distance", methods=["GET"])
def cars_by_capacity_distance():
    capacity = request.args.get("capacity", type=int)
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)

    if capacity is None or user_lat is None or user_lon is None:
        return jsonify({"error": "Missing required parameters"}), 400

    query = """
        SELECT c.*, l.city_name, l.name AS location_name,
               (111.111 * SQRT(POW(l.latitude - %s, 2) + POW(l.longitude - %s, 2))) AS distance_km
        FROM Car c
        JOIN Location l ON c.current_location_id = l.location_id
        WHERE c.capacity >= %s AND c.is_available = TRUE
        ORDER BY distance_km ASC;
    """
    cursor.execute(query, (user_lat, user_lon, capacity))
    return jsonify(cursor.fetchall())
  
@app.route("/reserve", methods=["POST"])
def create_reservation():
    data = request.get_json()

    required_fields = [
        "user_id", "car_id", "start_time", "end_time",
        "pickup_location_id", "dropoff_location_id",
        "trip_cost", "method_id"
    ]

    # Check all required fields are present
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required reservation fields"}), 400

    try:
        query_reservation = """
            INSERT INTO Reservation (
                user_id, car_id,
                pickup_location_id, dropoff_location_id,
                start_time, end_time
            ) VALUES (%s, %s, %s, %s, %s, %s);
        """
        values_reservation = (
            data["user_id"],
            data["car_id"],
            data["pickup_location_id"],
            data["dropoff_location_id"],
            data["start_time"],
            data["end_time"]
        )

        cursor.execute(query_reservation, values_reservation)

        query_payment = """
            INSERT INTO reservationpayment (
                reservation_id, method_id, trip_cost
            ) VALUES (%s, %s, %s);
        """
        values_payment = (
            cursor.lastrowid,
            data["method_id"],
            data["trip_cost"]
        )
        
        cursor.execute(query_payment, values_payment)
        conn.commit()

        return jsonify({"message": "Reservation created successfully"}), 201

    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/stations", methods=["GET"])
def get_charging_stations():
    query = """
        SELECT
            cs.station_id,
            l.city_name,
            l.name AS location_name,
            l.latitude,
            l.longitude
        FROM Charging_Station cs
        JOIN Location l ON cs.location_id = l.location_id
    """
    cursor.execute(query)
    stations = cursor.fetchall()
    return jsonify(stations)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
