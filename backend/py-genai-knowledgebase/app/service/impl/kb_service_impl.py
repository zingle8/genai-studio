# -*- coding: utf-8 -*-
"""知识库业务实现（service/impl）：空间/库/文档/检索的编排与多存储后端路由（sqlite/es/pg）"""
from fastapi import HTTPException

from app.config.settings import settings
from app.mapper import kb_mapper as storage
from app.service.kb_service import KbService


class KbServiceImpl(KbService):

    # ===== 选项与连通性 =====
    def options(self) -> dict:
        return {
            "dbTypes": [
                {"value": "es", "label": "Elasticsearch"},
                {"value": "pg", "label": "PostgreSQL"}],
            "kbTypes": [
                {"value": "golden_answer", "label": "Golden Answer（标准答案库）"},
                {"value": "qa", "label": "QA 问答对"},
                {"value": "doc", "label": "文档知识"},
                {"value": "faq", "label": "FAQ"}],
            "chunkModes": [
                {"value": "paragraph", "label": "按段落"},
                {"value": "sentence", "label": "按句子"},
                {"value": "fixed", "label": "固定长度"}],
            "embeddingModels": ["bge-m3", "text-embedding-ada-002", "nomic-embed-text", "bge-large-zh"],
            "rerankerModels": ["bge-reranker-v2-m3", "bge-reranker-large", "（无）"]
        }

    def ping(self, db_type: str, db_config: str) -> dict:
        cfg = storage.jload(db_config, {})
        if db_type == "es":
            ok = storage.es_ping(cfg)
            return {"ok": ok, "message": "ES 连接成功" if ok else "ES 连接失败（检查地址/凭据）"}
        if db_type == "pg":
            ok = storage.pg_ping(cfg)
            return {"ok": ok, "message": "PG 连接成功" if ok else "PG 连接失败（检查地址/凭据/库名）"}
        return {"ok": True, "message": "内置存储无需连接"}

    # ===== 知识空间 =====
    def space_list(self) -> list:
        ss = storage.rows("SELECT * FROM tb_kb_space ORDER BY id")
        for s in ss:
            s["kbCount"] = storage.one("SELECT COUNT(*) n FROM tb_kb WHERE space_id=?", (s["id"],))["n"]
        return ss

    def space_create(self, b) -> dict:
        if not b.name.strip():
            raise HTTPException(400, "空间名不能为空")
        sid = storage.run("INSERT INTO tb_kb_space(name, description) VALUES(?,?)", (b.name.strip(), b.description))
        return storage.one("SELECT * FROM tb_kb_space WHERE id=?", (sid,))

    def space_delete(self, sid: int) -> None:
        if storage.one("SELECT id FROM tb_kb WHERE space_id=?", (sid,)):
            raise HTTPException(400, "空间下还有知识库，先删除")
        storage.run("DELETE FROM tb_kb_space WHERE id=?", (sid,))

    # ===== 知识库 =====
    @staticmethod
    def _chunk_count(k) -> int:
        """按存储后端统计分块总数（内置/ES/PG）"""
        try:
            if k.get("db_type") == "es":
                return storage.es_req(k, "GET", f"/kb_{k['id']}/_count").get("count", 0)
            if k.get("db_type") == "pg":
                conn = storage.pg_conn(k)
                try:
                    with conn.cursor() as cur:
                        cur.execute(f"SELECT COUNT(*) FROM kb_{k['id']}_chunks")
                        return cur.fetchone()[0]
                finally:
                    conn.close()
            return storage.one("SELECT COUNT(*) n FROM tb_kb_chunk WHERE doc_id IN "
                               "(SELECT id FROM tb_kb_doc WHERE kb_id=?)", (k["id"],))["n"]
        except Exception:
            return 0

    def kb_list(self, space_id: int = 0) -> list:
        where, args = "", []
        if space_id:
            where, args = "WHERE space_id=?", [space_id]
        kbs = storage.rows(f"SELECT * FROM tb_kb {where} ORDER BY id DESC", args)
        for k in kbs:
            k["docCount"] = storage.one("SELECT COUNT(*) n FROM tb_kb_doc WHERE kb_id=?", (k["id"],))["n"]
            k["spaceName"] = (storage.one("SELECT name FROM tb_kb_space WHERE id=?", (k.get("space_id", 0),)) or {}).get("name", "")
            k["chunkCount"] = self._chunk_count(k)
            if k.get("db_type") == "es":
                k["dbOk"] = storage.es_ping(storage.es_cfg(k))
            elif k.get("db_type") == "pg":
                k["dbOk"] = storage.pg_ping(storage.jload(k.get("db_config"), {}))
        return kbs

    @staticmethod
    def _require_space(space_id) -> None:
        """知识库必须归属知识空间"""
        if not (space_id and storage.one("SELECT id FROM tb_kb_space WHERE id=?", (space_id,))):
            raise HTTPException(400, "知识库必须归属知识空间，请选择有效空间")

    @staticmethod
    def _require_db_type(b) -> None:
        """内置 SQLite 存储已移除：新建仅支持 ES / PG（存量 sqlite 库可原样保留）"""
        if b.db_type not in ("es", "pg"):
            raise HTTPException(400, "内置 SQLite 存储已移除，存储仅支持 Elasticsearch / PostgreSQL")

    def kb_create(self, b) -> dict:
        if not b.name.strip():
            raise HTTPException(400, "name 不能为空")
        self._require_space(b.space_id)
        self._require_db_type(b)
        if b.db_type == "es" and not storage.es_ping(storage.jload(b.db_config, {})):
            raise HTTPException(400, "ES 连接失败，请检查地址/凭据")
        if b.db_type == "pg" and not storage.pg_ping(storage.jload(b.db_config, {})):
            raise HTTPException(400, "PG 连接失败，请检查地址/凭据/库名")
        nid = storage.run(
            "INSERT INTO tb_kb(name, description, space_id, db_type, db_config, kb_type, chunk_mode, chunk_len, embedding_model, reranker_model) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            (b.name.strip(), b.description, b.space_id, b.db_type, b.db_config, b.kb_type,
             b.chunk_mode, b.chunk_len, b.embedding_model, b.reranker_model))
        if b.db_type == "es":
            try:
                storage.es_ensure_index(storage.one("SELECT * FROM tb_kb WHERE id=?", (nid,)), nid)
            except Exception:
                pass
        return storage.one("SELECT * FROM tb_kb WHERE id=?", (nid,))

    def kb_update(self, kid: int, b) -> dict:
        old = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
        if not old:
            raise HTTPException(404, "知识库不存在")
        self._require_space(b.space_id)
        self._require_db_type(b)
        storage.run(
            "UPDATE tb_kb SET name=?, description=?, space_id=?, db_type=?, db_config=?, kb_type=?, chunk_mode=?, chunk_len=?, embedding_model=?, reranker_model=? WHERE id=?",
            (b.name.strip(), b.description, b.space_id, b.db_type, b.db_config, b.kb_type,
             b.chunk_mode, b.chunk_len, b.embedding_model, b.reranker_model, kid))
        return storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))

    def kb_delete(self, kid: int) -> None:
        k = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
        if k:
            storage.run("DELETE FROM tb_kb_chunk WHERE kb_id=?", (kid,))
            storage.run("DELETE FROM tb_kb_doc WHERE kb_id=?", (kid,))
            storage.run("DELETE FROM tb_kb WHERE id=?", (kid,))
            if k.get("db_type") == "es":
                try:
                    storage.es_req(k, "DELETE", "/kb_%d" % kid)
                except Exception:
                    pass

    # ===== 文档 =====
    def doc_add(self, kid: int, name: str, text: str, file_bytes: bytes | None) -> dict:
        kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
        if not kb:
            raise HTTPException(404, "知识库不存在")
        if file_bytes is not None:
            try:
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("utf-8", errors="ignore")
        if not text.strip():
            raise HTTPException(400, "文档内容为空")
        chunks = storage.split_text(text, kb.get("chunk_mode") or "paragraph", kb.get("chunk_len") or 500)
        did = storage.run(
            "INSERT INTO tb_kb_doc(kb_id, name, source, size, chunks, status) VALUES(?,?,?,?,?, 'ready')",
            (kid, name, "upload", len(text), len(chunks)))
        try:
            backend = storage.insert_chunks(kb, kid, did, name, chunks)
        except Exception as e:
            storage.run("DELETE FROM tb_kb_doc WHERE id=?", (did,))
            raise HTTPException(400, f"分块写入 {kb.get('db_type')} 失败：{e}")
        return {"id": did, "name": name, "chunks": len(chunks), "size": len(text), "backend": kb.get("db_type")}

    def doc_list(self, kid: int, page: int = 1, size: int = 10) -> dict:
        """文档列表（分页），并富化 空间ID/空间名、知识库ID/知识库名 字段"""
        kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
        if not kb:
            raise HTTPException(404, "知识库不存在")
        sp = storage.one("SELECT name FROM tb_kb_space WHERE id=?", (kb.get("space_id") or 0,))
        total = storage.one("SELECT COUNT(*) AS c FROM tb_kb_doc WHERE kb_id=?", (kid,))["c"]
        rows = storage.rows(
            "SELECT id, name, source, size, chunks, status, created_at FROM tb_kb_doc "
            "WHERE kb_id=? ORDER BY id DESC LIMIT ? OFFSET ?", (kid, size, (page - 1) * size))
        enrich = {
            "kbId": kid, "kbName": kb.get("name"),
            "spaceId": kb.get("space_id"), "spaceName": sp.get("name") if sp else "",
        }
        for r in rows:
            r.update(enrich)
        return {"list": rows, "total": total, "page": page, "size": size}

    def chunk_list(self, kid: int, did: int) -> list:
        kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
        t = kb.get("db_type", "pg") if kb else "pg"
        if t == "es":
            j = storage.es_req(kb, "POST", "/kb_%d/_search" % kid,
                               {"query": {"term": {"doc_id": did}}, "size": 200, "sort": [{"idx": "asc"}]})
            return [{"idx": h["_source"]["idx"], "content": h["_source"]["content"]} for h in j["hits"]["hits"]]
        if t == "pg":
            with storage.pg_conn(kb) as c:
                cur = c.cursor()
                cur.execute("SELECT idx, content FROM kb_%d_chunks WHERE doc_id=%%s ORDER BY idx" % kid, (did,))
                return [{"idx": r[0], "content": r[1]} for r in cur.fetchall()]
        return storage.rows("SELECT idx, content FROM tb_kb_chunk WHERE doc_id=? ORDER BY idx", (did,))

    def doc_delete(self, kid: int, did: int) -> None:
        kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
        if kb:
            storage.delete_doc_chunks(kb, kid, did)
        storage.run("DELETE FROM tb_kb_doc WHERE id=? AND kb_id=?", (did, kid))

    # ===== 检索 =====
    def search(self, kid: int, q: str, top_k: int = 5) -> dict:
        kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
        if not kb:
            raise HTTPException(404, "知识库不存在")
        hits, backend = self._search_kw_one(kb, q, top_k)
        return {"hits": hits, "backend": backend}

    def _search_kw_one(self, kb, q, top_k):
        """单库关键词检索（分词 OR + 命中词数排序），返回 (hits, backend)"""
        kid = kb["id"]
        t = kb.get("db_type", "pg")
        if t in ("es", "pg", "sqlite"):
            try:
                return storage.search_chunks(kb, kid, q, top_k)
            except Exception as e:
                raise HTTPException(400, f"{t} 检索失败：{e}")
        # 内置：多词关键词打分
        terms = [x for x in q.replace("，", " ").replace("。", " ").split() if x] or [q.strip()]
        chunks = storage.rows("SELECT id, doc_id, idx, content FROM tb_kb_chunk WHERE kb_id=?", (kid,))
        scored = []
        for c in chunks:
            score = sum(c["content"].lower().count(x.lower()) for x in terms)
            if score > 0:
                doc = storage.one("SELECT name FROM tb_kb_doc WHERE id=?", (c["doc_id"],))
                scored.append({"chunkId": c["id"], "docId": c["doc_id"], "doc": doc["name"] if doc else "",
                               "idx": c["idx"], "score": score, "content": c["content"][:400]})
        scored.sort(key=lambda x: -x["score"])
        return scored[:top_k], "mysql"

    def search_multi(self, space_id: int = 0, kb_id: int = 0, q: str = "", top_k: int = 5, mode: str = "kw") -> dict:
        """跨空间/跨库聚合检索，结果带空间/知识库字段"""
        where, args = "", []
        if kb_id:
            where, args = "WHERE id=?", [kb_id]
        elif space_id:
            where, args = "WHERE space_id=?", [space_id]
        kbs = storage.rows(f"SELECT * FROM tb_kb {where} ORDER BY id DESC", args)
        if mode == "sem":
            return self._search_sem_multi(kbs, q, top_k)
        scored = []
        for kb in kbs:
            try:
                hits, _ = self._search_kw_one(kb, q, top_k)
            except HTTPException:
                continue
            meta = self._kb_meta(kb)
            for h in hits:
                h.update(meta)
                scored.append(h)
        scored.sort(key=lambda x: -x["score"])
        return {"hits": scored[:top_k], "backend": "multi-kw"}

    def _kb_meta(self, kb) -> dict:
        sp = storage.one("SELECT name FROM tb_kb_space WHERE id=?", (kb.get("space_id", 0),))
        return {"kbId": kb["id"], "kbName": kb["name"], "spaceId": kb.get("space_id", 0),
                "spaceName": sp["name"] if sp else ""}

    def _search_sem_multi(self, kbs, q, top_k):
        """跨库语义检索：合并全部库分块一次向量化，余弦排序"""
        pairs = []  # (kb, chunk)
        for kb in kbs:
            try:
                for c in storage.all_chunks(kb, kb["id"]):
                    pairs.append((kb, c))
            except Exception:
                continue
        if not pairs:
            return {"hits": [], "backend": "semantic:" + settings.embedding_model}
        texts = [q] + [(c.get("content") or "")[:512] for _, c in pairs]
        import requests as _rq
        try:
            r = _rq.post(settings.embedding_base + "/v1/embeddings",
                         json={"input": texts, "model": settings.embedding_model}, timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"向量服务 {r.status_code}：{r.text[:120]}")
            vecs = [d["embedding"] for d in r.json()["data"]]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(503, f"语义检索不可用（embedding 服务）：{e}")
        qv = self._normalize(vecs[0])
        scored = []
        for (kb, c), v in zip(pairs, vecs[1:]):
            cos = sum(a * b for a, b in zip(qv, self._normalize(v)))
            did = c.get("docId", c.get("doc_id"))
            doc = c.get("doc") or ""
            if not doc and did:
                d = storage.one("SELECT name FROM tb_kb_doc WHERE id=?", (did,))
                doc = d["name"] if d else ""
            hit = {"chunkId": c["chunkId"], "docId": did, "doc": doc,
                   "idx": c["idx"], "score": round(cos, 4), "content": c["content"][:400]}
            hit.update(self._kb_meta(kb))
            scored.append(hit)
        scored.sort(key=lambda x: -x["score"])
        return {"hits": scored[:top_k], "backend": "semantic:" + settings.embedding_model}

    def semantic_search(self, kid: int, q: str, top_k: int = 5) -> dict:
        """语义检索：bge-m3 向量化 query + 全部分块，余弦相似度排序"""
        kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
        if not kb:
            raise HTTPException(404, "知识库不存在")
        return self._search_sem_multi([kb], q, top_k)

    @staticmethod
    def _normalize(vec) -> list:
        import math
        n = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / n for x in vec]
