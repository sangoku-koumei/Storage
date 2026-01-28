/**
 * 【コピペするだけ】最小限の自動鑑定コード
 * 既存のCode.gsの最後に追加してください
 */

// ============================================
// プロンプト取得
// ============================================

function getPromptByProductId(productId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('ai_prompts');
  const data = sheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][2] === productId && data[i][5] === true) {
      return data[i][4]; // E列：content
    }
  }
  return null;
}

// ============================================
// 自動鑑定メイン
// ============================================

function generateReading(productId, customerData) {
  // 1. プロンプトを取得
  const prompt = getPromptByProductId(productId);
  if (!prompt) {
    Logger.log('プロンプトが見つかりません: ' + productId);
    return null;
  }
  
  // 2. プレースホルダーを置換
  let filled = prompt
    .replace(/{顧客名}/g, customerData.name || '')
    .replace(/{生年月日}/g, customerData.birthdate || '')
    .replace(/{性別}/g, customerData.gender || '')
    .replace(/{選択肢}/g, customerData.choice || '')
    .replace(/{彼の名前}/g, customerData.hisName || '')
    .replace(/{彼の生年月日}/g, customerData.hisBirthdate || '')
    .replace(/{恋愛状況}/g, customerData.situation || '')
    .replace(/{悩みの詳細}/g, customerData.problem || '')
    .replace(/{質問事項}/g, customerData.question || '');
  
  // 3. ChatGPT APIを呼び出し
  return callChatGPT(filled);
}

// ============================================
// ChatGPT API
// ============================================

function callChatGPT(prompt) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY');
  
  if (!apiKey) {
    Logger.log('APIキーが設定されていません。setApiKey()を実行してください。');
    return null;
  }
  
  const url = 'https://api.openai.com/v1/chat/completions';
  
  const payload = {
    model: 'gpt-4',
    messages: [{role: 'user', content: prompt}],
    temperature: 0.7,
    max_tokens: 4000
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {'Authorization': 'Bearer ' + apiKey},
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    const result = JSON.parse(response.getContentText());
    
    if (result.error) {
      Logger.log('APIエラー: ' + result.error.message);
      return null;
    }
    
    return result.choices[0].message.content;
  } catch (error) {
    Logger.log('エラー: ' + error);
    return null;
  }
}

// ============================================
// APIキー設定（最初に1回だけ実行）
// ============================================

function setApiKey() {
  const apiKey = Browser.inputBox('ChatGPT APIキーを入力してください');
  PropertiesService.getScriptProperties().setProperty('OPENAI_API_KEY', apiKey);
  SpreadsheetApp.getUi().alert('APIキーを設定しました！');
}

// ============================================
// テスト用
// ============================================

function testGenerateReading() {
  const customerData = {
    name: 'テスト太郎',
    birthdate: '1990年1月1日',
    gender: '男性',
    choice: 'A'
  };
  
  Logger.log('鑑定生成開始...');
  const reading = generateReading('FREE_001', customerData);
  
  if (reading) {
    Logger.log('=== 鑑定結果 ===');
    Logger.log(reading);
  } else {
    Logger.log('鑑定生成に失敗しました');
  }
}





