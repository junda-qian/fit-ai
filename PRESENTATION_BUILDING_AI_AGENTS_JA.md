# コーディングアシスタントを使ったAIエージェント構築: 実践的な旅

## 📋 ステップ1: 設計

### 実施方法

**1. エージェントの責任範囲を定義**
- 異なるドメインを識別（Coach、Nutrition、Training）
- ユーザーニーズをエージェント機能にマッピング
- エージェント間の相互作用パターンを設計

**2. 適切なLLMを選択**
- 各ユースケースに応じてモデルを評価
- コストと品質のトレードオフを検討
- モデルプロバイダーの多様性を計画

**3. データアーキテクチャの設計**
- ユーザージャーニーからデータ要件をマッピング
- アクセスパターンを考慮したデータベーススキーマ設計
- 会話メモリとコンテキストの管理計画

**4. インフラの概要設計**
- デプロイメントプラットフォームを選択（サーバーレス vs コンテナ）
- スケーラビリティとコスト最適化を計画
- APIアーキテクチャを設計

### 注意すべき点（教訓）

**❌ 失敗1: すべてにAIが必要だと思い込む**
- **問題**: Energy Calculatorを「インテリジェント」な計算のためにLLMを使う設計をした
- **現実**: TDEE計算は確立された公式を使用（Cunningham BMR）
- **解決策**: 決定論的なPythonコードを使用 - より高速、安価、信頼性が高い
- **教訓**: LLM使用を決める前に「これは本当にAIが必要か？」と問う

```python
# ❌ 間違い: 決定論的な計算に高価なLLMを使用
bedrock.converse("Calculate my TDEE based on 70kg, 175cm...")

# ✅ 正解: 公式を直接使用
def calculate_cunningham_bmr(fat_free_mass_kg: float) -> float:
    return 370 + (21.6 * fat_free_mass_kg)
```

**❌ 失敗2: 決定論的アルゴリズムで十分な場合にAIを使用**
- **問題**: 当初Nutrition/Training分析にBedrock Novaを使用する計画だった
- **コスト問題**: 週次自動分析で月額$30-50かかる予定だった
- **現実確認**: 栄養/トレーニング進捗は確立されたルールに従う
- **解決策**: ハイブリッド戦略
  - **OpenAI GPT-4**: Coach Agent（会話品質が重要）
  - **Bedrock Nova**: Workout Plannerのみ（創造的な計画はAIの恩恵を受ける）
  - **決定論的アルゴリズム**: Nutrition/Training Specialists（100%信頼性、$0コスト）
- **教訓**: 各コンポーネントが実際にAIを必要とするか疑問を持つ - 決定論的コードの方が優れていることが多い

**❌ 失敗3: 不完全なエージェントトリガー設計**
- **問題**: Training Agentを「イベント駆動のみ」として設計
- **ギャップ**: ワークアウトしないユーザーの週次トレンド分析が欠落
- **解決策**: デュアルトリガーパターン
  1. **ワークアウト後トリガー**: 即座のセッションフィードバック
  2. **週次スケジュール**: 月曜日5:55 AM UTCでトレンド分析
- **教訓**: リアクティブとプロアクティブの両方のエージェント動作を検討

**❌ 失敗4: データアクセスパターンの計画不足**
- **問題**: GSI（グローバルセカンダリインデックス）なしでDynamoDBをクエリ
- **結果**: 高コストなテーブルスキャン、遅いクエリ
- **解決策**: 事前に4つのGSIパターンを設計:
  - `UserIdDateIndex` (nutrition_logs, workout_logs, body_logs)
  - `UserIdIndex` (workout_plans, user_exercises)
  - `UserIdWeekIndex` (training_progress_summaries)
  - `UserIdCreatedAtIndex` (training_recommendations)
- **教訓**: DynamoDBクエリパターンは構築前に設計する必要がある

**🔧 Claude Codeの活用方法:**
- **Claudeに依頼**: 「エージェント要件を分析してLLM選択を提案して」
- **Claudeに依頼**: 「[ユースケース]のアクセスパターンを考慮したDynamoDBスキーマを設計して」
- **Claudeに依頼**: 「この設計をレビューして - AIが必要なものと決定論的コードで十分なものを教えて」

---

## 🛠️ ステップ2: 構築

### 実施方法

**1. 開発環境のセットアップ**
- ローカルバックエンド（FastAPI + FAISS）
- ローカルフロントエンド（Next.js開発サーバー）
- 環境変数管理

**2. AIエージェントの実装**
- 明確なインターフェースを持つエージェントクラス作成
- ツール/関数呼び出しの実装
- RAGパイプライン構築（埋め込み + ベクトル検索）

**3. APIレイヤーの構築**
- 各機能のFastAPIエンドポイント
- リクエスト/レスポンス検証
- エラーハンドリングとリトライ

**4. フロントエンド開発**
- コンポーネントベースUI（React）
- API統合
- 状態管理

### 注意すべき点（教訓）

**❌ 失敗1: Lambdaパッケージサイズの爆発**
- **問題**: 初期Lambdaパッケージ = 1.2GB（250MB制限を大幅に超過）
- **原因**: 開発ツールを含むすべての依存関係をインストール
- **解決策**: 別の`requirements-lambda.txt`を作成
  - 除外: `pytest`, `black`, `mypy`, 開発ツール
  - 公式Lambda Python 3.12イメージでDockerを使用
  - プラットフォーム固有ビルド: `--platform manylinux2014_x86_64`
- **最終サイズ**: 247MB（制限内！）
- **教訓**: Lambdaには厳しいサイズ制限がある - 早期に依存関係を最適化

```python
# backend/deploy.py
subprocess.run([
    "docker", "run", "--rm",
    "-v", f"{os.getcwd()}:/var/task",
    "--platform", "linux/amd64",  # ✅ Lambda互換性に必須
    "public.ecr.aws/lambda/python:3.12",
    "/bin/sh", "-c",
    "pip install --target /var/task/lambda-package -r /var/task/requirements-lambda.txt --platform manylinux2014_x86_64 --only-binary=:all:"
], check=True)
```

**❌ 失敗2: LLM API呼び出しのハードコーディング**
- **問題**: 初期プロトタイプでOpenAI SDKと密結合したコード
- **課題**: プロバイダー切り替えや決定論的コードへの移行に書き直しが必要
- **解決策**: AIコンポーネントと非AIコンポーネントの明確な分離

```python
# ❌ 間違い: アルゴリズムで十分な場合にLLMをハードコーディング
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "最適な赤字を計算..."}]
)

# ✅ 正解: 栄養分析のための決定論的アルゴリズム
class NutritionSpecialist:
    def analyze(self, user_profile, weight_trend, nutrition_summary):
        # 純粋なPython - LLM不要！
        maintenance = estimate_maintenance_calories(
            nutrition_summary.avg_calories,
            weight_trend.weekly_rate_pct
        )
        optimal_deficit = calculate_optimal_deficit(
            user_profile.body_fat_pct,
            user_profile.sex
        )
        # 構造化された推奨事項を返す（100%信頼性）
```

**❌ 失敗3: RAGコンテキスト品質の不足**
- **問題**: RAGが無関係な医学文書を返す
- **デバッグ**:
  1. 埋め込みモデルを確認（間違った次元数を使用していた）
  2. チャンクサイズを検証（1000文字が一部のコンテンツには大きすぎた）
  3. デバッグ用のソース追跡を追加
- **解決策**:
  - Bedrock Titan V1を使用（1536次元）
  - チャンクサイズを1000文字、200文字オーバーラップに削減
  - メタデータ追加: `{source, page, chunk_id}`
- **教訓**: RAG品質は埋め込み + チャンキング + 検索チューニングに依存

**❌ 失敗4: 非同期エージェントのエラーハンドリング不足**
- **問題**: Nutrition Agentが月曜日に黙って失敗
- **原因**: 欠落したユーザーデータ（14日未満のログを持つ新規ユーザー）
- **解決策**: グレースフルデグラデーションを追加

```python
# ✅ 適切なエラーハンドリング
try:
    nutrition_data = fetch_last_14_days(user_id)
    if len(nutrition_data) < 7:
        return {
            "status": "insufficient_data",
            "message": "分析には最低7日分のログが必要です"
        }
    analysis = agent.analyze(nutrition_data)
except Exception as e:
    logger.error(f"Nutrition agent failed: {e}")
    return {"status": "error", "message": str(e)}
```

**❌ 失敗5: Workout Plannerの幻覚**
- **問題**: AIが無効なエクササイズ名を生成
- **課題**: LLM出力の検証なし
- **解決策**: 検証ループ付きリトライ（最大5回試行）

```python
# ai_agents/workout_planner.py
for attempt in range(max_retries):
    plan = self.call_bedrock_for_workout(prompt)

    # ✅ 既知のエクササイズデータベースと照合検証
    validation = self.validate_workout_plan(plan, exercise_config)

    if validation["is_valid"]:
        return plan
    else:
        # 検証エラーをプロンプトに追加してリトライ
        prompt += f"\n前回の試行が失敗: {validation['errors']}"
```

**🔧 Claude Codeの活用方法:**
- **Claudeに依頼**: 「RAGが無関係な結果を返す理由をデバッグして」
- **Claudeに依頼**: 「複数のLLMプロバイダーをサポートするようにリファクタリングして」
- **Claudeに依頼**: 「このAPI呼び出しに指数バックオフ付きリトライロジックを追加して」

---

## 🚀 ステップ3: デプロイ

### 実施方法

**1. Lambda用コンテナ化**
- 公式AWS Lambdaベースイメージを使用
- プラットフォーム固有の依存関係をビルド
- デプロイパッケージを作成

**2. Infrastructure as Code（Terraform）**
- すべてのAWSリソースを定義
- 環境管理（dev/prod）
- インフラのバージョン管理

**3. デプロイの自動化**
- 再現可能なデプロイ用ビルドスクリプト
- 環境設定管理
- フロントエンドの静的エクスポートをS3へ

**4. モニタリング設定**
- CloudWatchログ
- エラー追跡
- パフォーマンスメトリクス

### 注意すべき点（教訓）

**❌ 失敗1: Next.jsルーティングがS3/CloudFrontで壊れる**
- **問題**: `/calculator` → CloudFrontで404エラー
- **原因**: Next.jsは`calculator.html`を出力するが、S3は`calculator/index.html`を期待
- **CloudFrontの動作**: `calculator`をディレクトリとして提供しようとする
- **解決策**: ビルド後スクリプトでディレクトリ構造を修正

```bash
# scripts/deploy.sh - フロントエンドデプロイ修正
cd out
for page in calculator chatbot workout-planner; do
  if [ -f "$page.html" ]; then
    mkdir -p "$page"
    cp "$page.html" "$page/index.html"  # ✅ S3ルーティング修正
  fi
done
```

**修正前:**
```
out/
├── calculator.html     ❌ CloudFrontがルーティングできない
├── chatbot.html
└── index.html
```

**修正後:**
```
out/
├── calculator/
│   └── index.html      ✅ /calculator → calculator/index.html
├── chatbot/
│   └── index.html      ✅ /chatbot → chatbot/index.html
└── index.html
```

**❌ 失敗2: Terraform Destroyが空でないS3バケットで失敗**
- **問題**: S3バケットにオブジェクトが含まれているため`terraform destroy`がエラー
- **AWSポリシー**: 空でないバケットは削除できない
- **解決策**: 破棄前のバケット空化スクリプト

```bash
# scripts/destroy.sh
echo "📦 S3バケットを空にしています..."
for bucket in frontend memory documents; do
    aws s3 rm "s3://${BUCKET_NAME}/" --recursive
    echo "✓ $bucket バケットを空にしました"
done

terraform destroy -auto-approve
```

**❌ 失敗3: 環境変数の混乱**
- **問題**: 本番フロントエンドがlocalhostのAPIを呼び出す
- **原因**: 本番ビルド用の`NEXT_PUBLIC_API_URL`を設定し忘れ
- **影響**: ユーザーに空白ページが表示（CORSエラー）
- **解決策**: デプロイスクリプトで環境を自動注入

```bash
# scripts/deploy.sh
API_URL=$(terraform output -raw api_gateway_url)

# ✅ ビルド前に本番環境ファイルを作成
echo "NEXT_PUBLIC_API_URL=$API_URL" > frontend/.env.production

cd frontend
npm run build  # 正しいAPI URLを使用
```

**❌ 失敗4: Lambdaコールドスタートタイムアウト**
- **問題**: 5分以上後の最初のリクエスト → 30秒タイムアウト
- **原因**: 大きなLambdaパッケージ（247MB）のコールドスタートに約10秒
- **初期タイムアウト**: 30秒（不十分）
- **解決策**: 120秒に増加

```hcl
# terraform/main.tf
resource "aws_lambda_function" "api" {
  timeout = 120  # ✅ 30秒から増加
  memory_size = 1024  # 高速初期化のためメモリも増加
}
```

**❌ 失敗5: Terraformワークスペース管理の欠落**
- **問題**: `terraform apply`が本番デプロイ中にdev環境を上書き
- **解決策**: 適切なワークスペース分離

```bash
# scripts/deploy.sh
ENVIRONMENT=${1:-dev}

if ! terraform workspace list | grep -q "$ENVIRONMENT"; then
  terraform workspace new "$ENVIRONMENT"  # ✅ 欠落している場合は作成
else
  terraform workspace select "$ENVIRONMENT"  # ✅ 正しい環境に切り替え
fi

terraform apply -var="environment=$ENVIRONMENT"
```

**❌ 失敗6: Lambdaデプロイパッケージが更新されない**
- **問題**: 新しいコードをデプロイしたが、Lambdaは古いバージョンを実行
- **原因**: Terraformがs3オブジェクトの変更を検出しない（同じファイル名）
- **解決策**: MD5ハッシュを追加して更新をトリガー

```hcl
# terraform/main.tf
resource "aws_lambda_function" "api" {
  s3_bucket = aws_s3_bucket.documents.id
  s3_key    = aws_s3_object.lambda_zip.key

  source_code_hash = filebase64sha256("${path.module}/../backend/lambda-deployment.zip")  # ✅ 変更時に強制更新
}
```

**🔧 Claude Codeの活用方法:**
- **Claudeに依頼**: 「CloudFrontルートが404を返す理由をデバッグして」
- **Claudeに依頼**: 「dev/prod環境を処理するデプロイスクリプトを作成して」
- **Claudeに依頼**: 「最初のリクエストでLambdaがタイムアウトする理由は？」

---

## 🔄 ステップ4: 保守と運用

### 実施方法

**1. アプリケーションヘルスの監視**
- CloudWatchログ分析
- エラー追跡とアラート
- パフォーマンスメトリクスレビュー

**2. デモ/テストデータの管理**
- デモデータを新鮮でリアルに保つ
- データ生成の自動化
- 定期的なデータリセット

**3. コスト最適化**
- AWS請求のレビュー
- リソース使用の最適化
- 未使用リソースの停止

**4. ドキュメントと知識共有**
- アーキテクチャドキュメントの維持
- オンボーディング資料の作成
- 学んだ教訓の文書化

### 注意すべき点（教訓）

**❌ 失敗1: 古いデモデータ**
- **問題**: デモユーザーが12/11のデータを表示しているが、日付は12/14
- **影響**: 古いデータでプレゼンテーションが不専門に見える
- **原因**: 数週間前の手動データ挿入
- **解決策**: 定期的なデータ更新ワークフロー

```bash
# ✅ 自動化されたデモデータ更新
python3 scripts/reset_demo_data.py    # 古いデータをクリア
sleep 5                                 # DynamoDBを待機
python3 scripts/insert_sample_data_to_dynamodb.py  # 新しいデータを挿入
```

**教訓**: デモデータはライフサイクル管理が必要 - 自動化しよう！

**❌ 失敗2: 並行データ操作による重複**
- **問題**: リセットと挿入スクリプトを同時実行 → データ重複
- **症状**: 「1週間に2週間分のデータ」
- **解決策**: 適切な待機を伴う順次実行

```bash
# ❌ 間違い: 並列実行
python3 reset_demo_data.py &
python3 insert_sample_data.py &

# ✅ 正解: 待機を伴う順次実行
python3 reset_demo_data.py && sleep 5 && python3 insert_sample_data.py
```

**❌ 失敗3: 各サービスの役割を忘れる**
- **問題**: 2ヶ月後、プレゼンテーション用のアーキテクチャを思い出すのが困難
- **解決策**: 3つのドキュメントファイルを作成
  1. `ARCHITECTURE_SLIDE.md` - ビジュアル図 + AWSリソース
  2. `REQUEST_FLOW.md` - ステップバイステップのリクエストトレース
  3. `REPOSITORY_WALKTHROUGH.md` - 完全なコードベースガイド

**教訓**: 構築中に文書化、後でではない - 未来の自分が感謝します！

**❌ 失敗4: コスト帰属の不明確さ**
- **問題**: AWS請求書に$15 - しかし何が高価？
- **初期推測**: Lambda呼び出し
- **現実**: OpenSearch Serverless（月額$7のアイドルコスト）
- **解決策**:
  - 請求コンソールで各サービスコストをレビュー
  - dev環境でOpenSearchを無効化
  - 開発中はローカルでFAISSを使用

**コスト内訳:**
```
OpenSearch Serverless: $7.20/月（アイドル！）
Lambda: $2.50/月（リクエスト単位課金）
DynamoDB: $0.80/月（リクエスト単位課金）
S3: $0.30/月
CloudFront: $0.00（無料枠）
```

**最適化:**
```bash
# ✅ 本番環境でのみOpenSearchを使用
USE_OPENSEARCH=false  # FAISSを使用したローカル開発
USE_OPENSEARCH=true   # 本番環境のみ
```

**❌ 失敗5: デプロイ履歴追跡なし**
- **問題**: 「どのバージョンがデプロイされている？」 → わからない
- **影響**: ロールバックが容易でない
- **解決策**: Gitタグ + デプロイメントのコミットハッシュ

```bash
# scripts/deploy.sh
COMMIT_HASH=$(git rev-parse --short HEAD)
echo "🚀 コミットをデプロイ中: $COMMIT_HASH"

# 成功したデプロイにタグを付ける
git tag "deploy-prod-$(date +%Y%m%d-%H%M%S)-$COMMIT_HASH"
git push origin --tags
```

**❌ 失敗6: 暗黙知の喪失**
- **問題**: チームメイトが「なぜTraining Agentはデュアルトリガーなの？」と質問
- **元の設計**: 自分の頭の中だけ
- **解決策**: 根拠を含む仕様ドキュメントを更新

```markdown
# docs/agents/TRAINING_AGENT_SPEC.md

## トリガーパターン: デュアルトリガー

**なぜイベント駆動だけではダメか？**
- ワークアウトをスキップするユーザーはフィードバックを得られない

**なぜスケジュールだけではダメか？**
- アクティブユーザーはワークアウト後の即座のインサイトを望む

**解決策: 両方！**
1. イベントトリガー: 即座のセッションフィードバック
2. スケジュールトリガー: 週次トレンド（月曜日5:55 AM UTC）
```

**❌ 失敗7: デモデプロイがローカルと一致しない**
- **問題**: 機能がローカルで動作するが、AWSで壊れる
- **デバッグプロセス**:
  1. CloudWatchログを確認
  2. 環境変数を検証
  3. Lambda関数を直接テスト
  4. IAM権限を確認
- **一般的な原因**:
  - Terraformで環境変数が欠落
  - 誤ったLambdaタイムアウト設定
  - IAMロールにBedrock権限が欠落

**🔧 Claude Codeの活用方法:**
- **Claudeに依頼**: 「AWS請求を分析してコスト最適化を提案して」
- **Claudeに依頼**: 「このアーキテクチャのドキュメントを作成して」
- **Claudeに依頼**: 「デモデータが重複する理由をデバッグして」
- **Claudeに依頼**: 「コードベースからプレゼンテーション資料を生成して」

---

## 🎯 重要なポイント: コーディングアシスタントを使ったAIエージェント構築

### Claude Codeが得意なこと:
1. **アーキテクチャ設計**: 「フィットネスコーチング用のマルチエージェントシステムを設計して」
2. **コード生成**: エージェント、API、インフラの実装
3. **デバッグ**: 「Lambdaがタイムアウトするのはなぜ？」 → 体系的な調査
4. **ドキュメント作成**: コードベースからアーキテクチャ図を自動生成
5. **リファクタリング**: 「複数のLLMプロバイダーで動作するようにして」

### 人間の判断が必要なこと:
1. **ビジネスロジック**: 「Energy CalculatorはAIを使うべき？」 → NO
2. **コストトレードオフ**: 「すべてGPT-4を使う？」 → ハイブリッド戦略
3. **ユーザー体験**: エージェントトリガーパターン、データの新鮮さ
4. **アーキテクチャ決定**: モノリシックLambda vs マイクロサービス

### 機能するワークフロー:
```
1. 人間: ビジネス要件を定義
2. Claude Code: 技術設計を提案
3. 人間: レビュー、改善、承認
4. Claude Code: 実装 + テスト
5. 人間: Claudeの自動化スクリプトでデプロイ
6. 両方: 実際の使用状況に基づいて監視、反復
```

### 最終的な教訓:
**AIコーディングアシスタントはあなたの生産性を増幅するが、あなたがアーキテクトであり続ける。**
- スピードにClaude Codeを使用（10倍高速な実装）
- 決定には人間の監督を維持（コスト、UX、ビジネスロジック）
- すべてを文書化（Claudeはコードからドキュメントを生成できる）
- 実世界のフィードバックに基づいて反復（Claudeは本番問題のデバッグを支援）

---

このプレゼンテーション構成は**実際の開発の物語**を伝え、成功と失敗の両方を示し、FitTracker AIの旅から具体的な例を提供します。「失敗 → 解決策」形式は非常に魅力的で、聴衆に実行可能な教訓を提供します。
