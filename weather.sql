CREATE DATABASE weather_forecasting;

USE weather_forecasting;

CREATE TABLE weather_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    temperature DECIMAL(5,2),
    feels_like DECIMAL(5,2),
    humidity INT,
    wind_speed DECIMAL(6,2),
    pressure INT,
    weather_condition VARCHAR(100),
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT *
FROM weather_history
ORDER BY searched_at DESC;

SHOW TABLES;


SELECT *
FROM weather_history
WHERE city = 'Jaipur';

UPDATE weather_history
SET temperature = 33.00
WHERE city = 'Jaipur'
LIMIT 1;

SELECT id, city, temperature
FROM weather_history
WHERE city = 'Jaipur';

DELETE FROM weather_history
WHERE city = 'Jaipur'
LIMIT 1;


SELECT *
FROM weather_history
WHERE city = 'Jaipur';


