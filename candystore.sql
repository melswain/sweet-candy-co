-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 02, 2025 at 01:01 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `candystore`
--

-- --------------------------------------------------------

--
-- Table structure for table `cart`
--

CREATE TABLE `cart` (
  `cartId` int(11) NOT NULL,
  `customerId` int(11) DEFAULT NULL,
  `totalCartPrice` decimal(10,2) NOT NULL,
  `totalRewardPoints` int(11) DEFAULT 0,
  `checkoutDate` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cart_item`
--

CREATE TABLE `cart_item` (
  `cartItemId` int(11) NOT NULL,
  `cartId` int(11) NOT NULL,
  `productId` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `totalProductPrice` decimal(10,0) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `customerId` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) NOT NULL,
  `totalRewardPoints` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `environment_reading`
--

CREATE TABLE `environment_reading` (
  `readingId` int(11) NOT NULL,
  `locationId` int(11) NOT NULL,
  `temperature` decimal(5,2) NOT NULL,
  `humidity` decimal(5,2) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
  `inventoryId` int(11) NOT NULL,
  `productId` int(11) NOT NULL,
  `locationId` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `lastUpdated` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `maintenance_alert`
--

CREATE TABLE `maintenance_alert` (
  `alertId` int(11) NOT NULL,
  `locationId` int(11) NOT NULL,
  `parameterType` enum('temperature','humidity') DEFAULT NULL,
  `value` decimal(5,2) NOT NULL,
  `thresholdBreach` enum('LOW','HIGH') DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `maintenance_threshold`
--

CREATE TABLE `maintenance_threshold` (
  `thresholdId` int(11) NOT NULL,
  `locationId` int(11) NOT NULL,
  `minTemperature` decimal(5,2) NOT NULL,
  `maxTemperature` decimal(5,2) NOT NULL,
  `minHumidity` decimal(5,2) NOT NULL,
  `maxHumidity` decimal(5,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `payment`
--

CREATE TABLE `payment` (
  `paymentId` int(11) NOT NULL,
  `cartId` int(11) DEFAULT NULL,
  `cardNumber` varchar(20) NOT NULL,
  `expiryDate` varchar(7) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `productId` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `type` varchar(50) NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `expirationDate` date NOT NULL,
  `discountPercentage` decimal(3,2) DEFAULT 1.00,
  `manufacturerName` varchar(100),
  `upc` varchar(50) NOT NULL,
  `epc` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `store_location`
--

CREATE TABLE `store_location` (
  `locationId` int(11) NOT NULL,
  `locationName` varchar(100) NOT NULL,
  `address` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cart`
--
ALTER TABLE `cart`
  ADD PRIMARY KEY (`cartId`),
  ADD KEY `customerId` (`customerId`);

--
-- Indexes for table `cart_item`
--
ALTER TABLE `cart_item`
  ADD PRIMARY KEY (`cartItemId`),
  ADD KEY `cartId` (`cartId`),
  ADD KEY `productId` (`productId`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`customerId`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `email_2` (`email`);

--
-- Indexes for table `environment_reading`
--
ALTER TABLE `environment_reading`
  ADD PRIMARY KEY (`readingId`),
  ADD KEY `locationId` (`locationId`);

--
-- Indexes for table `inventory`
--
ALTER TABLE `inventory`
  ADD PRIMARY KEY (`inventoryId`),
  ADD KEY `productId` (`productId`),
  ADD KEY `locationId` (`locationId`);

--
-- Indexes for table `maintenance_alert`
--
ALTER TABLE `maintenance_alert`
  ADD PRIMARY KEY (`alertId`),
  ADD KEY `locationId` (`locationId`);

--
-- Indexes for table `maintenance_threshold`
--
ALTER TABLE `maintenance_threshold`
  ADD PRIMARY KEY (`thresholdId`),
  ADD UNIQUE KEY `locationId` (`locationId`);

--
-- Indexes for table `payment`
--
ALTER TABLE `payment`
  ADD PRIMARY KEY (`paymentId`),
  ADD UNIQUE KEY `cartId` (`cartId`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`productId`),
  ADD UNIQUE KEY `upc` (`upc`);

--
-- Indexes for table `store_location`
--
ALTER TABLE `store_location`
  ADD PRIMARY KEY (`locationId`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cart`
--
ALTER TABLE `cart`
  MODIFY `cartId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cart_item`
--
ALTER TABLE `cart_item`
  MODIFY `cartItemId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `customerId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `environment_reading`
--
ALTER TABLE `environment_reading`
  MODIFY `readingId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `inventory`
--
ALTER TABLE `inventory`
  MODIFY `inventoryId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `maintenance_alert`
--
ALTER TABLE `maintenance_alert`
  MODIFY `alertId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `maintenance_threshold`
--
ALTER TABLE `maintenance_threshold`
  MODIFY `thresholdId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `payment`
--
ALTER TABLE `payment`
  MODIFY `paymentId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `productId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `store_location`
--
ALTER TABLE `store_location`
  MODIFY `locationId` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cart`
--
ALTER TABLE `cart`
  ADD CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`customerId`) REFERENCES `customer` (`customerId`);

--
-- Constraints for table `cart_item`
--
ALTER TABLE `cart_item`
  ADD CONSTRAINT `cartitem_ibfk_1` FOREIGN KEY (`cartId`) REFERENCES `cart` (`cartId`),
  ADD CONSTRAINT `cartitem_ibfk_2` FOREIGN KEY (`productId`) REFERENCES `product` (`productId`);

--
-- Constraints for table `environment_reading`
--
ALTER TABLE `environment_reading`
  ADD CONSTRAINT `environmentreading_ibfk_1` FOREIGN KEY (`locationId`) REFERENCES `store_location` (`locationId`);

--
-- Constraints for table `inventory`
--
ALTER TABLE `inventory`
  ADD CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`productId`) REFERENCES `product` (`productId`),
  ADD CONSTRAINT `inventory_ibfk_2` FOREIGN KEY (`locationId`) REFERENCES `store_location` (`locationId`);

--
-- Constraints for table `maintenance_alert`
--
ALTER TABLE `maintenance_alert`
  ADD CONSTRAINT `maintenancealert_ibfk_1` FOREIGN KEY (`locationId`) REFERENCES `store_location` (`locationId`);

--
-- Constraints for table `maintenance_threshold`
--
ALTER TABLE `maintenance_threshold`
  ADD CONSTRAINT `maintenancethreshold_ibfk_1` FOREIGN KEY (`locationId`) REFERENCES `store_location` (`locationId`),
  ADD CONSTRAINT `maintenancethreshold_ibfk_2` FOREIGN KEY (`locationId`) REFERENCES `store_location` (`locationId`);

--
-- Constraints for table `payment`
--
ALTER TABLE `payment`
  ADD CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`cartId`) REFERENCES `cart` (`cartId`),
  ADD CONSTRAINT `payment_ibfk_2` FOREIGN KEY (`cartId`) REFERENCES `cart` (`cartId`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- Store Locations
INSERT INTO store_location (locationName, address) VALUES
('Sweet Candy Co. - Laval', '545 Boulevard des Laurentides, Laval, QC H9S4K9'),
('Sweet Candy Co. - West Island', '20 Avenue Cartier, Pointe-Claire, QC H9R2V4');

-- Maintenance Thresholds
INSERT INTO maintenance_threshold (locationId, minTemperature, maxTemperature, minHumidity, maxHumidity) VALUES
(1, 5.00, 13.00, 35.00, 45.00),  -- Laval location
(2, 4.00, 12.00, 35.00, 45.00);  -- West Island location

-- Customers (with 0 initial points)
-- UPDATE ONE CUSTOMER WITH CHECKABLE EMAIL TO USE RECEIPTS
INSERT INTO customer (name, email, phone, totalRewardPoints) VALUES
('Sarah Johnson', 'sarah.j@email.com', '438-555-0101', 0),
('Michael Chen', 'mchen@email.com', '514-555-0102', 0),
('Emily Rodriguez', 'emily.r@email.com', '613-555-0103', 0),
('David Kim', 'davidk@email.com', '514-555-0104', 0);

-- Products
INSERT INTO product (name, type, price, expirationDate, discountPercentage, manufacturerName, upc, epc) VALUES
('Chocolate Dream Bar', 'Chocolate', 3.99, '2026-12-31', 1.00, 'Sweet Candy Co', '123456789001', 'EPC123001'),
('Rainbow Sour Strips', 'Gummy', 4.50, '2026-10-15', 1.00, 'Sweet Candy Co', '123456789002', 'EPC123002'),
('Peanut Butter Cups 4pk', 'Chocolate', 5.99, '2026-11-30', 1.00, 'Sweet Candy Co', '123456789003', 'EPC123003'),
('Cherry Licorice Twists', 'Licorice', 3.50, '2026-09-20', 1.00, 'Sweet Candy Co', '123456789004', 'EPC123004'),
('Sea Salt Caramels 6pc', 'Caramel', 6.99, '2026-08-15', 1.00, 'Sweet Candy Co', '123456789005', 'EPC123005'),
('Mixed Fruit Hard Candy', 'Hard Candy', 2.99, '2027-01-15', 1.00, 'Sweet Candy Co', '123456789006', 'EPC123006'),
('Mint Chocolate Thins', 'Chocolate', 4.99, '2026-11-15', 1.00, 'Sweet Candy Co', '123456789007', 'EPC123007'),
('Gummy Bears Pack', 'Gummy', 3.99, '2026-10-01', 1.00, 'Sweet Candy Co', '123456789008', 'EPC123008'),
('Toffee Crunch Bar', 'Toffee', 4.50, '2026-12-15', 1.00, 'Sweet Candy Co', '123456789009', 'EPC123009'),
('Assorted Lollipops 5pk', 'Lollipop', 5.99, '2027-02-28', 1.00, 'Sweet Candy Co', '123456789010', 'EPC123010');

INSERT INTO inventory (productId, locationId, quantity) VALUES
(1, 1, 10), (1, 2, 10),
(2, 1, 10), (2, 2, 10),
(3, 1, 10), (3, 2, 10),
(4, 1, 10), (4, 2, 10),
(5, 1, 10), (5, 2, 10),
(6, 1, 10), (6, 2, 10),
(7, 1, 10), (7, 2, 10),
(8, 1, 10), (8, 2, 10),
(9, 1, 10), (9, 2, 10),
(10, 1, 10), (10, 2, 10);