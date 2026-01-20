/**
 * SNS Auto Report Dashboard Script
 * 役割: スプレッドシートにSNSのフォロワー・エンゲージメントを毎日記録し、月末にAI考察を生成する。
 * Usage: Google Apps Script (GAS) にコピペして、トリガーを「毎日」に設定してください。
 */

// ==========================================
// 設定エリア (Configuration)
// ==========================================
const CONFIG = {
  SHEET_ID: 'YOUR_SPREADSHEET_ID_HERE', // スプレッドシートのID
  SHEET_NAME: 'Daily_Log',              // シート名
  OPENAI_API_KEY: 'YOUR_OPENAI_API_KEY' // OpenAI API Key (AI考察用)
};

// ==========================================
// メイン関数 (Main Function)
// トリガー設定: 毎日 夜間に実行
// ==========================================
function dailyReport() {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  
  // シートがなければ作成
  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAME);
    sheet.appendRow(['Date', 'Followers', 'Engagement', 'Notes']); // ヘッダー
  }

  const today = new Date();
  
  // 1. データ取得 (Data Fetching)
  // 本来はInstagram Graph APIを叩くが、プロトタイプではシミュレーション値を生成
  const stats = fetchMockStats(); 
  
  // 2. ログ保存 (Log Saving)
  sheet.appendRow([today, stats.followers, stats.engagement, '']);
  
  // 3. AI考察 (AI Analysis) - 月末のみ実行
  if (isEndOfMonth(today)) {
    const analysis = generateAIAnalysis(stats);
    // その日のNotes列に書き込む
    const lastRow = sheet.getLastRow();
    sheet.getRange(lastRow, 4).setValue(analysis);
  }
}

// ------------------------------------------
// ヘルパー関数群 (Helpers)
// ------------------------------------------

/**
 * モックデータを生成する関数
 * 実装時はここをUrlFetchApp.fetch()でGraph APIを叩く処理に変える
 */
function fetchMockStats() {
  // フォロワー数が少しずつ増減するシミュレーション
  const baseFollowers = 1200;
  const randomFluctuation = Math.floor(Math.random() * 20) - 5; // -5 to +14
  
  return {
    followers: baseFollowers + randomFluctuation,
    engagement: Math.floor(Math.random() * 50) + 10 // 10-60 likes
  };
}

/**
 * 月末判定ロジック
 */
function isEndOfMonth(date) {
  const tomorrow = new Date(date);
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.getDate() === 1;
}

/**
 * AIによる考察生成 (擬似)
 * OpenAI APIを使って、その月の傾向を分析させる
 */
function generateAIAnalysis(stats) {
  // ここで本来はUrlFetchAppでOpenAI APIを叩く
  // プロトタイプなので固定テキストを返す
  return `【AI自動考察】\n今月はフォロワーが${stats.followers}人に達しました。\n特に後半の投稿の反応率が高く、共感系コンテンツが寄与しています。来月はリールを強化しましょう。`;
}
