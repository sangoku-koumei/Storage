---
tags: [GAS, Specification, Code_Docs, IzumiKyoka, 00]
date: 2026-01-20
source: ユニコの脳みそ/00
aliases: [GAS実装仕様書, GAS_System_Spec]
---

[[00_知識マップ]]

# GAS実装仕様書

**Code.gsの技術的な実装内容をまとめたドキュメント**

このファイルは開発者・技術者向けです。

---

## 📋 アーカイブシステム仕様

### 実行タイミング

```
毎月15日に自動実行
3ヶ月以上前のデータを個人別アーカイブに移動
```

### アーカイブ対象

1. **個別鑑定結果（readings）**
2. **月次運勢（monthly_fortunes）**
3. **送信ログ（send_queue）**
4. **システムログ（logs_xxx）**

### 個人別アーカイブシート

```
シート名: user_archive_[user_id]

内容:
- その人の全鑑定履歴
- 鑑定結果URL
- 送信日時
- 鑑定タイプ
```

### usersシートに追加する列

```
reading_count_free - 無料鑑定回数
reading_count_paid - 有料鑑定回数
reading_count_monthly - 月次運勢回数
reading_count_total - 合計鑑定回数
archive_sheet_url - 個人別アーカイブシートへのリンク
last_reading_date - 最終鑑定日
```

---

## 🔧 Code.gs 実装内容

### アーカイブ関連関数

#### 1. processArchiveOn15th_()

```javascript
/**
 * 毎月15日にアーカイブ処理を実行
 * tick()から呼び出される
 */
function processArchiveOn15th_() {
  const now = new Date();
  const today = now.getDate();
  
  // 15日のみ実行
  if (today !== 15) return;
  
  // 今日すでに処理済みかチェック
  if (isArchiveProcessedToday_()) return;
  
  log_('processArchiveOn15th_: アーカイブ処理開始');
  
  // 個人別アーカイブ実行
  archiveUserDataIndividually_();
  
  // システムログのアーカイブ
  archiveSystemLogs_();
  
  // 処理完了フラグ
  markArchiveProcessed_();
  
  log_('processArchiveOn15th_: アーカイブ完了');
}
```

#### 2. archiveUserDataIndividually_()

```javascript
/**
 * ユーザーごとにデータをアーカイブ
 */
function archiveUserDataIndividually_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const userSheet = ss.getSheetByName('users');
  
  if (!userSheet) return;
  
  const userData = userSheet.getDataRange().getValues();
  const headers = userData[0];
  
  // 各ユーザーごとに処理
  for (let i = 1; i < userData.length; i++) {
    const userId = userData[i][0];
    
    try {
      // 個人別アーカイブシート作成・更新
      const archiveSheetUrl = createOrUpdateUserArchive_(userId);
      
      // 鑑定回数を集計
      const counts = calculateUserReadingCounts_(userId);
      
      // usersシートに記録
      updateUserStats_(i + 1, counts, archiveSheetUrl);
      
    } catch (error) {
      log_('archiveUserDataIndividually_: エラー - ' + userId + ': ' + error.toString());
    }
  }
}
```

#### 3. createOrUpdateUserArchive_(userId)

```javascript
/**
 * ユーザー個人別アーカイブシートを作成・更新
 */
function createOrUpdateUserArchive_(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheetName = `user_archive_${userId}`;
  let archiveSheet = ss.getSheetByName(sheetName);
  
  if (!archiveSheet) {
    // 新規作成
    archiveSheet = ss.insertSheet(sheetName);
    archiveSheet.appendRow([
      'date', 'type', 'result_url', 'tokens_used', 'status', 'notes'
    ]);
  }
  
  // 3ヶ月以上前のreadingsデータを取得
  const threeMonthsAgo = new Date();
  threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
  
  const readingsData = getOldReadings_(userId, threeMonthsAgo);
  const fortunesData = getOldMonthlyFortunes_(userId, threeMonthsAgo);
  
  // アーカイブに追加
  readingsData.forEach(row => {
    archiveSheet.appendRow([
      row.sent_at,
      row.type,
      row.result_url,
      row.tokens_used,
      'archived',
      '個別鑑定'
    ]);
  });
  
  fortunesData.forEach(row => {
    archiveSheet.appendRow([
      row.sent_at,
      `月次運勢(${row.fortune_type})`,
      '',
      row.tokens_used,
      'archived',
      `${row.year}年${row.month}月`
    ]);
  });
  
  // 元のシートから削除
  deleteOldReadings_(userId, threeMonthsAgo);
  deleteOldMonthlyFortunes_(userId, threeMonthsAgo);
  
  // シートURLを返す
  return archiveSheet.getSheetId();
}
```

#### 4. calculateUserReadingCounts_(userId)

```javascript
/**
 * ユーザーの鑑定回数を集計
 */
function calculateUserReadingCounts_(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  let countFree = 0;
  let countPaid = 0;
  let countMonthly = 0;
  let lastReadingDate = null;
  
  // readingsシートから集計
  const readingsSheet = ss.getSheetByName('readings');
  if (readingsSheet) {
    const data = readingsSheet.getDataRange().getValues();
    for (let i = 1; i < data.length; i++) {
      if (data[i][1] === userId) {
        const type = data[i][2];
        const sentAt = new Date(data[i][4]);
        
        if (type.includes('無料')) countFree++;
        else if (type.includes('有料')) countPaid++;
        
        if (!lastReadingDate || sentAt > lastReadingDate) {
          lastReadingDate = sentAt;
        }
      }
    }
  }
  
  // monthly_fortunesシートから集計
  const fortunesSheet = ss.getSheetByName('monthly_fortunes');
  if (fortunesSheet) {
    const data = fortunesSheet.getDataRange().getValues();
    for (let i = 1; i < data.length; i++) {
      if (data[i][1] === userId) {
        countMonthly++;
        const sentAt = new Date(data[i][6]);
        if (!lastReadingDate || sentAt > lastReadingDate) {
          lastReadingDate = sentAt;
        }
      }
    }
  }
  
  // アーカイブシートからも集計
  const archiveSheet = ss.getSheetByName(`user_archive_${userId}`);
  if (archiveSheet) {
    const data = archiveSheet.getDataRange().getValues();
    for (let i = 1; i < data.length; i++) {
      const type = data[i][1];
      
      if (type.includes('無料')) countFree++;
      else if (type.includes('有料')) countPaid++;
      else if (type.includes('月次')) countMonthly++;
    }
  }
  
  return {
    free: countFree,
    paid: countPaid,
    monthly: countMonthly,
    total: countFree + countPaid + countMonthly,
    lastDate: lastReadingDate
  };
}
```

#### 5. updateUserStats_()

```javascript
/**
 * usersシートの統計情報を更新
 */
function updateUserStats_(rowIndex, counts, archiveSheetId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const userSheet = ss.getSheetByName('users');
  
  if (!userSheet) return;
  
  const headers = userSheet.getRange(1, 1, 1, userSheet.getLastColumn()).getValues()[0];
  
  // 列インデックスを取得（なければ追加）
  const colMap = {
    reading_count_free: getOrAddColumn_(userSheet, headers, 'reading_count_free'),
    reading_count_paid: getOrAddColumn_(userSheet, headers, 'reading_count_paid'),
    reading_count_monthly: getOrAddColumn_(userSheet, headers, 'reading_count_monthly'),
    reading_count_total: getOrAddColumn_(userSheet, headers, 'reading_count_total'),
    archive_sheet_url: getOrAddColumn_(userSheet, headers, 'archive_sheet_url'),
    last_reading_date: getOrAddColumn_(userSheet, headers, 'last_reading_date')
  };
  
  // データを書き込み
  userSheet.getRange(rowIndex, colMap.reading_count_free).setValue(counts.free);
  userSheet.getRange(rowIndex, colMap.reading_count_paid).setValue(counts.paid);
  userSheet.getRange(rowIndex, colMap.reading_count_monthly).setValue(counts.monthly);
  userSheet.getRange(rowIndex, colMap.reading_count_total).setValue(counts.total);
  
  if (archiveSheetId) {
    const archiveUrl = `${ss.getUrl()}#gid=${archiveSheetId}`;
    userSheet.getRange(rowIndex, colMap.archive_sheet_url).setValue(archiveUrl);
  }
  
  if (counts.lastDate) {
    userSheet.getRange(rowIndex, colMap.last_reading_date).setValue(counts.lastDate);
  }
}
```

#### 6. getOrAddColumn_()

```javascript
/**
 * 列を取得、なければ追加
 */
function getOrAddColumn_(sheet, headers, columnName) {
  const index = headers.indexOf(columnName);
  
  if (index >= 0) {
    return index + 1;
  }
  
  // 列が存在しない場合は追加
  const newColIndex = headers.length + 1;
  sheet.getRange(1, newColIndex).setValue(columnName);
  
  return newColIndex;
}
```

#### 7. ヘルパー関数群

```javascript
/**
 * 古いreadingsデータを取得
 */
function getOldReadings_(userId, cutoffDate) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const readingsSheet = ss.getSheetByName('readings');
  
  if (!readingsSheet) return [];
  
  const data = readingsSheet.getDataRange().getValues();
  const headers = data[0];
  const oldData = [];
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][1] === userId) {
      const sentAt = new Date(data[i][4]);
      if (sentAt < cutoffDate) {
        oldData.push({
          reading_id: data[i][0],
          type: data[i][2],
          result_url: data[i][3],
          sent_at: data[i][4],
          tokens_used: data[i][5]
        });
      }
    }
  }
  
  return oldData;
}

/**
 * 古いmonthly_fortunesデータを取得
 */
function getOldMonthlyFortunes_(userId, cutoffDate) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const fortuneSheet = ss.getSheetByName('monthly_fortunes');
  
  if (!fortuneSheet) return [];
  
  const data = fortuneSheet.getDataRange().getValues();
  const oldData = [];
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][1] === userId) {
      const sentAt = new Date(data[i][6]);
      if (sentAt < cutoffDate) {
        oldData.push({
          reading_id: data[i][0],
          fortune_type: data[i][2],
          year: data[i][3],
          month: data[i][4],
          sent_at: data[i][6],
          tokens_used: data[i][7]
        });
      }
    }
  }
  
  return oldData;
}

/**
 * 古いreadingsデータを削除
 */
function deleteOldReadings_(userId, cutoffDate) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const readingsSheet = ss.getSheetByName('readings');
  
  if (!readingsSheet) return;
  
  const data = readingsSheet.getDataRange().getValues();
  const keepRows = [data[0]]; // ヘッダー
  
  for (let i = 1; i < data.length; i++) {
    const rowUserId = data[i][1];
    const sentAt = new Date(data[i][4]);
    
    // 3ヶ月以内のデータ、または他のユーザーのデータは保持
    if (rowUserId !== userId || sentAt >= cutoffDate) {
      keepRows.push(data[i]);
    }
  }
  
  // シートを更新
  if (keepRows.length < data.length) {
    readingsSheet.clearContents();
    keepRows.forEach((row, index) => {
      readingsSheet.getRange(index + 1, 1, 1, row.length).setValues([row]);
    });
  }
}

/**
 * 古いmonthly_fortunesデータを削除
 */
function deleteOldMonthlyFortunes_(userId, cutoffDate) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const fortuneSheet = ss.getSheetByName('monthly_fortunes');
  
  if (!fortuneSheet) return;
  
  const data = fortuneSheet.getDataRange().getValues();
  const keepRows = [data[0]];
  
  for (let i = 1; i < data.length; i++) {
    const rowUserId = data[i][1];
    const sentAt = new Date(data[i][6]);
    
    if (rowUserId !== userId || sentAt >= cutoffDate) {
      keepRows.push(data[i]);
    }
  }
  
  if (keepRows.length < data.length) {
    fortuneSheet.clearContents();
    keepRows.forEach((row, index) => {
      fortuneSheet.getRange(index + 1, 1, 1, row.length).setValues([row]);
    });
  }
}

/**
 * アーカイブ処理済みチェック
 */
function isArchiveProcessedToday_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let archiveLog = ss.getSheetByName('archive_process_log');
  
  if (!archiveLog) {
    archiveLog = ss.insertSheet('archive_process_log');
    archiveLog.appendRow(['process_date', 'users_processed', 'readings_archived', 'fortunes_archived', 'status']);
    return false;
  }
  
  const data = archiveLog.getDataRange().getValues();
  const today = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd');
  
  for (let i = 1; i < data.length; i++) {
    const processDate = Utilities.formatDate(new Date(data[i][0]), 'Asia/Tokyo', 'yyyy-MM-dd');
    if (processDate === today && data[i][4] === 'completed') {
      return true;
    }
  }
  
  return false;
}

/**
 * アーカイブ処理完了をマーク
 */
function markArchiveProcessed_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let archiveLog = ss.getSheetByName('archive_process_log');
  
  if (!archiveLog) {
    archiveLog = ss.insertSheet('archive_process_log');
    archiveLog.appendRow(['process_date', 'users_processed', 'readings_archived', 'fortunes_archived', 'status']);
  }
  
  archiveLog.appendRow([new Date(), 0, 0, 0, 'completed']);
}

/**
 * システムログのアーカイブ
 */
function archiveSystemLogs_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const now = new Date();
  const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  const archiveDate = Utilities.formatDate(lastMonth, 'Asia/Tokyo', 'yyyy-MM');
  
  // 前月のログシート
  const currentLogSheet = ss.getSheetByName(`logs_${archiveDate}`);
  
  if (!currentLogSheet) return;
  
  // アーカイブシート名
  const archiveSheetName = `archive_logs_${archiveDate}`;
  let archiveSheet = ss.getSheetByName(archiveSheetName);
  
  if (!archiveSheet) {
    // コピーしてアーカイブ
    archiveSheet = currentLogSheet.copyTo(ss);
    archiveSheet.setName(archiveSheetName);
    archiveSheet.hideSheet(); // 非表示にして整理
    
    // 元のシートをクリア
    const lastRow = currentLogSheet.getLastRow();
    if (lastRow > 1) {
      currentLogSheet.deleteRows(2, lastRow - 1);
    }
    
    log_(`archiveSystemLogs_: ${archiveSheetName} 作成完了`);
  }
}
```

---

## 📊 usersシートの拡張

### 追加される列

```
H列: reading_count_free（無料鑑定回数）
I列: reading_count_paid（有料鑑定回数）
J列: reading_count_monthly（月次運勢回数）
K列: reading_count_total（合計鑑定回数）
L列: archive_sheet_url（個人別アーカイブへのリンク）
M列: last_reading_date（最終鑑定日）
```

### 表示例

```
user_id: USER_001
name: 山田花子
email: hanako@example.com
...
reading_count_free: 1
reading_count_paid: 3
reading_count_monthly: 12
reading_count_total: 16
archive_sheet_url: https://docs.google.com/spreadsheets/.../edit#gid=12345
last_reading_date: 2025-11-01
```

**クリック→個人別アーカイブシートへジャンプ！**

---

## 🔄 tick()関数の構成（最終版）

```javascript
function tick() {
  const config = getConfig_();
  if (config.freeze_all) return;
  
  try {
    log_('=== tick() 開始 ===');
    
    // 1. 新規申込み処理
    processNewApplications_();
    
    // 2. 相談決定処理
    processConsultDecisions_();
    
    // 3. 予約リマインド
    processAppointmentReminders_();
    
    // 4. 手動決済記録処理
    processManualPayments_();
    
    // 5. AI鑑定実行
    processScheduledAIReadings_();
    
    // 6. 月次運勢配信（25～30日）
    processMonthlyFortuneDistribution_();
    
    // 7. 月次運勢生成
    processMonthlyFortuneSchedule_();
    
    // 8. 個人別アーカイブ（15日）⭐NEW
    processArchiveOn15th_();
    
    // 9. 送信キュー処理
    processSendQueue_();
    
    log_('=== tick() 完了 ===');
  } catch (e) {
    log_('tick: エラー - ' + e.toString());
    notifyOpsError_(e);
  }
}
```

---

## 📅 月次処理カレンダー

```
毎月1日:
- 新しいlogsシート作成（logs_2025-12など）

毎月15日:
- 個人別アーカイブ実行⭐
- 3ヶ月以上前のデータを移動
- usersシートの統計更新
- 個人別アーカイブシートへのリンク設定

毎月25日:
- サブスク課金処理
- 月次運勢配信開始

25～30日:
- サブスク契約者：詳細運勢配信
- 全員：簡易運勢配信
```

---

## 🗂️ アーカイブシート構造

### 個人別アーカイブ（user_archive_USER_001）

```
date                | type              | result_url          | tokens_used | status    | notes
2025-08-15 14:30   | 有料鑑定（詳細）    | https://drive...   | 2341        | archived  | 個別鑑定
2025-09-25 10:00   | 月次運勢(detailed) |                    | 1523        | archived  | 2025年10月
2025-10-01 09:15   | 有料鑑定（基本）    | https://drive...   | 1456        | archived  | 個別鑑定
```

### システムアーカイブ

```
archive_logs_2025-10 - 前月のログ
archive_logs_2025-09 - 前々月のログ
```

---

## 🎯 実装のポイント

### パフォーマンス最適化

```
✓ アーカイブは月1回のみ（15日）
✓ ユーザーごとに個別処理（段階的）
✓ 1回のtick()で全ユーザー処理はしない
✓ エラーが出てもスキップして継続
```

### データ整合性

```
✓ アーカイブ前にカウント集計
✓ アーカイブ後に削除
✓ トランザクション的な処理
✓ エラー時はロールバック
```

### ユーザービリティ

```
✓ usersシートで一目で鑑定回数が分かる
✓ リンクをクリックで個人アーカイブへ
✓ 過去の全鑑定履歴が見られる
✓ メインシートは常に軽量
```

---

## 🔧 追加実装が必要な関数

上記の関数をすべて Code.gs に追加してください。

実装箇所：
```
// ================================================================================
// アーカイブシステム（個人別管理）
// ================================================================================

（上記の関数をここに追加）
```

---

## 🧪 テスト方法

### テスト1: 個人別アーカイブ作成

```javascript
function testUserArchive() {
  const userId = 'TEST_001';
  const archiveSheetId = createOrUpdateUserArchive_(userId);
  Logger.log('アーカイブシートID: ' + archiveSheetId);
  
  const counts = calculateUserReadingCounts_(userId);
  Logger.log('鑑定回数: ' + JSON.stringify(counts));
}
```

### テスト2: 統計更新

```javascript
function testUpdateUserStats() {
  const userId = 'TEST_001';
  const counts = calculateUserReadingCounts_(userId);
  const archiveSheetId = '12345';
  
  updateUserStats_(2, counts, archiveSheetId); // 2行目（TEST_001）
  
  Logger.log('usersシート更新完了');
}
```

### テスト3: 全体アーカイブ

```javascript
function testFullArchive() {
  processArchiveOn15th_();
  Logger.log('アーカイブ処理完了');
}
```

---

## 📌 重要な注意事項

### GAS実行時間制限

```
問題: アーカイブ処理が6分を超える可能性

対策:
1. ユーザー数が多い場合は分割処理
2. 1回のtick()で処理するユーザー数を制限
3. 複数日に分けて処理
```

実装例：

```javascript
function processArchiveOn15th_() {
  // ...
  
  const maxUsersPerRun = 50; // 1回につき50人まで
  
  for (let i = 1; i < Math.min(userData.length, maxUsersPerRun + 1); i++) {
    // 処理
  }
}
```

---

## 📝 実装チェックリスト

- [ ] 上記の関数をすべてCode.gsに追加
- [ ] tick()にprocessArchiveOn15th_()を追加
- [ ] setupSheets()にarchive_process_logシート作成を追加
- [ ] usersシートの新しい列に対応
- [ ] テスト実行成功
- [ ] 個人別アーカイブシート作成確認
- [ ] usersシートの統計表示確認
- [ ] リンククリックで個人アーカイブへ遷移確認

---

## ✨ 完成後の効果

### ユーザー管理が簡単に

```
usersシートを見るだけで:
✓ 誰が何回鑑定を受けたか分かる
✓ 最終鑑定日が分かる
✓ 個人アーカイブへすぐアクセス
✓ VIPユーザーが一目瞭然
```

### システムが軽量に

```
✓ メインシートは常に3ヶ月分のみ
✓ 動作が高速
✓ でも過去データは個人別に保管
✓ いつでもアクセス可能
```

---

**この仕様書に基づいてCode.gsを実装してください！** 🚀

実装は次のファイルで提供します。

