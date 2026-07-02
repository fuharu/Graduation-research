# -*- coding: utf-8 -*-
"""RQ0パイロット：elicit実行スクリプト
タスク×プロンプト×モデル×反復 でLLMに前提を列挙させ、生出力とパース結果を保存する。
使い方: python run_elicit.py [--reps 3] [--temp 0.4]
環境変数:
  AWS Bedrock : BEDROCK_MODEL_IDS（カンマ区切りで複数可）, AWS_REGION
                （認証は aws configure / 環境変数の標準チェーン。要 pip install boto3）
  OpenAI互換  : OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL
  Gemini      : GEMINI_API_KEY / GEMINI_MODEL
設定されたものだけがプロバイダとして登録される（Bedrockのみでも可）。
"""
import argparse, json, os, re, sys, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
PROMPTS_DIR = ROOT / "prompts"
OUT_DIR = ROOT / "outputs" / "elicit"


def call_openai(prompt: str, temp: float) -> str:
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    r = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={"model": model, "temperature": temp,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_gemini(prompt: str, temp: float) -> str:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    r = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temp}}, timeout=120)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def make_bedrock_caller(model_id: str):
    def call(prompt: str, temp: float) -> str:
        import boto3  # 遅延import（Bedrock未使用時はboto3不要）
        client = boto3.client("bedrock-runtime",
                              region_name=os.environ.get("AWS_REGION", "us-east-1"))
        resp = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": temp, "maxTokens": 2048})
        return resp["output"]["message"]["content"][0]["text"]
    return call


PROVIDERS = {}
for mid in filter(None, os.environ.get("BEDROCK_MODEL_IDS", "").split(",")):
    mid = mid.strip()
    short = mid.split(".")[-1].split(":")[0]
    PROVIDERS[f"bedrock_{short}"] = make_bedrock_caller(mid)
if os.environ.get("OPENAI_API_KEY"):
    PROVIDERS["openai_" + os.environ.get("OPENAI_MODEL", "gpt-4o-mini")] = call_openai
if os.environ.get("GEMINI_API_KEY"):
    PROVIDERS["gemini_" + os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")] = call_gemini


def parse_assumptions(text: str):
    """出力からJSON配列を抽出。コードフェンス・前後の説明文に耐える。"""
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.S)
    raw = m.group(1) if m else None
    if raw is None:
        m = re.search(r"\[\s*\{.*\}\s*\]", text, re.S)
        raw = m.group(0) if m else None
    if raw is None:
        return None
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return None
    out = []
    for it in items:
        if isinstance(it, dict) and "statement" in it:
            out.append({"statement": str(it["statement"]),
                        "type": str(it.get("type", "?")),
                        "importance": str(it.get("importance", "?"))})
    return out or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--temp", type=float, default=0.4)
    args = ap.parse_args()

    if not PROVIDERS:
        sys.exit("プロバイダが未設定です（BEDROCK_MODEL_IDS / OPENAI_API_KEY / GEMINI_API_KEY のいずれか）")

    tasks = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted(TASKS_DIR.glob("task*.json"))]
    prompts = {p.stem: p.read_text(encoding="utf-8")
               for p in sorted(PROMPTS_DIR.glob("elicit_*.txt"))}
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    n_total = len(tasks) * len(prompts) * len(PROVIDERS) * args.reps
    print(f"tasks={len(tasks)} prompts={len(prompts)} models={list(PROVIDERS)} "
          f"reps={args.reps} -> {n_total} calls")

    done = 0
    for task in tasks:
        if not task.get("gold"):
            print(f"[警告] {task['id']}: gold が空です。プロトコル§3（ゴールドを先に作る）を確認。")
        for pname, ptext in prompts.items():
            prompt = ptext.replace("{TASK_DESCRIPTION}", task["description"])
            for mname, fn in PROVIDERS.items():
                for rep in range(1, args.reps + 1):
                    fname = f"{task['id']}__{pname}__{mname}__rep{rep}.json"
                    fpath = OUT_DIR / fname
                    if fpath.exists():
                        done += 1
                        continue  # 再実行時はスキップ（冪等）
                    try:
                        raw = fn(prompt, args.temp)
                    except Exception as e:
                        print(f"[失敗] {fname}: {e}")
                        continue
                    parsed = parse_assumptions(raw)
                    fpath.write_text(json.dumps({
                        "task": task["id"], "prompt": pname, "model": mname,
                        "rep": rep, "temperature": args.temp,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "raw": raw, "assumptions": parsed,
                        "parse_ok": parsed is not None,
                    }, ensure_ascii=False, indent=2), encoding="utf-8")
                    done += 1
                    print(f"[{done}/{n_total}] {fname} "
                          f"({len(parsed) if parsed else 'PARSE_FAIL'}件)")
                    time.sleep(1)
    print("完了。次: python scripts/score_coverage.py make-sheet")


if __name__ == "__main__":
    main()
