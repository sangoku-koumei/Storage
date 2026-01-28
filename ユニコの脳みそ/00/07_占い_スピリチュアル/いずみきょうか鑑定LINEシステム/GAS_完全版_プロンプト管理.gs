/**
 * 完全版プロンプト管理スクリプト
 * 
 * セットアップ手順：
 * 1. このファイル全体をコピー
 * 2. Google Apps Scriptエディタに貼り付け
 * 3. 各getPrompt関数の中身を、対応するtxtファイルの内容に置き換える
 * 4. importPrompts()を実行
 */

// ======================
// メイン関数
// ======================

/**
 * プロンプトをスプレッドシートにインポート
 */
function importPrompts() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('ai_prompts') || ss.insertSheet('ai_prompts');
  
  // シートをクリア
  sheet.clear();
  
  // ヘッダー行を設定
  const headers = ['prompt_id', 'prompt_type', 'product_id', 'title', 'content', 'active', 'sort_order', 'notes'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  // プロンプトデータ
  const prompts = [
    {
      prompt_id: 'prompt_free_001',
      prompt_type: 'love_reading',
      product_id: 'FREE_001',
      title: '溺愛され体験無料鑑定プロンプト',
      content: getPromptFree001(),
      active: true,
      sort_order: 1,
      notes: '無料鑑定・溺愛体験（500文字）'
    },
    {
      prompt_id: 'prompt_paid_5000',
      prompt_type: 'love_reading',
      product_id: 'PAID_5000',
      title: '彼の本心リーディング鑑定プロンプト',
      content: getPromptPaid5000(),
      active: true,
      sort_order: 2,
      notes: '有料鑑定5000円・彼の本心（2000-3000文字）'
    },
    {
      prompt_id: 'prompt_paid_10000',
      prompt_type: 'love_reading',
      product_id: 'PAID_10000',
      title: '溺愛スイッチ発動鑑定プロンプト',
      content: getPromptPaid10000(),
      active: true,
      sort_order: 3,
      notes: '有料鑑定10000円・溺愛スイッチ（5000-8000文字）'
    },
    {
      prompt_id: 'prompt_paid_30000',
      prompt_type: 'love_reading',
      product_id: 'PAID_30000',
      title: '溺愛体質完全変換・運命転換鑑定プロンプト',
      content: getPromptPaid30000(),
      active: true,
      sort_order: 4,
      notes: '最高級鑑定30000円・溺愛体質変換（10000文字以上）'
    },
    {
      prompt_id: 'prompt_subscription',
      prompt_type: 'love_reading',
      product_id: 'SUBSCRIPTION_MONTHLY',
      title: '溺愛サポート月次配信プロンプト',
      content: getPromptSubscription(),
      active: true,
      sort_order: 5,
      notes: 'サブスク月次配信（1500-2000文字）'
    }
  ];
  
  // データを挿入
  const data = prompts.map(p => [
    p.prompt_id,
    p.prompt_type,
    p.product_id,
    p.title,
    p.content,
    p.active,
    p.sort_order,
    p.notes
  ]);
  
  sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  
  // フォーマット調整
  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, 4);
  sheet.setColumnWidth(5, 800); // content列を広く
  
  Logger.log('プロンプトのインポートが完了しました！');
  SpreadsheetApp.getUi().alert('プロンプトのインポートが完了しました！');
}

/**
 * 商品IDからプロンプトを取得（自動鑑定で使用）
 */
function getPromptByProductId(productId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('ai_prompts');
  
  if (!sheet) {
    Logger.log('ai_promptsシートが見つかりません');
    return null;
  }
  
  const data = sheet.getDataRange().getValues();
  
  // ヘッダーを除いて検索
  for (let i = 1; i < data.length; i++) {
    if (data[i][2] === productId && data[i][5] === true) { // product_idとactiveをチェック
      return {
        prompt_id: data[i][0],
        content: data[i][4]
      };
    }
  }
  
  Logger.log('プロンプトが見つかりません: ' + productId);
  return null;
}

// ======================
// プロンプト取得関数
// ======================

/**
 * 無料鑑定プロンプト
 * 👇 prompt_FREE_001.txtの内容をここに貼り付けてください
 */
function getPromptFree001() {
  return `
【ここにprompt_FREE_001.txtの内容を貼り付け】

手順：
1. prompt_FREE_001.txtを開く
2. 全文をコピー
3. この文字列の中に貼り付ける
4. バッククォート（` ` `）で囲まれていることを確認
`;
}

/**
 * 5000円鑑定プロンプト
 * 👇 prompt_PAID_5000.txtの内容をここに貼り付けてください
 */
function getPromptPaid5000() {
  return `
【ここにprompt_PAID_5000.txtの内容を貼り付け】
`;
}

/**
 * 10000円鑑定プロンプト
 * 👇 prompt_PAID_10000.txtの内容をここに貼り付けてください
 */
function getPromptPaid10000() {
  return `
【ここにprompt_PAID_10000.txtの内容を貼り付け】
`;
}

/**
 * 30000円鑑定プロンプト
 * 👇 prompt_PAID_30000.txtの内容をここに貼り付けてください
 */
function getPromptPaid30000() {
  return `
【ここにprompt_PAID_30000.txtの内容を貼り付け】
`;
}

/**
 * サブスク配信プロンプト
 * 👇 prompt_SUBSCRIPTION_MONTHLY.txtの内容をここに貼り付けてください
 */
function getPromptSubscription() {
  return `
【ここにprompt_SUBSCRIPTION_MONTHLY.txtの内容を貼り付け】
`;
}

// ======================
// テスト関数
// ======================

/**
 * プロンプト取得のテスト
 */
function testGetPrompt() {
  const prompt = getPromptByProductId('FREE_001');
  
  if (prompt) {
    Logger.log('プロンプトID: ' + prompt.prompt_id);
    Logger.log('内容（最初の100文字）: ' + prompt.content.substring(0, 100));
  } else {
    Logger.log('プロンプトが見つかりませんでした');
  }
}






