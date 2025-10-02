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
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cartitem`
--

CREATE TABLE `cartitem` (
  `cartItemId` int(11) NOT NULL,
  `cartId` int(11) NOT NULL,
  `productId` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `totalProductPrice` decimal(10,0) NOT NULL,
  `totalRewardPoints` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `customerId` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `passwordHash` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `age` int(11) NOT NULL,
  `totalRewardPoints` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `environmentreading`
--

CREATE TABLE `environmentreading` (
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
-- Table structure for table `maintenancealert`
--

CREATE TABLE `maintenancealert` (
  `alertId` int(11) NOT NULL,
  `locationId` int(11) NOT NULL,
  `parameterType` enum('temperature','humidity') DEFAULT NULL,
  `value` decimal(5,2) NOT NULL,
  `thresholdBreach` enum('LOW','HIGH') DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `maintenancethreshold`
--

CREATE TABLE `maintenancethreshold` (
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
  `associatedRewardPoints` int(11) NOT NULL DEFAULT 0,
  `upc` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `storelocation`
--

CREATE TABLE `storelocation` (
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
-- Indexes for table `cartitem`
--
ALTER TABLE `cartitem`
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
-- Indexes for table `environmentreading`
--
ALTER TABLE `environmentreading`
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
-- Indexes for table `maintenancealert`
--
ALTER TABLE `maintenancealert`
  ADD PRIMARY KEY (`alertId`),
  ADD KEY `locationId` (`locationId`);

--
-- Indexes for table `maintenancethreshold`
--
ALTER TABLE `maintenancethreshold`
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
-- Indexes for table `storelocation`
--
ALTER TABLE `storelocation`
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
-- AUTO_INCREMENT for table `cartitem`
--
ALTER TABLE `cartitem`
  MODIFY `cartItemId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `customerId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `environmentreading`
--
ALTER TABLE `environmentreading`
  MODIFY `readingId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `inventory`
--
ALTER TABLE `inventory`
  MODIFY `inventoryId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `maintenancealert`
--
ALTER TABLE `maintenancealert`
  MODIFY `alertId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `maintenancethreshold`
--
ALTER TABLE `maintenancethreshold`
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
-- AUTO_INCREMENT for table `storelocation`
--
ALTER TABLE `storelocation`
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
-- Constraints for table `cartitem`
--
ALTER TABLE `cartitem`
  ADD CONSTRAINT `cartitem_ibfk_1` FOREIGN KEY (`cartId`) REFERENCES `cart` (`cartId`),
  ADD CONSTRAINT `cartitem_ibfk_2` FOREIGN KEY (`productId`) REFERENCES `product` (`productId`);

--
-- Constraints for table `environmentreading`
--
ALTER TABLE `environmentreading`
  ADD CONSTRAINT `environmentreading_ibfk_1` FOREIGN KEY (`locationId`) REFERENCES `storelocation` (`locationId`);

--
-- Constraints for table `inventory`
--
ALTER TABLE `inventory`
  ADD CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`productId`) REFERENCES `product` (`productId`),
  ADD CONSTRAINT `inventory_ibfk_2` FOREIGN KEY (`locationId`) REFERENCES `storelocation` (`locationId`);

--
-- Constraints for table `maintenancealert`
--
ALTER TABLE `maintenancealert`
  ADD CONSTRAINT `maintenancealert_ibfk_1` FOREIGN KEY (`locationId`) REFERENCES `storelocation` (`locationId`);

--
-- Constraints for table `maintenancethreshold`
--
ALTER TABLE `maintenancethreshold`
  ADD CONSTRAINT `maintenancethreshold_ibfk_1` FOREIGN KEY (`locationId`) REFERENCES `storelocation` (`locationId`),
  ADD CONSTRAINT `maintenancethreshold_ibfk_2` FOREIGN KEY (`locationId`) REFERENCES `storelocation` (`locationId`);

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
