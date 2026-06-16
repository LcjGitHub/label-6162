"""种子数据：5 条手写信封邮票收藏示例。"""

from database import get_connection, init_db

SEED_DATA = [
    {
        "origin": "上海",
        "destination": "北京",
        "year": 1952,
        "stamp_description": "纪1 庆祝中国人民政治协商会议成立",
        "postmark_type": "圆形日戳",
        "condition": "良好",
    },
    {
        "origin": "广州",
        "destination": "香港",
        "year": 1965,
        "stamp_description": "特50 中国古代建筑——故宫",
        "postmark_type": "方形纪念戳",
        "condition": "优秀",
    },
    {
        "origin": "成都",
        "destination": "重庆",
        "year": 1978,
        "stamp_description": "T38 万里长城",
        "postmark_type": "圆形日戳",
        "condition": "一般",
    },
    {
        "origin": "南京",
        "destination": "苏州",
        "year": 1988,
        "stamp_description": "J151 中国妇女",
        "postmark_type": "风景日戳",
        "condition": "良好",
    },
    {
        "origin": "西安",
        "destination": "兰州",
        "year": 1996,
        "stamp_description": "1996-1 丙子年（鼠）",
        "postmark_type": "圆形日戳",
        "condition": "优秀",
    },
]


def seed() -> None:
    """
     * 若表为空则写入 5 条种子数据。
     * @returns {None}
     """
    init_db()
    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) AS c FROM envelopes").fetchone()["c"]
        if count > 0:
            return
        for row in SEED_DATA:
            conn.execute(
                """
                INSERT INTO envelopes
                    (origin, destination, year, stamp_description, postmark_type, condition)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["origin"],
                    row["destination"],
                    row["year"],
                    row["stamp_description"],
                    row["postmark_type"],
                    row["condition"],
                ),
            )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
    print("Seed 完成，共写入 5 条记录。")
