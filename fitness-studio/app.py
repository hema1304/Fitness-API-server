from flask import Flask,jsonify,request,Response
from datetime import datetime
# from data import classes,bookings
from models import db, FitnessClass, Booking
from collections import OrderedDict
from utils import validate_booking_entry
import pytz ,json
import logging,re
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_studio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Initialize DB & create tables
@app.before_request
def create_tables():
    db.create_all()
    
    # Only insert if no data exist
    if not FitnessClass.query.first():
        try:
            with open('data.json') as f:
                class_data = json.load(f)
                for item in class_data:
                    db.session.add(FitnessClass(
                        id=item["id"],
                        name=item["name"],
                        datetime=item["datetime"],
                        instructor=item["instructor"],
                        available_slots=item["available_slots"]
                    ))
                db.session.commit()
                logging.info("Seeded data from data.json")
        except Exception as e:
           logging.error(f"Error loading JSON file: {e}")
    



@app.route('/classes', methods=['GET'])
def get_classes():
    user_tz = request.args.get('tz', 'Asia/Kolkata')  # Default to IST
    logging.info(f"GET /classes requested with timezone: {user_tz}")
    try:
        target_timezone = pytz.timezone(user_tz)
    except pytz.UnknownTimeZoneError:
        logging.error(f"Unknown timezone: {user_tz}")
        return jsonify({"error": f"Unknown timezone: {user_tz}"}), 400
    
    ist = pytz.timezone("Asia/Kolkata")
    classes = FitnessClass.query.all()
    converted_classes = []
    for c in classes:
        # Parse and localize datetime in IST
        try:
            ist_time = ist.localize(datetime.strptime(c.datetime, "%Y-%m-%d %H:%M"))
        except Exception as e:
            return jsonify({"error": f"Invalid datetime format in class data: {str(e)}"}), 500
        # Convert to user's timezone
        local_time = ist_time.astimezone(target_timezone)

        converted_classes.append(OrderedDict([
        ("id", c.id),
        ("name", c.name),
        ("datetime", local_time.strftime("%Y-%m-%d %H:%M %Z")),
        ("instructor", c.instructor),
        ("available_slots", c.available_slots)
        ]))
    
    return Response(
        json.dumps(converted_classes, ensure_ascii=False),
        content_type='application/json'
    )


@app.route('/book', methods=['POST'])
def book_class():
    logging.info("POST /book called")
    
    if not request.data or request.data.strip() == b'':
        return jsonify({"error": "Empty or missing JSON body"}), 400

    try:
        data = request.get_json()
    except Exception as e:
        logging.error(f"Malformed JSON received: {e}")
        return jsonify({"error": f"Malformed JSON : {str(e)}"}), 400

   
    if not isinstance(data, list):
        data = [data]  # Handle single booking as well

    responses = []
    for entry in data:
        errors = validate_booking_entry(entry)
        if errors:
            logging.error(f"Validation errors found: {errors}")
            return jsonify({"error": errors, "entry": entry}), 400

        class_id = entry['class_id']
        client_name = entry['client_name']
        client_email = entry['client_email']
        
        # Find the class
        fitness_class = FitnessClass.query.get(class_id)
        if not fitness_class:
            responses.append({"error": f"Class ID {class_id} not found"})
            continue

        # Check for available slots
        if fitness_class.available_slots <= 0:
            responses.append({"error": f"No slots available for the class: {fitness_class.name}"})
            continue

        # Book a slot
        fitness_class.available_slots -= 1
        booking = Booking(
            class_id=class_id,
            class_name=fitness_class.name,
            client_name=client_name,
            client_email=client_email
        )
        db.session.add(booking)
        db.session.commit()
        logging.info(f"Booking confirmed for {client_name} ({client_email}) for class {fitness_class.name}")
        responses.append({
            "message": "Booking confirmed",
            "class_id": class_id,
            "class_name": fitness_class.name,
            "client_name": client_name,
            "client_email": client_email
        })
    return jsonify(responses), 201



@app.route('/bookings',methods=['GET'])
def get_bookings():
    email = request.args.get('email')
    logging.info(f"GET /bookings called with email: {email}")
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400
    
    #validate the format of email
    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    
    
    #case sensitive match
    user_bookings = Booking.query.filter(Booking.client_email.like(email)).all()
    
    if not user_bookings:
        return jsonify({"error": f"No bookings found for the provided email: {email}"}), 404

    return jsonify([{
        "class_id": b.class_id,
        "class_name": b.class_name,
        "client_name": b.client_name,
        "client_email": b.client_email
    } for b in user_bookings])


if __name__ == '__main__':
    app.run(debug=True)