-- MySQL dump 10.13  Distrib 5.7.44, for Linux (x86_64)
--
-- Host: localhost    Database: genai_kb
-- ------------------------------------------------------
-- Server version	5.7.44

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
-- Table structure for table `tb_kb`
--

DROP TABLE IF EXISTS `tb_kb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_kb` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `space_id` int(11) DEFAULT '0',
  `db_type` varchar(32) DEFAULT 'pg',
  `db_config` text,
  `kb_type` varchar(64) DEFAULT 'doc',
  `chunk_mode` varchar(64) DEFAULT 'paragraph',
  `chunk_len` int(11) DEFAULT '500',
  `embedding_model` varchar(128) DEFAULT '',
  `reranker_model` varchar(128) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_kb`
--

LOCK TABLES `tb_kb` WRITE;
/*!40000 ALTER TABLE `tb_kb` DISABLE KEYS */;
INSERT INTO `tb_kb` VALUES (1,'产品手册','测试库','2026-11-18 03:05:09',1,'pg','','doc','paragraph',500,'',''),(2,'产品FAQ库','','2026-11-18 13:58:48',1,'pg','','faq','sentence',300,'bge-m3','bge-reranker-v2-m3'),(3,'ES产品FAQ','','2026-11-18 14:51:41',1,'es','{\"url\":\"http://localhost:9200\",\"user\":\"elastic\",\"password\":\"Es@123456\"}','faq','sentence',200,'bge-m3','bge-reranker-v2-m3'),(4,'PG产品手册','','2026-11-18 15:18:53',1,'pg','{\"host\": \"localhost\", \"port\": 5432, \"user\": \"postgres\", \"password\": \"Pg@123456\", \"dbname\": \"postgres\"}','doc','paragraph',300,'',''),(5,'子墨知识库','子墨知识库','2026-11-19 20:40:23',3,'pg','{\"host\":\"localhost\",\"port\":5432,\"user\":\"postgres\",\"password\":\"Pg@123456\",\"dbname\":\"postgres\"}','qa','paragraph',500,'bge-m3','bge-reranker-v2-m3');
/*!40000 ALTER TABLE `tb_kb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_kb_chunk`
--

DROP TABLE IF EXISTS `tb_kb_chunk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_kb_chunk` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `doc_id` int(11) NOT NULL,
  `kb_id` int(11) NOT NULL,
  `idx` int(11) DEFAULT '0',
  `content` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_kb_chunk`
--

LOCK TABLES `tb_kb_chunk` WRITE;
/*!40000 ALTER TABLE `tb_kb_chunk` DISABLE KEYS */;
INSERT INTO `tb_kb_chunk` VALUES (1,1,1,0,'RAG 是检索增强生成技术。知识库用于存储企业文档。流式输出可逐字返回。员工张三负责研发部。'),(2,2,1,0,'OCR 光学字符识别用于图片转文字。流式输出适合长文本生成场景。'),(3,3,2,0,'RAG 是检索增强生成技术。知识库用于存储企业文档。OCR 用于图片转文字。图谱用于关系存储'),(4,9,2,0,'分层重构后的内置存储写入测试');
/*!40000 ALTER TABLE `tb_kb_chunk` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_kb_doc`
--

DROP TABLE IF EXISTS `tb_kb_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_kb_doc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kb_id` int(11) NOT NULL,
  `name` varchar(512) NOT NULL,
  `source` varchar(64) DEFAULT 'upload',
  `size` int(11) DEFAULT '0',
  `chunk_size` int(11) DEFAULT '500',
  `chunks` int(11) DEFAULT '0',
  `status` varchar(32) DEFAULT 'ready',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_kb_doc`
--

LOCK TABLES `tb_kb_doc` WRITE;
/*!40000 ALTER TABLE `tb_kb_doc` DISABLE KEYS */;
INSERT INTO `tb_kb_doc` VALUES (1,1,'faq.txt','upload',46,500,1,'ready','2026-11-18 03:35:19'),(2,1,'notes','upload',32,500,1,'ready','2026-11-18 09:49:35'),(3,2,'faq','upload',47,500,1,'ready','2026-11-18 13:58:58'),(7,3,'faq-demo','upload',70,500,1,'ready','2026-11-18 15:18:34'),(8,4,'manual','upload',34,500,1,'ready','2026-11-18 15:18:53'),(9,2,'重构后测试','upload',15,500,1,'ready','2026-11-19 00:31:42');
/*!40000 ALTER TABLE `tb_kb_doc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_kb_space`
--

DROP TABLE IF EXISTS `tb_kb_space`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_kb_space` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_kb_space`
--

LOCK TABLES `tb_kb_space` WRITE;
/*!40000 ALTER TABLE `tb_kb_space` DISABLE KEYS */;
INSERT INTO `tb_kb_space` VALUES (1,'产品知识','产品文档与FAQ','2026-11-18 13:58:48'),(2,'测试空间-验证','','2026-11-19 20:37:29'),(3,'子墨空间','子墨空间','2026-11-19 20:39:38'),(4,'哈哈','哈哈','2026-11-19 21:11:18');
/*!40000 ALTER TABLE `tb_kb_space` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-26 22:13:12
