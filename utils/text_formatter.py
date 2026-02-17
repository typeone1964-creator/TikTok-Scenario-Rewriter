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
        テキストを14文字/行に整形
        重要: 元の発言内容は1文字も変えず、句読点と改行のみを調整
        """
        prompt = f"""あなたは厳格な校正者です。以下のテキストを整形してください。

【絶対厳守のルール】
1. 元のテキストの内容（単語、表現）を1文字も変更してはいけません
2. 1行は14文字以内にしてください
3. **重要**: 各行は必ず句点（。）または読点（、）で終わらせてください。句読点がない行は絶対に作らないでください
4. 文の途中で改行する場合は、必ず読点（、）を追加してください
5. 文の終わりで改行する場合は、必ず句点（。）を追加してください
6. 意味のまとまりや自然な区切りで改行してください
7. 読みやすい位置で改行してください（途中で単語が切れないように）
8. 要約や言い換えは絶対に禁止です

【良い例】
職場の嫌な奴は、← 読点で終わる
こう扱えば大丈夫。← 句点で終わる
職場に嫌いな人は、← 読点で終わる
一人はいますよね。← 句点で終わる
そんな人の対処法を、← 読点を追加
5つ紹介します。← 句点で終わる
この動画はもう二度と、← 読点を追加
おすすめに表示されませんので、← 読点で終わる
忘れないよう、← 読点で終わる
いいねと保存を、← 読点を追加
お願いします。← 句点で終わる

【悪い例（絶対NG）】
そんな人の対処法を ← ×句読点がない
この動画はもう ← ×句読点がない

【入力テキスト】
{text}

【出力】
整形後のテキストのみを出力してください。説明や追加コメントは不要です。
全ての行が句点（。）または読点（、）で終わることを確認してください。
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
2. 1行は最大14文字、できるだけ14文字に近づけてください
3. 各行は必ず句点（。）または読点（、）で終わらせてください
4. **重要**: 読点（、）は最低限にしてください。不要な読点は入れないでください
5. 文の途中で改行する場合のみ読点（、）を追加してください
6. 文の終わりは句点（。）で終わらせてください
7. 読み方がおかしくならない自然な位置で改行してください
8. 行数は元のテキストと同じか近い数を維持してください

【良い例】
職場の嫌な奴は、← 14文字に近い、文の途中なので読点
こう扱えば大丈夫。← 文の終わりなので句点
そんな人の対処法を、← 14文字に近い
5つ紹介します。← 句点で終わる

【悪い例】
職場の、← 短すぎる、不要な読点
嫌な奴は、← 短すぎる
こう、← 不要な読点が多い

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
        """キャラクター情報からプロンプト用のセクションを構築"""
        if not characters:
            return ""

        char_lines = []
        for c in characters:
            profile_parts = [f"名前: {c['name']}"]
            if c.get('age'):
                profile_parts.append(f"年代: {c['age']}")
            if c.get('gender'):
                profile_parts.append(f"性別: {c['gender']}")
            if c.get('appearance'):
                profile_parts.append(f"見た目: {c['appearance']}")
            if c.get('atmosphere'):
                profile_parts.append(f"雰囲気: {c['atmosphere']}")
            if c.get('background'):
                profile_parts.append(f"背景: {c['background']}")
            if c.get('tone'):
                profile_parts.append(f"口調: {c['tone']}")
            char_lines.append("- " + "／".join(profile_parts))
        char_list = "\n".join(char_lines)
        char_names = "、".join(c['name'] for c in characters)

        return f"""
【登場キャラクター】
{char_list}

【キャラクターシナリオのルール】
1. 各キャラクターのセリフは「【キャラ名】セリフ」の形式で書いてください
2. キャラクター名タグ（【〇〇】）は行の先頭に付け、セリフ文字数には含めません
3. 各キャラクターのプロフィール（年代・性別・見た目・雰囲気・背景・口調）を忠実に反映してください
4. 特に「口調」の設定は最重要です。キャラごとに話し方を明確に区別してください
5. 会話や掛け合いを自然に組み立ててください
6. ナレーション（キャラ名なしの地の文）も適宜入れてOKです
7. 使用キャラクター: {char_names}

【良い例】
【太郎】これ知ってる？
【太郎】実はこれヤバくて、
【花子】え、マジ？
【花子】全然知らなかった。
【太郎】だよね。
【太郎】じゃあ教えるけど、
今回紹介するのは、
誰でもできる方法です。
"""

    def rewrite_scenario(self, text: str, politeness: str = None, emotion: str = None,
                         style: str = None, custom_instruction: str = None,
                         characters: List[dict] = None) -> Optional[str]:
        """
        シナリオ全体の書き直し（内容再構成・表現変更OK）

        rephrase_text()との違い:
        - rephrase_text(): ニュアンスのみ変更、内容は維持
        - rewrite_scenario(): 内容の再構成・追加・削除・順序変更もOK

        Args:
            text: 整形済みテキスト
            politeness: 丁寧度（casual/polite/formal）
            emotion: 感情（gentle/strong/cool）
            style: 話し方（explanatory/conversational/narrative）
            custom_instruction: 自由指示テキスト（「もっと煽り気味にして」等）
            characters: キャラクター情報のリスト [{"name": "太郎", "description": "..."}]

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

        prompt = f"""あなたはTikTok動画のシナリオライターです。以下のテキストを書き直してください。

{nuance_text}
{custom_section}
{character_section}

【書き直しのルール】
1. 元のテキストのテーマ・主旨は維持してください
2. ただし、表現の変更、内容の追加・削除・順序変更は自由に行ってOKです
3. TikTok動画として視聴者を引き込む構成にしてください
4. 冒頭で注意を引き、最後まで見たくなる展開にしてください

【フォーマットルール】
1. セリフ部分は「【キャラ名】」の後に続けて書いてください
2. セリフのテキスト部分は最大14文字（キャラ名タグは文字数に含めない）
3. 各行は必ず句点（。）または読点（、）で終わらせてください
4. 文の途中で改行する場合のみ読点（、）を追加してください
5. 文の終わりは句点（。）で終わらせてください
6. 読み方がおかしくならない自然な位置で改行してください
7. 不要な読点は入れないでください

【入力テキスト】
{text}

【出力】
書き直し後のテキストのみを出力してください。説明や追加コメントは不要です。
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
                            characters: List[dict] = None) -> Optional[List[str]]:
        """
        複数パターンのシナリオを一括生成

        1回のAPI呼び出しで ===VARIATION=== 区切りの複数パターンを生成

        Args:
            text: 整形済みテキスト
            num_variations: 生成パターン数（1〜3）
            politeness: 丁寧度（casual/polite/formal）
            emotion: 感情（gentle/strong/cool）
            style: 話し方（explanatory/conversational/narrative）
            custom_instruction: 自由指示テキスト
            characters: キャラクター情報のリスト [{"name": "太郎", "description": "..."}]

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

        prompt = f"""あなたはTikTok動画のシナリオライターです。以下のテキストを{num_variations}パターン書き直してください。

{nuance_text}
{custom_section}
{character_section}

【書き直しのルール】
1. 元のテキストのテーマ・主旨は維持してください
2. 各パターンは異なるアプローチ・切り口で書いてください
3. TikTok動画として視聴者を引き込む構成にしてください
4. 冒頭で注意を引き、最後まで見たくなる展開にしてください

【フォーマットルール】
1. セリフ部分は「【キャラ名】」の後に続けて書いてください
2. セリフのテキスト部分は最大14文字（キャラ名タグは文字数に含めない）
3. 各行は必ず句点（。）または読点（、）で終わらせてください
4. 文の途中で改行する場合のみ読点（、）を追加してください
5. 文の終わりは句点（。）で終わらせてください
6. 不要な読点は入れないでください

【出力フォーマット（厳守）】
各パターンの間に「===VARIATION===」を挿入してください。
説明や追加コメントは不要です。テキストのみを出力してください。

例（2パターンの場合）：
【太郎】これ知ってる？
【太郎】実はこれヤバくて、
【花子】え、マジで？
【太郎】マジマジ。
【太郎】今日教えるから、
【花子】お願いします。
===VARIATION===
【花子】ちょっと聞いて。
【太郎】なに？
【花子】知らないと損する、
【花子】方法があるんだけど。
【太郎】気になる。教えて。

【入力テキスト】
{text}

【出力】
{num_variations}パターンを ===VARIATION=== で区切って出力してください。
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
