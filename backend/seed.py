"""种子数据：信封收藏与邮戳图鉴示例。"""

from database import get_connection, init_db

ENVELOPE_SEED_DATA = [
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


POSTMARK_SEED_DATA = [
    {
        "name": "圆形日戳",
        "shape": "圆形",
        "common_use": "日常信件盖销",
        "description": "最常见的邮戳类型，通常为圆形，包含地名、日期和时间信息，用于盖销邮票证明邮件已付邮资。",
    },
    {
        "name": "方形纪念戳",
        "shape": "方形",
        "common_use": "纪念活动与特殊事件",
        "description": "为纪念重大事件、节日或邮票发行而特制的方形邮戳，通常带有主题图案和纪念文字，具有收藏价值。",
    },
    {
        "name": "风景日戳",
        "shape": "圆形",
        "common_use": "旅游景点邮局",
        "description": "刻有当地风景名胜图案的特种日戳，常见于旅游景区邮局，兼具邮政功能与纪念意义，深受集邮爱好者喜爱。",
    },
]


def seed() -> None:
    """
     * 若表为空则写入种子数据（信封 + 邮戳）。
     * @returns {None}
     """
    init_db()
    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) AS c FROM envelopes").fetchone()["c"]
        if count == 0:
            for row in ENVELOPE_SEED_DATA:
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

        count = conn.execute("SELECT COUNT(*) AS c FROM postmarks").fetchone()["c"]
        if count == 0:
            for row in POSTMARK_SEED_DATA:
                conn.execute(
                    """
                    INSERT INTO postmarks
                        (name, shape, common_use, description)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        row["name"],
                        row["shape"],
                        row["common_use"],
                        row["description"],
                    ),
                )

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
    print("Seed 完成。")
