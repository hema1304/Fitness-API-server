# Fitness-API-server
Fitness-API-server is a RESTful Flask-based API designed to manage and streamline the booking of fitness classes.
<br>

##  Features<br>

  * View Available Classes (with timezone support)
  
  *  Book Classes with validation checks
  
  *  Fetch Bookings by Email
  
  *  Auto-seeds database from data.json if empty
  
  *  Input validation (including email format & slot availability)
  
  *  Detailed logging for debugging and traceability
    
## API Endpoints

  * GET /classes?tz=&lt;timezone&gt;
  * POST /book
  * GET /bookings?email=&lt;email&gt;

## Run Tests
  * cd fitness-studio
  * python -m pytest .\test_app.py


