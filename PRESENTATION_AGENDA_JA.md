# AIエージェント構築プレゼンテーション アジェンダ

**想定時間:** 15分
**対象者:** AIエージェント構築に興味がある開発者

---

## 📊 時間配分（推奨）

| セクション | 時間 | 割合 |
|-----------|------|------|
| 1. イントロ & メリット | 1分 | 7% |
| 2. AIエージェントとは | 1分 | 7% |
| 3. 問題提起 & アプリ紹介 | 2分 | 13% |
| 4. アーキテクチャ概要 | 2分 | 13% |
| **5. 構築手順（本題）** | **8分** | **53%** |
| 6. まとめ & 学び | 1分 | 7% |
| **合計** | **15分** | **100%** |

**注:** Q&Aはプレゼン外の専用時間で実施

---

## 1. 本発表の目的・メリット（1分）

### 📌 このプレゼンで得られること
- ✅ AIエージェントとは何かをイメージできる
- ✅ AIエージェントの構築手順とデプロイまでの工程を知る
- ✅ 実践から得た具体的な教訓とノウハウ

### 💡 AIエンジニアになるメリット
> 参考: Gmail "The shortest path to a $500K AI Engineering role"

**短く一言で:**
「市場価値を高めると同時に、社会に大きなインパクトを与えることができる」

**💬 提案:**
- このメリット部分は**30秒以内**に収めるべき
- 具体例を1つだけ: 「このアプリは1人の開発者が2ヶ月で作れた。これが5年前なら数人のチーム、半年はかかっていた」

---

## 2. AIエージェントとは何か（1分）

### 🎯 目的
実際の構築手順の話に入る前に「AIエージェントとはそもそも何か？」という前提の目線を合わせる

### 📝 内容（提案）

**簡潔な定義:**
「AIエージェント = 自律的にタスクを実行し、ツールを使い、判断するAIシステム」

**対比で説明:**

| 従来のチャットボット | AIエージェント |
|---------------------|---------------|
| 質問に答えるだけ | **行動する** |
| 1つの機能のみ | **複数のツールを使い分ける** |
| 毎回同じ回答 | **状況に応じて判断** |

**具体例（このアプリで）:**
- ❌ 単純なチャットボット: 「タンパク質は体重×2gが目安です」
- ✅ AIエージェント:
  1. ユーザーの過去2週間のデータを取得（ツール使用）
  2. 体重変化を分析（判断）
  3. 「あなたは減量中で体重が順調に減っているので、タンパク質を180gに増やしましょう」（個別化された行動指示）

**💬 提案:**
- この定義部分は**シンプルに保つ**（1分以内）
- 技術的詳細は後のアーキテクチャセクションで

---

## 3. 問題提起 & アプリ紹介（2分）

### ❓ 問題提起（30秒）

**フィットネスにおける3つの課題:**
1. ❌ 何を信じたらいいか分からない
   - 「朝食は抜くべき？」「タンパク質は何グラム？」「糖質制限しないと痩せない？」
2. ❌ 具体的なアクションプランが分からない
   - 「私の場合、何をすればいいの？」
3. ❌ 習慣化できない
   - 「続かない...」

### 💪 解決策: FitTracker AI（1.5分）

**3つのAIエージェントで3つの問題を解決:**

| 問題 | 解決策（エージェント） | 技術 |
|------|----------------------|------|
| ❌ 何を信じるか不明 | ✅ **Coach Agent** | RAG + GPT-4 |
| ❌ 行動プラン不明 | ✅ **Nutrition & Training Specialists** | 決定論的アルゴリズム |
| ❌ 習慣化できない | ⚠️ **Motivator Agent** | （未実装） |

**💬 提案:**
- **未実装の機能は軽く触れるだけ**（「今後の展望として...」程度）
- 実装済みの2つに焦点を当てる

### 🔗 デモ & リンク

**見せるもの（推奨）:**
- **スクリーンショット3枚**（チャット画面、栄養分析結果、ワークアウトプラン）
- ライブデモは**避ける**（時間リスクが高い）

**リンク提示:**
- AWS デプロイ URL
- GitHub リポジトリ

**💬 提案:**
「詳細はGitHubで公開しています。後ほどご覧ください」で十分

---

## 4. AIエージェントアーキテクチャ・テックスタック（2分）

### 🎯 目的
「複雑そうに見えるが、実は整理されている」と感じてもらう

### 📐 見せ方（提案）

**4.1 システム全体図（30秒）**
```
ユーザー
  ↓
Frontend (Next.js - S3/CloudFront)
  ↓
API Gateway
  ↓
Lambda (FastAPI) ← 全エージェントここに
  ↓
├─ OpenAI GPT-4 (Coach)
├─ Bedrock Nova (Workout Planner)
├─ OpenSearch (RAG)
└─ DynamoDB (データ)
```

**4.2 3つのエージェントの役割分担（1分）**

| エージェント | LLM使用? | 理由 |
|-------------|---------|------|
| **Coach** | ✅ OpenAI GPT-4 | 会話品質が重要 |
| **Workout Planner** | ✅ Bedrock Nova | *(注: 実は不要かも)* |
| **Nutrition/Training** | ❌ アルゴリズム | 決定論的ルールで十分 |

**💬 提案:**
- Workout Plannerが「実はLLM不要」という点を**軽く触れる**と説得力UP
- 「何でもAIを使えばいいわけではない」という伏線になる

**4.3 技術スタック（30秒）**

**表示方法（推奨）:**
```
Frontend:  Next.js 15 + React 19
Backend:   FastAPI + Python 3.12
AI:        OpenAI GPT-4 + Bedrock (Nova/Titan)
Infra:     AWS Serverless (Lambda, DynamoDB, S3, OpenSearch)
Deploy:    Terraform + Docker
```

**💬 提案:**
- 技術スタックは**列挙するだけ**（詳細は質問があれば後で）
- ここで時間を使いすぎないこと

---

## 5. AIエージェント構築手順（8分）⭐ **本題**

> **💡 統一フォーマット:** 各ステップで「ベストプラクティス → 教訓（1つのみ、深掘り） → 解決策」

---

### 📋 ステップ1: 設計（3分）

---

#### 📊 Slide 1: 手順 + 重要な原則（30秒）

**設計フェーズ（3ステップ）:**
1. **エージェントの責任範囲を定義** - 何ができて何ができないか明確に
   - *例: Coach = 会話のみ、Nutrition = 計算のみ、Training = 分析のみ*

2. **各機能に適切な技術を選択** - LLM vs アルゴリズム vs ルールベース
   - *例: Coach = GPT-4、Nutrition = 決定論的アルゴリズム、Energy = 数式*

3. **データフローを設計** - エージェント間の連携、データの流れを整理
   - *例: ユーザー → Coach → Nutrition ツール呼び出し → 推奨値返却*

**⚠️ 重要な原則:**
**「問題から始める、手段から始めない」**

---

#### 📊 Slide 2: 私の失敗事例（1分）

**❌ 陥りやすい罠:**

当初、私はこう思い込んでいた:
- ❌ 「AIエージェント = 全部LLMを使うもの」
- ❌ 「LangChainやOpenAI Agents SDKなどのフレームワークが必須」
- ❌ 「Workout Plannerも当然AIで」

**💡 なぜこの思い込みが危険か:**

**例: Workout Planner の分析**

当初の設計:
```
Workout Planner → Bedrock Nova (LLM)
理由: 「複雑な運動計画だからAIが必要だろう」
```

しかし実態を分析すると:
```
目標: 12筋肉群に週8-10セットの運動を割り当てる
制約:
  - 各筋肉群: 目標範囲内のセット数
  - 総頻度 ≤ 週の最大トレーニング日数
  - 1日1筋肉あたり ≤ 10セット
  - エクササイズは固定データベースから選択
```

**これは制約充足問題（CSP）= アルゴリズムで解ける！**

**実際の比較:**

| 指標 | LLM (現在) | 決定論的アルゴリズム |
|------|-----------|---------------------|
| コスト | $0.01-0.05/プラン | **$0** |
| 成功率 | ~80% (最大5回リトライ) | **100%** |
| 速度 | 5-15秒 | **<100ms** |
| デバッグ | 困難（ブラックボックス） | **容易（ロジック追跡可能）** |
| 一貫性 | 毎回異なる可能性 | **常に同じ入力=同じ出力** |

**同じことがフレームワークにも言える:**

当初: 「AIエージェント作るなら、LangChainやOpenAI Agents SDK必須だろう」

実際:
- このアプリの要件: シンプルな構成
- FastAPI + OpenAI SDK で**十分**
- 不要な抽象化を避けられた
- デバッグが簡単
- 学習コストが低い

---

#### 📊 Slide 3: 解決策 + 教訓（1分）

**✅ 実践した設計プロセス:**

1. **問題の本質を理解**
   - Workout Planner: 制約充足問題 → アルゴリズムで解ける
   - Coach: 自然言語理解 → LLM必須

2. **最小構成を選択**
   - フレームワーク不要 → FastAPI + OpenAI SDK
   - 不要な依存を避ける

3. **データアクセスパターン事前設計**
   - DynamoDB GSI を4つ設計（`UserIdDateIndex` など）
   - 構築前にクエリパターンを明確化

**📌 最終的な技術選定:**

| コンポーネント | 技術選択 | 理由 |
|--------------|---------|------|
| Coach Agent | **LLM (GPT-4)** | 自然言語理解・会話が必要 |
| Nutrition Specialist | **アルゴリズム** | 科学的ルールに基づく決定論的判断 |
| Training Specialist | **アルゴリズム** | 進捗ルールは明確 |
| Energy Calculator | **数式** | 確立された公式（Cunningham BMR） |

**結果:**
- コスト削減: 月額 $30-50（Nutrition/Training で LLM 不使用）
- 信頼性: 100%（決定論的アルゴリズム）
- デバッグ容易: ロジック追跡可能

**🎯 教訓: 「問題から始める、手段から始めない」**

技術選定で最も重要なのは『この問題は何か？』を理解すること。
手段ありきではなく、問題に最適な解決策を選ぶ。

---

### 📋 ステップ2: 開発（3分）

---

#### 📊 Slide 1: 手順 + 重要な原則（30秒）

**開発フェーズ（3ステップ）:**
1. **開発環境セットアップ** - ローカル環境、API キー、依存関係
   - *例: uv で依存関係管理、OpenAI API キー、ローカル FAISS for RAG*

2. **エージェントコア実装** - LLM 連携、ツール定義、プロンプト作成
   - *例: Coach エージェント、7つのツール定義、"Use this when..." プロンプト*

3. **API & フロントエンド統合** - エンドポイント作成、UI 接続、テスト
   - *例: FastAPI `/api/coach/ask` エンドポイント、React チャットコンポーネント*

**⚠️ 重要な原則:**
**「トップダウンで一度に全て構築しようとせず、ボトムアップで一歩一歩構築する」**

---

#### 📊 Slide 2: 私の失敗事例（1分30秒）

**❌ 最初の失敗: 全部一度に作ろうとした**

Coach Agent を作り始めた時、私はこう考えた:

「最初から完璧なチャットボットを作ろう！」

**最初の実装計画:**
```
Coach Agent v1.0 - 全機能実装
├─ 個人データ質問に回答（4ツール）
│   ├─ get_user_profile()      「目標は？」
│   ├─ get_nutrition_logs()    「カロリー摂取量は？」
│   ├─ get_workout_logs()      「最近のトレーニングは？」
│   └─ get_body_logs()         「体重の推移は？」
├─ 一般的な健康質問に回答（1ツール）
│   └─ search_knowledge_base() 「最適なタンパク質量は？」
└─ 専門家の分析を取得（2ツール）
    ├─ get_nutrition_recommendation() 「カロリーを調整すべき？」
    └─ get_training_summary()          「トレーニングの進捗は？」

合計: 7つのツールを OpenAI に渡す
```

**実装完了... テスト開始！**

**❌ 実際に何が起きたか:**

**問題: LLMが間違ったツールを呼ぶ**

```python
# テスト1
質問: 「私の最適なカロリーは？」

LLMの判断: どのツールを使う？
  - get_nutrition_logs()? (最近の食事ログ) ❌ 違う
  - search_knowledge_base()? (一般的な計算式) ❌ 違う
  - get_nutrition_recommendation()? (個別の推奨値) ✅ 正解！

実際の挙動:
  → 40%の確率で get_nutrition_logs() を呼ぶ ❌
  → 30%の確率で search_knowledge_base() を呼ぶ ❌
  → 30%しか get_nutrition_recommendation() を呼ばない

# テスト2
質問: 「最近のタンパク質摂取量は？」

LLMの判断: どのツールを使う？
  - get_nutrition_logs()? (実際の摂取ログ) ✅ 正解！
  - search_knowledge_base()? (一般的な知識) ❌ 違う

実際の挙動:
  → 60%の確率で search_knowledge_base() を呼ぶ ❌
  → "最適なタンパク質量は体重×2g..." と一般論を返す
  → ユーザーの実際のデータは見ていない
```

**なぜこうなるのか？**

```python
# 7つのツール定義を OpenAI に渡している
tools = [
    {
        "name": "get_nutrition_logs",
        "description": "Get user's nutrition logs"  # ⚠️ 曖昧
    },
    {
        "name": "search_knowledge_base",
        "description": "Search fitness knowledge"  # ⚠️ 曖昧
    },
    {
        "name": "get_nutrition_recommendation",
        "description": "Get nutrition recommendation"  # ⚠️ 曖昧
    },
    # ... 残り4つ
]

# LLMの視点:
# 「"カロリー" というキーワードが3つのツールの説明に含まれている...
#  どれを使えばいいか分からない！」
```

**デバッグ地獄...**
```
どのツールの説明が悪いのか分からない:
- get_nutrition_logs の説明を変える
  → 今度は search_knowledge_base が誤爆
- search_knowledge_base の説明を変える
  → 今度は get_nutrition_recommendation が呼ばれない
- すべて変える
  → 何が効いたのか分からない

→ 7つのツール説明が相互に影響しあって調整不可能
→ 1つ直すと別が壊れる無限ループ
```

**2週間後... ツール呼び出し成功率40% 😱**

---

#### 📊 Slide 3: 解決策 + 教訓（1分30秒）

**💡 方針転換: 小さく始めて段階的に拡張**

**ステップ1: RAGだけ（3日）**
```python
# Coach Agent v0.1 - 最小構成
tools = [
    {
        "name": "search_knowledge_base",
        "description": "Search fitness knowledge"  # シンプルな説明
    }
]

# テスト
質問: "最適なタンパク質量は？"
→ LLM calls search_knowledge_base() ✅ 100%成功！

# なぜ成功？
→ ツールが1つしかないので迷わない
→ RAGの問題だけに集中してデバッグできた
```

→ **3日でRAGが安定して動くように**

---

**ステップ2: ツール1つだけ追加（2日）**
```python
# Coach Agent v0.2 - ツール2つ
tools = [
    {
        "name": "search_knowledge_base",
        "description": "Search fitness knowledge"
    },
    {
        "name": "get_body_logs",
        "description": "Get user's body weight logs"  # 初期説明
    }
]

# テスト1
質問: "最近の体重は？"
→ get_body_logs() ✅ 正しい！

# テスト2
質問: "理想的な体重は？"
→ ❌ get_body_logs() を呼んでしまう（間違い！一般論を知りたい）
→ search_knowledge_base() を呼ぶべき

# プロンプトを改善:
{
    "name": "get_body_logs",
    "description": "Get user's PERSONAL body weight logs.
                    Use when asking about THEIR weight, not ideal weight"
}

# 再テスト
質問: "理想的な体重は？"
→ search_knowledge_base() ✅ 正しい！

# 学び: 2つのツールだけなので、どちらの説明が悪いか一目瞭然
```

→ **2日でツール説明を最適化、95%成功率**

---

**ステップ3: 2つ目のツール追加（2日）**
```python
# Coach Agent v0.3 - ツール3つ
tools = [
    {"name": "search_knowledge_base", ...},
    {"name": "get_body_logs", ...},
    {
        "name": "get_nutrition_logs",
        "description": "Get user's nutrition logs"  # 初期説明
    }
]

# テスト
質問: "今週のカロリー摂取量は？"
→ ❌ search_knowledge_base() を呼んでしまう

# プロンプトを改善:
{
    "name": "search_knowledge_base",
    "description": "Search GENERAL fitness knowledge.
                    NOT for user's personal data"  # ← 重要な追加
}

# 再テスト
→ get_nutrition_logs() ✅ 正しい！

# 学び: 新ツール追加時、既存ツールの説明も調整が必要
#       でも3つだけなので調整は簡単
```

→ **2日で3ツール体制が安定**

---

**ステップ4-7: 残り4ツールを順次追加（各2日）**
```python
# 同じプロセスを繰り返す:
v0.4: + get_workout_logs()
v0.5: + get_user_profile()
v0.6: + get_nutrition_recommendation()
v0.7: + get_training_summary()

# 各追加時:
1. 新ツールの説明を書く
2. テストする
3. 誤爆があれば説明を調整
4. 既存ツールの説明も必要なら調整
5. 全ツールで再テスト

# ツール数が増えても、1つずつ追加なので調整可能
```

---

**🎯 深い教訓:**

「なぜ『全部一度に』は失敗したのか？」

**問題の本質: ツール説明の相互干渉**

```
7つのツール × 曖昧な説明 = 無限の組み合わせ

どの説明を直せばいいか分からない:
- ツールAの説明を改善 → ツールBが誤爆
- ツールBの説明を改善 → ツールCが呼ばれなくなる
- 全部変える → 何が効いたのか不明

→ デバッグ不可能
```

**なぜ『小さく始める』は成功したのか？**

**1. ツール説明を1つずつ最適化できる**
```
v0.1: ツール1つ  → 説明の良し悪しがすぐ分かる ✅
v0.2: ツール2つ  → どちらの説明が悪いか一目瞭然 ✅
v0.3: ツール3つ  → 新ツールと既存ツールの調整が簡単 ✅
...
v0.7: ツール7つ  → 全ての説明が最適化済み ✅

結果: ツール呼び出し成功率 40% → 95%
```

**2. LLMの挙動は予測不可能 = テストしないと分からない**
```
理論: 「"PERSONAL" というキーワードで区別できるはず」
現実: 「やっぱり混乱する、"Use when asking about THEIR..." に変更」

→ 実際に動かして初めて分かる
→ 1-2ツールずつテストすれば即座にフィードバック
```

**3. プロンプトエンジニアリングは反復プロセス**
```
初期説明 → テスト → 失敗 → 改善 → 再テスト → 成功

このサイクルを:
- 7ツール同時: 数週間かかる（問題の切り分けに時間）
- 1ツールずつ: 数時間で完了（問題が明確）
```

**最終結果の比較:**

| 指標 | 全部一度に（失敗） | 小さく始める（成功） |
|------|------------------|-------------------|
| 開発時間 | 2週間 | **3+2×6 = 15日** |
| ツール成功率 | **40%** | **95%** |
| デバッグ時間 | 数日/問題 | **数時間/問題** |
| プロンプト調整 | ほぼ不可能 | **段階的に最適化** |
| 最終品質 | ❌ 不安定 | **✅ 堅牢** |

---

#### ✅ 解決策（30秒）

**実践: 段階的なツール追加 + プロンプト最適化**

**構築プロセス:**
```
各バージョンでやること:
1. 新しいツールを1つ追加
2. ツール説明を書く（初期版）
3. テストする（10-20パターン）
4. 誤爆を分析 → 説明を改善
5. 既存ツールの説明も必要なら調整
6. 全ツールで再テスト → 95%以上になるまで繰り返す
7. 次のツール追加へ

v0.1 (3日):  RAG のみ              → 成功率100% ✅
v0.2 (2日):  + get_body_logs       → 成功率95% ✅
v0.3 (2日):  + get_nutrition_logs  → 成功率95% ✅
v0.4 (2日):  + get_workout_logs    → 成功率95% ✅
v0.5-v0.7:   + 残り3ツール          → 各95% ✅
---------------------------------------------------
合計 15日で全機能完成、ツール成功率95%
（当初: 2週間、成功率40%）
```

**実際のプロンプト改善例:**
```python
# v0.2: 初期版
"Get user's body weight logs"
→ テスト: "理想的な体重は？" → ❌ このツールを呼ぶ（間違い）

# 改善版1
"Get user's PERSONAL body weight logs"
→ まだ誤爆 ❌

# 改善版2
"Get user's PERSONAL body weight logs.
Use when asking about THEIR weight, not ideal weight"
→ 成功 ✅

# v0.3: search_knowledge_base も調整
"Search GENERAL fitness knowledge. NOT for user's personal data"
→ さらに明確化、誤爆が減る ✅
```

**最終結果:**
- 開発期間: 2週間（失敗） → **15日で完成**（成功）
- ツール成功率: 40% → **95%**
- プロンプト調整: 不可能 → **段階的に最適化**

**🎯 教訓: 「トップダウンで一度に全て構築しようとせず、ボトムアップで一歩一歩構築する」**

LLMの挙動は予測不可能。実際に動かして初めて分かる。
小さく始めれば、テスト → 改善のサイクルが高速で回る。
一歩一歩積み上げることで、最終的により堅牢なシステムに。

---

### 📋 ステップ3: デプロイ（2分）

---

#### 📊 Slide 1: 手順 + 重要な原則（30秒）

**デプロイフェーズ（3ステップ）:**
1. **アプリケーションをパッケージ化** - コンテナ化、依存関係を含める
   - *例: Docker イメージで全 Python 依存関係を含める*

2. **インフラをコード化** - IaC（Infrastructure as Code）で再現可能に
   - *例: Terraform で Lambda、DynamoDB、S3、CloudFront を定義*

3. **デプロイを自動化** - スクリプトで一貫性のあるデプロイを実現
   - *例: deploy.sh でビルド → アップロード → HTML 構造変換を自動化*

**⚠️ 重要な原則:**
**「ローカルとクラウドの違いを理解する」**

---

#### 📊 Slide 2: 私の失敗事例（1分）

**陥った罠:**
- ローカル環境で完璧に動いていたので、「そのままデプロイすれば動くだろう」と思い込んでいた
- フレームワーク（Next.js、FastAPI）が開発時に多くの処理を自動で隠蔽していることを理解していなかった
- ローカルとクラウド（AWS Lambda、S3、DynamoDB）の根本的な違いを軽視していた

---

**❌ 3つの主要な問題**

ローカルで完璧に動いていたコードをデプロイ...

```python
# ローカル開発環境
db = JSONDatabase(data_dir="data/tracking")
profile = db.find_one("user_profiles", {"user_id": "test"})
logs = db.find("nutrition_logs", {"user_id": "test"})
# ✅ 完璧に動く！
```

デプロイして Lambda で実行 → **エラー連発 😱**

**問題1: データベース接続エラー**
```python
Error: "No such file or directory: data/tracking"
```
- ローカル: JSON ファイル（`data/tracking/*.json`）で動作
- Lambda: ファイルシステムがなく、DynamoDB が必要
- → コードがそのまま動かない ❌

**問題2: データ型エラー**
```python
Error: "Object of type Decimal is not JSON serializable"
```
- DynamoDB が返すデータ: `Decimal` 型（AWS 特有）
- JSON シリアライズ: `int/float` が必要
- → API レスポンスがエラー ❌

**問題3: SPA ルーティング 404**
```
ブラウザアクセス: /calculator
S3 の実際のファイル: calculator.html ❌
S3 が期待するパス: calculator/index.html ✅
```
- Next.js ビルド: `calculator.html` を生成
- S3/CloudFront: `/calculator` → `calculator/index.html` を期待
- → 全ページで 404 エラー ❌

**共通原因:**
フレームワーク/ローカル環境が隠蔽している処理を理解していなかった

---

#### 📊 Slide 3: 解決策 + 教訓（1分30秒）

**✅ 3つの解決策**

**解決策1: デュアルモードデータベースラッパー（問題1対応）**

環境変数で自動的に適切な DB を選択:

```python
# database.py (モジュールの最後)
import os

USE_DYNAMODB = os.getenv('USE_DYNAMODB', 'false').lower() == 'true'

if USE_DYNAMODB:
    from dynamodb_adapter import DynamoDBAdapter
    db = DynamoDBAdapter()  # 本番 → DynamoDB
    print("✅ Using DynamoDB for tracking data")
else:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, "data", "tracking")
    db = JSONDatabase(data_dir=data_path)  # ローカル → JSON
    print("✅ Using JSON files for tracking data")
```

**使用側のコードは環境非依存:**
```python
# server.py
from database import db  # ← 環境に応じて自動で適切な db が入る

# どこでも同じコード
profile = db.find_one("user_profiles", {"user_id": "test"})
logs = db.find("nutrition_logs", {"user_id": "test"})
# ✅ ローカルでも Lambda でも同じコードで動く！
```

---

**解決策2: Decimal 型自動変換（問題2対応）**

DynamoDB が返す `Decimal` 型を `int/float` に変換:

```python
# dynamodb_adapter.py
from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):
    """Decimal を float に変換"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class DynamoDBAdapter:
    def _convert_from_dynamodb(self, data: Dict) -> Dict:
        """DynamoDB 型を Python 型に変換"""
        return json.loads(json.dumps(data, cls=DecimalEncoder))

    def find_one(self, collection: str, query: Dict):
        table = self._get_table(collection)
        response = table.get_item(Key={"user_id": query["user_id"]})
        if 'Item' in response:
            # ⚠️ Decimal を自動変換
            return self._convert_from_dynamodb(response['Item'])
```

**結果:**
- Before: `{"calories": Decimal('2640')}` → JSON シリアライズエラー ❌
- After: `{"calories": 2640}` → 正常に動作 ✅

---

**解決策3: デプロイスクリプトで HTML 構造変換（問題3対応）**

Next.js ビルド後に S3 用の構造に自動変換:

```bash
# scripts/deploy.sh

# Next.js ビルド
cd frontend && npm run build && cd out

# S3/CloudFront 用に構造変換
for page in calculator chatbot workout-planner; do
  if [ -f "$page.html" ]; then
    mkdir -p "$page"
    cp "$page.html" "$page/index.html"  # ← 自動修正
  fi
done

# S3 にアップロード
aws s3 sync . s3://bucket-name/ --delete
```

**結果:**
```
Before: calculator.html → /calculator で 404 ❌
After:  calculator/index.html → /calculator で OK ✅
```

---

**🎯 教訓: 「ローカルとクラウドの違いを理解する」**

**問題の本質:**
- フレームワーク/ローカル環境が多くの処理を隠蔽している
- ローカル: ファイルシステム、Python 型、フレームワークが自動処理
- クラウド: DynamoDB、Decimal 型、S3 は静的ファイルのみ

**解決のポイント:**
1. **環境の違いを明確に理解する**（ローカル vs クラウドで何が違う？）
2. **抽象化レイヤーで差異を吸収**（自動判定、自動変換）
3. **デプロイスクリプトで自動修正**（手動作業ゼロ、再現性確保）

→ 同じコードがローカルでもクラウドでも動くようになる ✅

---

#### 📝 デプロイフェーズまとめ

**陥った罠:**
- ローカル環境で完璧に動いていたので、「そのままデプロイすれば動くだろう」と思い込んでいた
- フレームワーク（Next.js、FastAPI）が開発時に多くの処理を自動で隠蔽していることを理解していなかった
- ローカルとクラウド（AWS Lambda、S3、DynamoDB）の根本的な違いを軽視していた

**発生した問題:**
- **問題1 - データベース接続エラー**: ローカルは JSON ファイル（`data/tracking/*.json`）で動作、Lambda にはファイルシステムがなく DynamoDB が必要。コードがそのまま動かない。
- **問題2 - データ型エラー**: DynamoDB が返す `Decimal` 型を JSON シリアライズできず、`Object of type Decimal is not JSON serializable` エラー。API レスポンスが失敗。
- **問題3 - SPA ルーティング 404**: Next.js が生成する `calculator.html` を S3 が `/calculator` でアクセスできない（`calculator/index.html` が必要）。全ページで 404 エラー。

**解決策:**
- **解決策1 - デュアルモードデータベースラッパー**: `database.py` で環境変数 `USE_DYNAMODB` をチェック。True なら `DynamoDBAdapter`、False なら `JSONDatabase` を `db` として export。使用側は `from database import db` で環境非依存。
- **解決策2 - Decimal 型自動変換**: `DynamoDBAdapter` 内で `DecimalEncoder` を使い、DynamoDB の `Decimal` 型を `float` に自動変換。全ての読み取り操作で適用され、JSON シリアライズエラーを解消。
- **解決策3 - デプロイスクリプトで HTML 構造変換**: Next.js ビルド後に `calculator.html` → `calculator/index.html` へ自動変換。S3 アップロード前に処理、手動作業ゼロ。

---

## 6. まとめ & 学び（1分）

### 🎯 3つの重要な教訓

**1. 問題から始める、手段から始めない**
- ❌ 「AIエージェントだから全部LLM」
- ✅ 「この問題は何？→ 最適な解決策は？」
- 結果: Nutrition/Training で月額$30-50削減、100%の信頼性

**2. トップダウンで一度に全て構築しようとせず、ボトムアップで一歩一歩構築する**
- ❌ 「7ツール一度に実装」→ ツール成功率40%、デバッグ不可能
- ✅ 「1ツールずつ追加 + プロンプト最適化」
- 結果: 成功率40% → 95%、開発15日で完成

**3. ローカルとクラウドの違いを理解する**
- フレームワークが隠蔽している処理を理解する
- 本番の挙動を事前に確認
- デプロイスクリプトで差異を自動解決

### 💡 今後やりたいこと

- Motivator Agent の実装（習慣化支援）
- Workout Planner を決定論的アルゴリズムに置き換え
- コスト最適化（OpenSearchの削減）

### 🔗 リソース

- **GitHub**: (リンク)
- **デプロイ済みアプリ**: (AWSリンク)
- **技術ドキュメント**: REPOSITORY_WALKTHROUGH.md

---

## 📝 プレゼン準備チェックリスト

### 🎯 練習

- [ ] 全体を**3回通しで練習**（15分以内に収める）
- [ ] 各教訓セクションを**2-3分で話せるように**
- [ ] スライド切り替えタイミングを確認

### 📊 資料準備

- [ ] システム全体図（1枚）
- [ ] LLM vs 決定論的の比較表（1枚）
- [ ] Before/After比較（S3構造など、1枚）
- [ ] スクリーンショット（3枚：チャット、栄養、ワークアウト）
- [ ] 技術スタック表（1枚）

**合計: 15-20スライド推奨**

### 🔗 確認事項

- [ ] デモデータを最新に更新
- [ ] GitHubリンク、AWSリンク確認
- [ ] スライド内の用語説明準備（RAG、Lambda、DynamoDBなど）

### 💬 想定質問（プレゼン後のQ&A用）

**Q: なぜLangChainを使わなかった？**
A: このアプリの要件はシンプル。FastAPI + OpenAI SDKで十分だった。不要な抽象化を避けることで、デバッグも簡単に。

**Q: コストはどのくらい？**
A: 月額約$15（OpenSearch $7、Lambda $2.5、DynamoDB $0.8、その他）。

**Q: なぜ決定論的アルゴリズムを選んだ？**
A: 栄養・トレーニング進捗は科学的ルールに従う。LLMは不要で、100%の信頼性とゼロコストを実現できた。

**Q: 一番苦労した点は？**
A: RAG品質の調整。埋め込み次元、チャンクサイズ、検索パラメータのチューニングに時間がかかった。

**Q: 2ヶ月で作れたコツは？**
A: AI コーディングアシスタント（Claude Code）の活用。実装速度10倍。ただし設計判断は人間がやるべき。

---

## 🎤 オープニング例（30秒）

> 「フィットネス業界は情報過多です。
>
> 『朝食は抜くべき？』『タンパク質は何グラム？』『糖質制限しないと痩せない？』
>
> 誰もが混乱しています。
>
> そこで私は、科学的根拠に基づき、個人に最適化されたAIエージェントを**2ヶ月で**構築しました。
>
> 今日はその構築プロセスで得た、**失敗から学んだ教訓**をシェアします。」

---

**Good luck with your presentation! 🎤**
