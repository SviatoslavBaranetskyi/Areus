-- Create Database 1
CREATE DATABASE IF NOT EXISTS Company;
USE Company;

-- Create tables in Database 1
CREATE TABLE IF NOT EXISTS Employees (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Department VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Projects (
    ProjectID INT PRIMARY KEY,
    ProjectName VARCHAR(100),
    StartDate DATE,
    EndDate DATE
);

-- Insert data into tables in Database 1
INSERT INTO Employees (EmployeeID, FirstName, LastName, Department)
VALUES 
    (1, 'John', 'Doe', 'IT'),
    (2, 'Jane', 'Smith', 'HR');

INSERT INTO Projects (ProjectID, ProjectName, StartDate, EndDate)
VALUES 
    (101, 'Website Redesign', '2024-02-01', '2024-04-01'),
    (102, 'Employee Training', '2024-03-01', '2024-05-01');

-- Create Database 2
CREATE DATABASE IF NOT EXISTS Inventory;
USE Inventory;

-- Create tables in Database 2
CREATE TABLE IF NOT EXISTS Products (
    ProductID INT PRIMARY KEY,
    ProductName VARCHAR(100),
    StockQuantity INT,
    Price DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS Suppliers (
    SupplierID INT PRIMARY KEY,
    SupplierName VARCHAR(100),
    ContactPerson VARCHAR(50),
    Phone VARCHAR(20)
);

-- Insert data into tables in Database 2
INSERT INTO Products (ProductID, ProductName, StockQuantity, Price)
VALUES 
    (201, 'Laptop', 50, 1200.00),
    (202, 'Smartphone', 100, 800.00);

INSERT INTO Suppliers (SupplierID, SupplierName, ContactPerson, Phone)
VALUES 
    (301, 'Tech Supplier Inc.', 'John Supplier', '123-456-7890'),
    (302, 'Gadget World', 'Jane Contact', '987-654-3210');

-- Create Database 3
CREATE DATABASE IF NOT EXISTS Library;
USE Library;

-- Create tables in Database 3
CREATE TABLE IF NOT EXISTS Books (
    BookID INT PRIMARY KEY,
    Title VARCHAR(100),
    Author VARCHAR(100),
    Genre VARCHAR(50),
    PublicationYear INT
);

CREATE TABLE IF NOT EXISTS Members (
    MemberID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100)
);

-- Insert data into tables in Database 3
INSERT INTO Books (BookID, Title, Author, Genre, PublicationYear)
VALUES 
    (1, 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 1925),
    (2, 'To Kill a Mockingbird', 'Harper Lee', 'Drama', 1960);

INSERT INTO Members (MemberID, FirstName, LastName, Email)
VALUES 
    (101, 'Alice', 'Johnson', 'alice.j@example.com'),
    (102, 'Bob', 'Smith', 'bob.s@example.com');

-- Create Database 4
CREATE DATABASE IF NOT EXISTS Hospital;
USE Hospital;

-- Create tables in Database 4
CREATE TABLE IF NOT EXISTS Patients (
    PatientID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    AdmissionDate DATE,
    DischargeDate DATE
);

CREATE TABLE IF NOT EXISTS Doctors (
    DoctorID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Specialty VARCHAR(100)
);

-- Insert data into tables in Database 4
INSERT INTO Patients (PatientID, FirstName, LastName, AdmissionDate, DischargeDate)
VALUES 
    (1, 'Mary', 'Johnson', '2024-02-01', '2024-02-10'),
    (2, 'Michael', 'Smith', '2024-02-05', '2024-02-15');

INSERT INTO Doctors (DoctorID, FirstName, LastName, Specialty)
VALUES 
    (201, 'Dr. Emily', 'Jones', 'Cardiology'),
    (202, 'Dr. David', 'Wilson', 'Orthopedics');

-- Create Database 5
CREATE DATABASE IF NOT EXISTS E_Commerce;
USE E_Commerce;

-- Create tables in Database 5
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Orders (
    OrderID INT PRIMARY KEY,
    CustomerID INT,
    ProductID INT,
    Quantity INT,
    OrderDate DATE,
    FOREIGN KEY (CustomerID) REFERENCES E_Commerce.Customers(CustomerID)
);

-- Insert data into tables in Database 5
INSERT INTO Customers (CustomerID, FirstName, LastName, Email)
VALUES 
    (1, 'Eva', 'Miller', 'eva.m@example.com'),
    (2, 'Daniel', 'Brown', 'daniel.b@example.com');

INSERT INTO Orders (OrderID, CustomerID, ProductID, Quantity, OrderDate)
VALUES 
    (1, 1, 301, 2, '2024-02-01'),
    (2, 2, 302, 1, '2024-02-02');