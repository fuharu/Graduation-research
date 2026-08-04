# 卒業研究：前提可視化と設計回帰

## 現在地
Phase 0a（分岐分析）を実行中。RQ0パイロットはその後。
実行手順は `phase0_rq0_pilot/README.md`、実験条件は `プロトコル_RQ0_凍結版.md`（凍結）。

## 絶対に変更しないファイル（凍結済み・deny設定済み）
- `phase0_rq0_pilot/tasks/*.json` の `gold`
  → 人手でelicit実行前に作成する。AIが書くとRQ0が無効になる
- `phase0_rq0_pilot/prompts/*.txt`
- `phase0_rq0_pilot/プロトコル_RQ0_凍結版.md`
- `phase0_rq0_pilot/outputs/` の既存データ

## 人間が判断する作業（AIは補助しない）
- `annotation_sheet.csv` の分岐の解釈・類型付与
  → これが論文の貢献C4そのもの。AIが分類すると評価に循環が生じる
- タクソノミの改訂・飽和判定
- ゴールド前提の作成

## 変更してよいもの
`scripts/` のコード、環境構築、集計・可視化、README

## 実行時の注意
- 分岐分析は `BEDROCK_MODEL_IDS` を1モデルにする（プロトコル§3手順0が「同一モデル」を要求）
- elicit は2モデル（プロトコル§2）
- 環境変数は PowerShell の `$env:` で設定する（`set` は効かない）

## 上記に触る必要が出たら
勝手に変更せず、理由を説明して確認を取ること。