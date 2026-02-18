import google.generativeai as genai
from typing import Optional, List


class GeminiFormatter:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # gemini-2.0-flash または gemini-1.5-flash を使用
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except:
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def format_text(self, text: str) -> Optional[str]:
        """
        テキストを読みやすく整形（句読点と改行の調整）
        重要: 元の発言内容は1文字も変えず、句読点と改行のみを調整
        """
        prompt = f"""あなたは厳格な校正者です。以下のテキストを整形してください。

【手順】
1. まず、テキストに句読点（句点「。」と読点「、」）がない場合は、文の意味に合った適切な位置に句読点を付けてください
2. 次に、句点（。）の位置でのみ改行してください

【絶対厳守のルール】
1. 元のテキストの単語・表現は変更しないでください（句読点の追加のみ許可）
2. 句読点がない入力テキストには、適切な位置に句点（。）と読点（、）を追加してください
3. 改行は句点（。）の後でのみ行ってください
4. 読点（、）の位置では絶対に改行しないでください
5. 1つの文は句点（。）まで1行にまとめてください
6. 要約や言い換えは禁止です

【良い例】
職場の嫌な奴は、こう扱えば大丈夫。
職場に嫌いな人は、一人はいますよね。
そんな人の対処法を、5つ紹介します。

【悪い例（絶対NG）】
職場の嫌な奴はこう扱えば大丈夫職場に嫌いな人は ← 句読点がない
職場の嫌な奴は、 ← 句点でないのに改行している

【入力テキスト】
{text}

【出力】
整形後のテキストのみを出力してください。説明や追加コメントは不要です。
"""

        try:
            print(f"Gemini APIリクエスト中... (テキスト長: {len(text)}文字)")
            response = self.model.generate_content(prompt)
            print(f"Gemini APIレスポンス受信完了")

            # レスポンスの内容を確認
            if hasattr(response, 'text'):
                result = response.text.strip()
                print(f"整形結果: {len(result)}文字")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"テキスト整形エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_filename(self, formatted_text: str) -> Optional[str]:
        """
        整形済みテキストの1〜3行目から、20文字以内の適切なファイル名を生成
        """
        lines = formatted_text.split('\n')
        first_lines = '\n'.join(lines[:3])

        prompt = f"""以下のテキストから、適切なファイル名を生成してください。

【ルール】
1. 20文字以内
2. 内容を端的に表すタイトル
3. ファイル名として使える文字のみ（記号は使用しない）
4. 日本語でOK

【テキスト】
{first_lines}

【出力】
ファイル名のみを出力してください。説明や追加コメントは不要です。
拡張子（.txtや.wav）は付けないでください。
"""

        try:
            print(f"Gemini APIでファイル名生成中...")
            response = self.model.generate_content(prompt)
            print(f"ファイル名生成レスポンス受信完了")

            if hasattr(response, 'text'):
                filename = response.text.strip()
                # 不適切な文字を削除
                filename = filename.replace('/', '').replace('\\', '').replace(':', '').replace('*', '')
                filename = filename.replace('?', '').replace('"', '').replace('<', '').replace('>', '')
                filename = filename.replace('|', '').replace('\n', '').replace('\r', '')
                result = filename[:20]  # 20文字制限
                print(f"生成されたファイル名: {result}")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"ファイル名生成エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_metadata(self, text: str) -> Optional[str]:
        """
        テキストからタイトル案、紹介文案、ハッシュタグを生成

        Returns:
            フォーマット済みのメタデータ文字列
        """
        prompt = f"""以下のテキストから、TikTok/SNS投稿用のタイトル、紹介文、ハッシュタグを生成してください。

【ルール】
1. タイトル案：3つ提案（各30字以内、【見出し】本文 の形式）
2. 紹介文案：3つ提案（各100字前後）
3. ハッシュタグ：5つ提案

【入力テキスト】
{text}

【出力フォーマット（このフォーマット厳守）】
【タイトル案（『【見出し】本文』／各30字以内）】

1）……

2）……

3）……

【紹介文案（各100字前後）】

1）……

2）……

3）……

【ハッシュタグ（5つ）】

#〇〇 #〇〇 #〇〇 #〇〇 #〇〇

上記のフォーマットに従って、テキストの内容に基づいた魅力的なメタデータを生成してください。
説明や追加コメントは不要です。フォーマット通りに出力してください。
"""

        try:
            print(f"Gemini APIでメタデータ生成中... (テキスト長: {len(text)}文字)")
            response = self.model.generate_content(prompt)
            print(f"メタデータ生成レスポンス受信完了")

            if hasattr(response, 'text'):
                result = response.text.strip()
                print(f"生成されたメタデータ: {len(result)}文字")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"メタデータ生成エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def rephrase_text(self, text: str, politeness: str = None, emotion: str = None, style: str = None) -> Optional[str]:
        """
        テキストのニュアンスを変更

        Args:
            text: 整形済みテキスト
            politeness: 丁寧度（casual/polite/formal）
            emotion: 感情（gentle/strong/cool）
            style: 話し方（explanatory/conversational/narrative）

        Returns:
            ニュアンス変更後のテキスト
        """
        # ニュアンス指示を構築
        nuance_instructions = []

        if politeness:
            politeness_map = {
                "casual": "カジュアルで親しみやすい口調（タメ口、くだけた表現）",
                "polite": "丁寧で礼儀正しい口調（です・ます調）",
                "formal": "フォーマルで格式高い口調（敬語、ビジネス調）"
            }
            nuance_instructions.append(f"【丁寧度】{politeness_map.get(politeness, '')}")

        if emotion:
            emotion_map = {
                "gentle": "優しく穏やかな雰囲気（柔らかい表現、共感的）",
                "strong": "力強く情熱的な雰囲気（断定的、エネルギッシュ）",
                "cool": "クールで落ち着いた雰囲気（淡々と、客観的）"
            }
            nuance_instructions.append(f"【感情】{emotion_map.get(emotion, '')}")

        if style:
            style_map = {
                "explanatory": "説明的な話し方（論理的、順序立てて）",
                "conversational": "会話的な話し方（語りかける、問いかける）",
                "narrative": "物語的な話し方（ストーリー調、引き込む）"
            }
            nuance_instructions.append(f"【話し方】{style_map.get(style, '')}")

        nuance_text = "\n".join(nuance_instructions)

        prompt = f"""あなたは文章のニュアンス調整の専門家です。以下のテキストを指定されたニュアンスに変更してください。

{nuance_text}

【絶対厳守のルール】
1. 内容・意味は変えずに、ニュアンス（トーン・雰囲気）だけを変更してください
2. 改行は句点（。）の位置でのみ行ってください
3. 読点（、）の位置では改行しないでください
4. 1つの文は句点（。）まで1行にまとめてください

【入力テキスト】
{text}

【出力】
ニュアンス変更後のテキストのみを出力してください。説明や追加コメントは不要です。
"""

        try:
            nuance_desc = f"丁寧度={politeness}, 感情={emotion}, 話し方={style}"
            print(f"Gemini APIでニュアンス変更中... ({nuance_desc})")
            response = self.model.generate_content(prompt)
            print(f"ニュアンス変更レスポンス受信完了")

            if hasattr(response, 'text'):
                result = response.text.strip()
                print(f"ニュアンス変更結果: {len(result)}文字")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"ニュアンス変更エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _build_character_prompt(self, characters: List[dict] = None) -> str:
        """キャラクター情報からプロンプト用のセクションを構築（役割システム付き）"""
        if not characters:
            return ""

        protagonist = characters[0]  # 最初に登録されたキャラ = 回答者（主人公）
        questioners = characters[1:] if len(characters) > 1 else []

        # 主人公のプロフィール構築
        def build_profile(c):
            parts = [f"名前: {c['name']}"]
            for field, label in [('age', '年代'), ('gender', '性別'), ('appearance', '見た目'),
                                 ('atmosphere', '雰囲気'), ('background', '背景'), ('tone', '口調')]:
                if c.get(field):
                    parts.append(f"{label}: {c[field]}")
            return "／".join(parts)

        protagonist_line = f"- {build_profile(protagonist)} 【回答者・主人公】"
        questioner_lines = [f"- {build_profile(c)} 【質問者】" for c in questioners]

        char_list = protagonist_line
        if questioner_lines:
            char_list += "\n" + "\n".join(questioner_lines)

        all_names = "、".join(c['name'] for c in characters)

        # 役割ルール（ソロ/マルチで分岐）
        if len(characters) == 1:
            role_rules = f"""
【キャラクターの役割】
- {protagonist['name']} が1人で語るモノローグ形式です。
- {protagonist['name']} の口調・キャラ設定を反映した語りにしてください。"""
        else:
            q_names = "、".join(c['name'] for c in questioners)
            role_rules = f"""
【キャラクターの役割】
- {protagonist['name']}：回答者・主人公。知識を持っている側。質問に答えたり、情報を説明する役割。
- {q_names}：質問者。知らない側。疑問を投げかけたり、驚いたり、興味を示す役割。
- 質問者が疑問や関心を投げかけ → 主人公が答える、という掛け合いで進行してください。"""

        return f"""
【登場キャラクター】
{char_list}
{role_rules}

【漫画動画シナリオのルール】
1. これは漫画動画のシナリオです。各ページにト書き・テロップ・セリフを組み合わせて構成します
2. キャラクターのセリフは「【キャラ名】セリフ」の形式で書いてください
3. テロップ（画面に表示する強調テキスト）は「【テロップ】テキスト」の形式で書いてください
4. ト書き（シーンの状況・キャラの表情や動き）は「（ト書き: 〇〇）」の形式で各ページの冒頭に書いてください
5. テロップは特に重要なことを伝えるときに使います。全ページに入れる必要はありません
6. **テロップとセリフの内容は絶対に被らないでください**。同じことをテロップとセリフ両方で言わない
7. 各キャラクターのプロフィール（年代・性別・見た目・雰囲気・背景・口調）を忠実に反映してください
8. 特に「口調」の設定は最重要です。キャラごとに話し方を明確に区別してください
9. 使用キャラクター: {all_names}

【ページの種類】
- テロップのみのページ: 重要な情報や煽りを画面テキストだけで見せる
- セリフのみのページ: キャラクターの会話・掛け合いで進行する
- テロップ＋セリフのページ: 重要ポイントをテロップで示しつつ、キャラがリアクションする（内容は被らせない）

【良い例】""" + (f"""
--- P1 ---
（ト書き: 暗い背景に衝撃的なテキストが表示される）
【テロップ】知らないと絶対損する、退職前にやるべきこと。

--- P2 ---
（ト書き: {protagonist['name']}が真剣な表情でこちらを見ている）
【{protagonist['name']}】これ知ってる？
【{protagonist['name']}】実はこれヤバくて、

--- P3 ---
（ト書き: {questioners[0]['name']}が驚いた表情）
【{questioners[0]['name']}】え、マジ？
【{questioners[0]['name']}】全然知らなかった。

--- P4 ---
（ト書き: {protagonist['name']}が指を立てて説明する）
【テロップ】最大240日分の失業手当が受け取れる。
【{protagonist['name']}】しかも条件を満たせば、すぐに申請できるんだよ。
""" if questioners else f"""
--- P1 ---
（ト書き: 暗い背景に衝撃的なテキストが表示される）
【テロップ】知らないと絶対損する、退職前にやるべきこと。

--- P2 ---
（ト書き: {protagonist['name']}が真剣な表情でこちらを見ている）
【{protagonist['name']}】これ知ってる？
【{protagonist['name']}】実はこれヤバくて、

--- P3 ---
（ト書き: {protagonist['name']}が指を立てて説明する）
【テロップ】最大240日分の失業手当が受け取れる。
【{protagonist['name']}】しかも条件を満たせば、すぐに申請できるんだよ。
""")

    def rewrite_scenario(self, text: str, politeness: str = None, emotion: str = None,
                         style: str = None, custom_instruction: str = None,
                         characters: List[dict] = None,
                         lead_templates: str = None,
                         num_pages: int = 15) -> Optional[str]:
        """
        漫画動画シナリオの書き直し（ページ構成・ト書き付き）

        Args:
            text: 整形済みテキスト
            politeness: 丁寧度（casual/polite/formal）
            emotion: 感情（gentle/strong/cool）
            style: 話し方（explanatory/conversational/narrative）
            custom_instruction: 自由指示テキスト
            characters: キャラクター情報のリスト（[0]=回答者、[1:]= 質問者）
            lead_templates: 誘導文テンプレート
            num_pages: ページ数

        Returns:
            書き直し後のテキスト
        """
        # ニュアンス指示を構築
        nuance_instructions = []

        if politeness:
            politeness_map = {
                "casual": "カジュアルで親しみやすい口調（タメ口、くだけた表現）",
                "polite": "丁寧で礼儀正しい口調（です・ます調）",
                "formal": "フォーマルで格式高い口調（敬語、ビジネス調）"
            }
            nuance_instructions.append(f"【丁寧度】{politeness_map.get(politeness, '')}")

        if emotion:
            emotion_map = {
                "gentle": "優しく穏やかな雰囲気（柔らかい表現、共感的）",
                "strong": "力強く情熱的な雰囲気（断定的、エネルギッシュ）",
                "cool": "クールで落ち着いた雰囲気（淡々と、客観的）"
            }
            nuance_instructions.append(f"【感情】{emotion_map.get(emotion, '')}")

        if style:
            style_map = {
                "explanatory": "説明的な話し方（論理的、順序立てて）",
                "conversational": "会話的な話し方（語りかける、問いかける）",
                "narrative": "物語的な話し方（ストーリー調、引き込む）"
            }
            nuance_instructions.append(f"【話し方】{style_map.get(style, '')}")

        nuance_text = "\n".join(nuance_instructions) if nuance_instructions else ""

        # カスタム指示
        custom_section = ""
        if custom_instruction and custom_instruction.strip():
            custom_section = f"\n【追加指示】\n{custom_instruction.strip()}\n"

        # キャラクター指示
        character_section = self._build_character_prompt(characters)

        # 誘導文テンプレート
        lead_section = ""
        if lead_templates and lead_templates.strip():
            lead_section = f"""
【誘導文テンプレート（重要）】
以下はシナリオの終盤〜締めに自然に組み込む誘導表現の例です。
そのままコピーせず、シナリオの流れやキャラクターの口調に合わせてアレンジしてください。
シナリオの最後が「制度の紹介 → 行動を促す」流れになるように構成してください。
定型文（フォローやリンク誘導）はこの後に別途付加されるので、シナリオ側では書かないでください。

{lead_templates.strip()}
"""

        prompt = f"""あなたはTikTok漫画動画のシナリオライターです。以下のテキストを{num_pages}ページの漫画動画シナリオに書き直してください。

{nuance_text}
{custom_section}
{character_section}
{lead_section}

【書き直しのルール】
1. 元のテキストのテーマ・主旨は維持してください
2. ただし、表現の変更、内容の追加・削除・順序変更は自由に行ってOKです
3. TikTok漫画動画として視聴者を引き込む構成にしてください
4. **必ず{num_pages}ページで構成してください**
5. **元テキストの衝撃的・インパクトのある表現はできるだけそのまま使ってください**
   - 具体的な数字を含む煽り（「200万円以上得する情報」「99%が知らない」等）
   - 強烈なワード（「ゼニゲバ」「大暴露」「ヤバい」等）
   - 感情を揺さぶるフレーズ（「一切教えてくれません」「全額消えます」等）
   - これらは書き直し後も原文のまま、またはほぼそのまま残してください

【シナリオの構成（この順番で必ず書いてください）】
1. **P1のみ: 冒頭テロップ（問題提起・煽り）**: 視聴者の危機感や興味を煽るテロップのみのページ
   - 元テキストにインパクトのある冒頭表現があればそのまま活用する
   - **ここでは詳しい情報や解決策はまだ出さない**
   - **テロップのみのページはP1だけ**。P2以降はセリフ中心で進行する
2. **P2以降はセリフ中心で進行**: 煽り・保存促進・本題・誘導・締め、全てキャラのセリフで展開する
   - 保存・いいね促進もキャラのセリフとして自然に言わせる
   - 挨拶・導入は不要。いきなり本題に入る
   - 元テキストの衝撃的な表現はキャラのセリフ内でも積極的に使う
   - **テロップはセリフの代わりではなく、見出し・キーワード・数字の強調にだけ使う**
   - テロップの良い使い方：項目の見出し（「1 失業手当」）、金額（「最大240日分」）
   - テロップとセリフで同じことを言わない。テロップ＝見出しや要点、セリフ＝説明や感情
3. **誘導文**: シナリオ終盤に、誘導文テンプレートを参考に行動喚起をキャラのセリフで組み込む
4. **締め**: 次のアクションにつなげるセリフで終わる

【トーンのルール】
- 冒頭テロップ：興味と危機感を煽るだけ。詳細はまだ出さない
- キャラ会話（保存促進の後）：ここで初めて詳しい情報と解決策をセリフで出す
- 元テキストのパンチある表現（「国はゼニゲバ」「200万円以上得する」「合法の制度」等）はそのまま活かす
- NGな表現：挨拶、導入文（「今回は〜をご紹介」）、メタ発言（「私が解説します」「大丈夫！」「メモして」）

【フォーマットルール（厳守）】
1. 各ページは「--- P1 ---」「--- P2 ---」...の区切りで始めてください
2. 各ページの最初にト書きを書いてください：「（ト書き: シーンの状況、キャラの表情・動きの描写）」
3. セリフは「【キャラ名】セリフ」の形式
4. テロップは「【テロップ】テキスト」の形式
5. **テロップとセリフで同じ内容を言わないでください**
6. 改行は句点（。）の位置でのみ行ってください
7. 読点（、）の位置では改行しないでください

【テロップの使い分け】
- P1のみ: テロップだけのページ（タイトル・煽り）
- P2以降: セリフが中心。テロップや背景文字は重要ポイント・見出し・数字の強調に使う
  - 良い例：【テロップ】1 失業手当 → 【ナミ】これはもう定番よね。
  - 良い例：（ト書き: 画面に「最大240日分」の文字）→ 【ナミ】条件を満たせばすぐ申請できるよ。
  - NG例：【テロップ】失業手当は65歳で受け取れなくなる → 【ナミ】失業手当は65歳で…（内容被り）

【参考シナリオ構成例】
--- P1 ---
（ト書き: 暗い背景に赤い文字がドンと表示される）
【テロップ】マジかよ…退職でもらえる給付金、知らなきゃ損する11選！

--- P2 ---
（ト書き: ナミが険しい表情で腕組みをしている）
【ナミ】国はゼニゲバだから、200万円以上得する情報なんて絶対教えてくれないんだよ。
【ナミ】自分がどれに当てはまるか、マジでちゃんと聞いて！

--- P3 ---
（ト書き: ナミがこちらに手を差し出す。周りに「いいね」「保存」のアイコン）
【ナミ】二度とおすすめに出てこないかもだから、今のうちにいいねと保存、お願いね！

--- P4 ---
（ト書き: ナミが指を1本立てて、キリッとした表情。画面に「1 失業手当」の文字）
【テロップ】1 失業手当
【ナミ】これはもう定番よね。
【ナミ】あなたの給料の約6割がもらえるの。

--- P5 ---
（ト書き: ナミが驚いた表情で身を乗り出す）
【ナミ】でもね、申請した人も失業保険の延長ができるって知ってた？
【ナミ】実はコレ、マジで知らない人多いんだよね。

--- P6 ---
（ト書き: ナミが指を2本立てる。画面に「2 傷病手当金」の文字）
【テロップ】2 傷病手当金
【ナミ】これ、最大18ヶ月も受け取れるの。
【ナミ】一番受け取りやすい制度だから、絶対チェックして。

【入力テキスト】
{text}

【出力】
{num_pages}ページの漫画動画シナリオのみを出力してください。説明や追加コメントは不要です。
"""

        try:
            desc_parts = []
            if politeness:
                desc_parts.append(f"丁寧度={politeness}")
            if emotion:
                desc_parts.append(f"感情={emotion}")
            if style:
                desc_parts.append(f"話し方={style}")
            if characters:
                desc_parts.append(f"キャラ={','.join(c['name'] for c in characters)}")
            if lead_templates:
                desc_parts.append("誘導文あり")
            if custom_instruction:
                desc_parts.append(f"指示={custom_instruction[:20]}")
            desc = ", ".join(desc_parts) if desc_parts else "デフォルト"
            print(f"Gemini APIでシナリオ書き直し中... ({desc})")
            response = self.model.generate_content(prompt)
            print(f"シナリオ書き直しレスポンス受信完了")

            if hasattr(response, 'text'):
                result = response.text.strip()
                print(f"シナリオ書き直し結果: {len(result)}文字")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"シナリオ書き直しエラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_variations(self, text: str, num_variations: int = 3,
                            politeness: str = None, emotion: str = None,
                            style: str = None, custom_instruction: str = None,
                            characters: List[dict] = None,
                            lead_templates: str = None,
                            num_pages: int = 15) -> Optional[List[str]]:
        """
        複数パターンの漫画動画シナリオを一括生成

        Args:
            text: 整形済みテキスト
            num_variations: 生成パターン数（1〜3）
            politeness: 丁寧度
            emotion: 感情
            style: 話し方
            custom_instruction: 自由指示テキスト
            characters: キャラクター情報のリスト（[0]=回答者、[1:]=質問者）
            lead_templates: 誘導文テンプレート
            num_pages: ページ数

        Returns:
            バリエーションのリスト
        """
        num_variations = max(1, min(3, num_variations))

        # ニュアンス指示を構築
        nuance_instructions = []

        if politeness:
            politeness_map = {
                "casual": "カジュアルで親しみやすい口調（タメ口、くだけた表現）",
                "polite": "丁寧で礼儀正しい口調（です・ます調）",
                "formal": "フォーマルで格式高い口調（敬語、ビジネス調）"
            }
            nuance_instructions.append(f"【丁寧度】{politeness_map.get(politeness, '')}")

        if emotion:
            emotion_map = {
                "gentle": "優しく穏やかな雰囲気（柔らかい表現、共感的）",
                "strong": "力強く情熱的な雰囲気（断定的、エネルギッシュ）",
                "cool": "クールで落ち着いた雰囲気（淡々と、客観的）"
            }
            nuance_instructions.append(f"【感情】{emotion_map.get(emotion, '')}")

        if style:
            style_map = {
                "explanatory": "説明的な話し方（論理的、順序立てて）",
                "conversational": "会話的な話し方（語りかける、問いかける）",
                "narrative": "物語的な話し方（ストーリー調、引き込む）"
            }
            nuance_instructions.append(f"【話し方】{style_map.get(style, '')}")

        nuance_text = "\n".join(nuance_instructions) if nuance_instructions else ""

        # カスタム指示
        custom_section = ""
        if custom_instruction and custom_instruction.strip():
            custom_section = f"\n【追加指示】\n{custom_instruction.strip()}\n"

        # キャラクター指示
        character_section = self._build_character_prompt(characters)

        # 誘導文テンプレート
        lead_section = ""
        if lead_templates and lead_templates.strip():
            lead_section = f"""
【誘導文テンプレート（重要）】
以下はシナリオの終盤〜締めに自然に組み込む誘導表現の例です。
そのままコピーせず、シナリオの流れやキャラクターの口調に合わせてアレンジしてください。
各パターンの最後が「制度の紹介 → 行動を促す」流れになるように構成してください。
定型文（フォローやリンク誘導）はこの後に別途付加されるので、シナリオ側では書かないでください。

{lead_templates.strip()}
"""

        # 主人公名を取得（良い例で使用）
        protagonist_name = characters[0]['name'] if characters else "太郎"
        questioner_name = characters[1]['name'] if characters and len(characters) > 1 else "花子"

        prompt = f"""あなたはTikTok漫画動画のシナリオライターです。以下のテキストを{num_variations}パターン、各{num_pages}ページの漫画動画シナリオに書き直してください。

{nuance_text}
{custom_section}
{character_section}
{lead_section}

【書き直しのルール】
1. 元のテキストのテーマ・主旨は維持してください
2. **各パターンは異なるアプローチ・切り口・トーンで書いてください**
   - 切り口の変え方の例：冒頭の煽り方、情報の出し順、キャラの感情表現、テンポ感
   - トーンの変え方の例：パターン1は力強く煽る、パターン2は優しく寄り添う、パターン3はクールに淡々と
3. TikTok漫画動画として視聴者を引き込む構成にしてください
4. **各パターン必ず{num_pages}ページで構成してください**
5. **元テキストの衝撃的・インパクトのある表現はできるだけそのまま使ってください**
   - 具体的な数字を含む煽り（「200万円以上得する情報」「99%が知らない」等）
   - 強烈なワード（「ゼニゲバ」「大暴露」「ヤバい」等）
   - 感情を揺さぶるフレーズ（「一切教えてくれません」「全額消えます」等）
   - これらは書き直し後も原文のまま、またはほぼそのまま残してください

【各パターンの構成（この順番で必ず書いてください）】
1. **P1のみ: 冒頭テロップ（問題提起・煽り）**: テロップのみのページ
   - 元テキストにインパクトのある冒頭表現があればそのまま活用する
   - **ここでは詳しい情報や解決策はまだ出さない**
   - **テロップのみのページはP1だけ**
2. **P2以降はセリフ中心で進行**: 煽り・保存促進・本題・誘導・締め、全てキャラのセリフで展開する
   - 保存・いいね促進もキャラのセリフとして自然に言わせる（パターンごとに異なる表現）
   - 挨拶・導入は不要。いきなり本題に入る
   - 元テキストの衝撃的な表現はキャラのセリフ内でも積極的に使う
   - **テロップはセリフの代わりではなく、見出し・キーワード・数字の強調にだけ使う**
   - テロップとセリフで同じことを言わない
3. **誘導文**: シナリオ終盤に、誘導文テンプレートを参考に行動喚起をキャラのセリフで組み込む
4. **締め**: 次のアクションにつなげるセリフで終わる

【トーンのルール】
- P1テロップ：興味と危機感を煽るだけ。詳細はまだ出さない
- P2以降のセリフ：ここで初めて詳しい情報と解決策を出す
- 元テキストのパンチある表現（「国はゼニゲバ」「200万円以上得する」「合法の制度」等）はそのまま活かす
- NGな表現：挨拶、導入文（「今回は〜をご紹介」）、メタ発言（「私が解説します」「大丈夫！」「メモして」）

【テロップの使い分け】
- P1のみ: テロップだけのページ（タイトル・煽り）
- P2以降: セリフが中心。テロップや背景文字は重要ポイント・見出し・数字の強調に使う
  - 良い例：【テロップ】1 失業手当 → 【ナミ】これはもう定番よね。
  - 良い例：（ト書き: 画面に「最大240日分」の文字）→ 【ナミ】条件を満たせばすぐ申請できるよ。
  - NG例：【テロップ】失業手当は65歳で受け取れなくなる → 【ナミ】失業手当は65歳で…（内容被り）

【フォーマットルール（厳守）】
1. 各ページは「--- P1 ---」「--- P2 ---」...の区切りで始めてください
2. 各ページの最初にト書きを書いてください：「（ト書き: シーンの状況、キャラの表情・動きの描写）」
3. セリフは「【キャラ名】セリフ」の形式
4. テロップは「【テロップ】テキスト」の形式
5. **テロップとセリフで同じ内容を言わないでください**
6. 改行は句点（。）の位置でのみ行ってください
7. 読点（、）の位置では改行しないでください

【出力フォーマット（厳守）】
各パターンの間に「===VARIATION===」を挿入してください。
説明や追加コメントは不要です。テキストのみを出力してください。

例（2パターン・各5ページの場合）：
--- P1 ---
（ト書き: 暗い背景に赤い文字がドンと表示される）
【テロップ】忘れると大損！60から64歳しか受け取れない、給付金3選。
--- P2 ---
（ト書き: {protagonist_name}が険しい表情で腕組みをしている）
【{protagonist_name}】国はゼニゲバだから、200万円以上得する情報なんて絶対教えてくれないんだよ。
【{protagonist_name}】二度とおすすめに出てこないかもだから、今のうちにいいねと保存、お願いね！
--- P3 ---
（ト書き: {protagonist_name}が指を1本立てて、キリッとした表情。画面に「1 失業手当」の文字）
【テロップ】1 失業手当
【{protagonist_name}】これはもう定番よね。
【{protagonist_name}】あなたの給料の約6割がもらえるの。
--- P4 ---
（ト書き: {protagonist_name}が驚いた表情で身を乗り出す）
【{protagonist_name}】でもね、失業保険の延長ができるって知ってた？
【{protagonist_name}】実はコレ、マジで知らない人多いんだよね。
--- P5 ---
（ト書き: {protagonist_name}がこちらに手を差し伸べる）
【{protagonist_name}】気になる人はフォローしてね。
===VARIATION===
--- P1 ---
（ト書き: 給与明細のアップ、赤字で「損」の文字）
【テロップ】退職後のお金、9割の人が損してます。
...（以下同様にP2〜P5）

【入力テキスト】
{text}

【出力】
{num_variations}パターンを ===VARIATION=== で区切って、各{num_pages}ページで出力してください。
"""

        try:
            print(f"Gemini APIで{num_variations}パターン生成中...")
            response = self.model.generate_content(prompt)
            print(f"バリエーション生成レスポンス受信完了")

            if hasattr(response, 'text'):
                raw_result = response.text.strip()
                print(f"バリエーション生成結果: {len(raw_result)}文字")

                # ===VARIATION=== で分割
                variations = [v.strip() for v in raw_result.split("===VARIATION===")]
                # 空のバリエーションを除去
                variations = [v for v in variations if v]

                print(f"生成されたバリエーション数: {len(variations)}")
                return variations
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"バリエーション生成エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
