#!/usr/bin/env bash
# 数据库常用命令速查（MySQL + PostgreSQL + Neo4j + Redis）
# 用法：source sql/db-commands.sh 后调用下方函数，或 sh sql/db-commands.sh <命令名>

# ===== 容器与连接参数 =====
MYSQL_CONTAINER=mysql57
PG_CONTAINER=genai-postgres
MYSQL_ROOT=root
MYSQL_PWD_LOCAL='Root@123456'
PG_USER=genai

# ---------- 容器启动 ----------
db_start_all() {
  docker start "$MYSQL_CONTAINER"        # MySQL 5.7  :3306  (root/Root@123456)
  docker start "$PG_CONTAINER"           # PostgreSQL16:5433 (genai/genai123)
  docker start neo4j                     # Neo4j 5.26 :7474/:7687 (neo4j)
}
db_stop_all()  { docker stop "$MYSQL_CONTAINER" "$PG_CONTAINER" neo4j; }
db_ps()        { docker ps | grep -E 'mysql|postgres|neo4j|redis'; }

# ---------- MySQL ----------
my_shell()  { docker exec -it "$MYSQL_CONTAINER" mysql -u"$MYSQL_ROOT" -p"$MYSQL_PWD_LOCAL"; }
my_dbs()    { docker exec "$MYSQL_CONTAINER" mysql -u"$MYSQL_ROOT" -p"$MYSQL_PWD_LOCAL" -e 'SHOW DATABASES;'; }
my_tables() { local db=${1:-genai_kb}; docker exec "$MYSQL_CONTAINER" mysql -u"$MYSQL_ROOT" -p"$MYSQL_PWD_LOCAL" -e "USE $db; SHOW TABLES;"; }
my_count()  { local db=${1:-genai_kb} t=${2:-tb_kb}; docker exec "$MYSQL_CONTAINER" mysql -u"$MYSQL_ROOT" -p"$MYSQL_PWD_LOCAL" -e "USE $db; SELECT COUNT(*) FROM $t;"; }
my_create() { local db=$1; docker exec "$MYSQL_CONTAINER" mysql -u"$MYSQL_ROOT" -p"$MYSQL_PWD_LOCAL" -e "CREATE DATABASE IF NOT EXISTS $db DEFAULT CHARACTER SET utf8mb4;"; }
my_import() { local db=$1 f=$2; docker exec -i "$MYSQL_CONTAINER" mysql -u"$MYSQL_ROOT" -p"$MYSQL_PWD_LOCAL" "$db" < "$f"; }
my_dump()   { local db=$1; docker exec "$MYSQL_CONTAINER" mysqldump -u"$MYSQL_ROOT" -p"$MYSQL_PWD_LOCAL" --single-transaction --default-character-set=utf8mb4 "$db"; }

# ---------- PostgreSQL ----------
pg_shell()  { docker exec -it "$PG_CONTAINER" psql -U "$PG_USER" genai_graph; }
pg_dbs()    { docker exec "$PG_CONTAINER" psql -U "$PG_USER" -c '\l'; }
pg_tables() { local db=${1:-genai_graph}; docker exec "$PG_CONTAINER" psql -U "$PG_USER" -d "$db" -c '\dt'; }
pg_count()  { local db=${1:-genai_graph} t=${2:-tb_graph}; docker exec "$PG_CONTAINER" psql -U "$PG_USER" -d "$db" -c "SELECT COUNT(*) FROM $t;"; }
pg_create() { local db=$1; docker exec "$PG_CONTAINER" psql -U "$PG_USER" -c "CREATE DATABASE $db;"; }
pg_import() { local db=$1 f=$2; docker exec -i "$PG_CONTAINER" psql -U "$PG_USER" -d "$db" < "$f"; }
pg_dumpdb() { local db=$1; docker exec "$PG_CONTAINER" pg_dump -U "$PG_USER" --no-owner --no-privileges "$db"; }

# ---------- Neo4j (Cypher over HTTP) ----------
n4_query() {
  local q=${1:-'MATCH (n) RETURN count(n) AS total'}
  local user=${NEO4J_USER:-neo4j} pwd=${NEO4J_PASSWORD:-neo4j123}
  curl -s -u "$user:$pwd" -H 'Content-Type: application/json' \
    -d "{\"statements\":[{\"statement\":\"$q\"}]}" \
    http://localhost:7474/db/neo4j/tx/commit
}

# ---------- 项目数据库连接串（供 Python 服务环境变量使用） ----------
# export PG_DSN="host=localhost port=5433 dbname=genai_graph user=genai password=genai123"
# export MYSQL_HOST=localhost MYSQL_PORT=3306 MYSQL_USER=root MYSQL_PASSWORD='Root@123456'
# 本体库由 mapper 内 pg_dsn('genai_ontology') / kb 等由 mysql_dsn('genai_kb') 自动选择 dbname

# ---------- 恢复示例 ----------
# my_import genai_kb  sql/22_genai_kb_structure_data.sql
# my_import genai_ocr sql/22_genai_ocr_structure_data.sql
# my_import genai_rag sql/22_genai_rag_structure_data.sql
# pg_import genai_graph     sql/23_genai_graph_structure_data.sql
# pg_import genai_ontology  sql/24_genai_ontology_structure_data.sql

if [ "${1:-}" ]; then "$@"; else echo " sourced: 可用函数 db_start_all/db_ps/my_*/pg_*/n4_query"; fi
