import streamlit as st
import os
import json
import tempfile
from dotenv import load_dotenv
from utils.transcription import GladiaAPI
from utils.text_formatter import GeminiFormatter

# 環境変数を読み込み
load_dotenv()

# 保存ファイルパス
CHARACTERS_FILE = os.path.join(os.path.dirname(__file__), "characters.json")
TEMPLATES_FILE = os.path.join(os.path.dirname(__file__), "templates.json")


def load_characters():
    """JSONファイルからキャラクターを読み込む"""
    if os.path.exists(CHARACTERS_FILE):
        try:
            with open(CHARACTERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_characters(characters):
    """キャラクターをJSONファイルに保存"""
    with open(CHARACTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)


def load_templates():
    """JSONファイルから誘導文・定型文を読み込む"""
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def save_templates(lead_templates, closing_text):
    """誘導文・定型文をJSONファイルに保存"""
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump({"lead_templates": lead_templates, "closing_text": closing_text}, f, ensure_ascii=False, indent=2)


# ページ設定
st.set_page_config(
    page_title="TikTok Scenario Rewriter",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 翻訳を無効化
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# カスタムCSS - TikTokスタイルのボタンとUI
st.markdown("""
<style>
    /* TikTokカラー: シアン #00f2ea, ピンク #fe2c55, 黒背景 */

    /* ダークテーマの背景 */
    .stApp {
        background: #000000;
        color: #ffffff;
    }

    /* ヘッダースタイル */
    h1 {
        color: #ffffff !important;
        text-shadow:
            2px 2px 0px #fe2c55,
            -2px -2px 0px #00f2ea;
        font-weight: bold !important;
    }

    h2, h3 {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0, 242, 234, 0.5);
    }

    /* サイドバーを非表示 */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* 本文の左右余白を均等に */
    .block-container {
        padding: 2rem 3rem 2rem 3rem !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }

    .stApp {
        overflow-x: hidden !important;
    }

    /* expanderのスタイル - コンパクトに */
    [data-testid="stExpander"] {
        background: #00f2ea !important;
        border: none !important;
        border-radius: 8px !important;
        margin-bottom: 20px !important;
        width: fit-content !important;
    }
    [data-testid="stExpander"] summary {
        color: #000000 !important;
        font-weight: bold !important;
        padding: 8px 16px !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: #00d4d4 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #1a1a1a !important;
        border: 1px solid #00f2ea !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin-top: 10px !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] label {
        color: #ffffff !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] a {
        color: #00f2ea !important;
    }

    /* 全てのボタンを左寄せ・同じ大きさに統一 */
    .stButton > button,
    .stButton button,
    .stDownloadButton > button,
    .stDownloadButton button,
    [data-testid="stFormSubmitButton"] button,
    button[kind="primary"] {
        background: #000000 !important;
        color: white !important;
        border: 2px solid #00f2ea !important;
        border-radius: 10px !important;
        padding: 12px 30px !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.5) !important;
        transition: all 0.3s ease !important;
        width: auto !important;
        max-width: 100% !important;
        min-height: 45px !important;
        height: 45px !important;
        line-height: 1.2 !important;
        margin-right: auto !important;
        margin-left: 0 !important;
        display: block !important;
    }

    .stButton > button:hover:not(:disabled),
    .stButton button:hover:not(:disabled),
    .stDownloadButton > button:hover,
    .stDownloadButton button:hover,
    [data-testid="stFormSubmitButton"] button:hover,
    button[kind="primary"]:hover {
        background: #1a1a1a !important;
        border: 3px solid #00f2ea !important;
        color: #00f2ea !important;
        box-shadow:
            0 0 40px rgba(0, 242, 234, 1),
            0 0 60px rgba(0, 242, 234, 0.6),
            inset 0 0 20px rgba(0, 242, 234, 0.2) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }

    /* テキストエリア */
    .stTextArea textarea {
        background: rgba(10, 10, 10, 0.9) !important;
        color: #ffffff !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.3) !important;
        caret-color: #00f2ea !important;
        padding: 10px !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    /* プレースホルダーの色 */
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: rgba(0, 242, 234, 0.6) !important;
    }

    /* テキストインプット */
    .stTextInput input {
        background: rgba(10, 10, 10, 0.9) !important;
        color: #ffffff !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.3) !important;
        caret-color: #00f2ea !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
    }

    /* セレクトボックス */
    .stSelectbox > div > div {
        background: rgba(10, 10, 10, 0.9) !important;
        color: #ffffff !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 10px !important;
    }

    /* スライダー */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00f2ea 0%, #fe2c55 100%) !important;
    }

    /* 各種ラベルを白文字に */
    .stFileUploader label,
    [data-testid="stFileUploader"] label,
    .stFileUploader p,
    [data-testid="stFileUploader"] p,
    .stTextArea label,
    .stTextInput label,
    .stSelectbox label,
    .stSlider label {
        color: #ffffff !important;
    }

    /* インフォボックス */
    .stInfo {
        background: rgba(0, 242, 234, 0.1) !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.3) !important;
        color: #ffffff !important;
    }

    /* ファイルアップローダー */
    .stFileUploader {
        background: rgba(10, 10, 10, 0.9) !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }

    /* タブスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: transparent !important;
        padding: 15px 10px 20px 10px;
        border: none !important;
        display: flex !important;
        flex-direction: row !important;
    }

    .stTabs [data-baseweb="tab"] {
        flex: 1 !important;
        width: 100% !important;
        height: 45px !important;
        padding: 12px 30px !important;
        background: #000000 !important;
        border: 2px solid #00f2ea !important;
        border-radius: 10px !important;
        color: white !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.5) !important;
        transition: all 0.25s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #1a1a1a !important;
        border: 3px solid #00f2ea !important;
        color: #00f2ea !important;
        box-shadow: 0 0 40px rgba(0, 242, 234, 1) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }

    /* サクセスボックス - ピンク系 */
    .stSuccess {
        background: rgba(254, 44, 85, 0.1) !important;
        border: 2px solid rgba(254, 44, 85, 0.5) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }

    /* ラジオボタン */
    .stRadio > div {
        color: #ffffff !important;
    }
    .stRadio label {
        color: #ffffff !important;
    }

    /* バリエーションカード */
    .variation-card {
        background: rgba(10, 10, 10, 0.9);
        border: 2px solid rgba(0, 242, 234, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .variation-card:hover {
        border-color: #00f2ea;
        box-shadow: 0 0 20px rgba(0, 242, 234, 0.3);
    }
    .variation-card.selected {
        border-color: #fe2c55;
        box-shadow: 0 0 20px rgba(254, 44, 85, 0.5);
    }
    .variation-label {
        color: #00f2ea;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 10px;
    }
    .variation-text {
        color: #ffffff;
        font-size: 14px;
        line-height: 1.8;
        white-space: pre-wrap;
    }

    /* キャラクターカード */
    .char-card {
        background: rgba(10, 10, 10, 0.9);
        border: 2px solid rgba(254, 44, 85, 0.3);
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
    }
    .char-card:hover {
        border-color: #fe2c55;
        box-shadow: 0 0 15px rgba(254, 44, 85, 0.3);
    }
    .char-card-protagonist {
        background: rgba(10, 10, 10, 0.9);
        border: 2px solid rgba(0, 242, 234, 0.5);
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        box-shadow: 0 0 10px rgba(0, 242, 234, 0.2);
    }
    .char-number {
        color: #fe2c55;
        font-weight: bold;
        font-size: 14px;
    }
    .role-badge-protagonist {
        background: #00f2ea;
        color: #000;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
    }
    .role-badge-questioner {
        background: #fe2c55;
        color: #fff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
    }

    /* マルチセレクト */
    .stMultiSelect > div > div {
        background: rgba(10, 10, 10, 0.9) !important;
        color: #ffffff !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 10px !important;
    }
    .stMultiSelect label {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# セッションステートの初期化
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None
if 'formatted_text' not in st.session_state:
    st.session_state.formatted_text = None
if 'filename' not in st.session_state:
    st.session_state.filename = None
if 'rewritten_text' not in st.session_state:
    st.session_state.rewritten_text = None
if 'rewrite_variations' not in st.session_state:
    st.session_state.rewrite_variations = None
if 'selected_variation' not in st.session_state:
    st.session_state.selected_variation = None
if 'adopted_scenario' not in st.session_state:
    st.session_state.adopted_scenario = None
if 'generated_sns_content' not in st.session_state:
    st.session_state.generated_sns_content = None
if 'characters' not in st.session_state:
    st.session_state.characters = load_characters()  # JSONファイルから読み込み
if 'closing_text' not in st.session_state or 'lead_templates' not in st.session_state:
    saved_templates = load_templates()
    if saved_templates:
        if 'closing_text' not in st.session_state:
            st.session_state.closing_text = saved_templates.get("closing_text", "")
        if 'lead_templates' not in st.session_state:
            st.session_state.lead_templates = saved_templates.get("lead_templates", "")
    else:
        if 'closing_text' not in st.session_state:
            st.session_state.closing_text = """詳しく知りたい人は、
このアカウントをフォロー、
画面のようにタップし、
リンクから、
1分でできる無料診断を、
受けてみてください。"""
        if 'lead_templates' not in st.session_state:
            st.session_state.lead_templates = """・今の仕事で問題を抱えている人へ。早めの行動があなたを守るかもしれません。退職を考えている人は、退職給付金の活用でお金の問題は解決できる場合があります。最大400万円以上受け取っている人もいる国の制度があります。

・社会保険に1年以上加入していれば最大28ヶ月の給付が可能。平均支給額は450万円以上。これを逃すのはもったいないです。ただ、申請がちょっと難しいのと退職前に準備を始めないといけないのが難点。制度を知らず損してしまう人は本当に多いんです。自分が対象かどうか気になる人はまずはいくらもらえるか確認してみてください。

・退職前に申請すれば400万以上受け取れる給付金制度があるのをご存知ですか。ですが申請方法を知らずに損している人が多数。あなたには損をしてほしくないのでこのアカウントをフォローして教えてとコメントしてください。

・賢く退職する人はみんな制度を味方にしています。400万以上もらえる可能性のある国の制度。しかし申請ミスや期限切れでチャンスを逃す人も多いです。正しい申請方法を知りたい人はこのアカウントをフォローしてプロフのリンクから1分の無料診断を受けてみてください。

・今の生活が不安な方は制度を正しく知ることが大切です。もしあなたが65歳未満なら28ヶ月受給できる給付制度もあります。

・退職後の生活が不安な方へ。

・「自分はどれに当てはまりそうか」「退職前に何をしておくべきか」を知りたい場合は。

・「次が決まっていないのにお金がない」という不安は、焦りを生み、ブラック企業への誤入社を招くリスクがあります。しかし、会社を辞めた後に使える国の公的制度をフル活用すれば、数ヶ月から1年は生活費の心配を減らすことが可能です。経済的な余裕は、精神的な「盾」となります。目先の生活に追われず、じっくり会社を見極める時間を確保することで、変な会社に捕まらずに納得のいく再就職を目指せます。"""

# API設定（折りたたみ式）- タイトルの上に配置
with st.expander("API設定", expanded=False):
    # プレースホルダーテキストは空白として扱う
    env_gladia = os.getenv("GLADIA_API_KEY", "")
    if env_gladia == "ここに貼り付け":
        env_gladia = ""
    env_gemini = os.getenv("GEMINI_API_KEY", "")
    if env_gemini == "ここに貼り付け":
        env_gemini = ""

    col1, col2 = st.columns(2)
    with col1:
        gladia_api_key = st.text_input("Gladia API Key", value=env_gladia, type="password")
        st.markdown('<a href="https://www.gladia.io/" target="_blank" style="color: #00f2ea; font-size: 12px;">Gladia APIキーを取得</a>', unsafe_allow_html=True)
    with col2:
        gemini_api_key = st.text_input("Gemini API Key", value=env_gemini, type="password")
        st.markdown('<a href="https://aistudio.google.com/apikey" target="_blank" style="color: #00f2ea; font-size: 12px;">Gemini APIキーを取得</a>', unsafe_allow_html=True)

    # APIキー保存ボタン
    if st.button("APIキーを保存", key="save_api_keys"):
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, "w") as f:
            f.write(f"GLADIA_API_KEY={gladia_api_key}\n")
            f.write(f"GEMINI_API_KEY={gemini_api_key}\n")
        st.success("APIキーを保存しました")

    st.markdown('テキスト入力のみの場合、Gladia APIは不要です')

# タイトル
st.markdown('<h1 translate="no">TikTok Scenario Rewriter</h1>', unsafe_allow_html=True)
st.markdown("キャラ設定 → 入力 → 整形 → 誘導文設定 → **AI書き直し** → SNS生成 → DL")

# APIクライアントの初期化
gladia = GladiaAPI(gladia_api_key) if gladia_api_key else None
gemini = GeminiFormatter(gemini_api_key) if gemini_api_key else None

# ===========================================
# セクション1: キャラクター設定
# ===========================================
st.header("1. キャラクター設定")
st.markdown("最大5人のキャラクターを登録できます。**最初に登録した人物が回答者（主人公）**になります。2人目以降は質問者です。")

# --- 登録済みキャラクター表示 ---
if st.session_state.characters:
    st.subheader(f"登録済みキャラクター（{len(st.session_state.characters)}人）")
    for i, char in enumerate(st.session_state.characters):
        is_protagonist = (i == 0)
        if is_protagonist:
            role_badge = '<span class="role-badge-protagonist">回答者・主人公</span>'
            card_class = "char-card-protagonist"
        else:
            role_badge = '<span class="role-badge-questioner">質問者</span>'
            card_class = "char-card"

        card_html = f"""<div class="{card_class}">
<span class="char-number">#{i + 1}</span>
<strong style="color: {'#00f2ea' if is_protagonist else '#fe2c55'}; font-size: 18px; margin-left: 8px;">{char['name']}</strong>
{role_badge}
<span style="color: #888; margin-left: 12px;">{char['gender']} / {char['age']}</span>
<br><span style="color: #aaa;">見た目:</span> {char['appearance']}
　<span style="color: #aaa;">雰囲気:</span> {char['atmosphere']}
<br><span style="color: #aaa;">背景:</span> {char['background']}
　<span style="color: #aaa;">口調:</span> {char['tone']}
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)
        if st.button(f"削除: {char['name']}", key=f"del_char_{i}"):
            st.session_state.characters.pop(i)
            save_characters(st.session_state.characters)
            st.rerun()

# --- 新規キャラクター登録フォーム ---
if len(st.session_state.characters) < 5:
    role_label = "回答者（主人公）" if len(st.session_state.characters) == 0 else "質問者"
    st.subheader(f"キャラクター登録（次の登録は「{role_label}」になります）")

    with st.form("char_register_form", clear_on_submit=True):
        col_n, col_a, col_g = st.columns([2, 1, 1])
        with col_n:
            new_name = st.text_input("名前", placeholder="例：太郎")
        with col_a:
            new_age = st.selectbox("年代", ["10代", "20代", "30代", "40代", "50代", "60代以上"], index=1)
        with col_g:
            new_gender = st.selectbox("性別", ["男性", "女性", "その他"])

        col_ap, col_at = st.columns(2)
        with col_ap:
            new_appearance = st.text_input("見た目", placeholder="例：短髪、メガネ、スーツ姿")
        with col_at:
            new_atmosphere = st.text_input("雰囲気", placeholder="例：明るく元気、頼れる兄貴")

        col_bg, col_tn = st.columns(2)
        with col_bg:
            new_background = st.text_input("背景", placeholder="例：IT企業の新入社員、趣味はゲーム")
        with col_tn:
            new_tone = st.text_input("口調", placeholder="例：タメ口、テンション高め、語尾に「っす」")

        submitted = st.form_submit_button("REGISTER")

    if submitted:
        if not new_name.strip():
            st.error("名前を入力してください")
        elif any(c["name"] == new_name.strip() for c in st.session_state.characters):
            st.error(f"「{new_name.strip()}」は既に登録されています")
        else:
            st.session_state.characters.append({
                "name": new_name.strip(),
                "age": new_age,
                "gender": new_gender,
                "appearance": new_appearance.strip(),
                "atmosphere": new_atmosphere.strip(),
                "background": new_background.strip(),
                "tone": new_tone.strip(),
            })
            save_characters(st.session_state.characters)
            st.rerun()
else:
    st.info("キャラクター登録の上限（5人）に達しています。追加するには既存のキャラクターを削除してください。")

# ===========================================
# セクション2: 入力ソース選択
# ===========================================
st.header("2. 入力ソース選択")

tab1, tab2, tab3 = st.tabs(["動画から生成", "ファイルから生成", "テキスト入力"])

with tab1:
    st.subheader("動画アップロード")

    uploaded_file = st.file_uploader(
        "動画ファイルを選択してください",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        key="video_uploader"
    )

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        st.info(f"アップロードされたファイル: {uploaded_file.name}")

        if st.button("START", key="transcribe_btn"):
            if not gladia_api_key or not gemini_api_key:
                st.error("API設定でGladia APIキーとGemini APIキーを入力してください")
                st.stop()

            progress_bar = st.progress(0)

            progress_bar.progress(10)
            audio_url = gladia.upload_file(tmp_file_path)

            if audio_url:
                progress_bar.progress(30)
                transcribed = gladia.transcribe(audio_url, language="ja")

                if transcribed:
                    st.session_state.transcribed_text = transcribed
                    progress_bar.progress(60)
                    formatted = gemini.format_text(transcribed)

                    if formatted:
                        st.session_state.formatted_text = formatted
                        progress_bar.progress(80)
                        filename = gemini.generate_filename(formatted)
                        st.session_state.filename = filename or "output"
                        progress_bar.progress(100)
                        st.success("Complete!")

        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

with tab2:
    st.subheader("テキストファイルアップロード")

    text_file = st.file_uploader(
        "テキストファイルを選択してください (.txt)",
        type=["txt"],
        key="text_file_uploader"
    )

    if text_file is not None:
        st.info(f"アップロードされたファイル: {text_file.name}")

        if st.button("START", key="text_process_btn"):
            try:
                progress_bar = st.progress(0)

                progress_bar.progress(20)
                raw_text = text_file.read().decode('utf-8', errors='replace')

                if raw_text.strip():
                    st.session_state.transcribed_text = raw_text
                    progress_bar.progress(40)

                    # Geminiで句読点追加＋句点改行の整形
                    if gemini:
                        formatted_text = gemini.format_text(raw_text)
                        if formatted_text:
                            st.session_state.formatted_text = formatted_text
                        else:
                            st.session_state.formatted_text = raw_text
                    else:
                        st.session_state.formatted_text = raw_text
                    progress_bar.progress(80)

                    filename = os.path.splitext(text_file.name)[0]
                    st.session_state.filename = filename
                    progress_bar.progress(100)
                    st.success("Complete!")
                else:
                    st.error("テキストファイルが空です")
            except Exception as e:
                st.error(f"テキスト読み込みエラー: {str(e)}")

with tab3:
    st.subheader("テキストを直接入力")

    direct_text = st.text_area(
        "テキストを貼り付けてください（そのまま整形済みテキストとして使用します）",
        height=250,
        placeholder="ここにテキストを貼り付け...\n\n例：\n大暴露、退職前にもらえる給付金11選。\n国はゼニゲバなので、200万円以上得する情報は一切教えてくれません。",
        key="direct_text_input"
    )

    if st.button("START", key="direct_text_btn"):
        if direct_text.strip():
            st.session_state.transcribed_text = direct_text
            st.session_state.formatted_text = direct_text

            # ファイル名生成
            if gemini:
                filename = gemini.generate_filename(direct_text)
                st.session_state.filename = filename or "output"
            else:
                clean = direct_text.strip().replace('\n', '')[:20]
                st.session_state.filename = clean if clean else "output"

            st.success("Complete!")
        else:
            st.error("テキストを入力してください")

# ===========================================
# セクション3: 整形済みテキスト表示・編集
# ===========================================
if st.session_state.formatted_text:
    st.header("3. テキスト編集")

    if "text_editor" not in st.session_state:
        st.session_state.text_editor = st.session_state.formatted_text

    if "filename" not in st.session_state or not st.session_state.filename:
        st.session_state.filename = "output"

    st.subheader("整形済みテキスト")
    # text_areaの値を明示的に取得して保存
    current_text = st.text_area(
        "整形されたテキスト（編集可能）",
        value=st.session_state.get("text_editor", st.session_state.formatted_text),
        height=400,
        key="text_editor_widget"
    )
    # 編集されたテキストをセッションに保存
    st.session_state.text_editor = current_text

    st.download_button(
        label="DOWNLOAD TEXT",
        data=current_text,
        file_name=f"{st.session_state.filename}.txt",
        mime="text/plain",
        key="download_text"
    )

    # ファイル名入力
    final_filename = st.text_input("ファイル名（編集可能）", value=st.session_state.filename, key="filename_input")

    # ===========================================
    # セクション4: 誘導文・定型文設定
    # ===========================================
    st.header("4. 誘導文・定型文設定")
    st.markdown("シナリオ末尾に自然につなげる誘導文と、最後に必ず付加する定型文を設定します。")

    lead_templates = st.text_area(
        "誘導文テンプレート（AIが参考にする表現集）",
        value=st.session_state.lead_templates,
        height=300,
        key="lead_templates_editor",
        help="AIはこのテンプレートを参考に、シナリオの流れに合った誘導文を自然に組み込みます"
    )
    st.session_state.lead_templates = lead_templates

    closing_text = st.text_area(
        "定型文（シナリオ末尾に必ず付加）",
        value=st.session_state.closing_text,
        height=150,
        key="closing_text_editor",
        help="この定型文はAI生成後にそのまま末尾に付加されます（AI生成の対象外）"
    )
    st.session_state.closing_text = closing_text

    # 変更があればファイルに保存
    save_templates(lead_templates, closing_text)

    # ===========================================
    # セクション5: AI書き直し（メイン機能）
    # ===========================================
    st.header("5. AI書き直し")

    st.markdown("シナリオ全体を書き直します。テーマは維持しつつ、キャラクターの会話・説明形式に変換します。")

    # キャラクター選択（役割システム）
    selected_chars_for_rewrite = []
    if st.session_state.characters:
        protagonist = st.session_state.characters[0]
        st.markdown(f'**回答者（主人公）**: <span style="color: #00f2ea; font-weight: bold;">{protagonist["name"]}</span> - 常に参加（固定）', unsafe_allow_html=True)

        # 質問者の選択（2人目以降）
        if len(st.session_state.characters) > 1:
            questioner_names = [c["name"] for c in st.session_state.characters[1:]]
            selected_questioner_names = st.multiselect(
                "質問者を選択（複数可 / 選択しない場合は主人公の1人語り）",
                options=questioner_names,
                default=questioner_names,
                key="selected_questioners"
            )
            # 主人公 + 選択された質問者
            selected_chars_for_rewrite = [protagonist] + [c for c in st.session_state.characters[1:] if c["name"] in selected_questioner_names]
        else:
            st.info(f"{protagonist['name']} の1人語り（モノローグ）モードになります。")
            selected_chars_for_rewrite = [protagonist]
    else:
        st.warning("キャラクターが登録されていません。セクション1でキャラクターを登録してください。")

    # ニュアンス選択
    col_p, col_e, col_s = st.columns(3)

    with col_p:
        politeness = st.selectbox(
            "丁寧度",
            options=["指定なし", "casual", "polite", "formal"],
            format_func=lambda x: {
                "指定なし": "指定なし",
                "casual": "カジュアル（タメ口）",
                "polite": "丁寧（です・ます）",
                "formal": "フォーマル（敬語）"
            }.get(x, x),
            key="rewrite_politeness"
        )

    with col_e:
        emotion = st.selectbox(
            "感情",
            options=["指定なし", "gentle", "strong", "cool"],
            format_func=lambda x: {
                "指定なし": "指定なし",
                "gentle": "優しい・穏やか",
                "strong": "力強い・情熱的",
                "cool": "クール・落ち着き"
            }.get(x, x),
            key="rewrite_emotion"
        )

    with col_s:
        style = st.selectbox(
            "話し方",
            options=["指定なし", "explanatory", "conversational", "narrative"],
            format_func=lambda x: {
                "指定なし": "指定なし",
                "explanatory": "説明的（論理的）",
                "conversational": "会話的（語りかけ）",
                "narrative": "物語的（ストーリー）"
            }.get(x, x),
            key="rewrite_style"
        )

    # 自由指示テキスト
    st.markdown("""**自由指示（オプション）** — 例：「もっと煽りを強くして」「50代男性向けに」「失業手当を中心に」「テロップ多めで」「ナミの出番を増やして」「最後にもっと危機感を出して」""")
    custom_instruction = st.text_area(
        "自由指示（オプション）",
        placeholder="AIへの追加指示を入力...",
        height=100,
        key="custom_instruction",
        label_visibility="collapsed"
    )

    # ページ数・パターン数を横並び
    col_pages, col_vars = st.columns(2)
    with col_pages:
        num_pages = st.slider("ページ数", min_value=5, max_value=40, value=15, key="num_pages",
                              help="漫画動画のページ数")
    with col_vars:
        num_variations = st.selectbox(
            "比較パターン数",
            options=[1, 2, 3],
            format_func=lambda x: {1: "1パターン", 2: "2パターン（比較用）", 3: "3パターン（比較用）"}.get(x, str(x)),
            key="num_variations",
            help="異なる切り口でシナリオを同時生成し、比較して選べます"
        )

    # 書き直しボタン
    if st.button("REWRITE", key="rewrite_btn"):
        if not gemini_api_key:
            st.error("API設定でGemini APIキーを入力してください")
        elif not st.session_state.text_editor:
            st.error("テキストが見つかりません")
        elif not selected_chars_for_rewrite:
            st.error("キャラクターを登録してください")
        else:
            # パラメータ準備
            p = politeness if politeness != "指定なし" else None
            e = emotion if emotion != "指定なし" else None
            s = style if style != "指定なし" else None
            ci = custom_instruction if custom_instruction.strip() else None

            # 誘導文テンプレート
            lt = st.session_state.lead_templates.strip() if st.session_state.lead_templates.strip() else None
            # 定型文（末尾付加用）
            ct = st.session_state.closing_text.strip()

            if num_variations == 1:
                # 1パターンの場合は rewrite_scenario を使用
                with st.spinner("AIがシナリオを書き直し中..."):
                    result = gemini.rewrite_scenario(
                        st.session_state.text_editor,
                        politeness=p, emotion=e, style=s,
                        custom_instruction=ci,
                        characters=selected_chars_for_rewrite,
                        lead_templates=lt,
                        num_pages=num_pages
                    )
                    if result:
                        # 定型文を末尾に付加
                        if ct:
                            result = result.rstrip() + "\n" + ct
                        # 前回のウィジェット状態をクリア
                        for k in ["rewritten_editor"]:
                            if k in st.session_state:
                                del st.session_state[k]
                        st.session_state.rewritten_text = result
                        st.session_state.rewrite_variations = None
                        st.session_state.selected_variation = None
                        st.rerun()
                    else:
                        st.error("書き直しに失敗しました")
            else:
                # 複数パターンの場合は generate_variations を使用
                with st.spinner(f"AIが{num_variations}パターン生成中..."):
                    variations = gemini.generate_variations(
                        st.session_state.text_editor,
                        num_variations=num_variations,
                        politeness=p, emotion=e, style=s,
                        custom_instruction=ci,
                        characters=selected_chars_for_rewrite,
                        lead_templates=lt,
                        num_pages=num_pages
                    )
                    if variations:
                        # 各パターンに定型文を末尾付加
                        if ct:
                            variations = [v.rstrip() + "\n" + ct for v in variations]
                        st.session_state.rewrite_variations = variations
                        st.session_state.rewritten_text = None
                        st.session_state.selected_variation = None
                        st.rerun()
                    else:
                        st.error("バリエーション生成に失敗しました")

    # 書き直し結果の表示
    if st.session_state.rewritten_text:
        st.subheader("書き直し結果")
        rewritten_edit = st.text_area(
            "書き直されたテキスト（編集可能）",
            value=st.session_state.rewritten_text,
            height=400,
            key="rewritten_editor"
        )
        st.session_state.rewritten_text = rewritten_edit

        col_apply, col_download, col_clear = st.columns(3)
        with col_apply:
            if st.button("この結果を採用", key="apply_rewrite"):
                st.session_state.adopted_scenario = st.session_state.rewritten_text
                st.session_state.text_editor = st.session_state.rewritten_text
                st.session_state.formatted_text = st.session_state.rewritten_text
                st.session_state.rewritten_text = None
                if "rewritten_editor" in st.session_state:
                    del st.session_state["rewritten_editor"]
                st.rerun()
        with col_download:
            st.download_button(
                label="DOWNLOAD REWRITE",
                data=rewritten_edit,
                file_name=f"{final_filename}_rewrite.txt",
                mime="text/plain",
                key="download_rewrite"
            )
        with col_clear:
            if st.button("結果をクリア", key="clear_rewrite"):
                st.session_state.rewritten_text = None
                if "rewritten_editor" in st.session_state:
                    del st.session_state["rewritten_editor"]
                st.rerun()

    elif st.session_state.rewrite_variations:
        st.subheader("書き直し結果（複数パターン）")

        variations = st.session_state.rewrite_variations
        num_vars = len(variations)

        # 横並びで表示
        cols = st.columns(num_vars)
        for i, (col, var) in enumerate(zip(cols, variations)):
            with col:
                st.markdown(f"**パターン {i + 1}**")
                st.text_area(
                    f"パターン {i + 1}",
                    value=var,
                    height=500,
                    key=f"var_editor_{i}",
                    label_visibility="collapsed"
                )
                if st.button(f"パターン {i + 1} を採用", key=f"select_var_{i}"):
                    selected_var = st.session_state.get(f"var_editor_{i}", var)
                    st.session_state.selected_variation = i
                    st.session_state.adopted_scenario = selected_var
                    st.session_state.rewritten_text = selected_var
                    st.session_state.rewrite_variations = None
                    st.session_state.text_editor = selected_var
                    st.session_state.formatted_text = selected_var
                    st.rerun()
                st.download_button(
                    label=f"DOWNLOAD P{i + 1}",
                    data=var,
                    file_name=f"{final_filename}_pattern{i + 1}.txt",
                    mime="text/plain",
                    key=f"download_var_{i}"
                )

    # 採用済みシナリオのダウンロード（常に表示）
    if st.session_state.adopted_scenario:
        st.markdown("---")
        st.subheader("採用済みシナリオ")
        st.download_button(
            label="DOWNLOAD SCENARIO",
            data=st.session_state.adopted_scenario,
            file_name=f"{final_filename}_scenario.txt",
            mime="text/plain",
            key="download_adopted_scenario"
        )

    # ===========================================
    # セクション6: タイトル・紹介文・ハッシュタグ生成
    # ===========================================
    st.header("6. タイトル・紹介文・ハッシュタグ生成")

    if st.button("GENERATE SNS", key="generate_sns_content_btn"):
        if not gemini_api_key:
            st.error("API設定でGemini APIキーを入力してください")
        elif not st.session_state.text_editor:
            st.error("テキストが見つかりません")
        else:
            progress_bar = st.progress(0)
            progress_bar.progress(30)
            sns_content = gemini.generate_metadata(st.session_state.text_editor)
            progress_bar.progress(90)
            if sns_content:
                st.session_state.generated_sns_content = sns_content
                progress_bar.progress(100)

    if st.session_state.generated_sns_content:
        st.subheader("生成されたコンテンツ（編集可能）")
        if "sns_content_editor" not in st.session_state:
            st.session_state.sns_content_editor = st.session_state.generated_sns_content
        st.text_area("タイトル・紹介文・ハッシュタグ", height=400, key="sns_content_editor")

        # ===========================================
        # セクション7: まとめてダウンロード
        # ===========================================
        st.header("7. まとめてダウンロード")

        # 全テキストをまとめる
        full_parts = []

        # 採用済みシナリオ
        if st.session_state.adopted_scenario:
            full_parts.append("【シナリオ】\n" + st.session_state.adopted_scenario)

        # SNSコンテンツ
        full_parts.append("【SNSコンテンツ】\n" + st.session_state.sns_content_editor)

        full_text = "\n\n" + ("=" * 50) + "\n\n".join(full_parts)

        st.download_button(
            label="DOWNLOAD ALL",
            data=full_text,
            file_name=f"{final_filename}_full.txt",
            mime="text/plain",
            key="download_full_text"
        )

# フッター
st.markdown("---")
st.markdown("Made with Streamlit, Gladia API & Gemini API | **TikTok Scenario Rewriter**")
