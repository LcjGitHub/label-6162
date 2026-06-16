"""手写信封邮票组合收藏 — Flask API。"""

from flask import Flask, jsonify, request

from database import get_connection, init_db
from seed import seed

app = Flask(__name__)

REQUIRED_FIELDS = (
    "origin",
    "destination",
    "year",
    "stamp_description",
    "postmark_type",
    "condition",
)


def row_to_dict(row) -> dict:
    """
     * 将 sqlite3.Row 转为 JSON 可序列化字典。
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


def validate_payload(data: dict) -> str | None:
    """
     * 校验请求体字段，返回错误信息或 None。
     * @param {dict} data
     * @returns {str | None}
     """
    if not data:
        return "请求体不能为空"
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] in (None, ""):
            return f"缺少必填字段: {field}"
    try:
        year = int(data["year"])
        if year < 1800 or year > 2100:
            return "年份范围应在 1800–2100"
    except (TypeError, ValueError):
        return "年份必须为整数"
    return None


@app.route("/api/envelopes", methods=["GET"])
def list_envelopes():
    """获取全部信封收藏。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM envelopes ORDER BY year DESC, id DESC"
        ).fetchall()
        return jsonify([row_to_dict(r) for r in rows])
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
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.route("/api/envelopes", methods=["POST"])
def create_envelope():
    """新建信封收藏。"""
    data = request.get_json(silent=True) or {}
    error = validate_payload(data)
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
        return jsonify(row_to_dict(row)), 201
    finally:
        conn.close()


@app.route("/api/envelopes/<int:envelope_id>", methods=["PUT"])
def update_envelope(envelope_id: int):
    """更新信封收藏。"""
    data = request.get_json(silent=True) or {}
    error = validate_payload(data)
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
        return jsonify(row_to_dict(row))
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


if __name__ == "__main__":
    init_db()
    seed()
    app.run(host="0.0.0.0", port=4000, debug=True)
