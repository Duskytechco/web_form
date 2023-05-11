-- MariaDB dump 10.19  Distrib 10.11.2-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: webform
-- ------------------------------------------------------
-- Server version	10.11.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Banking Info`
--

DROP TABLE IF EXISTS `Banking Info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Banking Info` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NRIC` varchar(14) NOT NULL,
  `Bank Name` varchar(50) DEFAULT NULL,
  `Bank Account Number` varchar(20) DEFAULT NULL,
  `Type Of Account` enum('Saving','Current','Other') NOT NULL,
  `pdfFilePath` varchar(255) DEFAULT NULL,
  `Best time to contact` varchar(30) DEFAULT NULL,
  `Have license or not` enum('Yes','No') DEFAULT NULL,
  `License Type` varchar(50) DEFAULT NULL,
  `How user know Motosing` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `NRIC` (`NRIC`),
  CONSTRAINT `Banking Info_ibfk_1` FOREIGN KEY (`NRIC`) REFERENCES `Personal Info` (`NRIC`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Banking Info`
--

LOCK TABLES `Banking Info` WRITE;
/*!40000 ALTER TABLE `Banking Info` DISABLE KEYS */;
INSERT INTO `Banking Info` VALUES
(2,'030726080765','HONG LEONG BANK','1231231212','Saving','./pdfFiles/Assignment (AAPP004-4-2-JP).pdf','Anytime','Yes','None','Other');
/*!40000 ALTER TABLE `Banking Info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Personal Info`
--

DROP TABLE IF EXISTS `Personal Info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Personal Info` (
  `NRIC` varchar(14) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `Phone Number` varchar(15) NOT NULL,
  `Email` varchar(50) NOT NULL,
  `Title` varchar(50) DEFAULT NULL,
  `Gender` enum('Male','Female') DEFAULT NULL,
  `Race` varchar(20) DEFAULT NULL,
  `Marital Status` varchar(20) DEFAULT NULL,
  `Bumi` enum('Yes','No') DEFAULT NULL,
  `Address` varchar(100) DEFAULT NULL,
  `No of year in residence` varchar(20) DEFAULT NULL,
  `Ownership Status` varchar(20) DEFAULT NULL,
  `Stay in registered address` enum('Yes','No') DEFAULT NULL,
  `Where user stay(If not stay in registered address)` varchar(100) NOT NULL DEFAULT 'None',
  `Product Type` varchar(50) DEFAULT NULL,
  `Brand` varchar(255) DEFAULT NULL,
  `Modal` varchar(255) DEFAULT NULL,
  `User Type` varchar(20) DEFAULT NULL,
  `Number Plate` varchar(20) DEFAULT NULL,
  `Tenure` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`NRIC`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Personal Info`
--

LOCK TABLES `Personal Info` WRITE;
/*!40000 ALTER TABLE `Personal Info` DISABLE KEYS */;
INSERT INTO `Personal Info` VALUES
('030726080765','chong mun seong','0186662127','alfred@gmail.com','MR','Male','Chinese','Single','No','1, testing road, 31350, ipoh, perak','1-2','parents home','Yes','None','bigbike (1000cc and below)','GPX','DEMON GR150R','New','None','60 months (5 years)');
/*!40000 ALTER TABLE `Personal Info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Reference Contact`
--

DROP TABLE IF EXISTS `Reference Contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Reference Contact` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NRIC` varchar(14) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `Phone Number` varchar(15) NOT NULL,
  `Stay with user` enum('Yes','No') DEFAULT NULL,
  `Stay where(If no)` varchar(100) NOT NULL,
  `Relation to user` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `NRIC` (`NRIC`),
  CONSTRAINT `Reference Contact_ibfk_1` FOREIGN KEY (`NRIC`) REFERENCES `Personal Info` (`NRIC`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Reference Contact`
--

LOCK TABLES `Reference Contact` WRITE;
/*!40000 ALTER TABLE `Reference Contact` DISABLE KEYS */;
INSERT INTO `Reference Contact` VALUES
(9,'030726080765','test','+601231231231','Yes','None','parents'),
(10,'030726080765','test1','+601243241231','No','123, test road, 31350, ipoh, perak','parents');
/*!40000 ALTER TABLE `Reference Contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Working Info`
--

DROP TABLE IF EXISTS `Working Info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Working Info` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NRIC` varchar(14) NOT NULL,
  `Employment Status` varchar(50) DEFAULT NULL,
  `Status` varchar(40) DEFAULT NULL,
  `Position` varchar(50) DEFAULT 'N/A',
  `Department` varchar(50) DEFAULT 'N/A',
  `Business Nature` varchar(50) DEFAULT NULL,
  `Company Name` varchar(100) DEFAULT NULL,
  `Company Phone Number` varchar(15) DEFAULT NULL,
  `Working in Singapore` enum('Yes','No') DEFAULT NULL,
  `Company Address` varchar(100) DEFAULT NULL,
  `When user joined company` varchar(15) DEFAULT NULL,
  `Gross Salary` varchar(30) DEFAULT NULL,
  `Salary Term` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `NRIC` (`NRIC`),
  CONSTRAINT `Working Info_ibfk_1` FOREIGN KEY (`NRIC`) REFERENCES `Personal Info` (`NRIC`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Working Info`
--

LOCK TABLES `Working Info` WRITE;
/*!40000 ALTER TABLE `Working Info` DISABLE KEYS */;
INSERT INTO `Working Info` VALUES
(4,'030726080765','self-employed','freeLance','general worker','IT','IT / research / development','test','+601234123123','No','789, testing road, 31350. ipoh. perak','2022-01','RM 10000.21','7');
/*!40000 ALTER TABLE `Working Info` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-11 14:53:54
