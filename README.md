# Graduation Research: Assumption-Aware Agents

AIの「前提」を可視化し、前提違反時に設計へ立ち返る（return-to-design）機構の研究用リポジトリ。

- 研究ノート・企画書は Obsidian vault（`卒業論文/`、別管理）にあり、本リポジトリは**コードと実験データ**を置く。
- 現在の進行：Phase 0（RQ0パイロット：前提列挙カバレッジの検証）→ `phase0_rq0_pilot/README.md`

## 構成

```
phase0_rq0_pilot/   RQ0パイロット（プロトコル・タスク・プロンプト・スクリプト）
```

## セットアップ

```
pip install boto3 requests
set BEDROCK_MODEL_IDS=anthropic.claude-3-5-haiku-20241022-v1:0,amazon.nova-lite-v1:0
set AWS_REGION=us-east-1
```
