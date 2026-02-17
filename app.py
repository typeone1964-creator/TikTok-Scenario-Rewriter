import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from utils.transcription import GladiaAPI
from utils.text_formatter import GeminiFormatter

# 環境変数を読み込み
load_dotenv()

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
    .char-number {
        color: #fe2c55;
        font-weight: bold;
        font-size: 14px;
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
if 'generated_sns_content' not in st.session_state:
    st.session_state.generated_sns_content = None
if 'characters' not in st.session_state:
    st.session_state.characters = []  # 登録済みキャラクターのリスト（最大5人）

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
st.markdown("文字起こし → 整形 → キャラ設定 → **AI書き直し** → SNS生成 → ダウンロード")

# APIクライアントの初期化
gladia = GladiaAPI(gladia_api_key) if gladia_api_key else None
gemini = GeminiFormatter(gemini_api_key) if gemini_api_key else None

# ===========================================
# セクション1: 入力ソース選択
# ===========================================
st.header("1. 入力ソース選択")

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
                    progress_bar.progress(50)

                    # テキスト整形：改行ごとに句読点を追加
                    lines = raw_text.strip().split('\n')
                    formatted_lines = []
                    punctuation = ('。', '、', '！', '？', '!', '?', '．', '，')

                    for i, line in enumerate(lines):
                        line = line.strip()
                        if not line:
                            continue
                        # 既に句読点で終わっている場合はそのまま
                        if line.endswith(punctuation):
                            formatted_lines.append(line)
                        else:
                            # 最後の行は「。」、それ以外は「、」
                            if i == len(lines) - 1:
                                formatted_lines.append(line + '。')
                            else:
                                formatted_lines.append(line + '、')

                    formatted_text = '\n'.join(formatted_lines)
                    st.session_state.formatted_text = formatted_text
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
        "テキストを貼り付けてください（自動整形されます）",
        height=250,
        placeholder="ここにテキストを貼り付け...\n\n例：\nこれもちょっとした誤解で\n落とし穴がいっぱいあるのです",
        key="direct_text_input"
    )

    if st.button("START", key="direct_text_btn"):
        if direct_text.strip():
            progress_bar = st.progress(0)
            progress_bar.progress(20)

            # テキスト整形：改行ごとに句読点を追加
            lines = direct_text.strip().split('\n')
            formatted_lines = []
            punctuation = ('。', '、', '！', '？', '!', '?', '．', '，')

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                if line.endswith(punctuation):
                    formatted_lines.append(line)
                else:
                    if i == len(lines) - 1:
                        formatted_lines.append(line + '。')
                    else:
                        formatted_lines.append(line + '、')

            formatted_text = '\n'.join(formatted_lines)
            st.session_state.formatted_text = formatted_text
            st.session_state.transcribed_text = direct_text
            progress_bar.progress(50)

            # ファイル名生成
            if gemini:
                # Gemini APIでファイル名を生成
                filename = gemini.generate_filename(formatted_text)
                st.session_state.filename = filename or "output"
            else:
                # テキストの最初の行から自動生成（句読点除去、最大20文字）
                first_line = formatted_lines[0] if formatted_lines else "output"
                clean_name = first_line.replace('、', '').replace('。', '').replace('！', '').replace('？', '')
                st.session_state.filename = clean_name[:20] if len(clean_name) > 20 else clean_name

            progress_bar.progress(100)
            st.success("Complete!")
        else:
            st.error("テキストを入力してください")

# ===========================================
# セクション2: 整形済みテキスト表示・編集
# ===========================================
if st.session_state.formatted_text:
    st.header("2. テキスト編集")

    if "text_editor" not in st.session_state:
        st.session_state.text_editor = st.session_state.formatted_text

    if "filename" not in st.session_state or not st.session_state.filename:
        st.session_state.filename = "output"

    # テキストダウンロード用のフォーマット関数
    def format_text_for_download(text: str, target_length: int = 14) -> str:
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            chunks = []
            current_chunk = ""
            for char in line:
                if char in ['。', '、']:
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = ""
                else:
                    current_chunk += char
            if current_chunk:
                chunks.append(current_chunk)

            current_line = ""
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue
                if not current_line:
                    current_line = chunk
                    continue
                combined_len = len(current_line + chunk)
                if combined_len > target_length + 4:
                    new_lines.append(current_line)
                    current_line = chunk
                elif abs(target_length - combined_len) <= abs(target_length - len(current_line)):
                    current_line += chunk
                else:
                    new_lines.append(current_line)
                    current_line = chunk
            if current_line:
                new_lines.append(current_line)
        return '\n'.join(new_lines)

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

    formatted_main_text = format_text_for_download(current_text)
    st.download_button(
        label="DOWNLOAD TEXT",
        data=formatted_main_text,
        file_name=f"{st.session_state.filename}.txt",
        mime="text/plain",
        key="download_text"
    )

    # ファイル名入力
    final_filename = st.text_input("ファイル名（編集可能）", value=st.session_state.filename, key="filename_input")

    # ===========================================
    # セクション3: キャラクター設定
    # ===========================================
    st.header("3. キャラクター設定")
    st.markdown("最大5人のキャラクターを登録できます。書き直し時に選択したキャラクターがシナリオ内でセリフを話します。")

    # --- 登録済みキャラクター表示 ---
    if st.session_state.characters:
        st.subheader(f"登録済みキャラクター（{len(st.session_state.characters)}人）")
        for i, char in enumerate(st.session_state.characters):
            card_html = f"""<div class="char-card">
<span class="char-number">#{i + 1}</span>
<strong style="color: #fe2c55; font-size: 18px; margin-left: 8px;">{char['name']}</strong>
<span style="color: #888; margin-left: 12px;">{char['gender']} / {char['age']}</span>
<br><span style="color: #aaa;">見た目:</span> {char['appearance']}
　<span style="color: #aaa;">雰囲気:</span> {char['atmosphere']}
<br><span style="color: #aaa;">背景:</span> {char['background']}
　<span style="color: #aaa;">口調:</span> {char['tone']}
</div>"""
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"削除: {char['name']}", key=f"del_char_{i}"):
                st.session_state.characters.pop(i)
                st.rerun()

    # --- 新規キャラクター登録フォーム ---
    if len(st.session_state.characters) < 5:
        st.subheader("キャラクター登録")
        col_n, col_a, col_g = st.columns([2, 1, 1])
        with col_n:
            new_name = st.text_input("名前", placeholder="例：太郎", key="new_char_name")
        with col_a:
            new_age = st.selectbox("年代", ["10代", "20代", "30代", "40代", "50代", "60代以上"], index=1, key="new_char_age")
        with col_g:
            new_gender = st.selectbox("性別", ["男性", "女性", "その他"], key="new_char_gender")

        col_ap, col_at = st.columns(2)
        with col_ap:
            new_appearance = st.text_input("見た目", placeholder="例：短髪、メガネ、スーツ姿", key="new_char_appearance")
        with col_at:
            new_atmosphere = st.text_input("雰囲気", placeholder="例：明るく元気、頼れる兄貴", key="new_char_atmosphere")

        col_bg, col_tn = st.columns(2)
        with col_bg:
            new_background = st.text_input("背景", placeholder="例：IT企業の新入社員、趣味はゲーム", key="new_char_background")
        with col_tn:
            new_tone = st.text_input("口調", placeholder="例：タメ口、テンション高め、語尾に「っす」", key="new_char_tone")

        if st.button("REGISTER", key="register_char_btn"):
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
                st.success(f"「{new_name.strip()}」を登録しました!（{len(st.session_state.characters)}/5人）")
                st.rerun()
    else:
        st.info("キャラクター登録の上限（5人）に達しています。追加するには既存のキャラクターを削除してください。")

    # ===========================================
    # セクション4: AI書き直し（メイン機能）
    # ===========================================
    st.header("4. AI書き直し")

    st.markdown("シナリオ全体を書き直します。テーマは維持しつつ、選択したキャラクターの会話・説明形式に変換します。")

    # キャラクター選択（登録済みキャラから複数選択）
    selected_char_names = []
    if st.session_state.characters:
        char_name_list = [c["name"] for c in st.session_state.characters]
        selected_char_names = st.multiselect(
            "使用するキャラクターを選択（複数可）",
            options=char_name_list,
            default=char_name_list,
            key="selected_characters"
        )
    else:
        st.warning("キャラクターが登録されていません。上のセクションでキャラクターを登録してください。")

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
    custom_instruction = st.text_area(
        "自由指示（オプション）",
        placeholder="例：もっと煽り気味にして / 冒頭で問いかけて / 数字を入れて具体的に / Z世代向けに",
        height=80,
        key="custom_instruction"
    )

    # パターン数選択
    num_variations = st.slider("生成パターン数", min_value=1, max_value=3, value=1, key="num_variations")

    # 書き直しボタン
    if st.button("REWRITE", key="rewrite_btn"):
        if not gemini_api_key:
            st.error("API設定でGemini APIキーを入力してください")
        elif not st.session_state.text_editor:
            st.error("テキストが見つかりません")
        elif not selected_char_names:
            st.error("使用するキャラクターを1人以上選択してください")
        else:
            # パラメータ準備
            p = politeness if politeness != "指定なし" else None
            e = emotion if emotion != "指定なし" else None
            s = style if style != "指定なし" else None
            ci = custom_instruction if custom_instruction.strip() else None

            # 選択されたキャラクター情報を構築
            selected_chars = [c for c in st.session_state.characters if c["name"] in selected_char_names]

            if num_variations == 1:
                # 1パターンの場合は rewrite_scenario を使用
                with st.spinner("AIがシナリオを書き直し中..."):
                    result = gemini.rewrite_scenario(
                        st.session_state.text_editor,
                        politeness=p, emotion=e, style=s,
                        custom_instruction=ci,
                        characters=selected_chars
                    )
                    if result:
                        st.session_state.rewritten_text = result
                        st.session_state.rewrite_variations = None
                        st.session_state.selected_variation = None
                        st.success("書き直し完了!")
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
                        characters=selected_chars
                    )
                    if variations:
                        st.session_state.rewrite_variations = variations
                        st.session_state.rewritten_text = None
                        st.session_state.selected_variation = None
                        st.success(f"{len(variations)}パターン生成完了!")
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

        col_apply, col_download = st.columns(2)
        with col_apply:
            if st.button("この結果を採用", key="apply_rewrite"):
                st.session_state.text_editor = st.session_state.rewritten_text
                st.session_state.formatted_text = st.session_state.rewritten_text
                st.success("採用しました! テキスト編集欄に反映されます。")
                st.rerun()
        with col_download:
            st.download_button(
                label="DOWNLOAD REWRITE",
                data=format_text_for_download(rewritten_edit),
                file_name=f"{final_filename}_rewrite.txt",
                mime="text/plain",
                key="download_rewrite"
            )

    elif st.session_state.rewrite_variations:
        st.subheader("書き直し結果（複数パターン）")

        variations = st.session_state.rewrite_variations

        for i, var in enumerate(variations):
            st.markdown(f'<div class="variation-card"><div class="variation-label">パターン {i + 1}</div><div class="variation-text">{var}</div></div>', unsafe_allow_html=True)

            col_select, col_dl = st.columns([1, 1])
            with col_select:
                if st.button(f"パターン {i + 1} を採用", key=f"select_var_{i}"):
                    st.session_state.selected_variation = i
                    st.session_state.rewritten_text = var
                    st.session_state.rewrite_variations = None
                    st.session_state.text_editor = var
                    st.session_state.formatted_text = var
                    st.success(f"パターン {i + 1} を採用しました!")
                    st.rerun()
            with col_dl:
                st.download_button(
                    label=f"DOWNLOAD P{i + 1}",
                    data=format_text_for_download(var),
                    file_name=f"{final_filename}_pattern{i + 1}.txt",
                    mime="text/plain",
                    key=f"download_var_{i}"
                )

    # ===========================================
    # セクション5: タイトル・紹介文・ハッシュタグ生成
    # ===========================================
    st.header("5. タイトル・紹介文・ハッシュタグ生成")

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
        # セクション6: まとめてダウンロード
        # ===========================================
        st.header("6. まとめてダウンロード")

        # 全テキストをまとめる
        full_text = "【整形テキスト】\n" + formatted_main_text

        # 書き直しテキストがあれば追加
        if st.session_state.rewritten_text:
            full_text += "\n\n【書き直しテキスト】\n" + st.session_state.rewritten_text

        full_text += "\n\n" + st.session_state.sns_content_editor

        st.download_button(
            label="DOWNLOAD ALL TEXT",
            data=full_text,
            file_name=f"{final_filename}_full.txt",
            mime="text/plain",
            key="download_full_text"
        )

# フッター
st.markdown("---")
st.markdown("Made with Streamlit, Gladia API & Gemini API | **TikTok Scenario Rewriter**")
