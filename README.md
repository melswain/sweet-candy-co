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