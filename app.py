import streamlit as st
import sqlite3
import re
from datetime import date, datetime

DB = "life_os.db"

conn = sqlite3.connect(DB, check_same_thread=False)
cur = conn.cursor()


# =========================================================
# DATABASE
# =========================================================

cur.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    category TEXT,
    content TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    title TEXT,
    content TEXT,
    status TEXT,
    created_at TEXT
)
""")

# 既存knowledgeテーブルにstatusがない場合への対応
try:
    cur.execute("ALTER TABLE knowledge ADD COLUMN status TEXT DEFAULT '継続中'")
except sqlite3.OperationalError:
    pass

cur.execute("""
CREATE TABLE IF NOT EXISTS workout_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_date TEXT,
    day_name TEXT,
    exercise_name TEXT,
    weight REAL,
    reps INTEGER,
    sets INTEGER,
    impression TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS money_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT,
    amount REAL,
    category TEXT,
    content TEXT,
    created_at TEXT
)
""")

conn.commit()


# =========================================================
# WORKOUT MENU
# =========================================================

workout_menu = {

    "Day 1：Upper A": [
        ("ベンチプレス", 67.5, 5, 4, "3分"),
        ("シーテッドロウ", 50, 10, 3, "3分"),
        ("インクラインプレス(マシン)", 30, 8, 3, "3分"),
        ("ケーブルラットプルダウン", 50, 10, 3, "3分"),
        ("サイドレイズ", 6, 15, 3, "2分"),
        ("インクラインダンベルカール", 9, 10, 3, "2分"),
    ],

    "Day 2：Lower A": [
        ("シーテッドレッグプレス", None, 8, 5, "3分"),
        ("レッグカール", 40, 15, 4, "2分"),
        ("レッグエクステンション", 40, 15, 4, "2分"),
    ],

    "Day 3：Upper B": [
        ("ベンチプレス", 65, 8, 3, "3分"),
        ("懸垂（アシスト）", None, 10, 3, "3分"),
        ("ケーブルオーバーヘッドEX", 12.5, 12, 3, "2分"),
        ("フェイスプル", 15, 15, 3, "2分"),
        ("サイドレイズ", 6, 15, 3, "2分"),
        ("ダンベルカール", 10, 12, 3, "2分"),
    ],

    "Day 4：Lower B": [
        ("シーテッドレッグプレス", None, 10, 4, "3分"),
        ("レッグカール", 40, 15, 4, "2分"),
        ("レッグエクステンション", 40, 15, 4, "2分"),
    ],
}


# =========================================================
# FUNCTIONS
# =========================================================

def get_last_workout(exercise_name, day_name):

    cur.execute("""
        SELECT workout_date, weight, reps, sets, impression
        FROM workout_history
        WHERE exercise_name = ?
        AND day_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (exercise_name, day_name))

    return cur.fetchone()


def save_workout(
    workout_date,
    day_name,
    exercise_name,
    weight,
    reps,
    sets,
    impression
):

    cur.execute("""
        INSERT INTO workout_history
        (
            workout_date,
            day_name,
            exercise_name,
            weight,
            reps,
            sets,
            impression
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(workout_date),
        day_name,
        exercise_name,
        weight,
        reps,
        sets,
        impression
    ))

    conn.commit()


def parse_workout_text(
    text,
    default_weight,
    default_reps,
    default_sets
):

    weight = default_weight
    reps = default_reps
    sets = default_sets

    weight_match = re.search(
        r'(\d+(?:\.\d+)?)\s*(?:kg|キロ)',
        text,
        re.IGNORECASE
    )

    if weight_match:
        weight = float(weight_match.group(1))

    reps_match = re.search(
        r'(\d+)\s*(?:回|rep|reps)',
        text,
        re.IGNORECASE
    )

    if reps_match:
        reps = int(reps_match.group(1))

    sets_match = re.search(
        r'(\d+)\s*(?:セット|set|sets)',
        text,
        re.IGNORECASE
    )

    if sets_match:
        sets = int(sets_match.group(1))

    return weight, reps, sets


def save_knowledge(category, title, content, status):

    cur.execute("""
        INSERT INTO knowledge
        (
            category,
            title,
            content,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        category,
        title,
        content,
        status,
        datetime.now().isoformat()
    ))

    conn.commit()


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="LIFE OS",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 LIFE OS")


# =========================================================
# SIDEBAR
# =========================================================

page = st.sidebar.radio(
    "メニュー",
    [
        "🏠 ダッシュボード",
        "🏋️ 今日の筋トレ",
        "🧠 基礎データ登録",
        "📚 登録データ",
        "💰 お金"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 ダッシュボード":

    st.header("🏠 ダッシュボード")

    st.write(
        "記録 → 蓄積 → 分析 → 判断 → 行動促進"
    )

    cur.execute("SELECT COUNT(*) FROM records")
    record_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM knowledge")
    knowledge_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM workout_history")
    workout_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM money_records")
    money_count = cur.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("日々の記録", record_count)

    with col2:
        st.metric("基礎データ", knowledge_count)

    with col3:
        st.metric("筋トレ記録", workout_count)

    with col4:
        st.metric("お金の記録", money_count)

    st.divider()

    st.subheader("現在のLIFE OS")

    st.write("""
    あなたの生活に関する情報を蓄積し、
    将来的にAIによる分析・判断・行動促進につなげます。
    """)


# =========================================================
# WORKOUT
# =========================================================

elif page == "🏋️ 今日の筋トレ":

    st.header("🏋️ 今日の筋トレ")

    workout_date = st.date_input(
        "日付",
        value=date.today()
    )

    day_name = st.selectbox(
        "今日のDay",
        list(workout_menu.keys())
    )

    st.divider()

    st.info(
        "メニューはLIFE OSが覚えています。"
        "実際にやった内容・感想だけ入力してください。"
    )

    for exercise_name, target_weight, target_reps, target_sets, rest in workout_menu[day_name]:

        st.markdown(f"### {exercise_name}")

        if target_weight is None:
            target_weight_text = "重量：未設定"
        elif exercise_name == "インクラインプレス(マシン)":
            target_weight_text = f"片側 {target_weight}kg"
        else:
            target_weight_text = f"{target_weight}kg"

        st.caption(
            f"目標：{target_weight_text} / "
            f"{target_reps}回 / "
            f"{target_sets}セット / "
            f"休憩 {rest}"
        )

        previous = get_last_workout(
            exercise_name,
            day_name
        )

        if previous:

            prev_date = previous[0]
            prev_weight = previous[1]
            prev_reps = previous[2]
            prev_sets = previous[3]

            if prev_weight is None:
                prev_weight_text = "重量未記録"
            else:
                prev_weight_text = f"{prev_weight}kg"

            st.write(
                f"前回：{prev_weight_text} / "
                f"{prev_reps}回 / "
                f"{prev_sets}セット "
                f"（{prev_date}）"
            )

        impression = st.text_area(
            "今日の実績・感想",
            placeholder=(
                "例：67.5kgで5回4セット。"
                "最後かなりきつかったけどフォームは安定。"
                "次回は70kgいけそう。"
            ),
            key=f"impression_{day_name}_{exercise_name}"
        )

        if st.button(
            "💾 記録",
            key=f"save_{day_name}_{exercise_name}"
        ):

            if not impression.strip():

                st.warning(
                    "実績・感想を入力してください。"
                )

            else:

                actual_weight, actual_reps, actual_sets = parse_workout_text(
                    impression,
                    target_weight,
                    target_reps,
                    target_sets
                )

                save_workout(
                    workout_date,
                    day_name,
                    exercise_name,
                    actual_weight,
                    actual_reps,
                    actual_sets,
                    impression
                )

                st.success(
                    "記録しました！"
                )

        st.divider()


# =========================================================
# KNOWLEDGE INPUT
# =========================================================

elif page == "🧠 基礎データ登録":

    st.header("🧠 基礎データ登録")

    st.write(
        "あなた自身に関する大量の情報をまとめて登録できます。"
    )

    mode = st.radio(
        "登録方法",
        [
            "📝 一括登録",
            "➕ 1件ずつ登録"
        ]
    )

    # -----------------------------------------------------
    # BULK
    # -----------------------------------------------------

    if mode == "📝 一括登録":

        st.subheader("大量データを一気に登録")

        category = st.selectbox(
            "カテゴリー",
            [
                "美容",
                "仕事",
                "筋トレ",
                "お金",
                "生活",
                "目標",
                "その他"
            ],
            key="bulk_category"
        )

        status = st.selectbox(
            "現在の状態",
            [
                "今やる",
                "継続中",
                "後でやる",
                "条件が整ったらやる",
                "いつかやりたい",
                "完了",
                "やめた"
            ],
            key="bulk_status"
        )

        title = st.text_input(
            "タイトル",
            placeholder="例：現在の美容計画"
        )

        bulk_content = st.text_area(
            "内容",
            height=400,
            placeholder="""
ここに関連する情報をまとめて貼り付けてください。

例：

最終目標：
〜〜〜

現在：
〜〜〜

今後やりたいこと：
〜〜〜

優先順位：
〜〜〜

注意点：
〜〜〜
"""
        )

        if st.button(
            "🚀 このデータを一括登録",
            type="primary"
        ):

            if title.strip() and bulk_content.strip():

                save_knowledge(
                    category,
                    title,
                    bulk_content,
                    status
                )

                st.success(
                    "大量データを1件の基礎データとして保存しました！"
                )

            else:

                st.warning(
                    "タイトルと内容を入力してください。"
                )

    # -----------------------------------------------------
    # SINGLE
    # -----------------------------------------------------

    else:

        st.subheader("1件ずつ登録")

        category = st.selectbox(
            "カテゴリー",
            [
                "美容",
                "仕事",
                "筋トレ",
                "お金",
                "生活",
                "目標",
                "その他"
            ],
            key="single_category"
        )

        status = st.selectbox(
            "現在の状態",
            [
                "今やる",
                "継続中",
                "後でやる",
                "条件が整ったらやる",
                "いつかやりたい",
                "完了",
                "やめた"
            ],
            key="single_status"
        )

        title = st.text_input(
            "タイトル",
            key="single_title"
        )

        content = st.text_area(
            "内容",
            height=250,
            key="single_content"
        )

        if st.button(
            "登録する",
            key="single_save"
        ):

            if title.strip() and content.strip():

                save_knowledge(
                    category,
                    title,
                    content,
                    status
                )

                st.success(
                    "登録しました！"
                )

            else:

                st.warning(
                    "タイトルと内容を入力してください。"
                )


# =========================================================
# KNOWLEDGE LIST
# =========================================================

elif page == "📚 登録データ":

    st.header("📚 登録データ")

    cur.execute("""
        SELECT
            id,
            category,
            title,
            content,
            status,
            created_at
        FROM knowledge
        ORDER BY id DESC
    """)

    data = cur.fetchall()

    if not data:

        st.info(
            "まだ登録データはありません。"
        )

    else:

        for (
            item_id,
            category,
            title,
            content,
            status,
            created_at
        ) in data:

            with st.expander(
                f"{category}｜{title}｜{status}"
            ):

                st.write(content)

                st.caption(
                    f"登録：{created_at}"
                )


# =========================================================
# MONEY
# =========================================================

elif page == "💰 お金":

    st.header("💰 お金")

    st.write(
        "現在は収入・支出を記録する土台です。"
    )

    money_date = st.date_input(
        "日付",
        value=date.today(),
        key="money_date"
    )

    money_type = st.selectbox(
        "種類",
        [
            "支出",
            "収入"
        ]
    )

    amount = st.number_input(
        "金額",
        min_value=0,
        step=100
    )

    category = st.selectbox(
        "カテゴリー",
        [
            "食費",
            "交通費",
            "美容",
            "仕事",
            "筋トレ",
            "固定費",
            "買い物",
            "その他"
        ]
    )

    content = st.text_input(
        "内容",
        placeholder="例：昼食、ジム用品、仕事用教材など"
    )

    if st.button(
        "💾 お金を記録"
    ):

        if amount > 0:

            final_amount = amount

            if money_type == "支出":
                final_amount = -amount

            cur.execute("""
                INSERT INTO money_records
                (
                    record_date,
                    amount,
                    category,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(money_date),
                final_amount,
                category,
                content,
                datetime.now().isoformat()
            ))

            conn.commit()

            st.success(
                "記録しました！"
            )

        else:

            st.warning(
                "金額を入力してください。"
            )

    st.divider()

    st.subheader("最近のお金の記録")

    cur.execute("""
        SELECT
            record_date,
            amount,
            category,
            content
        FROM money_records
        ORDER BY id DESC
        LIMIT 20
    """)

    money_data = cur.fetchall()

    if not money_data:

        st.info(
            "まだお金の記録はありません。"
        )

    else:

        for (
            record_date,
            amount,
            category,
            content
        ) in money_data:

            if amount < 0:

                amount_text = (
                    f"-¥{abs(amount):,.0f}"
                )

            else:

                amount_text = (
                    f"+¥{amount:,.0f}"
                )

            st.write(
                f"**{record_date}**　"
                f"{amount_text}　"
                f"{category}　"
                f"{content}"
            )
