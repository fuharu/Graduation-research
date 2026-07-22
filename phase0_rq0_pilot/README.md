# Phase 0 キット：RQ0パイロット（前提列挙カバレッジの検証）

関連ノート（Obsidian vault側）：研究ロードマップ_前提可視化_Phase0-4 / 統計設計_前提違反検知と設計回帰

## 実行順序（この順を守る。特に 2→4 の順序が妥当性に直結）

0. **Phase 0a：分岐分析（ゴールド作成の前に）** → プロトコル§3手順0
   - `python scripts/run_divergence.py run`（同一タスク×N回コード生成。動作確認は `MOCK=1` で）
   - `python scripts/run_divergence.py digest` → `outputs/divergence/digest_*.md` を見比べ、実装が割れた箇所を `annotation_sheet.csv` に記録（型IDは `taxonomy_draft.md`）
   - 新しい型が出なくなったら（飽和）タクソノミを確定
1. **プロトコルを読む・確定する** → `プロトコル_RQ0_凍結版.md`（変更したら履歴に追記してから開始）
2. **ゴールド前提を作る（人手・elicit実行前に！）** → `tasks/task01〜03.json` の `gold` を埋める
   - LLM出力を見る前に書く。書式は `tasks/_example_toy.json` 参照。**Phase 0aで確定した類型をチェックリストとして使う**
3. **プロンプト凍結** → `prompts/` の3変種を確認、変えるなら今
4. **elicit実行** → `python scripts/run_elicit.py`
5. **マッチングシート生成→人手判定** → `python scripts/score_coverage.py make-sheet` → 出力CSVの `matched_gold_id` 列を埋める
6. **採点** → `python scripts/score_coverage.py score` → 再現率/適合率＋ブートストラップCI
7. **分岐判定** → プロトコル§6の基準（70%/50%）で次の一手を決め、結果をログvault（`卒業論文ログ/卒業研究/実験ログ/`）に記録

## 環境変数（AWS Bedrock 推奨構成）

```
# AWS Bedrock（カンマ区切りで2モデル指定＝これだけで2モデル要件を満たす）
set BEDROCK_MODEL_IDS=anthropic.claude-3-5-haiku-20241022-v1:0,amazon.nova-lite-v1:0
set AWS_REGION=us-east-1
# 認証: aws configure 済みならそれでOK（またはAWS_ACCESS_KEY_ID等の標準環境変数）
```

事前確認（初回のみ）：
1. AWSコンソール → Bedrock → Model access で使用モデルを有効化（リージョンに注意）
2. `aws sts get-caller-identity` で認証確認
3. IAMに `bedrock:InvokeModel` 権限があること

依存：`pip install boto3 requests`

<details><summary>代替：OpenAI互換 / Gemini（Bedrockを使わない場合）</summary>

```
set OPENAI_API_KEY=...
set OPENAI_BASE_URL=https://api.openai.com/v1   # 省略可
set OPENAI_MODEL=gpt-4o-mini
set GEMINI_API_KEY=...
set GEMINI_MODEL=gemini-2.0-flash
```
</details>

## 費用の目安
3タスク×3プロンプト×2モデル×3反復＝54呼び出し、各1Kトークン程度 → 数十円〜数百円。
