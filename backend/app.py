"""手写信封邮票组合收藏 — Flask API。"""

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
            return f"缺少必填字段: {field}"
    try:
        year = int(data["year"])
        if year < 1800 or year > 2100:
            return "年份范围应在 1800–2100"
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
    """获取全部信封收藏。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM envelopes ORDER BY year DESC, id DESC"
        ).fetchall()
        return jsonify([envelope_row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.route("/api/envelopes/<int:envelope_id>", methods=["GET"])
def get_envelope(envelope_id: int):
    """获取单条信封详情。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM envelopes WHERE id = ?", (envelope_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "记录不存在"}), 404
        return jsonify(envelope_row_to_dict(row))
    finally:
        conn.close()


@app.route("/api/envelopes", methods=["POST"])
def create_envelope():
    """新建信封收藏。"""
    data = request.get_json(silent=True) or {}
    error = validate_envelope_payload(data)
    if error:
        return jsonify({"error": error}), 400

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
        conn.commit()
        row = conn.execute(
            "SELECT * FROM envelopes WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return jsonify(envelope_row_to_dict(row)), 201
    finally:
        conn.close()


@app.route("/api/envelopes/<int:envelope_id>", methods=["PUT"])
def update_envelope(envelope_id: int):
    """更新信封收藏。"""
    data = request.get_json(silent=True) or {}
    error = validate_envelope_payload(data)
    if error:
        return jsonify({"error": error}), 400

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
        conn.commit()
        row = conn.execute(
            "SELECT * FROM envelopes WHERE id = ?", (envelope_id,)
        ).fetchone()
        return jsonify(envelope_row_to_dict(row))
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


if __name__ == "__main__":
    init_db()
    seed()
    app.run(host="0.0.0.0", port=4000, debug=True)
