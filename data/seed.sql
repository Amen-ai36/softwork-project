-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: the_food_mas2
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add food',7,'add_food'),(26,'Can change food',7,'change_food'),(27,'Can delete food',7,'delete_food'),(28,'Can view food',7,'view_food'),(29,'Can add user',8,'add_user'),(30,'Can change user',8,'change_user'),(31,'Can delete user',8,'delete_user'),(32,'Can view user',8,'view_user'),(33,'Can add order',9,'add_order'),(34,'Can change order',9,'change_order'),(35,'Can delete order',9,'delete_order'),(36,'Can view order',9,'view_order'),(37,'Can add blog',10,'add_blog'),(38,'Can change blog',10,'change_blog'),(39,'Can delete blog',10,'delete_blog'),(40,'Can view blog',10,'view_blog'),(41,'Can add comment',11,'add_comment'),(42,'Can change comment',11,'change_comment'),(43,'Can delete comment',11,'delete_comment'),(44,'Can view comment',11,'view_comment'),(45,'Can add hotel',12,'add_hotel'),(46,'Can change hotel',12,'change_hotel'),(47,'Can delete hotel',12,'delete_hotel'),(48,'Can view hotel',12,'view_hotel'),(49,'Can add hotel order',13,'add_hotelorder'),(50,'Can change hotel order',13,'change_hotelorder'),(51,'Can delete hotel order',13,'delete_hotelorder'),(52,'Can view hotel order',13,'view_hotelorder'),(53,'Can add play',14,'add_play'),(54,'Can change play',14,'change_play'),(55,'Can delete play',14,'delete_play'),(56,'Can view play',14,'view_play'),(57,'Can add play order',15,'add_playorder'),(58,'Can change play order',15,'change_playorder'),(59,'Can delete play order',15,'delete_playorder'),(60,'Can view play order',15,'view_playorder'),(61,'Can add group buy coupon',16,'add_groupbuycoupon'),(62,'Can change group buy coupon',16,'change_groupbuycoupon'),(63,'Can delete group buy coupon',16,'delete_groupbuycoupon'),(64,'Can view group buy coupon',16,'view_groupbuycoupon'),(65,'Can add temp',17,'add_temp'),(66,'Can change temp',17,'change_temp'),(67,'Can delete temp',17,'delete_temp'),(68,'Can view temp',17,'view_temp');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(10,'myapp','blog'),(11,'myapp','comment'),(7,'myapp','food'),(16,'myapp','groupbuycoupon'),(12,'myapp','hotel'),(13,'myapp','hotelorder'),(9,'myapp','order'),(14,'myapp','play'),(15,'myapp','playorder'),(17,'myapp','temp'),(8,'myapp','user'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-06-01 02:35:54.811209'),(2,'auth','0001_initial','2026-06-01 02:35:55.413590'),(3,'admin','0001_initial','2026-06-01 02:35:55.568793'),(4,'admin','0002_logentry_remove_auto_add','2026-06-01 02:35:55.579792'),(5,'admin','0003_logentry_add_action_flag_choices','2026-06-01 02:35:55.587802'),(6,'contenttypes','0002_remove_content_type_name','2026-06-01 02:35:55.682325'),(7,'auth','0002_alter_permission_name_max_length','2026-06-01 02:35:55.738635'),(8,'auth','0003_alter_user_email_max_length','2026-06-01 02:35:55.755338'),(9,'auth','0004_alter_user_username_opts','2026-06-01 02:35:55.761336'),(10,'auth','0005_alter_user_last_login_null','2026-06-01 02:35:55.807526'),(11,'auth','0006_require_contenttypes_0002','2026-06-01 02:35:55.810525'),(12,'auth','0007_alter_validators_add_error_messages','2026-06-01 02:35:55.818526'),(13,'auth','0008_alter_user_username_max_length','2026-06-01 02:35:55.877045'),(14,'auth','0009_alter_user_last_name_max_length','2026-06-01 02:35:55.937560'),(15,'auth','0010_alter_group_name_max_length','2026-06-01 02:35:55.953937'),(16,'auth','0011_update_proxy_permissions','2026-06-01 02:35:55.960239'),(17,'auth','0012_alter_user_first_name_max_length','2026-06-01 02:35:56.019899'),(18,'myapp','0001_initial','2026-06-01 02:35:56.179585'),(19,'sessions','0001_initial','2026-06-01 02:35:56.213655'),(20,'myapp','0002_auto_20260601_1125','2026-06-01 03:25:53.621808'),(21,'myapp','0003_auto_20260601_1248','2026-06-01 04:48:30.639697'),(22,'myapp','0004_auto_20260601_1254','2026-06-01 04:55:03.330680'),(23,'myapp','0005_auto_20260601_1306','2026-06-01 05:06:35.842878'),(24,'myapp','0006_blog','2026-06-02 06:54:19.503046'),(25,'myapp','0007_blog_isdeleted_comment','2026-06-02 11:04:13.038575'),(26,'myapp','0008_alter_blog_id_alter_comment_id_alter_food_id_and_more','2026-06-05 00:15:15.010015'),(27,'myapp','0009_order_cost','2026-06-05 00:16:23.133509'),(28,'myapp','0010_hotel','2026-06-08 08:11:21.569074'),(29,'myapp','0011_user_usertype','2026-06-08 08:19:39.161833'),(30,'myapp','0012_hotelorder','2026-06-08 08:20:43.556235'),(31,'myapp','0013_food_hotel_merchant','2026-06-08 08:20:43.564510'),(32,'myapp','0014_order_rider_play_playorder','2026-06-08 08:20:43.567238'),(33,'myapp','0015_alter_user_usertype','2026-06-08 08:20:53.347193'),(34,'myapp','0016_groupbuycoupon','2026-06-09 05:08:03.259709'),(35,'myapp','0017_temp','2026-06-09 07:36:53.839383');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('322ylcjapw82dxmzpadm57pqz9vblnf4','eyJ1c2VyX2lkIjo3fQ:1wVmuS:qbyOSNrDAySJFDzyIJRq2NopWpFEyMFzMLUPujHN4A4','2026-06-20 09:01:40.063063'),('a8k62xk4aegicf6pphdsr9xucwhlw2qw','eyJ1c2VyX2lkIjoxNH0:1wWXRY:y7mNffsveLKDPO4cA-fIaN1J0esnvNJjdhHm8Y3VEbQ','2026-06-22 10:42:56.046644'),('cbnqz3scsykgfu281lve99xdxlm3chtr','eyJ1c2VyX2lkIjoxMn0:1wVmt4:xDYEB2aqdEk8WzFjtFrwGmlji_zmP0-uX5UFBURuy6U','2026-06-20 09:00:14.605532'),('dqio9y64sdbl4fntnhfbw66bwzoiqxxe','eyJ1c2VyX2lkIjoxMH0:1wWrn1:65cT6oKhfkulL448AzwpF82e0GsdpvDQIcmyWnQetoc','2026-06-23 08:26:27.538314'),('pidme424fvvtezp1kuich9wft5146y64','eyJ1c2VyX2lkIjoxMX0:1wVmnX:dzECFWdklzyp52sKXHTfNgAERc2VfR2PeUdsf3ETnuk','2026-06-20 08:54:31.840930'),('uhtznhzru8zwt13y6fmcccvaicvycwzg','eyJ1c2VyX2lkIjoxfQ:1wWr8V:y99gpCb_F6dx1TPPf3RPnMbgDwny0VU6i1WpeFf1Yls','2026-06-23 07:44:35.458112');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_blog`
--

DROP TABLE IF EXISTS `myapp_blog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_blog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `authorid_id` bigint NOT NULL,
  `isdeleted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_blog_authorid_id_470749b4_fk` (`authorid_id`),
  CONSTRAINT `myapp_blog_authorid_id_470749b4_fk` FOREIGN KEY (`authorid_id`) REFERENCES `myapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_blog`
--

LOCK TABLES `myapp_blog` WRITE;
/*!40000 ALTER TABLE `myapp_blog` DISABLE KEYS */;
INSERT INTO `myapp_blog` VALUES (1,'这个水煮鱼怎么还没到','愁死我了，我十一点多下的单，现在眼瞅着12：40了，还在配送中，这是赶上午高峰了吗？怎么还堵着了？我寻思着这也就是几km啊要这么久？不至于吧','2026-06-02 08:23:09.972353',5,0),(2,'孜然羊肉哭死我','兄弟们发现一个特别好吃的羊肉，这个无肉不欢果然是有点东西的，我说我强烈推荐啊啊啊，有没有谁懂那种第一口就惊艳我的感觉啊啊啊，只能说是人间美味了','2026-06-02 08:41:50.975803',2,0),(3,'人果然不能共情哪怕一年前的自己','今天重做了一年前做过的数据结构题，先把去年的代码交上去，80/100，然后打算重构以前的代码，结果死活看不懂之前的代码的逻辑，索性直接把那部分推倒重写，花了几分钟就过了。说真的，不知道当时写这么复杂的代码是为了干什么，纯纯屎山','2026-06-02 12:29:29.882421',1,0),(4,'虾米好吃','嘿嘿……虾米好吃……音游好玩……嘿嘿……嘿嘿……','2026-06-02 14:24:31.414334',3,0),(5,'标题五个字','不吹不黑，大家觉得这个平台怎么样？我感觉还可以，至少应该是有认真在搞这件事的','2026-06-03 03:33:05.941546',6,0),(6,'825623','这条博客仅用于测试功能','2026-06-03 05:50:26.031194',1,0),(7,'初来乍到','求资深老吃家推荐一些不错的，谢了','2026-06-05 02:29:55.187143',7,0),(8,'aqweqeqeqe','你好','2026-06-05 11:41:24.055832',8,0);
/*!40000 ALTER TABLE `myapp_blog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_comment`
--

DROP TABLE IF EXISTS `myapp_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_comment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `userid` int NOT NULL,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `isdeleted` tinyint(1) NOT NULL,
  `blogid_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_comment_blogid_id_592cf1eb_fk` (`blogid_id`),
  CONSTRAINT `myapp_comment_blogid_id_592cf1eb_fk` FOREIGN KEY (`blogid_id`) REFERENCES `myapp_blog` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_comment`
--

LOCK TABLES `myapp_comment` WRITE;
/*!40000 ALTER TABLE `myapp_comment` DISABLE KEYS */;
INSERT INTO `myapp_comment` VALUES (1,1,'北京的交通就是这样的，习惯就好','2026-06-02 11:43:14.453140',0,1),(2,1,'闻讯而来，意满而离','2026-06-02 11:46:01.778410',1,2),(3,3,'虽然但是这和美食博客有什么关系？？','2026-06-02 12:30:35.503020',0,3),(4,1,'那想必会很好吃了','2026-06-02 14:15:24.917681',1,2),(5,2,'谁家小学生过来了我操\n开智了吗你就瞎几把乱叫','2026-06-02 14:25:36.774610',0,4),(6,1,'要不说互联网发达呢，一只成年边牧也能发表自己的观点','2026-06-03 03:02:05.922600',0,4),(7,5,'到了到了，挺好吃，谢谢喵','2026-06-03 03:04:51.912335',0,1),(8,1,'初创平台罢了，刚开始都搞的好，到最后都会收敛成一个眼中只有钱的平台的','2026-06-03 04:28:29.459398',0,5),(9,1,'建议\n香辣虾✅\n孜然羊肉✅\n别的不清楚','2026-06-05 03:15:40.362986',0,7),(10,8,'sdadadadada','2026-06-05 11:37:24.105676',0,1),(11,1,'hello world','2026-06-07 09:21:05.316695',0,8);
/*!40000 ALTER TABLE `myapp_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_food`
--

DROP TABLE IF EXISTS `myapp_food`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_food` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` double NOT NULL,
  `image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sale` int NOT NULL DEFAULT '0',
  `providor` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inf` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `rating` decimal(2,1) NOT NULL,
  `ratenum` int NOT NULL,
  `saleperson` int NOT NULL,
  `merchant_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_food_merchant_id_fk` (`merchant_id`),
  CONSTRAINT `myapp_food_merchant_id_fk` FOREIGN KEY (`merchant_id`) REFERENCES `myapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_food`
--

LOCK TABLES `myapp_food` WRITE;
/*!40000 ALTER TABLE `myapp_food` DISABLE KEYS */;
INSERT INTO `myapp_food` VALUES (1,'鱼香肉丝',15.8,'images/food/1.jpg',6,'家味','鱼香肉丝酸甜微辣，肉丝嫩滑，木耳胡萝卜脆爽，酱汁浓郁。拌饭一绝，经典川味，每次必点。',4.6,5,7,12),(2,'宫保鸡丁',18.5,'images/food/2.jpg',0,'小川家常菜','鸡丁嫩滑不柴，花生酥脆，糊辣荔枝味平衡得恰到好处。酸甜开胃，下饭神器。',0.0,0,0,12),(3,'麻婆豆腐',12,'images/food/3.jpg',2,'川菜大师','麻辣鲜香，豆腐入口即化，牛肉末增鲜，花椒麻味十足。拌饭吃三碗，正宗川味。',4.5,2,3,12),(4,'回锅肉',22,'images/food/4.jpg',1,'家味','五花肉肥瘦相间，煸至微卷，蒜苗清香，豆豉酱香浓郁。咸鲜微辣，肥而不腻。',4.5,1,2,12),(5,'糖醋里脊',25,'images/food/5.jpg',0,'小川家常菜','外酥里嫩，酸甜汁浓稠红亮。一口咬下咔吱脆，老少皆宜，小朋友最爱。',0.0,0,0,12),(6,'水煮鱼',38,'images/food/6.jpg',1,'川菜大师','鱼片嫩滑无刺，麻辣汤底油香四溢，豆芽脆爽。重口味福音，辣得过瘾。',4.6,2,2,12),(7,'酸菜鱼',35,'images/food/7.jpg',1,'赌上厨师生涯的菜','酸辣开胃，鱼片鲜嫩，酸菜脆爽，汤底金黄浓郁。先喝汤再吃鱼，温暖满足。',4.4,2,2,12),(8,'干煸豆角',14,'images/food/8.jpg',3,'家味','豆角干香微焦，肉末花椒提味，咸鲜微麻。越嚼越香，下酒好菜。',3.7,4,4,12),(9,'地三鲜',13.5,'images/food/9.jpg',2,'家味','土豆软糯，茄子吸汁，青椒清甜。咸香适口，东北家常味，朴实好吃。',0.0,0,1,13),(10,'红烧肉',28,'images/food/10.jpg',0,'赌上厨师生涯的菜','五花肉酥烂，冰糖上色红亮，肥而不腻，入口即化。甜咸交织，米饭杀手。',0.0,0,0,13),(11,'西红柿炒蛋',10.5,'images/food/11.jpg',2,'家味','酸甜多汁，鸡蛋嫩滑，汤汁浓稠。简单却经典，拌饭能吃两大碗。',4.4,2,2,13),(12,'醋溜白菜',9.8,'images/food/12.jpg',1,'家味','白菜脆爽，醋香浓郁，辣椒提味。酸辣爽口，解腻佳品，家常快手菜。',4.5,2,2,13),(13,'蒜蓉西兰花',12.8,'images/food/13.jpg',1,'素斋','西兰花脆绿，蒜香浓郁，清淡健康。保留了原味，低脂营养。',3.9,2,2,13),(14,'孜然羊肉',32,'images/food/14.jpg',2,'无肉不欢','羊肉焦香有嚼劲，孜然味浓，辣香扑鼻。不膻不腻，配馕或米饭都香。',5.0,2,2,13),(15,'京酱肉丝',26,'images/food/15.jpg',0,'家味','肉丝酱香咸甜，嫩滑适口，葱丝脆爽。用豆腐皮卷着吃，地道京味。',0.0,0,0,13),(16,'红烧排骨',30,'images/food/16.jpg',0,'无肉不欢','排骨炖得酥烂，轻轻一咬脱骨，酱香浓郁。汤汁浓稠浇饭，大口吃肉满足。',0.0,0,0,13),(17,'干锅花菜',16,'images/food/17.jpg',2,'家味','花菜干香微焦，五花肉煸出油，麻辣干香。越加热越入味，下酒好菜。',4.7,2,4,13),(18,'香辣虾',42,'images/food/18.jpg',6,'有原则的虾米','虾壳酥脆，虾肉Q弹，香麻辣味渗透。配菜土豆条也好吃，吮指回味。',4.9,8,9,13),(19,'清炒时蔬',11,'images/food/19.jpg',1,'素斋','时令蔬菜脆嫩清甜，少油少盐，保留本味。清淡解腻，健康之选。',0.0,0,2,12),(20,'铁板牛肉',36,'images/food/20.jpg',0,'无肉不欢','上桌滋滋作响，牛肉嫩滑多汁，黑椒酱香浓郁。洋葱脆甜，热辣过瘾。',0.0,0,0,12),(21,'火锅鸡',30,'images/food/1.jpg',2,'成府路88号','火锅里面的鸡',4.1,1,2,12),(22,'蚂蚁上树',9.9,'images/food/ff979ab4133c4653b620cbc3bff463e2_1780897059.jpg',0,'航味','正宗航味（北京航空航天大学官方出品）',0.0,0,0,13),(23,'蛋炒饭',7.9,'images/food/04e0ff5b921c4479aadbfd19c4287742_1780914774.jpg',2,'航味','依旧航味',4.6,2,3,13);
/*!40000 ALTER TABLE `myapp_food` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_groupbuycoupon`
--

DROP TABLE IF EXISTS `myapp_groupbuycoupon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_groupbuycoupon` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `num` int NOT NULL,
  `cost` double NOT NULL,
  `code` varchar(20) NOT NULL,
  `status` int NOT NULL,
  `time` datetime(6) NOT NULL,
  `used_at` datetime(6) DEFAULT NULL,
  `food_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `myapp_groupbuycoupon_food_id_fe81d299_fk_myapp_food_id` (`food_id`),
  KEY `myapp_groupbuycoupon_user_id_73a8a2ab_fk_myapp_user_id` (`user_id`),
  CONSTRAINT `myapp_groupbuycoupon_food_id_fe81d299_fk_myapp_food_id` FOREIGN KEY (`food_id`) REFERENCES `myapp_food` (`id`),
  CONSTRAINT `myapp_groupbuycoupon_user_id_73a8a2ab_fk_myapp_user_id` FOREIGN KEY (`user_id`) REFERENCES `myapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_groupbuycoupon`
--

LOCK TABLES `myapp_groupbuycoupon` WRITE;
/*!40000 ALTER TABLE `myapp_groupbuycoupon` DISABLE KEYS */;
INSERT INTO `myapp_groupbuycoupon` VALUES (1,1,12,'A2B64EB1CD',0,'2026-06-09 05:45:00.248179',NULL,3,1),(2,1,42,'E31C5ED38F',0,'2026-06-09 08:26:39.830578',NULL,18,10);
/*!40000 ALTER TABLE `myapp_groupbuycoupon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_hotel`
--

DROP TABLE IF EXISTS `myapp_hotel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_hotel` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `addr` varchar(100) NOT NULL,
  `price_clock` double DEFAULT NULL,
  `price_day` double DEFAULT NULL,
  `price_double_clock` double DEFAULT NULL,
  `price_double_day` double DEFAULT NULL,
  `price_special` double DEFAULT NULL,
  `image` varchar(100) NOT NULL,
  `rating` decimal(2,1) DEFAULT NULL,
  `inf` varchar(200) NOT NULL,
  `orders` int NOT NULL,
  `ratenum` int NOT NULL,
  `merchant_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_hotel_merchant_id_fk` (`merchant_id`),
  CONSTRAINT `myapp_hotel_merchant_id_fk` FOREIGN KEY (`merchant_id`) REFERENCES `myapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_hotel`
--

LOCK TABLES `myapp_hotel` WRITE;
/*!40000 ALTER TABLE `myapp_hotel` DISABLE KEYS */;
INSERT INTO `myapp_hotel` VALUES (1,'维也纳3好酒店','河北省邢台市任泽区任泽镇人民街与同济路交叉口',19,99,39,169,229,'images/hotel/1.jpg',4.3,'低调酒店，门面简约大气，停车方便，离市中心近，旅行居住首选',3,3,12),(2,'如家精选酒店','上海市黄浦区南京东路步行街100号',39,159,59,259,319,'images/hotel/1.jpg',3.8,'地处南京东路，出门即是地铁站，外滩夜景近在咫尺',1,1,12),(3,'汉庭酒店','广东省深圳市南山区科技园科发路8号',35,139,55,229,289,'images/hotel/1.jpg',0.0,'紧邻腾讯大厦，科技氛围浓厚，适合IT差旅人士',0,0,12),(4,'全季酒店','浙江省杭州市西湖区北山街15号',49,199,79,299,399,'images/hotel/1.jpg',0.0,'步行至西湖断桥仅需5分钟，部分房间可观湖景',0,0,12),(5,'丽枫酒店','江苏省苏州市姑苏区平江路88号',45,179,69,269,359,'images/hotel/1.jpg',0.0,'位于平江路历史街区，苏式园林风格，闹中取静',0,0,12),(6,'桔子酒店','四川省成都市锦江区春熙路西段66号',42,169,65,249,329,'images/hotel/1.jpg',0.0,'春熙路商圈核心位置，楼下就是太古里，美食云集',0,0,13),(7,'亚朵酒店','湖北省武汉市武昌区黄鹤楼南路12号',38,149,59,239,299,'images/hotel/1.jpg',0.0,'黄鹤楼景区旁，江景房视野开阔，文化主题设计',0,0,13),(8,'锦江之星','湖南省长沙市天心区五一大道188号',32,129,49,199,259,'images/hotel/1.jpg',0.0,'五一广场附近，距离橘子洲头仅2站地铁',0,0,13),(9,'城市便捷酒店','山东省青岛市市南区香港中路50号',36,149,55,239,289,'images/hotel/1.jpg',0.0,'五四广场东侧，步行至海边8分钟，夏季避暑热门',0,0,13),(10,'7天连锁酒店','陕西省西安市碑林区东大街钟楼旁300号',28,119,45,189,249,'images/hotel/1.jpg',0.0,'钟楼商圈，回民街步行可达，性价比高',0,0,13),(11,'哈喽酒店','月球28号',12,100,24,220,32,'images/hotel/1.jpg',5.0,'我的梦想是去月球',2,2,12),(12,'云上客栈','N/A',29,129,39,169,218,'images/hotel/1.jpg',0.0,'一个小小的客栈',0,0,13),(13,'红尘客栈（？）','不知道',99,369,119,499,699,'images/hotel/536482b5cda24db39117a44037270182_1780896355.jpg',0.0,'红尘来去散无痕，醉酒当歌思故人',0,0,13);
/*!40000 ALTER TABLE `myapp_hotel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_hotelorder`
--

DROP TABLE IF EXISTS `myapp_hotelorder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_hotelorder` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `hotel_id` bigint NOT NULL,
  `room_type` varchar(20) NOT NULL COMMENT '房型：single_clock/single_day/double_clock/double_day/special_day',
  `duration` int NOT NULL COMMENT '入住时长，钟点房为小时，日租房为天数',
  `checkin_time` datetime(6) NOT NULL COMMENT '预计入住时间',
  `time` datetime(6) NOT NULL COMMENT '预定时间',
  `cost` double NOT NULL DEFAULT '0',
  `comment` varchar(200) NOT NULL DEFAULT '' COMMENT '入住评价内容',
  `score` decimal(2,1) NOT NULL DEFAULT '0.0' COMMENT '入住评分 0.0-5.0',
  `pos` int NOT NULL DEFAULT '4' COMMENT '4-可评价，5-已评价',
  PRIMARY KEY (`id`),
  KEY `myapp_hotelorder_user_id_fk` (`user_id`),
  KEY `myapp_hotelorder_hotel_id_fk` (`hotel_id`),
  CONSTRAINT `myapp_hotelorder_hotel_id_fk` FOREIGN KEY (`hotel_id`) REFERENCES `myapp_hotel` (`id`),
  CONSTRAINT `myapp_hotelorder_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `myapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_hotelorder`
--

LOCK TABLES `myapp_hotelorder` WRITE;
/*!40000 ALTER TABLE `myapp_hotelorder` DISABLE KEYS */;
INSERT INTO `myapp_hotelorder` VALUES (1,8,1,'single_clock',2,'2026-06-05 22:18:00.000000','2026-06-05 14:19:30.550982',38,'不赖',4.7,5),(2,8,2,'special_day',3,'2026-06-05 22:29:00.000000','2026-06-05 14:29:29.406106',957,'一般般',3.8,5),(3,8,1,'single_clock',2,'2026-06-05 22:41:00.000000','2026-06-05 14:41:16.411699',38,'222',4.2,5),(4,10,1,'double_day',2,'2026-06-05 22:56:00.000000','2026-06-05 14:56:55.701567',338,'一般',4.0,5),(5,8,11,'single_day',2,'2026-06-05 23:38:00.000000','2026-06-05 15:38:35.252132',200,'其实也不是想去月球',5.0,5),(6,1,11,'double_day',1,'2026-06-12 21:00:00.000000','2026-06-08 02:50:53.236481',220,'真不戳，月球真的有嫦娥仙子，真不戳',4.9,5);
/*!40000 ALTER TABLE `myapp_hotelorder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_order`
--

DROP TABLE IF EXISTS `myapp_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_order` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `num` int NOT NULL,
  `time` datetime(6) NOT NULL,
  `comment` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `food_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `scoretodeliver` decimal(2,1) DEFAULT NULL,
  `scoretofood` decimal(2,1) DEFAULT NULL,
  `pos` int NOT NULL DEFAULT '0',
  `cost` double NOT NULL,
  `rider_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_order_food_id_da9a8556_fk` (`food_id`),
  KEY `myapp_order_user_id_98783cea_fk` (`user_id`),
  KEY `myapp_order_rider_id_fk` (`rider_id`),
  CONSTRAINT `myapp_order_food_id_da9a8556_fk` FOREIGN KEY (`food_id`) REFERENCES `myapp_food` (`id`),
  CONSTRAINT `myapp_order_rider_id_fk` FOREIGN KEY (`rider_id`) REFERENCES `myapp_user` (`id`),
  CONSTRAINT `myapp_order_user_id_98783cea_fk` FOREIGN KEY (`user_id`) REFERENCES `myapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_order`
--

LOCK TABLES `myapp_order` WRITE;
/*!40000 ALTER TABLE `myapp_order` DISABLE KEYS */;
INSERT INTO `myapp_order` VALUES (1,1,'2026-06-01 12:34:56.325782','很好吃，麻婆豆腐麻辣鲜香，可惜送餐的速度稍稍慢了些超时几分钟了',3,1,'北京市海淀区学院路37号北京航空航天大学学院路校区新北区',4.3,4.5,5,12,9),(2,2,'2026-05-24 18:01:22.485899','非常美味，酥脆，绝了',18,3,'北京市昌平区沙河镇高教园南三街9号北京航空航天大学沙河校区西区',4.9,4.7,5,84,9),(3,2,'2026-06-01 13:21:24.471511','炒的有点老了，不是很好吃。配送不错，很贴心',8,1,'湖南省邵阳市邵东县两市镇建设北路234号',4.9,3.8,5,28,9),(4,1,'2026-06-01 13:34:37.497278','这位商家，你无疑是赢麻了，这玩意确实是过于的好吃，让我无法组织有效的语言去评价他，总之一句话，好吃！配送小哥哥也很有礼貌，好评点了！',18,4,'河北省邢台市任泽区人民街233号',4.9,4.9,5,42,11),(5,1,'2026-06-01 13:39:09.084967','好吃还是很好吃的，选材不错，白菜不老，做的也还可以，可惜配送不咋地，汤都撒了啊',12,4,'河北省邢台市任泽区人民街233号',3.2,4.5,5,9.8,11),(6,1,'2026-06-02 07:00:24.192355','辣，但好吃，就是等了挺久',6,5,'河南省洛阳市洛龙区通衢路48号',3.8,4.6,5,38,14),(7,2,'2026-06-02 07:07:05.239709','配送的速度还可以，味道还算行吧，可能我还是更习惯于西红柿开汤，总体中规中矩',11,5,'湖北省襄阳市樊城区紫贞街道长虹北路93号',4.5,4.4,5,21,14),(8,2,'2026-06-02 08:37:31.870583','足以封神，特别好吃，肥而不腻，麻辣鲜美，配送很快，大赞！！',14,2,'上海市杨浦区邯郸路220号复旦大学邯郸校区7号宿舍楼1单元402',4.9,5.0,5,64,14),(9,1,'2026-06-02 12:32:22.561649','',17,3,'北京市昌平区沙河镇高教园南三街9号北京航空航天大学沙河校区西区',0.0,0.0,2,16,9),(10,1,'2026-06-03 03:17:53.456200','',19,5,'河南省洛阳市洛龙区通衢路92号',0.0,0.0,2,11,9),(11,1,'2026-06-03 03:23:56.673106','最好的一集，无论味道和配送都足以封神',18,6,'安徽省合肥市包河区金寨路96号中国科学技术大学东校区统一取餐点',5.0,5.0,5,42,11),(12,1,'2026-06-03 03:25:52.911766','这个豆角有点太干了，要么是选材问题要么是烹饪问题了，刚吃几口还可以吃到后面简直不喝水吃不下去',8,6,'安徽省合肥市包河区金寨路96号中国科学技术大学东校区统一取餐点',4.4,3.5,5,14,14),(13,1,'2026-06-03 03:26:03.844123','不是很好吃，或许是这种食材的这种做法本身就很难做的好吃吧，感觉店主可以下架这道菜换一个新的做法',13,6,'安徽省合肥市包河区金寨路96号中国科学技术大学东校区统一取餐点',4.0,3.9,5,12.8,14),(14,1,'2026-06-03 03:30:42.994669','这个显然就好吃不少了，比那个蒜蓉西兰花强远了',17,6,'安徽省合肥市包河区金寨路96号中国科学技术大学东校区统一取餐点',4.8,4.7,5,16,14),(15,1,'2026-06-03 03:35:59.183732','好吃，配上土豆条和啤酒无敌了',18,1,'北京市海淀区学院路37号北京航空航天大学学院路校区新北区',4.7,5.0,5,42,9),(16,1,'2026-06-03 05:49:38.114244','挺不错，中规中矩的，还挺好吃，稍咸了，配送稍慢了些',1,1,'湖南省邵阳市邵东县两市镇建设北路234号',4.2,4.5,5,15.8,9),(17,1,'2026-06-05 02:27:06.814245','还不错，酸菜酸酸爽口，鱼也比较嫩，鲜甜，就是鱼刺有点多了，',7,7,'湖南省长沙市岳麓区麓山南路932号中南大学岳麓山校区',4.3,4.4,5,35,14),(18,1,'2026-06-05 02:35:04.075067','11',4,7,'湖南省长沙市岳麓区麓山南路932号中南大学岳麓山校区',4.5,4.5,5,22,11),(19,1,'2026-06-05 11:37:44.453726','不赖',1,8,'wasda',4.8,4.5,5,15.8,11),(20,1,'2026-06-05 11:45:42.376242','不赖',1,8,'wasda',4.5,4.9,5,15.8,11),(21,1,'2026-06-05 13:13:41.861129','不戳',1,8,'wasda',4.2,4.7,5,15.8,9),(22,1,'2026-06-05 13:54:55.745244','',1,8,'wasda',0.0,0.0,4,15.8,9),(23,1,'2026-06-05 13:55:01.419802','不赖',1,8,'wasda',4.8,4.5,5,15.8,11),(24,1,'2026-06-05 15:31:50.884358','',21,8,'wasda',0.0,0.0,4,30,14),(25,1,'2026-06-06 07:06:54.372359','可以',21,8,'wasda',4.2,4.1,5,30,9),(27,1,'2026-06-08 10:40:54.082828','牛逼',23,1,'中国北京市海淀区学院路37号 北航学院路校区',4.4,4.7,5,7.9,14),(28,1,'2026-06-08 10:58:05.636231','没有上次的好吃',23,1,'中国北京市海淀区学院路37号 北航学院路校区',4.5,4.4,5,7.9,14),(29,2,'2026-06-09 08:17:10.963824','',9,1,'湖南省邵阳市邵东县两市镇建设北路233号',0.0,0.0,0,54,NULL);
/*!40000 ALTER TABLE `myapp_order` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_after_order_insert` AFTER INSERT ON `myapp_order` FOR EACH ROW BEGIN
    UPDATE myapp_food 
    SET saleperson = saleperson + 1,
        sale = sale + NEW.num
    WHERE id = NEW.food_id;
    
    IF NEW.pos = 5 AND NEW.scoretofood > 0 AND NEW.scoretodeliver > 0 THEN
        UPDATE myapp_food
        SET 
            rating = (rating * ratenum + NEW.scoretofood) / (ratenum + 1),
            ratenum = ratenum + 1
        WHERE id = NEW.food_id;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_after_order_update` AFTER UPDATE ON `myapp_order` FOR EACH ROW BEGIN
    IF OLD.pos != 5 AND NEW.pos = 5 AND NEW.scoretofood > 0 THEN
        UPDATE myapp_food
        SET 
            rating = (rating * ratenum + NEW.scoretofood) / (ratenum + 1),
            ratenum = ratenum + 1
        WHERE id = NEW.food_id;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `myapp_play`
--

DROP TABLE IF EXISTS `myapp_play`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_play` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `addr` varchar(100) NOT NULL,
  `price` float NOT NULL,
  `open_time` varchar(50) DEFAULT '24h',
  `image` varchar(100) NOT NULL,
  `rating` decimal(2,1) DEFAULT '0.0',
  `ratenum` int DEFAULT '0',
  `inf` varchar(200) DEFAULT '',
  `orders` int DEFAULT '0',
  `merchant_id` bigint DEFAULT NULL,
  `start_time` varchar(50) NOT NULL DEFAULT '09:00' COMMENT '开始营业时间',
  PRIMARY KEY (`id`),
  KEY `merchant_id` (`merchant_id`),
  CONSTRAINT `myapp_play_ibfk_1` FOREIGN KEY (`merchant_id`) REFERENCES `myapp_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_play`
--

LOCK TABLES `myapp_play` WRITE;
/*!40000 ALTER TABLE `myapp_play` DISABLE KEYS */;
INSERT INTO `myapp_play` VALUES (1,'水上乐园','月球29号',120,'8h','images/play/1.png',4.6,2,'水上乐园玩水',2,12,'09:00'),(2,'欢乐谷','月球11号',99,'12h','images/play/1.png',0.0,0,'游乐园',0,12,'09:00'),(3,'香山','北京000号',100,'24h','images/play/1.png',0.0,0,'爬山',0,12,'09:20'),(4,'环球大影城','太阳系火星火链联邦大成域xx市xx大道',49,'12h','images/play/78685a375abd48aba52052d985c8131a_1780894783.jpg',0.0,0,'第一个火星影城',0,13,'09:00'),(5,'多乐台球厅','北京市海淀区学院路33号',19,'12h','images/play/35c226f917e243548ed35ff37896a11e_1780895157.jpg',0.0,0,'a 台球厅',0,13,'09:00');
/*!40000 ALTER TABLE `myapp_play` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_playorder`
--

DROP TABLE IF EXISTS `myapp_playorder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_playorder` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `play_id` bigint NOT NULL,
  `num` int NOT NULL,
  `visit_time` datetime NOT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  `cost` float DEFAULT '0',
  `comment` varchar(200) DEFAULT '',
  `score` decimal(2,1) DEFAULT '0.0',
  `pos` int DEFAULT '4',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `play_id` (`play_id`),
  CONSTRAINT `myapp_playorder_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `myapp_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `myapp_playorder_ibfk_2` FOREIGN KEY (`play_id`) REFERENCES `myapp_play` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_playorder`
--

LOCK TABLES `myapp_playorder` WRITE;
/*!40000 ALTER TABLE `myapp_playorder` DISABLE KEYS */;
INSERT INTO `myapp_playorder` VALUES (1,8,1,1,'2026-06-06 15:45:00','2026-06-06 07:45:07',120,'不赖',4.5,5),(2,1,1,2,'2026-06-13 09:30:00','2026-06-07 09:17:56',240,'非常好玩',4.7,5);
/*!40000 ALTER TABLE `myapp_playorder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_temp`
--

DROP TABLE IF EXISTS `myapp_temp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_temp` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `num` int NOT NULL,
  `cost` double NOT NULL,
  `address` varchar(100) NOT NULL,
  `pos` int NOT NULL,
  `food_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_temp_food_id_ae8ab49a_fk_myapp_food_id` (`food_id`),
  KEY `myapp_temp_user_id_c0340a70_fk_myapp_user_id` (`user_id`),
  CONSTRAINT `myapp_temp_food_id_ae8ab49a_fk_myapp_food_id` FOREIGN KEY (`food_id`) REFERENCES `myapp_food` (`id`),
  CONSTRAINT `myapp_temp_user_id_c0340a70_fk_myapp_user_id` FOREIGN KEY (`user_id`) REFERENCES `myapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_temp`
--

LOCK TABLES `myapp_temp` WRITE;
/*!40000 ALTER TABLE `myapp_temp` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_temp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_user`
--

DROP TABLE IF EXISTS `myapp_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `isDelete` tinyint(1) NOT NULL DEFAULT '0',
  `word` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `usertype` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_user`
--

LOCK TABLES `myapp_user` WRITE;
/*!40000 ALTER TABLE `myapp_user` DISABLE KEYS */;
INSERT INTO `myapp_user` VALUES (1,'adminZwj','Buaa362880!','13036732080',0,'啊，好次，好次，都好好次（喜欢辣，不要太甜版）',0),(2,'admin002','zwj061007','13548896609',0,'a pure foodie',0),(3,'user001','hahahage233','14637292508',0,'',0),(4,'user002','123456qwerty','15573916695',0,'立志吃遍天下美食！！！',0),(5,'user003','eating2580','18235782948',0,'饭不在多，好吃就行',0),(6,'user004','whatcanisay=24','13948854790',0,'',0),(7,'你的好友Tom猫','tomeatjerry111','',0,'立志吃到杰瑞的一天',0),(8,'a','Wsy2006bhh','',0,'',0),(9,'test2','Wsy2006test','',0,'',1),(10,'sola','ppd114514','',0,'',0),(11,'b','Wsy2006qqh','',0,'',1),(12,'testShop','test114514','',0,'',2),(13,'asmallcoder','qwerty2580','11122223333',0,'凉心商家在此！！',2),(14,'rider001','hahaha233','',0,'总有一天，特朗普会爱上送外卖的我',1),(15,'admin','quanju123','12345678910',0,'111',3),(16,'user','zwj1234567','',0,'',0),(17,'rider002','sbisme233','',0,'',1);
/*!40000 ALTER TABLE `myapp_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-09 16:45:29
