CREATE DATABASE bmi_app;
USE bmi_app;

CREATE TABLE bmi_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    weight FLOAT,
    height FLOAT,
    bmi FLOAT,
    category VARCHAR(50),
    unit_system VARCHAR(10),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
