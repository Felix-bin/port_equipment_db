/*
 Navicat Premium Dump SQL

 Source Server         : Mysql
 Source Server Type    : MySQL
 Source Server Version : 80044 (8.0.44)
 Source Host           : localhost:3306
 Source Schema         : port_equipment_db

 Target Server Type    : MySQL
 Target Server Version : 80044 (8.0.44)
 File Encoding         : 65001

 Date: 11/12/2025 23:07:51
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for billing
-- ----------------------------
DROP TABLE IF EXISTS `billing`;
CREATE TABLE `billing`  (
  `bill_id` int NOT NULL AUTO_INCREMENT,
  `bill_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_id` int NOT NULL,
  `customer_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `rental_fee` float NULL DEFAULT NULL,
  `repair_fee` float NULL DEFAULT NULL,
  `other_fee` float NULL DEFAULT NULL,
  `total_amount` float NULL DEFAULT NULL,
  `status` enum('PENDING','CONFIRMED','PAID','OVERDUE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `billing_date` date NULL DEFAULT NULL,
  `payment_date` date NULL DEFAULT NULL,
  `discount` float NULL DEFAULT NULL,
  `payment_method` enum('CASH','TRANSFER','CHECK','OTHER') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `invoice_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `paid_amount` float NULL DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`bill_id`) USING BTREE,
  UNIQUE INDEX `ix_billing_bill_code`(`bill_code` ASC) USING BTREE,
  INDEX `order_id`(`order_id` ASC) USING BTREE,
  INDEX `ix_billing_bill_id`(`bill_id` ASC) USING BTREE,
  INDEX `ix_billing_status`(`status` ASC) USING BTREE,
  INDEX `ix_billing_invoice_no`(`invoice_no` ASC) USING BTREE,
  INDEX `ix_billing_payment_method`(`payment_method` ASC) USING BTREE,
  CONSTRAINT `billing_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `lease_orders` (`order_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 71 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for customers
-- ----------------------------
DROP TABLE IF EXISTS `customers`;
CREATE TABLE `customers`  (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_person` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `phone` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `credit_rating` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`customer_id`) USING BTREE,
  UNIQUE INDEX `customer_name`(`customer_name` ASC) USING BTREE,
  INDEX `ix_customers_customer_id`(`customer_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 55 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for equipment
-- ----------------------------
DROP TABLE IF EXISTS `equipment`;
CREATE TABLE `equipment`  (
  `equipment_id` int NOT NULL AUTO_INCREMENT,
  `equipment_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` enum('IN_STOCK','OUT','MAINTENANCE','SCRAPPED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `storage_location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `purchase_price` float NULL DEFAULT NULL,
  `daily_rental_rate` float NULL DEFAULT NULL,
  `specifications` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `supplier` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `manufacturer` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `purchase_date` date NULL DEFAULT NULL,
  `warranty_date` date NULL DEFAULT NULL,
  `last_maintenance_date` date NULL DEFAULT NULL,
  `serial_number` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`equipment_id`) USING BTREE,
  UNIQUE INDEX `ix_equipment_equipment_code`(`equipment_code` ASC) USING BTREE,
  INDEX `ix_equipment_status`(`status` ASC) USING BTREE,
  INDEX `ix_equipment_equipment_id`(`equipment_id` ASC) USING BTREE,
  INDEX `ix_equipment_category`(`category` ASC) USING BTREE,
  INDEX `ix_equipment_supplier`(`supplier` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 161 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for inbound_items
-- ----------------------------
DROP TABLE IF EXISTS `inbound_items`;
CREATE TABLE `inbound_items`  (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `inbound_id` int NOT NULL,
  `equipment_id` int NULL DEFAULT NULL,
  `equipment_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `specifications` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `quantity` int NULL DEFAULT NULL,
  `unit_price` float NULL DEFAULT NULL,
  `subtotal` float NULL DEFAULT NULL,
  `storage_location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`item_id`) USING BTREE,
  INDEX `inbound_id`(`inbound_id` ASC) USING BTREE,
  INDEX `equipment_id`(`equipment_id` ASC) USING BTREE,
  INDEX `ix_inbound_items_item_id`(`item_id` ASC) USING BTREE,
  INDEX `ix_inbound_items_equipment_code`(`equipment_code` ASC) USING BTREE,
  CONSTRAINT `inbound_items_ibfk_1` FOREIGN KEY (`inbound_id`) REFERENCES `inbound_records` (`inbound_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `inbound_items_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`equipment_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 156 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for inbound_records
-- ----------------------------
DROP TABLE IF EXISTS `inbound_records`;
CREATE TABLE `inbound_records`  (
  `inbound_id` int NOT NULL AUTO_INCREMENT,
  `inbound_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `supplier` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `purchase_date` date NULL DEFAULT NULL,
  `inbound_date` datetime NOT NULL,
  `operator` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `total_quantity` int NULL DEFAULT NULL,
  `total_amount` float NULL DEFAULT NULL,
  `status` enum('PENDING','COMPLETED','CANCELLED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`inbound_id`) USING BTREE,
  UNIQUE INDEX `ix_inbound_records_inbound_code`(`inbound_code` ASC) USING BTREE,
  INDEX `ix_inbound_records_status`(`status` ASC) USING BTREE,
  INDEX `ix_inbound_records_inbound_id`(`inbound_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 31 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for inspection_records
-- ----------------------------
DROP TABLE IF EXISTS `inspection_records`;
CREATE TABLE `inspection_records`  (
  `inspection_id` int NOT NULL AUTO_INCREMENT,
  `return_id` int NOT NULL,
  `equipment_id` int NOT NULL,
  `equipment_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `inspector` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `appearance_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `function_test` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `repair_needed` int NULL DEFAULT NULL,
  `repair_cost` float NULL DEFAULT NULL,
  `result` enum('PASS','REPAIR_NEEDED','FAILED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `inspection_date` datetime NOT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`inspection_id`) USING BTREE,
  INDEX `return_id`(`return_id` ASC) USING BTREE,
  INDEX `equipment_id`(`equipment_id` ASC) USING BTREE,
  INDEX `ix_inspection_records_inspection_id`(`inspection_id` ASC) USING BTREE,
  CONSTRAINT `inspection_records_ibfk_1` FOREIGN KEY (`return_id`) REFERENCES `return_records` (`return_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `inspection_records_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`equipment_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 86 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for lease_orders
-- ----------------------------
DROP TABLE IF EXISTS `lease_orders`;
CREATE TABLE `lease_orders`  (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `order_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` int NOT NULL,
  `customer_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `voyage_no` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `start_date` date NOT NULL,
  `expected_return_date` date NULL DEFAULT NULL,
  `actual_return_date` date NULL DEFAULT NULL,
  `status` enum('PENDING','IN_PROGRESS','COMPLETED','CANCELLED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_amount` float NULL DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`order_id`) USING BTREE,
  UNIQUE INDEX `ix_lease_orders_order_code`(`order_code` ASC) USING BTREE,
  INDEX `customer_id`(`customer_id` ASC) USING BTREE,
  INDEX `ix_lease_orders_order_id`(`order_id` ASC) USING BTREE,
  INDEX `ix_lease_orders_status`(`status` ASC) USING BTREE,
  INDEX `ix_lease_orders_voyage_no`(`voyage_no` ASC) USING BTREE,
  CONSTRAINT `lease_orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 101 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for maintenance_records
-- ----------------------------
DROP TABLE IF EXISTS `maintenance_records`;
CREATE TABLE `maintenance_records`  (
  `maintenance_id` int NOT NULL AUTO_INCREMENT,
  `maintenance_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_id` int NOT NULL,
  `equipment_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `maintenance_type` enum('ROUTINE','REPAIR','OVERHAUL') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `problem_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `maintenance_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `maintenance_date` datetime NOT NULL,
  `completion_date` datetime NULL DEFAULT NULL,
  `technician` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `maintenance_cost` float NULL DEFAULT NULL,
  `parts_cost` float NULL DEFAULT NULL,
  `labor_cost` float NULL DEFAULT NULL,
  `status` enum('PENDING','IN_PROGRESS','COMPLETED','CANCELLED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`maintenance_id`) USING BTREE,
  UNIQUE INDEX `ix_maintenance_records_maintenance_code`(`maintenance_code` ASC) USING BTREE,
  INDEX `equipment_id`(`equipment_id` ASC) USING BTREE,
  INDEX `ix_maintenance_records_maintenance_id`(`maintenance_id` ASC) USING BTREE,
  INDEX `ix_maintenance_records_status`(`status` ASC) USING BTREE,
  CONSTRAINT `maintenance_records_ibfk_1` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`equipment_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for operation_logs
-- ----------------------------
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE `operation_logs`  (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NULL DEFAULT NULL,
  `username` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `action` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `table_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `record_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `ip_address` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`log_id`) USING BTREE,
  INDEX `ix_operation_logs_log_id`(`log_id` ASC) USING BTREE,
  INDEX `ix_operation_logs_created_at`(`created_at` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for order_items
-- ----------------------------
DROP TABLE IF EXISTS `order_items`;
CREATE TABLE `order_items`  (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `equipment_id` int NOT NULL,
  `equipment_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `daily_rate` float NOT NULL,
  `rental_days` int NULL DEFAULT NULL,
  `subtotal` float NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`item_id`) USING BTREE,
  INDEX `order_id`(`order_id` ASC) USING BTREE,
  INDEX `equipment_id`(`equipment_id` ASC) USING BTREE,
  INDEX `ix_order_items_item_id`(`item_id` ASC) USING BTREE,
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `lease_orders` (`order_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`equipment_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 323 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for outbound_items
-- ----------------------------
DROP TABLE IF EXISTS `outbound_items`;
CREATE TABLE `outbound_items`  (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `outbound_id` int NOT NULL,
  `equipment_id` int NOT NULL,
  `equipment_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int NULL DEFAULT NULL,
  `daily_rate` float NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`item_id`) USING BTREE,
  INDEX `outbound_id`(`outbound_id` ASC) USING BTREE,
  INDEX `equipment_id`(`equipment_id` ASC) USING BTREE,
  INDEX `ix_outbound_items_item_id`(`item_id` ASC) USING BTREE,
  CONSTRAINT `outbound_items_ibfk_1` FOREIGN KEY (`outbound_id`) REFERENCES `outbound_records` (`outbound_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `outbound_items_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`equipment_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 217 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for outbound_records
-- ----------------------------
DROP TABLE IF EXISTS `outbound_records`;
CREATE TABLE `outbound_records`  (
  `outbound_id` int NOT NULL AUTO_INCREMENT,
  `outbound_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_id` int NULL DEFAULT NULL,
  `outbound_date` datetime NOT NULL,
  `operator` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `recipient` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `recipient_phone` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `total_quantity` int NULL DEFAULT NULL,
  `status` enum('PENDING','COMPLETED','CANCELLED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`outbound_id`) USING BTREE,
  UNIQUE INDEX `ix_outbound_records_outbound_code`(`outbound_code` ASC) USING BTREE,
  INDEX `order_id`(`order_id` ASC) USING BTREE,
  INDEX `ix_outbound_records_status`(`status` ASC) USING BTREE,
  INDEX `ix_outbound_records_outbound_id`(`outbound_id` ASC) USING BTREE,
  CONSTRAINT `outbound_records_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `lease_orders` (`order_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 71 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for return_items
-- ----------------------------
DROP TABLE IF EXISTS `return_items`;
CREATE TABLE `return_items`  (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `return_id` int NOT NULL,
  `equipment_id` int NOT NULL,
  `equipment_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_condition` enum('GOOD','NORMAL','DAMAGED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `damage_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `damage_fee` float NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`item_id`) USING BTREE,
  INDEX `return_id`(`return_id` ASC) USING BTREE,
  INDEX `equipment_id`(`equipment_id` ASC) USING BTREE,
  INDEX `ix_return_items_item_id`(`item_id` ASC) USING BTREE,
  INDEX `ix_return_items_equipment_condition`(`equipment_condition` ASC) USING BTREE,
  CONSTRAINT `return_items_ibfk_1` FOREIGN KEY (`return_id`) REFERENCES `return_records` (`return_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `return_items_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`equipment_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 86 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for return_records
-- ----------------------------
DROP TABLE IF EXISTS `return_records`;
CREATE TABLE `return_records`  (
  `return_id` int NOT NULL AUTO_INCREMENT,
  `return_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_id` int NOT NULL,
  `voyage_no` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `return_date` datetime NOT NULL,
  `return_person` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `equipment_count` int NULL DEFAULT NULL,
  `inspection_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `total_damage_fee` float NULL DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`return_id`) USING BTREE,
  UNIQUE INDEX `ix_return_records_return_code`(`return_code` ASC) USING BTREE,
  INDEX `order_id`(`order_id` ASC) USING BTREE,
  INDEX `ix_return_records_return_id`(`return_id` ASC) USING BTREE,
  CONSTRAINT `return_records_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `lease_orders` (`order_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 28 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for suppliers
-- ----------------------------
DROP TABLE IF EXISTS `suppliers`;
CREATE TABLE `suppliers`  (
  `supplier_id` int NOT NULL AUTO_INCREMENT,
  `supplier_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `supplier_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_person` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `phone` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `bank_account` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `credit_rating` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`supplier_id`) USING BTREE,
  UNIQUE INDEX `ix_suppliers_supplier_code`(`supplier_code` ASC) USING BTREE,
  INDEX `ix_suppliers_supplier_name`(`supplier_name` ASC) USING BTREE,
  INDEX `ix_suppliers_supplier_id`(`supplier_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for trigger_logs
-- ----------------------------
DROP TABLE IF EXISTS `trigger_logs`;
CREATE TABLE `trigger_logs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `log_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `trigger_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `operation` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `table_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `record_id` int NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_trigger_logs_id`(`id` ASC) USING BTREE,
  INDEX `ix_trigger_logs_trigger_name`(`trigger_name` ASC) USING BTREE,
  INDEX `ix_trigger_logs_created_at`(`created_at` ASC) USING BTREE,
  INDEX `ix_trigger_logs_log_type`(`log_type` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `real_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `phone` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `last_login` datetime NULL DEFAULT NULL,
  `nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `profile` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `country_region` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `area` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `is_deleted` int NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `ix_users_username`(`username` ASC) USING BTREE,
  INDEX `ix_users_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_user_email`(`email` ASC) USING BTREE,
  INDEX `idx_user_phone`(`phone` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for v_billing_summary
-- ----------------------------
DROP VIEW IF EXISTS `v_billing_summary`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_billing_summary` AS select `b`.`bill_id` AS `bill_id`,`b`.`bill_code` AS `bill_code`,`b`.`order_id` AS `order_id`,`lo`.`order_code` AS `order_code`,`b`.`customer_name` AS `customer_name`,`c`.`customer_id` AS `customer_id`,`c`.`contact_person` AS `contact_person`,`c`.`phone` AS `customer_phone`,`c`.`email` AS `customer_email`,`b`.`rental_fee` AS `rental_fee`,`b`.`repair_fee` AS `repair_fee`,`b`.`other_fee` AS `other_fee`,`b`.`discount` AS `discount`,`b`.`total_amount` AS `total_amount`,`b`.`paid_amount` AS `paid_amount`,(`b`.`total_amount` - coalesce(`b`.`paid_amount`,0)) AS `unpaid_amount`,`b`.`status` AS `billing_status`,`b`.`payment_method` AS `payment_method`,`b`.`invoice_no` AS `invoice_no`,`b`.`billing_date` AS `billing_date`,`b`.`payment_date` AS `payment_date`,`b`.`remarks` AS `remarks`,`b`.`created_at` AS `created_at`,`b`.`updated_at` AS `updated_at`,`lo`.`voyage_no` AS `voyage_no`,`lo`.`start_date` AS `start_date`,`lo`.`expected_return_date` AS `expected_return_date`,`lo`.`actual_return_date` AS `actual_return_date`,`lo`.`status` AS `order_status`,coalesce(`item_stats`.`equipment_count`,0) AS `equipment_count`,coalesce(`item_stats`.`total_rental_days`,0) AS `total_rental_days` from (((`billing` `b` left join `lease_orders` `lo` on((`b`.`order_id` = `lo`.`order_id`))) left join `customers` `c` on((`lo`.`customer_id` = `c`.`customer_id`))) left join (select `order_items`.`order_id` AS `order_id`,count(0) AS `equipment_count`,sum(`order_items`.`rental_days`) AS `total_rental_days` from `order_items` group by `order_items`.`order_id`) `item_stats` on((`b`.`order_id` = `item_stats`.`order_id`))) where (`b`.`is_deleted` = 0);

-- ----------------------------
-- View structure for v_customer_rental_stats
-- ----------------------------
DROP VIEW IF EXISTS `v_customer_rental_stats`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_customer_rental_stats` AS select `c`.`customer_id` AS `customer_id`,`c`.`customer_name` AS `customer_name`,`c`.`contact_person` AS `contact_person`,`c`.`phone` AS `phone`,`c`.`email` AS `email`,`c`.`address` AS `address`,`c`.`credit_rating` AS `credit_rating`,`c`.`created_at` AS `created_at`,coalesce(`order_stats`.`total_orders`,0) AS `total_orders`,coalesce(`order_stats`.`completed_orders`,0) AS `completed_orders`,coalesce(`order_stats`.`in_progress_orders`,0) AS `in_progress_orders`,coalesce(`order_stats`.`pending_orders`,0) AS `pending_orders`,coalesce(`order_stats`.`total_amount`,0.0) AS `total_rental_amount`,coalesce(`order_stats`.`paid_amount`,0.0) AS `paid_amount`,coalesce(`order_stats`.`pending_amount`,0.0) AS `pending_amount`,coalesce(`order_stats`.`total_equipment_count`,0) AS `total_equipment_count`,`order_stats`.`last_order_date` AS `last_order_date`,`order_stats`.`last_order_code` AS `last_order_code` from (`customers` `c` left join (select `lo`.`customer_id` AS `customer_id`,count(distinct `lo`.`order_id`) AS `total_orders`,sum((case when (`lo`.`status` = '已完结') then 1 else 0 end)) AS `completed_orders`,sum((case when (`lo`.`status` = '航次执行中') then 1 else 0 end)) AS `in_progress_orders`,sum((case when (`lo`.`status` = '待提货') then 1 else 0 end)) AS `pending_orders`,sum(`lo`.`total_amount`) AS `total_amount`,sum(coalesce(`b`.`paid_amount`,0)) AS `paid_amount`,sum((case when (`b`.`status` in ('待确认','已确认')) then coalesce(`b`.`total_amount`,0) else 0 end)) AS `pending_amount`,sum(`oi_stats`.`equipment_count`) AS `total_equipment_count`,max(`lo`.`created_at`) AS `last_order_date`,max(`lo`.`order_code`) AS `last_order_code` from ((`lease_orders` `lo` left join `billing` `b` on(((`lo`.`order_id` = `b`.`order_id`) and (`b`.`is_deleted` = 0)))) left join (select `order_items`.`order_id` AS `order_id`,count(0) AS `equipment_count` from `order_items` group by `order_items`.`order_id`) `oi_stats` on((`lo`.`order_id` = `oi_stats`.`order_id`))) where (`lo`.`is_deleted` = 0) group by `lo`.`customer_id`) `order_stats` on((`c`.`customer_id` = `order_stats`.`customer_id`))) where (`c`.`is_deleted` = 0);

-- ----------------------------
-- View structure for v_equipment_category_stats
-- ----------------------------
DROP VIEW IF EXISTS `v_equipment_category_stats`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_equipment_category_stats` AS select `e`.`category` AS `category`,count(0) AS `total_count`,sum((case when (`e`.`status` = '在库') then 1 else 0 end)) AS `in_stock_count`,sum((case when (`e`.`status` = '已出库') then 1 else 0 end)) AS `out_stock_count`,sum((case when (`e`.`status` = '维修中') then 1 else 0 end)) AS `maintenance_count`,sum(`e`.`purchase_price`) AS `total_purchase_value`,avg(`e`.`daily_rental_rate`) AS `avg_daily_rate`,coalesce(`rental_stats`.`total_rental_count`,0) AS `total_rental_count`,coalesce(`rental_stats`.`total_revenue`,0.0) AS `total_revenue` from (`equipment` `e` left join (select `e2`.`category` AS `category`,count(distinct `oi`.`order_id`) AS `total_rental_count`,sum(`oi`.`subtotal`) AS `total_revenue` from ((`equipment` `e2` join `order_items` `oi` on((`e2`.`equipment_id` = `oi`.`equipment_id`))) join `lease_orders` `lo` on((`oi`.`order_id` = `lo`.`order_id`))) where ((`e2`.`is_deleted` = 0) and (`lo`.`is_deleted` = 0)) group by `e2`.`category`) `rental_stats` on((`e`.`category` = `rental_stats`.`category`))) where (`e`.`is_deleted` = 0) group by `e`.`category`;

-- ----------------------------
-- View structure for v_equipment_inventory
-- ----------------------------
DROP VIEW IF EXISTS `v_equipment_inventory`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_equipment_inventory` AS select `e`.`equipment_id` AS `equipment_id`,`e`.`equipment_code` AS `equipment_code`,`e`.`equipment_name` AS `equipment_name`,`e`.`category` AS `category`,`e`.`status` AS `status`,`e`.`storage_location` AS `storage_location`,`e`.`purchase_price` AS `purchase_price`,`e`.`daily_rental_rate` AS `daily_rental_rate`,`e`.`supplier` AS `supplier`,`e`.`manufacturer` AS `manufacturer`,`e`.`purchase_date` AS `purchase_date`,`e`.`warranty_date` AS `warranty_date`,`e`.`last_maintenance_date` AS `last_maintenance_date`,`e`.`serial_number` AS `serial_number`,`e`.`specifications` AS `specifications`,`e`.`created_at` AS `created_at`,`e`.`updated_at` AS `updated_at`,(case when (`e`.`status` = '在库') then 1 else 0 end) AS `available_quantity`,(case when (`e`.`status` = '已出库') then 1 else 0 end) AS `rented_quantity`,(case when (`e`.`status` = '维修中') then 1 else 0 end) AS `maintenance_quantity`,coalesce(`rental_stats`.`rental_count`,0) AS `rental_count`,coalesce(`rental_stats`.`total_rental_days`,0) AS `total_rental_days`,coalesce(`rental_stats`.`total_revenue`,0.0) AS `total_revenue` from (`equipment` `e` left join (select `oi`.`equipment_id` AS `equipment_id`,count(distinct `oi`.`order_id`) AS `rental_count`,sum(`oi`.`rental_days`) AS `total_rental_days`,sum(`oi`.`subtotal`) AS `total_revenue` from (`order_items` `oi` join `lease_orders` `lo` on((`oi`.`order_id` = `lo`.`order_id`))) where (`lo`.`is_deleted` = 0) group by `oi`.`equipment_id`) `rental_stats` on((`e`.`equipment_id` = `rental_stats`.`equipment_id`))) where (`e`.`is_deleted` = 0);

-- ----------------------------
-- View structure for v_equipment_usage
-- ----------------------------
DROP VIEW IF EXISTS `v_equipment_usage`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_equipment_usage` AS select `e`.`equipment_id` AS `equipment_id`,`e`.`equipment_code` AS `equipment_code`,`e`.`equipment_name` AS `equipment_name`,`e`.`category` AS `category`,`e`.`status` AS `status`,`e`.`storage_location` AS `storage_location`,`e`.`purchase_price` AS `purchase_price`,`e`.`daily_rental_rate` AS `daily_rental_rate`,`e`.`supplier` AS `supplier`,`e`.`manufacturer` AS `manufacturer`,`e`.`purchase_date` AS `purchase_date`,`e`.`warranty_date` AS `warranty_date`,`e`.`last_maintenance_date` AS `last_maintenance_date`,`e`.`created_at` AS `created_at`,coalesce(`usage_stats`.`rental_count`,0) AS `rental_count`,coalesce(`usage_stats`.`total_rental_days`,0) AS `total_rental_days`,coalesce(`usage_stats`.`total_revenue`,0.0) AS `total_revenue`,coalesce(`usage_stats`.`avg_rental_days`,0.0) AS `avg_rental_days`,`usage_stats`.`last_rental_date` AS `last_rental_date`,`usage_stats`.`last_customer_name` AS `last_customer_name`,coalesce(`maintenance_stats`.`maintenance_count`,0) AS `maintenance_count`,coalesce(`maintenance_stats`.`total_maintenance_cost`,0.0) AS `total_maintenance_cost`,(case when (`e`.`purchase_date` is not null) then round(((coalesce(`usage_stats`.`total_rental_days`,0) / (to_days(curdate()) - to_days(`e`.`purchase_date`))) * 100),2) else 0 end) AS `utilization_rate` from ((`equipment` `e` left join (select `oi`.`equipment_id` AS `equipment_id`,count(distinct `oi`.`order_id`) AS `rental_count`,sum(`oi`.`rental_days`) AS `total_rental_days`,sum(`oi`.`subtotal`) AS `total_revenue`,avg(`oi`.`rental_days`) AS `avg_rental_days`,max(`lo`.`created_at`) AS `last_rental_date`,max(`lo`.`customer_name`) AS `last_customer_name` from (`order_items` `oi` join `lease_orders` `lo` on((`oi`.`order_id` = `lo`.`order_id`))) where (`lo`.`is_deleted` = 0) group by `oi`.`equipment_id`) `usage_stats` on((`e`.`equipment_id` = `usage_stats`.`equipment_id`))) left join (select `maintenance_records`.`equipment_id` AS `equipment_id`,count(0) AS `maintenance_count`,sum(((`maintenance_records`.`maintenance_cost` + `maintenance_records`.`parts_cost`) + `maintenance_records`.`labor_cost`)) AS `total_maintenance_cost` from `maintenance_records` where (`maintenance_records`.`is_deleted` = 0) group by `maintenance_records`.`equipment_id`) `maintenance_stats` on((`e`.`equipment_id` = `maintenance_stats`.`equipment_id`))) where (`e`.`is_deleted` = 0);

-- ----------------------------
-- View structure for v_inbound_outbound_summary
-- ----------------------------
DROP VIEW IF EXISTS `v_inbound_outbound_summary`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_inbound_outbound_summary` AS select 'inbound' AS `record_type`,`ir`.`inbound_id` AS `record_id`,`ir`.`inbound_code` AS `record_code`,`ir`.`supplier` AS `supplier`,`ir`.`purchase_date` AS `purchase_date`,`ir`.`inbound_date` AS `operation_date`,`ir`.`operator` AS `operator`,`ir`.`total_quantity` AS `total_quantity`,`ir`.`total_amount` AS `total_amount`,`ir`.`status` AS `status`,`ir`.`remarks` AS `remarks`,`ir`.`created_at` AS `created_at`,count(distinct `ii`.`item_id`) AS `item_count`,group_concat(distinct `ii`.`equipment_name` separator ', ') AS `equipment_names` from (`inbound_records` `ir` left join `inbound_items` `ii` on((`ir`.`inbound_id` = `ii`.`inbound_id`))) where (`ir`.`is_deleted` = 0) group by `ir`.`inbound_id`,`ir`.`inbound_code`,`ir`.`supplier`,`ir`.`purchase_date`,`ir`.`inbound_date`,`ir`.`operator`,`ir`.`total_quantity`,`ir`.`total_amount`,`ir`.`status`,`ir`.`remarks`,`ir`.`created_at` union all select 'outbound' AS `record_type`,`or_rec`.`outbound_id` AS `record_id`,`or_rec`.`outbound_code` AS `record_code`,NULL AS `supplier`,NULL AS `purchase_date`,`or_rec`.`outbound_date` AS `operation_date`,`or_rec`.`operator` AS `operator`,`or_rec`.`total_quantity` AS `total_quantity`,0.0 AS `total_amount`,`or_rec`.`status` AS `status`,`or_rec`.`remarks` AS `remarks`,`or_rec`.`created_at` AS `created_at`,count(distinct `oi`.`item_id`) AS `item_count`,group_concat(distinct `oi`.`equipment_name` separator ', ') AS `equipment_names` from ((`outbound_records` `or_rec` left join `outbound_items` `oi` on((`or_rec`.`outbound_id` = `oi`.`outbound_id`))) left join `lease_orders` `lo` on((`or_rec`.`order_id` = `lo`.`order_id`))) where (`or_rec`.`is_deleted` = 0) group by `or_rec`.`outbound_id`,`or_rec`.`outbound_code`,`or_rec`.`outbound_date`,`or_rec`.`operator`,`or_rec`.`total_quantity`,`or_rec`.`status`,`or_rec`.`remarks`,`or_rec`.`created_at`;

-- ----------------------------
-- View structure for v_order_summary
-- ----------------------------
DROP VIEW IF EXISTS `v_order_summary`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_order_summary` AS select `lo`.`order_id` AS `order_id`,`lo`.`order_code` AS `order_code`,`lo`.`customer_id` AS `customer_id`,`lo`.`customer_name` AS `customer_name`,`c`.`contact_person` AS `contact_person`,`c`.`phone` AS `customer_phone`,`c`.`email` AS `customer_email`,`c`.`credit_rating` AS `credit_rating`,`lo`.`voyage_no` AS `voyage_no`,`lo`.`start_date` AS `start_date`,`lo`.`expected_return_date` AS `expected_return_date`,`lo`.`actual_return_date` AS `actual_return_date`,`lo`.`status` AS `order_status`,`lo`.`total_amount` AS `total_amount`,`lo`.`created_by` AS `created_by`,`lo`.`created_at` AS `created_at`,`lo`.`updated_at` AS `updated_at`,coalesce(`item_stats`.`equipment_count`,0) AS `equipment_count`,coalesce(`item_stats`.`total_rental_days`,0) AS `total_rental_days`,coalesce(`item_stats`.`avg_daily_rate`,0.0) AS `avg_daily_rate`,`b`.`bill_id` AS `bill_id`,`b`.`bill_code` AS `bill_code`,`b`.`status` AS `billing_status`,`b`.`total_amount` AS `billing_amount`,`b`.`payment_method` AS `payment_method`,`b`.`paid_amount` AS `paid_amount`,`rr`.`return_id` AS `return_id`,`rr`.`return_code` AS `return_code`,`rr`.`return_date` AS `return_date`,`rr`.`inspection_status` AS `inspection_status`,`rr`.`total_damage_fee` AS `total_damage_fee` from ((((`lease_orders` `lo` left join `customers` `c` on((`lo`.`customer_id` = `c`.`customer_id`))) left join (select `order_items`.`order_id` AS `order_id`,count(0) AS `equipment_count`,sum(`order_items`.`rental_days`) AS `total_rental_days`,avg(`order_items`.`daily_rate`) AS `avg_daily_rate` from `order_items` group by `order_items`.`order_id`) `item_stats` on((`lo`.`order_id` = `item_stats`.`order_id`))) left join `billing` `b` on(((`lo`.`order_id` = `b`.`order_id`) and (`b`.`is_deleted` = 0)))) left join `return_records` `rr` on((`lo`.`order_id` = `rr`.`order_id`))) where (`lo`.`is_deleted` = 0);

-- ----------------------------
-- Triggers structure for table billing
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_billing_before_insert`;
delimiter ;;
CREATE TRIGGER `trg_billing_before_insert` BEFORE INSERT ON `billing` FOR EACH ROW BEGIN
    IF NEW.total_amount IS NULL OR NEW.total_amount = 0 THEN
        SET NEW.total_amount = COALESCE(NEW.rental_fee, 0) + 
                               COALESCE(NEW.repair_fee, 0) + 
                               COALESCE(NEW.other_fee, 0) - 
                               COALESCE(NEW.discount, 0);
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table billing
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_billing_before_update`;
delimiter ;;
CREATE TRIGGER `trg_billing_before_update` BEFORE UPDATE ON `billing` FOR EACH ROW BEGIN
    IF (NEW.rental_fee != OLD.rental_fee) OR 
       (NEW.repair_fee != OLD.repair_fee) OR 
       (NEW.other_fee != OLD.other_fee) OR 
       (NEW.discount != OLD.discount) THEN
        SET NEW.total_amount = COALESCE(NEW.rental_fee, 0) + 
                               COALESCE(NEW.repair_fee, 0) + 
                               COALESCE(NEW.other_fee, 0) - 
                               COALESCE(NEW.discount, 0);
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table billing
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_billing_after_update`;
delimiter ;;
CREATE TRIGGER `trg_billing_after_update` AFTER UPDATE ON `billing` FOR EACH ROW BEGIN
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('info', '账单更新触发器', 'UPDATE', 'billing', NEW.bill_id, 
            CONCAT('账单更新，账单号: ', NEW.bill_code, '，总金额: ¥', NEW.total_amount));
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table equipment
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_equipment_status_change`;
delimiter ;;
CREATE TRIGGER `trg_equipment_status_change` AFTER UPDATE ON `equipment` FOR EACH ROW BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
        VALUES ('info', '设备状态触发器', 'STATUS_CHANGE', 'equipment', NEW.equipment_id, 
                CONCAT('设备状态变更，设备: ', NEW.equipment_name, ' (', NEW.equipment_code, ')，状态从 "', 
                       OLD.status, '" 变更为 "', NEW.status, '"'));
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table inbound_records
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_inbound_record_created`;
delimiter ;;
CREATE TRIGGER `trg_inbound_record_created` AFTER INSERT ON `inbound_records` FOR EACH ROW BEGIN
    UPDATE equipment e
    INNER JOIN inbound_items ii ON e.equipment_id = ii.equipment_id
    SET e.status = '在库',
        e.updated_at = NOW()
    WHERE ii.inbound_id = NEW.inbound_id
      AND e.is_deleted = 0;

    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '入库记录触发器', 'INSERT', 'inbound_records', NEW.inbound_id, 
            CONCAT('入库记录创建，入库单号: ', NEW.inbound_code, '，供应商: ', COALESCE(NEW.supplier, '未知'), '，设备数量: ', NEW.total_quantity));
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table inspection_records
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_inspection_record_created`;
delimiter ;;
CREATE TRIGGER `trg_inspection_record_created` AFTER INSERT ON `inspection_records` FOR EACH ROW BEGIN
    DECLARE new_status VARCHAR(20);

    IF NEW.repair_needed = 1 OR NEW.function_test = '故障' THEN
        SET new_status = '维修中';
    ELSE
        SET new_status = '在库';
    END IF;

    UPDATE equipment
    SET status = new_status,
        updated_at = NOW()
    WHERE equipment_id = NEW.equipment_id
      AND is_deleted = 0;

    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '质检记录触发器', 'INSERT', 'inspection_records', NEW.inspection_id, 
            CONCAT('质检记录创建，设备: ', NEW.equipment_code, '，质检结果: ', NEW.result, '，设备状态更新为: ', new_status));
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table lease_orders
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_order_created`;
delimiter ;;
CREATE TRIGGER `trg_order_created` AFTER INSERT ON `lease_orders` FOR EACH ROW BEGIN
    UPDATE equipment e
    INNER JOIN order_items oi ON e.equipment_id = oi.equipment_id
    SET e.status = '已出库',
        e.updated_at = NOW()
    WHERE oi.order_id = NEW.order_id
      AND e.status = '在库'
      AND e.is_deleted = 0;

    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '订单创建触发器', 'INSERT', 'lease_orders', NEW.order_id, 
            CONCAT('订单创建，订单号: ', NEW.order_code, '，客户: ', NEW.customer_name, '，总金额: ¥', COALESCE(NEW.total_amount, 0)));
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table order_items
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_order_item_insert`;
delimiter ;;
CREATE TRIGGER `trg_order_item_insert` AFTER INSERT ON `order_items` FOR EACH ROW BEGIN
    UPDATE lease_orders
    SET total_amount = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM order_items
        WHERE order_id = NEW.order_id
    ),
    updated_at = NOW()
    WHERE order_id = NEW.order_id;

    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '订单金额触发器', 'INSERT', 'order_items', NEW.item_id, 
            CONCAT('订单明细插入，订单ID: ', NEW.order_id, '，设备: ', COALESCE(NEW.equipment_name, ''), '，小计: ¥', NEW.subtotal));
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table order_items
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_order_item_update`;
delimiter ;;
CREATE TRIGGER `trg_order_item_update` AFTER UPDATE ON `order_items` FOR EACH ROW BEGIN
    UPDATE lease_orders
    SET total_amount = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM order_items
        WHERE order_id = NEW.order_id
    ),
    updated_at = NOW()
    WHERE order_id = NEW.order_id;

    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('info', '订单金额触发器', 'UPDATE', 'order_items', NEW.item_id, 
            CONCAT('订单明细更新，订单ID: ', NEW.order_id, '，小计从 ¥', COALESCE(OLD.subtotal, 0), ' 变更为 ¥', NEW.subtotal));
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table order_items
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_order_item_delete`;
delimiter ;;
CREATE TRIGGER `trg_order_item_delete` AFTER DELETE ON `order_items` FOR EACH ROW BEGIN
    UPDATE lease_orders
    SET total_amount = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM order_items
        WHERE order_id = OLD.order_id
    ),
    updated_at = NOW()
    WHERE order_id = OLD.order_id;

    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('info', '订单金额触发器', 'DELETE', 'order_items', OLD.item_id, 
            CONCAT('订单明细删除，订单ID: ', OLD.order_id, '，设备: ', COALESCE(OLD.equipment_name, '')));
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table outbound_records
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_outbound_record_created`;
delimiter ;;
CREATE TRIGGER `trg_outbound_record_created` AFTER INSERT ON `outbound_records` FOR EACH ROW BEGIN
    UPDATE equipment e
    INNER JOIN outbound_items oi ON e.equipment_id = oi.equipment_id
    SET e.status = '已出库',
        e.updated_at = NOW()
    WHERE oi.outbound_id = NEW.outbound_id
      AND e.status = '在库'
      AND e.is_deleted = 0;

    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '出库记录触发器', 'INSERT', 'outbound_records', NEW.outbound_id, 
            CONCAT('出库记录创建，出库单号: ', NEW.outbound_code, '，设备数量: ', NEW.total_quantity));
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table return_records
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_return_record_created`;
delimiter ;;
CREATE TRIGGER `trg_return_record_created` AFTER INSERT ON `return_records` FOR EACH ROW BEGIN
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '归还记录触发器', 'INSERT', 'return_records', NEW.return_id, 
            CONCAT('归还记录创建，归还单号: ', NEW.return_code, '，订单ID: ', NEW.order_id, '，设备数量: ', NEW.equipment_count));
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
