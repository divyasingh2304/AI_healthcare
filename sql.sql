DROP DATABASE IF EXISTS healthcare;
CREATE DATABASE healthcare;
USE healthcare;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100),
    fees INT,
    available_from TIME,
    available_to TIME
);

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(100),
    doctor_name VARCHAR(100),
    specialization VARCHAR(100),
    doctor_fees INT,
    appointment_date DATE,
    appointment_time TIME,
    status VARCHAR(50) DEFAULT 'Pending',
    meet_link VARCHAR(255),
    login_user VARCHAR(100)
);

CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(100),
    receiver VARCHAR(100),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT,
    user_name VARCHAR(100),
    rating INT,
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO admins (full_name, email, password)
VALUES ('Rajesh Singh', 'admin@gmail.com', '123');

INSERT INTO users (name, email, password)
VALUES ('Rahul', 'rahul@gmail.com', '123');

INSERT INTO doctors (name, specialization, fees, available_from, available_to)
VALUES
('Dr. Mehta', 'Cardiologist', 800, '10:00:00', '14:00:00'),
('Dr. Singh', 'Dermatologist', 600, '09:00:00', '13:00:00'),
('Dr. Sharma', 'Orthopedic', 700, '11:00:00', '15:00:00'),
('Dr. Priya Mehta', 'Gynecologist', 900, '12:00:00', '16:00:00'),
('Dr. Raj Kumar', 'Neurologist', 1000, '10:00:00', '17:00:00'),
('Dr. Anjali Verma', 'Pediatrician', 500, '08:00:00', '12:00:00'),
('Dr. Rohan Das', 'ENT Specialist', 650, '13:00:00', '18:00:00');

DROP DATABASE IF EXISTS healthcare;
CREATE DATABASE healthcare;
USE healthcare;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100),
    fees INT,
    available_from TIME,
    available_to TIME
);

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(100),
    doctor_name VARCHAR(100),
    specialization VARCHAR(100),
    doctor_fees INT,
    appointment_date DATE,
    appointment_time TIME,
    status VARCHAR(50) DEFAULT 'Pending',
    meet_link VARCHAR(255),
    login_user VARCHAR(100)
);

CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(100),
    receiver VARCHAR(100),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT,
    user_name VARCHAR(100),
    rating INT,
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO admins (full_name, email, password)
VALUES ('Rajesh Singh', 'admin@gmail.com', '123');

INSERT INTO users (name, email, password)
VALUES ('Rahul', 'rahul@gmail.com', '123');

INSERT INTO doctors (name, specialization, fees, available_from, available_to)
VALUES
('Dr. Mehta', 'Cardiologist', 800, '10:00:00', '14:00:00'),
('Dr. Singh', 'Dermatologist', 600, '09:00:00', '13:00:00'),
('Dr. Sharma', 'Orthopedic', 700, '11:00:00', '15:00:00'),
('Dr. Priya Mehta', 'Gynecologist', 900, '12:00:00', '16:00:00'),
('Dr. Raj Kumar', 'Neurologist', 1000, '10:00:00', '17:00:00'),
('Dr. Anjali Verma', 'Pediatrician', 500, '08:00:00', '12:00:00'),
('Dr. Rohan Das', 'ENT Specialist', 650, '13:00:00', '18:00:00');

CREATE TABLE contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    message TEXT
);
ALTER TABLE contact_messages ADD reply TEXT;

SELECT * FROM users;
DESCRIBE users;