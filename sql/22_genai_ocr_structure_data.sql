-- MySQL dump 10.13  Distrib 5.7.44, for Linux (x86_64)
--
-- Host: localhost    Database: genai_ocr
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
-- Table structure for table `tb_ocr_task`
--

DROP TABLE IF EXISTS `tb_ocr_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_ocr_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `engine` varchar(64) DEFAULT 'auto',
  `size` int(11) DEFAULT '0',
  `status` varchar(32) DEFAULT 'pending',
  `text` text,
  `error` text,
  `cost_ms` int(11) DEFAULT '0',
  `prompt` text,
  `image_path` varchar(1024) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_ocr_task`
--

LOCK TABLES `tb_ocr_task` WRITE;
/*!40000 ALTER TABLE `tb_ocr_task` DISABLE KEYS */;
INSERT INTO `tb_ocr_task` VALUES (1,'prompt-page.png','ollama:minicpm-v4.6:1b',102063,'done','</think>\n\nGenAI Studio\n\n调试版v1.03\n\n管理员\n\n首页\n开发中心\nAPI Key\n账单\n成本统计\n使用志\n模型与能力\n模型管理\n体验中心\n\n管理员\nAdmin\n\n提示词管理\n\n查询\n\n<table>\n  <tr>\n    <td>模创新创/变量/标签</td>\n    <td>~y=stem-prompt</td>\n    <td rowspan=\"2\">变量</td>\n    <td rowspan=\"2\">标签</td>\n    <td rowspan=\"2\">状态</td>\n    <td rowspan=\"2\">操作</td>\n    <td colspan=\"2\">共4个模板</td>\n  </tr>\n  <tr>\n    <td>名称/标签</td>\n    <td>内容</td>\n    <td>文案颜色</td>\n    <td>请润色以下文案,使更加专业流畅:{{text}}</td>\n    <td>变量</td>\n    <td>标签</td>\n    <td>状态</td>\n    <td>操作</td>\n  </tr>\n  <tr>\n    <td></td>\n    <td>基于地下参考资料回答用户问题,若资料中没有容...</td>\n    <td>[context](question)</td>\n    <td>RAG 问答</td>\n    <td>启用</td>\n    <td>编辑|删除</td>\n    <td>10个页</td>\n    <td>文字</td>\n    <td>编辑|暂停|删除</td>\n    <td></td>\n  </tr>\n  <tr>\n    <td>知识库问答</td>\n    <td>请验以下代码,从正确性、可读性、性能三方面...</td>\n    <td>[code](code)</td>\n    <td>编程 评审</td>\n    <td>启用</td>\n    <td>编辑|暂停|删除</td>\n    <td></td>\n    <td>编程</td>\n    <td>编辑|暂停|删除</td>\n    <td></td>\n  </tr>\n  <tr>\n    <td>代码评审</td>\n    <td></td>\n    <td></td>\n    <td></td>\n    <td></td>\n    <td></td>\n    <td></td>\n    <td></td>\n    <td></td>\n    <td></td>\n  </tr>\n  <tr>\n    <td>通用助手</td>\n    <td>你是一个众助人的AI助手,请用简洁清晰的...</td>\n    <td>-</td>\n    <td>通用 默认</td>\n    <td>启用</td>\n    <td>编辑|暂停|删除</td>\n    <td></td>\n    <td>-</td>\n    <td>通用 默认</td>\n    <td>编辑|暂停|删除</td>\n    <td></td>\n  </tr>\n  <tr>\n    <td>共4个模板</td>\n    <td></td>\n    <td></td>\n    <td></td>\n    <td></td>\n    <td>编辑|暂停|删除</td>\n    <td>10个页</td>\n    <td></td>\n    <td></td>\n    <td>1页 | 上 一页 | 下 页 ></td>\n    <td></td>\n  </tr>\n</table>','',12349,'','','2026-11-18 09:50:31'),(2,'test.png','auto',1,'failed','','Client error \'400 Bad Request\' for url \'http://localhost:11434/api/generate\'\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400',0,'识别图片中的全部文字，按原样输出，不要解释。','/Users/wanzenggui/Documents/文档/代码开发项目/code_codex_project/project_genai-studio/backend/py-genai-ocr/app/../uploads/2_test.png','2026-11-18 14:01:57'),(3,'prompt-page.png','ollama:minicpm-v4.6:1b',102063,'done','我们需要的列表菜单项是上面的左边一列的菜单项，它们包括：首页、开发中心、API Key、账单、成本统计、使用志、模型与能力、模型广场、模型管理、体验中心、管理员。题目要求列出图片中的菜单项，所以我们要提取这些标题。\n\n根据图片，菜单项是左侧的导航栏，从上到下：\n\n1. 首页\n2. 开发中心\n3. API Key\n4. 账单\n5. 成本统计\n6. 使用志\n7. 模型与能力\n8. 模型管理\n9. 体验中心\n10. 管理员（但注意，题目说“列出图片中的菜单项”，可能包括所有导航栏的标题）\n\n不过通常在GenAI Studio中，菜单项是左侧的折叠列表。根据图片，菜单项包括：\n\n- 首页\n- 开发中心\n- API Key\n- 账单\n- 成本统计\n- 使用志\n- 模型与能力\n- 模型管理\n- 体验中心\n- 管理员\n\n但注意，题目说“列出图片中的菜单项”，所以我们要把这些标题列出来。\n\n为了准确，我们看看图片中的菜单部分，左侧的折叠菜单，包含这些标题。\n\n所以最终列表应该是这些菜单项的名称。\n</think>\n\n图片中的菜单项包括以下标题：\n\n- 首页  \n- 开发中心  \n- API Key  \n- 账单  \n- 成本统计  \n- 使用志  \n- 模型与能力  \n- 模型管理  \n- 体验中心  \n- 管理员','',4111,'列出图片中的菜单项','/Users/wanzenggui/Documents/文档/代码开发项目/code_codex_project/project_genai-studio/backend/py-genai-ocr/app/../uploads/3_prompt-page.png','2026-11-18 14:02:00');
/*!40000 ALTER TABLE `tb_ocr_task` ENABLE KEYS */;
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
