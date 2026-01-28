---
tags: [Guide, Setup, Proline, PayPal, IzumiKyoka, 00]
date: 2026-01-20
source: ユニコの脳みそ/00
aliases: [3_プロライン×PayPal連携ガイド, Proline_PayPal_Setup]
---

# [[00_知識マップ]]
# 3️⃣ プロライン×PayPal決済連携ガイド

**所要時間：45分**

プロライン内でPayPal決済を設定し、Webhook経由でGASに自動連携します。

---

## ✅ このステップでやること

```
☐ PayPalビジネスアカウント作成
☐ プロライン決済機能設定
☐ 商品登録（プロライン内）
☐ GAS Webhook設定
☐ 決済→フォーム送信フロー構築
☐ テスト決済
```

---

## 💡 プロライン決済のメリット

### GAS商品ページ vs プロライン決済

```
【プロライン決済】✅ 推奨
✓ LINE内で完結（シームレス）
✓ 設定が簡単
✓ プロラインで商品管理
✓ 購入者リストが見やすい
✓ リッチメニューから直接決済

【GAS商品ページ】
✓ 完全カスタマイズ可能
✓ 外部サイトとしても使える
△ LINEから外部ブラウザに遷移
△ HTMLコーディングが必要
```

**プロライン決済の方が運用が楽です！**

---

## 💳 Step 3-1: PayPalビジネスアカウント設定（15分）

### 1. PayPalアカウント作成

1. [PayPal Business](https://www.paypal.com/jp/business) にアクセス
2. 「今すぐ登録」をクリック
3. ビジネスアカウントを選択
4. 情報入力：
   ```
   ビジネス名: いずみきょうか占い
   業種: コンサルティング・専門サービス
   メールアドレス: izumi.kyouka.uranai@gmail.com
   ```
5. 本人確認を完了（銀行口座登録）

### 2. PayPal.Me リンク作成（オプション）

簡易決済用：

1. PayPal管理画面 →「PayPal.Me」
2. リンクを作成：`paypal.me/izumikyouka`
3. これで簡易的な決済リンクが完成

### 3. PayPal確認

- [ ] PayPal管理画面にログインできる
- [ ] 銀行口座が登録されている
- [ ] 本人確認が完了している

✅ PayPalアカウント準備完了！

---

## 🔗 Step 3-2: プロライン決済機能設定（20分）

### 1. プロラインフリーの制約確認

**重要**: プロラインフリー（無料プラン）では、**標準の決済機能は使えません**。

以下の方法で対応します：

#### 方法A: PayPal.Me + プロライン（推奨・無料）

```
プロライン
  ↓
PayPal.Me リンクをボタンに設置
  ↓
PayPal決済ページへ遷移
  ↓
決済完了
  ↓
GASに手動またはWebhookで通知
```

#### 方法B: プロラインPro + 決済連携（有料）

```
月額: 無料〜（機能による）

プロラインPro版では：
✓ Stripe決済統合
✓ PayPal連携
✓ Webhook自動送信

※ 本格運用時に検討
```

### 2. PayPal.Me決済ボタンの設置（方法A）

プロライン管理画面で：

#### 商品1: 有料鑑定（基本）- ¥5,000

1. 「商品」→「商品を追加」
2. 商品情報入力：
   ```
   商品名: 有料鑑定（基本）
   価格: ¥5,000
   説明: 30分の詳細鑑定
   ```
3. 「決済リンク」に PayPal.Me を設定：
   ```
   https://paypal.me/izumikyouka/5000
   ```
4. 「購入ボタン」のテキスト：
   ```
   PayPalで決済する
   ```

#### 商品2: 有料鑑定（詳細）- ¥10,000

同様に設定：
```
https://paypal.me/izumikyouka/10000
```

#### 商品3: 恋愛専門鑑定 - ¥8,000

```
https://paypal.me/izumikyouka/8000
```

#### 商品4: 仕事・転職鑑定 - ¥8,000

```
https://paypal.me/izumikyouka/8000
```

#### 商品5: 月次詳細運勢（単発）- ¥3,980

```
https://paypal.me/izumikyouka/3980
```

#### 商品6: 月次詳細運勢（サブスク）- ¥2,980

```
https://paypal.me/izumikyouka/2980
```

**注意**: PayPal.Meのユーザー名「izumikyouka」は、あなたのPayPal.Me IDに置き換えてください。

### PayPal.Meリンク一覧（コピー用）

```
有料鑑定（基本）: https://paypal.me/izumikyouka/5000
有料鑑定（詳細）: https://paypal.me/izumikyouka/10000
恋愛専門鑑定: https://paypal.me/izumikyouka/8000
仕事・転職鑑定: https://paypal.me/izumikyouka/8000
月次詳細（単発）: https://paypal.me/izumikyouka/3980
月次サブスク: https://paypal.me/izumikyouka/2980
```

### 3. 決済完了後のアクション設定

プロラインで「購入後アクション」を設定：

#### オプション1: Googleフォームに誘導

```
決済完了後のメッセージ:

お支払いありがとうございます！

次のステップとして、ご相談内容を
詳しくお聞かせください。

↓ こちらのフォームにご記入ください
[Googleフォーム URL]

※1回のみ回答可能です
```

#### オプション2: GAS Webhookに通知（高度）

プロラインPro版の場合：
```
購入後 → Webhook送信 → GAS
```

### 4. 手動運用フロー（無料プランの場合）

```
1. ユーザーがPayPal決済
2. PayPal管理画面で決済確認
3. 決済者のメールアドレスを確認
4. スプレッドシートに手動で記録：
   - payments シートに決済記録
   - users シートにユーザー登録
   - applications シートに申込み記録
5. フォームトークン生成（GAS関数実行）
6. メール送信（自動）
```

**or**

```
Code.gs に「手動決済記録」関数を追加（後述）
→ スプシに1行追加するだけで自動処理
```

✅ プロライン決済設定完了！

---

## 🔧 Step 3-3: GAS Webhook受信設定（10分）

### 1. doPost()関数の修正

`Code.gs` の `doPost()` 関数を、プロラインのデータ形式に対応させます：

```javascript
/**
 * Webhook受信（プロライン対応版）
 */
function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    
    // プロラインからのWebhook
    if (payload.source === 'proline') {
      handleProlineWebhook_(payload);
    }
    // 独自PayPal Webhook
    else if (payload.type === 'payment_completed') {
      handlePayPalPayment_(payload);
    }
    
    return ContentService.createTextOutput(JSON.stringify({status: 'success'}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    log_('doPost: エラー - ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({status: 'error', message: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * プロラインWebhookの処理
 */
function handleProlineWebhook_(payload) {
  const eventType = payload.event_type;
  
  if (eventType === 'payment') {
    // 決済完了
    handleProlinePayment_(payload.data);
  } else if (eventType === 'friend_added') {
    // 友だち追加
    handleProlineFriendAdded_(payload.data);
  } else if (eventType === 'survey_answer') {
    // アンケート回答
    handleProlineSurveyAnswer_(payload.data);
  }
}

/**
 * プロライン決済の処理
 */
function handleProlinePayment_(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // データ抽出
  const userName = data.user_name || '';
  const userEmail = data.user_email || '';
  const birthDate = data.birth_date || '';
  const lineId = data.line_id || '';
  const productName = data.product_name || '';
  const amount = data.amount || 0;
  const transactionId = data.transaction_id || '';
  
  // ユーザー登録
  let userId = getUserByEmail_(userEmail) || getUserByLineId_(lineId);
  if (!userId) {
    userId = 'USER_' + Utilities.getUuid();
    ss.getSheetByName('users').appendRow([
      userId, userName, userEmail, birthDate, lineId, new Date(), false, 'プロライン決済'
    ]);
  }
  
  // 商品ID取得
  const productId = getProductIdByName_(productName);
  
  // 決済記録
  const paymentId = 'PAY_' + transactionId;
  ss.getSheetByName('payments').appendRow([
    paymentId, userId, productId, amount, new Date(), 'completed', userEmail, transactionId, JSON.stringify(data)
  ]);
  
  // 申込み記録
  const appId = 'APP_' + Utilities.getUuid();
  ss.getSheetByName('applications').appendRow([
    appId, userId, '有料鑑定', new Date(), '', '', false, 'プロライン決済', '', productId
  ]);
  
  // フォームトークン生成＆メール送信
  const token = generateFormToken_(userId, '有料鑑定');
  const formURL = generatePaidFormURL_(token);
  
  addToSendQueue_(userId, 'tmpl_paid_form_link', {
    name: userName,
    form_url: formURL
  }, new Date());
  
  // 運営通知
  const config = getConfig_();
  if (config.ops_email) {
    GmailApp.sendEmail(config.ops_email, '[決済完了] 有料鑑定',
      `プロライン決済完了\n\nユーザー: ${userName}\nメール: ${userEmail}\n金額: ¥${amount}\n商品: ${productName}\nトランザクションID: ${transactionId}`);
  }
  
  log_('handleProlinePayment_: 決済処理完了 - ' + paymentId);
}

/**
 * LINE IDでユーザーを取得
 */
function getUserByLineId_(lineId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const userSheet = ss.getSheetByName('users');
  
  if (!userSheet || !lineId) return null;
  
  const data = userSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][4] === lineId) {
      return data[i][0];
    }
  }
  
  return null;
}

/**
 * 商品名から商品IDを取得
 */
function getProductIdByName_(productName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const productSheet = ss.getSheetByName('products');
  
  if (!productSheet) return 'PROD_001';
  
  const data = productSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][1] === productName || productName.includes(data[i][1])) {
      return data[i][0];
    }
  }
  
  return 'PROD_001'; // デフォルト
}
```

### 2. GASをWebアプリとしてデプロイ

1. Apps Script エディタで「デプロイ」→「新しいデプロイ」
2. 種類：**ウェブアプリ**
3. 設定：
   ```
   説明: プロラインWebhook受信
   次のユーザーとして実行: 自分
   アクセスできるユーザー: 全員
   ```
4. **デプロイ**をクリック
5. **Webhook URL**をコピー：
   ```
   https://script.google.com/macros/s/ABC123.../exec
   ```

### 3. プロラインにWebhook設定

#### プロラインPro版の場合

1. プロライン管理画面 →「設定」→「Webhook」
2. Webhook URLを貼り付け
3. イベント選択：「決済完了」
4. 保存

#### プロライン無料版の場合

Webhookは使えないので、以下の代替案：

**代替案1: 手動記録補助関数**

Apps Script エディタで以下の関数を追加：

```javascript
/**
 * PayPal決済を手動で記録（簡易版）
 */
function recordPayPalPaymentManually() {
  const ui = SpreadsheetApp.getUi();
  
  // ユーザー情報を入力
  const userName = ui.prompt('お名前を入力').getResponseText();
  const userEmail = ui.prompt('メールアドレスを入力').getResponseText();
  const birthDate = ui.prompt('生年月日を入力（YYYY-MM-DD）').getResponseText();
  const productName = ui.prompt('商品名を入力（例：有料鑑定（基本））').getResponseText();
  const amount = ui.prompt('金額を入力（例：5000）').getResponseText();
  const transactionId = ui.prompt('PayPal取引IDを入力').getResponseText();
  
  // データ作成
  const payload = {
    type: 'payment_completed',
    user: { name: userName, email: userEmail, birth_date: birthDate },
    product: { 
      id: getProductIdByName_(productName),
      name: productName,
      price: parseInt(amount)
    },
    paypal: { order_id: transactionId }
  };
  
  // 既存の処理を実行
  handlePayPalPayment_(payload);
  
  ui.alert('記録完了', 'フォームURL案内メールが送信されます。', ui.ButtonSet.OK);
}
```

**使い方**：
1. PayPal管理画面で決済を確認
2. Apps Script で `recordPayPalPaymentManually` を実行
3. ダイアログで情報を入力
4. 自動処理が開始される

**代替案2: manual_payments シートで管理**

1. `manual_payments` シートを作成
2. 決済情報を1行追加
3. tick()で自動処理

```javascript
/**
 * manual_payments シートを確認して処理
 */
function processManualPayments_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const manualSheet = ss.getSheetByName('manual_payments');
  
  if (!manualSheet) return;
  
  const data = manualSheet.getDataRange().getValues();
  const headers = data[0];
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const processed = row[headers.indexOf('processed')];
    
    if (processed) continue;
    
    // データ抽出
    const userName = row[headers.indexOf('name')];
    const userEmail = row[headers.indexOf('email')];
    const birthDate = row[headers.indexOf('birth_date')];
    const productName = row[headers.indexOf('product_name')];
    const amount = row[headers.indexOf('amount')];
    const transactionId = row[headers.indexOf('transaction_id')];
    
    // 処理
    const payload = {
      type: 'payment_completed',
      user: { name: userName, email: userEmail, birth_date: birthDate },
      product: { 
        id: getProductIdByName_(productName),
        name: productName,
        price: amount
      },
      paypal: { order_id: transactionId }
    };
    
    handlePayPalPayment_(payload);
    
    // processed フラグ
    manualSheet.getRange(i + 1, headers.indexOf('processed') + 1).setValue(true);
  }
}
```

**tick()に追加**：

```javascript
function tick() {
  // ...
  processScheduledAIReadings_();
  processManualPayments_(); // ← 追加
  processSendQueue_();
  // ...
}
```

✅ プロライン決済設定完了！

---

## 📋 Step 3-4: manual_payments シート作成（方法2を使う場合）

### シート作成

1. 新しいシート追加
2. 名前を `manual_payments` に変更
3. ヘッダー行：

```
name	email	birth_date	product_name	amount	transaction_id	paid_at	processed
```

### 使い方

PayPal決済が入ったら：

1. PayPal管理画面で決済を確認
2. `manual_payments` シートに1行追加：

```
山田花子	hanako@example.com	1990-05-15	有料鑑定（基本）	5000	8AB123456...	2025-11-03 14:30	FALSE
```

3. 保存
4. 1分以内に自動処理される：
   - users に登録
   - payments に記録
   - applications に記録
   - フォームURL送信
   - processed が TRUE に更新

✅ 手動決済記録フロー完成！

---

## 🧪 Step 3-5: テスト実行（10分）

### テストフロー

#### 1. manual_payments でテスト

`manual_payments` シートに以下を追加：

```
テスト太郎	test@example.com	1990-01-01	有料鑑定（基本）	5000	TEST_001	2025-11-03 10:00	FALSE
```

#### 2. 1分待つ

tick()が実行されるのを待つ

#### 3. 確認

- [ ] users シートに「テスト太郎」が追加された
- [ ] payments シートに決済記録が追加された
- [ ] applications シートに申込みが記録された
- [ ] form_tokens シートにトークンが生成された
- [ ] send_queue シートにメールキューが追加された
- [ ] preview_to にメールが届いた
- [ ] メール内のフォームURLにアクセスできる
- [ ] manual_payments の processed が TRUE になった

✅ すべてOKならテスト成功！

---

## 🎯 完了チェックリスト

プロライン×PayPal連携が完了したか確認：

- [ ] PayPalビジネスアカウント作成済み
- [ ] PayPal.Me リンク作成済み
- [ ] プロラインに商品登録済み
- [ ] PayPal.Me リンク設置済み
- [ ] GAS doPost()関数更新済み
- [ ] GAS Webアプリデプロイ済み
- [ ] manual_payments シート作成済み（方法2の場合）
- [ ] processManualPayments_()をtick()に追加済み
- [ ] テスト実行成功

**すべて✅なら次へ！**

---

## 📌 重要な設定まとめ

### PayPal.Me リンク

```
基本鑑定（¥5,000）:
https://paypal.me/izumikyouka/5000

詳細鑑定（¥10,000）:
https://paypal.me/izumikyouka/10000

恋愛専門（¥8,000）:
https://paypal.me/izumikyouka/8000
```

### GAS Webhook URL

```
https://script.google.com/macros/s/ABC123.../exec
```

### 運用フロー

```
【プロライン無料版の場合】
決済確認（PayPal管理画面）
  ↓
manual_payments に1行追加
  ↓
自動処理開始

【プロラインPro版の場合】
決済完了
  ↓
Webhook → GAS
  ↓
自動処理開始
```

---

## 🆘 トラブルシューティング

### Q: manual_payments に追加しても処理されない

**対処**:
- [ ] processManualPayments_() が tick() に追加されているか確認
- [ ] processed が FALSE になっているか確認
- [ ] トリガーが設定されているか確認

### Q: フォームURLが届かない

**対処**:
- [ ] send_queue シートにキューが追加されているか確認
- [ ] form_tokens シートにトークンが生成されているか確認
- [ ] preview_mode が TRUE なら preview_to を確認

### Q: PayPal.Me リンクが機能しない

**対処**:
- [ ] PayPal.Me が有効になっているか確認
- [ ] リンクの金額が正しいか確認
- [ ] PayPalアカウントが本人確認済みか確認

---

## ✨ 次のステップ

プロライン×PayPal連携が完了しました！

**→ [4_LINE完全統合ガイド.md](./4_LINE完全統合ガイド.md) へ進む**

次は、LINEリッチメニューとすべてを統合します！

