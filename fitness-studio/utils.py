import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_booking_entry(entry):
    required_fields = ['class_id', 'client_name', 'client_email']
    errors = []

    for field in required_fields:
        if field not in entry:
            errors.append(f"Missing required field {field}")
            return errors
        
    # type validation
    if not isinstance(entry['class_id'], int):
        errors.append("class_id must be an integer")

    elif not isinstance(entry['client_name'], str) or not entry['client_name'].strip():
        errors.append("client_name must be a non-empty string")

    elif not isinstance(entry['client_email'], str) or not entry['client_email'].strip():
        errors.append("client_email must be a non-empty string")
    elif not EMAIL_REGEX.match(entry['client_email']):
        errors.append("Invalid email format")

    return errors
