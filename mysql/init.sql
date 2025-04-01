CREATE DATABASE company;
USE company;

CREATE TABLE Department (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Employee (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    salary DECIMAL(10,2),
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
);

INSERT INTO Department (name) VALUES
    ('IT'),
    ('HR'),
    ('Finance');

INSERT INTO Employee (name, email, salary, dept_id) VALUES
    ('Alice', 'alice@example.com', 60000, 1),
    ('Bob', 'bob@example.com', 50000, 2),
    ('Charlie', 'charlie@example.com', 70000, 1),
    ('David', 'david@example.com', 55000, 3);
