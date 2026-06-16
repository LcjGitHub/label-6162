"""手写信封邮票组合收藏 — Flask API。"""

import csv
import io

from flask import Flask, jsonify, request

from database import get_connection, init_db
from seed import seed

app = Flask(__name__)
app.json.sort_keys = False

ENVELOPE_REQUIRED_FIELDS = (
    "origin",
    "destination",
    "year",
    "stamp_description",
    "postmark_type",
    "condition",
)

ENVELOPE_FIELD_LABELS = {
    "origin": "寄出地",
    "destination": "目的地",
    "year": "年份",
    "stamp_description": "邮票描述",
    "postmark_type": "邮戳类型",
    "condition": "品相",
}

POSTMARK_REQUIRED_FIELDS = (
    "name",
    "shape",
    "common_use",
    "description",
)


def envelope_row_to_dict(row) -> dict:
    """
     * 将信封 sqlite3.Row 转为 JSON 可序列化字典。
     * @param {sqlite3.Row} row
     * @returns {dict}
     """
    return {
        "id": row["id"],
        "origin": row["origin"],
        "destination": row["destination"],
        "year": row["year"],
        "stamp_description": row["stamp_description"],
        "postmark_type": row["postmark_type"],
        "condition": row["condition"],
    }


def postmark_row_to_dict(row) -> dict:
    """
     * 将邮戳 sqlite3.Row 转为 JSON 可序列化字典。
     * @param {sqlite3.Row} row
     * @returns {dict}
     """
    return {
        "id": row["id"],
        "name": row["name"],
        "shape": row["shape"],
        "common_use": row["common_use"],
        "description": row["description"],
    }


def tag_row_to_dict(row) -> dict:
    """
     * 将标签 sqlite3.Row 转为 JSON 可序列化字典。
     * @param {sqlite3.Row} row
     * @returns {dict}
     """
    return {
        "id": row["id"],
        "name": row["name"],
        "color": row["color"],
        "created_at": row["created_at"] if "created_at" in row.keys() else None,
    }


def envelope_row_to_dict_with_tags(row, tags=None) -> dict:
    """
     * 将信封 sqlite3.Row 转为 JSON 可序列化字典，包含标签。
     * @param {sqlite3.Row} row
     * @param {list | None} tags
     * @returns {dict}
     """
    d = envelope_row_to_dict(row)
    d["tags"] = tags or []
    return d


def get_envelope_tags(conn, envelope_id: int) -> list:
    """
     * 获取指定信封的所有标签。
     * @param {sqlite3.Connection} conn
     * @param {int} envelope_id
     * @returns {list}
     """
    rows = conn.execute(
        """
        SELECT t.* FROM tags t
        INNER JOIN envelope_tags et ON t.id = et.tag_id
        WHERE et.envelope_id = ?
        ORDER BY t.id ASC
        """,
        (envelope_id,),
    ).fetchall()
    return [tag_row_to_dict(r) for r in rows]


def validate_envelope_payload(data: dict) -> str | None:
    """
     * 校验信封请求体字段，返回错误信息或 None。
     * @param {dict} data
     * @returns {str | None}
     """
    if not data:
        return "请求体不能为空"
    for field in ENVELOPE_REQUIRED_FIELDS:
        if field not in data or data[field] in (None, ""):
            return f"缺少必填字段：{ENVELOPE_FIELD_LABELS[field]}"
    try:
        year = int(data["year"])
        if year < 1800 or year > 2100:
            return "年份范围应在 1800–2100 之间"
    except (TypeError, ValueError):
        return "年份必须为整数"
    return None


def validate_postmark_payload(data: dict) -> str | None:
    """
     * 校验邮戳请求体字段，返回错误信息或 None。
     * @param {dict} data
     * @returns {str | None}
     """
    if not data:
        return "请求体不能为空"
    for field in POSTMARK_REQUIRED_FIELDS:
        if field not in data or data[field] in (None, ""):
            return f"缺少必填字段: {field}"
    return None


ERA_RANGES = [
    ("清末及以前", 0, 1911),
    ("民国时期", 1912, 1949),
    ("建国初期", 1950, 1979),
    ("改革开放", 1980, 1999),
    ("新世纪", 2000, 9999),
]

CONDITION_ORDER = ["优秀", "良好", "一般"]


@app.route("/api/envelopes/stats", methods=["GET"])
def envelope_stats():
    """收藏数据统计：总数、按品相分组、按年代区间分组。"""
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) AS c FROM envelopes").fetchone()["c"]

        condition_rows = conn.execute(
            "SELECT condition, COUNT(*) AS c FROM envelopes GROUP BY condition"
        ).fetchall()
        condition_map = {r["condition"]: r["c"] for r in condition_rows}
        by_condition = {cond: condition_map.get(cond, 0) for cond in CONDITION_ORDER}

        by_era = {}
        for label, lo, hi in ERA_RANGES:
            cnt = conn.execute(
                "SELECT COUNT(*) AS c FROM envelopes WHERE year BETWEEN ? AND ?",
                (lo, hi),
            ).fetchone()["c"]
            by_era[label] = cnt

        return jsonify({"total": total, "by_condition": by_condition, "by_era": by_era})
    finally:
        conn.close()


@app.route("/api/envelopes", methods=["GET"])
def list_envelopes():
    """获取全部信封收藏（含标签）。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM envelopes ORDER BY year DESC, id DESC"
        ).fetchall()
        result = []
        for row in rows:
            tags = get_envelope_tags(conn, row["id"])
            result.append(envelope_row_to_dict_with_tags(row, tags))
        return jsonify(result)
    finally:
        conn.close()


@app.route("/api/envelopes/<int:envelope_id>", methods=["GET"])
def get_envelope(envelope_id: int):
    """获取单条信封详情（含标签）。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM envelopes WHERE id = ?", (envelope_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "记录不存在"}), 404
        tags = get_envelope_tags(conn, envelope_id)
        return jsonify(envelope_row_to_dict_with_tags(row, tags))
    finally:
        conn.close()


@app.route("/api/envelopes", methods=["POST"])
def create_envelope():
    """新建信封收藏（可同时指定标签ID列表）。"""
    data = request.get_json(silent=True) or {}
    error = validate_envelope_payload(data)
    if error:
        return jsonify({"error": error}), 400

    tag_ids = data.get("tag_ids", []) or []

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO envelopes
                (origin, destination, year, stamp_description, postmark_type, condition)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["origin"],
                data["destination"],
                int(data["year"]),
                data["stamp_description"],
                data["postmark_type"],
                data["condition"],
            ),
        )
        envelope_id = cursor.lastrowid

        for tag_id in tag_ids:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO envelope_tags (envelope_id, tag_id) VALUES (?, ?)",
                    (envelope_id, tag_id),
                )
            except Exception:
                pass

        conn.commit()

        row = conn.execute(
            "SELECT * FROM envelopes WHERE id = ?", (envelope_id,)
        ).fetchone()
        tags = get_envelope_tags(conn, envelope_id)
        return jsonify(envelope_row_to_dict_with_tags(row, tags)), 201
    finally:
        conn.close()


@app.route("/api/envelopes/<int:envelope_id>", methods=["PUT"])
def update_envelope(envelope_id: int):
    """更新信封收藏（可同时更新标签ID列表）。"""
    data = request.get_json(silent=True) or {}
    error = validate_envelope_payload(data)
    if error:
        return jsonify({"error": error}), 400

    tag_ids = data.get("tag_ids", None)

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM envelopes WHERE id = ?", (envelope_id,)
        ).fetchone()
        if existing is None:
            return jsonify({"error": "记录不存在"}), 404

        conn.execute(
            """
            UPDATE envelopes SET
                origin = ?,
                destination = ?,
                year = ?,
                stamp_description = ?,
                postmark_type = ?,
                condition = ?
            WHERE id = ?
            """,
            (
                data["origin"],
                data["destination"],
                int(data["year"]),
                data["stamp_description"],
                data["postmark_type"],
                data["condition"],
                envelope_id,
            ),
        )

        if tag_ids is not None:
            conn.execute(
                "DELETE FROM envelope_tags WHERE envelope_id = ?",
                (envelope_id,),
            )
            for tag_id in tag_ids:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO envelope_tags (envelope_id, tag_id) VALUES (?, ?)",
                        (envelope_id, tag_id),
                    )
                except Exception:
                    pass

        conn.commit()
        row = conn.execute(
            "SELECT * FROM envelopes WHERE id = ?", (envelope_id,)
        ).fetchone()
        tags = get_envelope_tags(conn, envelope_id)
        return jsonify(envelope_row_to_dict_with_tags(row, tags))
    finally:
        conn.close()


@app.route("/api/envelopes/<int:envelope_id>", methods=["DELETE"])
def delete_envelope(envelope_id: int):
    """删除信封收藏。"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM envelopes WHERE id = ?", (envelope_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "记录不存在"}), 404
        return jsonify({"message": "已删除"})
    finally:
        conn.close()


CSV_HEADERS_ZH = ["寄出地", "目的地", "年份", "邮票描述", "邮戳类型", "品相"]
CSV_FIELDS = ["origin", "destination", "year", "stamp_description", "postmark_type", "condition"]


def validate_csv_row(row_values: list[str], line_no: int) -> tuple[dict | None, str | None]:
    """
    * 校验单行 CSV 数据，返回 (合法字典, 错误信息)。
    * @param {list[str]} row_values - 已去掉空首尾的六列值
    * @param {int} line_no - 原始行号（用于错误提示）
    * @returns {tuple[dict | None, str | None]}
    """
    if len(row_values) != 6:
        return None, f"列数应为 6 列，实际 {len(row_values)} 列"

    data = {}
    for field, value in zip(CSV_FIELDS, row_values):
        data[field] = value.strip() if isinstance(value, str) else value

    error = validate_envelope_payload(data)
    if error:
        return None, error

    data["year"] = int(data["year"])
    return data, None


@app.route("/api/envelopes/import", methods=["POST"])
def import_envelopes():
    """
    批量导入信封收藏。
    接收 multipart/form-data，字段名：file（CSV 文本文件）。
    CSV 格式：UTF-8，逗号分隔，含表头（寄出地,目的地,年份,邮票描述,邮戳类型,品相）。
    """
    if "file" not in request.files:
        return jsonify({"error": "缺少上传文件字段 file"}), 400

    file_storage = request.files["file"]
    if not file_storage.filename:
        return jsonify({"error": "未选择文件"}), 400

    try:
        raw_bytes = file_storage.read()
        try:
            content = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                content = raw_bytes.decode("gbk")
            except UnicodeDecodeError:
                return jsonify({"error": "文件编码不支持，请使用 UTF-8 或 GBK 编码"}), 400
    except Exception as e:
        return jsonify({"error": f"读取文件失败：{str(e)}"}), 400

    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    if not rows:
        return jsonify({"error": "文件内容为空"}), 400

    header = [h.strip() for h in rows[0]]
    if header != CSV_HEADERS_ZH:
        return (
            jsonify(
                {
                    "error": "表头格式不正确",
                    "expected": CSV_HEADERS_ZH,
                    "actual": header,
                }
            ),
            400,
        )

    data_rows = rows[1:]
    valid_records = []
    failed_lines = []
    failed_row_numbers = []

    for idx, row in enumerate(data_rows):
        line_no = idx + 2
        non_empty = [c for c in row if (c.strip() if isinstance(c, str) else c)]
        if not non_empty:
            continue
        record, err = validate_csv_row(row, line_no)
        if err:
            failed_lines.append(f"第 {line_no} 行：{err}")
            failed_row_numbers.append(line_no)
        else:
            valid_records.append((line_no, record))

    success_count = 0
    conn = get_connection()
    try:
        for line_no, rec in valid_records:
            try:
                conn.execute(
                    """
                    INSERT INTO envelopes
                        (origin, destination, year, stamp_description, postmark_type, condition)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rec["origin"],
                        rec["destination"],
                        rec["year"],
                        rec["stamp_description"],
                        rec["postmark_type"],
                        rec["condition"],
                    ),
                )
                success_count += 1
            except Exception as e:
                failed_lines.append(f"第 {line_no} 行：数据库写入失败：{str(e)}")
                failed_row_numbers.append(line_no)
        conn.commit()
    finally:
        conn.close()

    return jsonify(
        {
            "success": success_count,
            "failed_count": len(failed_lines),
            "failed_lines": failed_lines,
            "failed_row_numbers": failed_row_numbers,
            "processed": len(data_rows),
        }
    )


@app.route("/api/postmarks", methods=["GET"])
def list_postmarks():
    """获取全部邮戳图鉴。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM postmarks ORDER BY id ASC"
        ).fetchall()
        return jsonify([postmark_row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.route("/api/postmarks/<int:postmark_id>", methods=["GET"])
def get_postmark(postmark_id: int):
    """获取单条邮戳详情。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM postmarks WHERE id = ?", (postmark_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "记录不存在"}), 404
        return jsonify(postmark_row_to_dict(row))
    finally:
        conn.close()


@app.route("/api/postmarks", methods=["POST"])
def create_postmark():
    """新建邮戳图鉴。"""
    data = request.get_json(silent=True) or {}
    error = validate_postmark_payload(data)
    if error:
        return jsonify({"error": error}), 400

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO postmarks
                (name, shape, common_use, description)
            VALUES (?, ?, ?, ?)
            """,
            (
                data["name"],
                data["shape"],
                data["common_use"],
                data["description"],
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM postmarks WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return jsonify(postmark_row_to_dict(row)), 201
    finally:
        conn.close()


@app.route("/api/postmarks/<int:postmark_id>", methods=["PUT"])
def update_postmark(postmark_id: int):
    """更新邮戳图鉴。"""
    data = request.get_json(silent=True) or {}
    error = validate_postmark_payload(data)
    if error:
        return jsonify({"error": error}), 400

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM postmarks WHERE id = ?", (postmark_id,)
        ).fetchone()
        if existing is None:
            return jsonify({"error": "记录不存在"}), 404

        conn.execute(
            """
            UPDATE postmarks SET
                name = ?,
                shape = ?,
                common_use = ?,
                description = ?
            WHERE id = ?
            """,
            (
                data["name"],
                data["shape"],
                data["common_use"],
                data["description"],
                postmark_id,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM postmarks WHERE id = ?", (postmark_id,)
        ).fetchone()
        return jsonify(postmark_row_to_dict(row))
    finally:
        conn.close()


@app.route("/api/postmarks/<int:postmark_id>", methods=["DELETE"])
def delete_postmark(postmark_id: int):
    """删除邮戳图鉴。"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM postmarks WHERE id = ?", (postmark_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "记录不存在"}), 404
        return jsonify({"message": "已删除"})
    finally:
        conn.close()


TAG_REQUIRED_FIELDS = ("name",)


def validate_tag_payload(data: dict) -> str | None:
    """
     * 校验标签请求体字段，返回错误信息或 None。
     * @param {dict} data
     * @returns {str | None}
     """
    if not data:
        return "请求体不能为空"
    for field in TAG_REQUIRED_FIELDS:
        if field not in data or data[field] in (None, ""):
            return f"缺少必填字段：{field}"
    if len(data["name"].strip()) > 50:
        return "标签名称不能超过 50 个字符"
    return None


@app.route("/api/tags", methods=["GET"])
def list_tags():
    """获取全部标签。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM tags ORDER BY id ASC"
        ).fetchall()
        return jsonify([tag_row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.route("/api/tags/<int:tag_id>", methods=["GET"])
def get_tag(tag_id: int):
    """获取单条标签详情。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM tags WHERE id = ?", (tag_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "标签不存在"}), 404
        return jsonify(tag_row_to_dict(row))
    finally:
        conn.close()


@app.route("/api/tags", methods=["POST"])
def create_tag():
    """新建标签。"""
    data = request.get_json(silent=True) or {}
    error = validate_tag_payload(data)
    if error:
        return jsonify({"error": error}), 400

    conn = get_connection()
    try:
        color = data.get("color", "#6366f1") or "#6366f1"
        name = data["name"].strip()

        existing = conn.execute(
            "SELECT id FROM tags WHERE name = ?", (name,)
        ).fetchone()
        if existing:
            return jsonify({"error": "标签名称已存在"}), 409

        cursor = conn.execute(
            "INSERT INTO tags (name, color) VALUES (?, ?)",
            (name, color),
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM tags WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return jsonify(tag_row_to_dict(row)), 201
    finally:
        conn.close()


@app.route("/api/tags/<int:tag_id>", methods=["PUT"])
def update_tag(tag_id: int):
    """更新标签。"""
    data = request.get_json(silent=True) or {}
    error = validate_tag_payload(data)
    if error:
        return jsonify({"error": error}), 400

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM tags WHERE id = ?", (tag_id,)
        ).fetchone()
        if existing is None:
            return jsonify({"error": "标签不存在"}), 404

        name = data["name"].strip()
        color = data.get("color", "#6366f1") or "#6366f1"

        duplicate = conn.execute(
            "SELECT id FROM tags WHERE name = ? AND id != ?",
            (name, tag_id),
        ).fetchone()
        if duplicate:
            return jsonify({"error": "标签名称已存在"}), 409

        conn.execute(
            "UPDATE tags SET name = ?, color = ? WHERE id = ?",
            (name, color, tag_id),
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM tags WHERE id = ?", (tag_id,)
        ).fetchone()
        return jsonify(tag_row_to_dict(row))
    finally:
        conn.close()


@app.route("/api/tags/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id: int):
    """删除标签（同时删除所有关联）。"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM tags WHERE id = ?", (tag_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "标签不存在"}), 404
        return jsonify({"message": "已删除"})
    finally:
        conn.close()


@app.route("/api/envelopes/<int:envelope_id>/tags", methods=["GET"])
def get_envelope_tags_route(envelope_id: int):
    """获取指定信封的所有标签。"""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM envelopes WHERE id = ?", (envelope_id,)
        ).fetchone()
        if existing is None:
            return jsonify({"error": "信封不存在"}), 404
        tags = get_envelope_tags(conn, envelope_id)
        return jsonify(tags)
    finally:
        conn.close()


@app.route("/api/envelopes/<int:envelope_id>/tags", methods=["PUT"])
def update_envelope_tags(envelope_id: int):
    """更新信封的标签（全量替换）。"""
    data = request.get_json(silent=True) or {}
    tag_ids = data.get("tag_ids", []) or []

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM envelopes WHERE id = ?", (envelope_id,)
        ).fetchone()
        if existing is None:
            return jsonify({"error": "信封不存在"}), 404

        conn.execute(
            "DELETE FROM envelope_tags WHERE envelope_id = ?",
            (envelope_id,),
        )
        for tag_id in tag_ids:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO envelope_tags (envelope_id, tag_id) VALUES (?, ?)",
                    (envelope_id, tag_id),
                )
            except Exception:
                pass

        conn.commit()
        tags = get_envelope_tags(conn, envelope_id)
        return jsonify(tags)
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    seed()
    app.run(host="0.0.0.0", port=4000, debug=True)
