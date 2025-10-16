# Sweet Candy Co.

This project is a Raspberry Pi-based IoT system for managing customer data in a smart store. It is a candy store called Sweet Candy Co. It uses Python, MySQL, and GPIO hardware feedback (LEDs, buzzers) to provide real-time interaction and alerts.

## Features

- Add new customers to the MySQL database
- Trigger hardware feedback (blue LED for success, red LED + buzzer for failure)
- MVC architecture
- Environment-based configuration

## Dependencies

Install all required packages using pip:

```bash
pip install sqlalchemy pymysql python-dotenv RPi.GPIO
```

## Configuration

Make sure to create a .env file that contains the necessary information.
- DB_HOST
- DB_PORT
- DB_USER
- DB_PASSWORD

## Using a Flask Server

1. Make sure Flask in installed: ```bash pip install flask```
2. Set up the .env file by installing python-dotenv ```bash pip install python-dotenv```
3. Include the Flask secret key in the .env as FLASK_SECRET_KEY
4. d
