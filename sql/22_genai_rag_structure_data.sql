-- MySQL dump 10.13  Distrib 5.7.44, for Linux (x86_64)
--
-- Host: localhost    Database: genai_rag
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
-- Table structure for table `tb_rag_eval`
--

DROP TABLE IF EXISTS `tb_rag_eval`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_rag_eval` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` varchar(128) NOT NULL,
  `source_type` varchar(32) DEFAULT 'kb',
  `source_id` int(11) DEFAULT NULL,
  `source_name` varchar(512) DEFAULT '',
  `q` text NOT NULL,
  `expect` text,
  `top_k` int(11) DEFAULT '5',
  `hit` int(11) DEFAULT '0',
  `rank` int(11) DEFAULT '0',
  `score` double DEFAULT '0',
  `latency_ms` int(11) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_rag_eval`
--

LOCK TABLES `tb_rag_eval` WRITE;
/*!40000 ALTER TABLE `tb_rag_eval` DISABLE KEYS */;
INSERT INTO `tb_rag_eval` VALUES (1,'26d8d4d8f5','kb',2,'ES产品FAQ','如何计费','token',3,0,0,0,4,'2026-11-19 00:46:09'),(2,'26d8d4d8f5','kb',2,'ES产品FAQ','OCR 支持什么格式','图片',3,1,1,1,2,'2026-11-19 00:46:09'),(3,'26d8d4d8f5','kb',2,'ES产品FAQ','公司聚餐','',3,0,0,0,2,'2026-11-19 00:46:09'),(4,'ec6fb581b0','kb',1,'产品手册','如何计费','token',3,0,0,0,13,'2026-11-19 00:52:34'),(5,'ec6fb581b0','kb',1,'产品手册','OCR 支持什么格式','图片',3,1,1,1,5,'2026-11-19 00:52:34'),(6,'ec6fb581b0','kb',1,'产品手册','今天天气如何','',3,0,0,0,4,'2026-11-19 00:52:34');
/*!40000 ALTER TABLE `tb_rag_eval` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_rag_pipeline`
--

DROP TABLE IF EXISTS `tb_rag_pipeline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_rag_pipeline` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `kb_id` int(11) DEFAULT '0',
  `kb_name` varchar(512) DEFAULT '',
  `strategy` varchar(32) DEFAULT 'keyword',
  `embed_model` varchar(128) DEFAULT 'bge-m3',
  `rerank_model` varchar(128) DEFAULT 'bge-reranker-v2-m3',
  `rerank_on` int(11) DEFAULT '0',
  `top_k` int(11) DEFAULT '5',
  `chunk_size` int(11) DEFAULT '500',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_rag_pipeline`
--

LOCK TABLES `tb_rag_pipeline` WRITE;
/*!40000 ALTER TABLE `tb_rag_pipeline` DISABLE KEYS */;
INSERT INTO `tb_rag_pipeline` VALUES (1,'默认管道',1,'产品手册','keyword','bge-m3','bge-reranker-v2-m3',0,5,500,'2026-11-18 09:49:55');
/*!40000 ALTER TABLE `tb_rag_pipeline` ENABLE KEYS */;
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
