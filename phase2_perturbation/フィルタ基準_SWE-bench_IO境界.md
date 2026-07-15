# SWE-bench Lite I/O境界フィルタ基準 v0.1（Phase 2準備）

目的：SWE-bench Lite（300件）から、本研究のスコープ「I/O境界を持つ小規模Pythonタスク」に合致するインスタンスを選定する。**基準を先に凍結してから選定する**（cherry-picking防止。選定結果は全件記録し、除外理由も残す）。

## 1. 包含基準（すべて満たす）
- **IN-A（I/O境界）**：修正対象（gold patch が触るコード）が次のいずれかに関与する
  - 外部データの読み書き：ファイルI/O、シリアライズ/デシリアライズ（json/csv/yaml/pickle/xml）
  - ネットワーク・API呼び出し：requests/urllib/http系
  - データフォーマット処理：パース、エンコーディング、日時処理（datetime/tz）、型変換
  - 外部ライブラリのAPI契約：引数の意味・戻り値形状・例外挙動の解釈が関わる修正
- **IN-B（規模）**：gold patch の変更が概ね300行以内・関与ファイル1〜3個
- **IN-C（摂動可能性）**：I/O相手（データ・API・環境）をモック/フィクスチャで差し替え可能（＝「途中で前提が覆る」摂動を注入できる）
- **IN-D（判定可能性）**：既存のFAIL_TO_PASSテストが成果物の正否のオラクルとして機能する

## 2. 除外基準（いずれかに該当したら除外）
- EX-1：GUI・描画・画像出力が主対象（matplotlib描画結果の見た目等）
- EX-2：並行処理・非同期・性能最適化が主対象
- EX-3：ビルド・パッケージング・CI設定のみの修正
- EX-4：アルゴリズム内部の数値精度・数学的正しさのみ（I/O境界に触れない）
- EX-5：修正理解にリポジトリ固有の深いドメイン知識が必要（前提のゴールド化が困難）

## 3. 選定手順（2段階）
1. **機械プリフィルタ**：issue本文＋gold patchに対するキーワードマッチで候補を粗選定。
   - キーワード例：`json, csv, yaml, parse, serial, encod, decod, datetime, timezone, utc, request, http, url, api, read, write, load, dump, file, path, header, schema, format, locale`
   - patch対象ファイルのimport文に io/json/csv/requests/datetime 系が含まれるか
2. **人手確認**：候補を基準IN-A〜D／EX-1〜5で判定し、`selection_log.csv`に全件記録
   - 列：instance_id, prefilter_hit, IN-A〜D判定, EX該当, 採否, 理由メモ
- **目標件数：10〜20件**。20件を超えたら層化（ライブラリ種別で散らす）でサンプリング。

## 4. 摂動注入の型との対応（メモ）
採択インスタンスごとに、注入する摂動タイプ（taxonomy_draft.md の型ID）を割り当てる。例：datetime系issue→EV-1/IN-3摂動、requests系→API-1/API-2摂動。割り当て表はPhase 2プロトコル本体で凍結する。

## 5. 更新履歴
- v0.1（2026-07-08）：初版。実データでの試行後に v1.0 として凍結する。
