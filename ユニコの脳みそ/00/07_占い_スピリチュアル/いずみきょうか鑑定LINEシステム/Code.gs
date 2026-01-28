/**
 * 占い師用LINEメールステップ配信システム
 * 
 * メイン処理：tick() を毎分実行して、申込み処理・送信キュー処理等を自動化
 */

// ================================================================================
// グローバル定数
// ================================================================================

const TIMEZONE = 'Asia/Tokyo';
const MAX_EMAILS_PER_DAY = 2;

// 申込みタイプ
const APP_TYPE = {
  FREE_CONSULT: '無料相談',
  FREE_READING: '無料鑑定',
  PAID_READING: '有料鑑定'
};

// 送信ステータス
const SEND_STATUS = {
  PENDING: 'pending',
  SENT: 'sent',
  ERROR: 'error',
  CANCELLED: 'cancelled'
};

// ================================================================================
// メイン処理：定期実行（毎分）
// ================================================================================

/**
 * メインのtick関数
 * トリガーで毎分実行される
 */
function tick() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const config = getConfig_();
  
  // freeze_all が有効なら全処理を停止
  if (config.freeze_all) {
    log_('tick: freeze_all が有効のため、全処理をスキップ');
    return;
  }
  
  try {
    log_('=== tick() 開始 ===');
    
    // 1. 新規申込みの処理
    processNewApplications_();
    
    // 2. 相談決定の処理
    processConsultDecisions_();
    
    // 3. 予約リマインドの処理
    processAppointmentReminders_();
    
    // 4. 手動決済記録の処理
    processManualPayments_();
    
    // 5. AI鑑定スケジュールの処理
    processScheduledAIReadings_();
    
    // 6. 月次運勢配信の処理
    processMonthlyFortuneDistribution_();
    
    // 7. 月次運勢スケジュールの処理
    processMonthlyFortuneSchedule_();
    
    // 8. 個人別アーカイブの処理（毎月15日）⭐
    processArchiveOn15th_();
    
    // 9. 送信キューの処理
    processSendQueue_();
    
    log_('=== tick() 完了 ===');
  } catch (e) {
    log_('tick: エラー - ' + e.toString());
    // 運営にエラー通知（オプション）
    notifyOpsError_(e);
  }
}

// ================================================================================
// 1. 新規申込みの処理
// ================================================================================

/**
 * applications シートの未処理行を確認して、send_queue に追加
 */
function processNewApplications_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const appSheet = ss.getSheetByName('applications');
  const config = getConfig_();
  
  if (!appSheet) {
    log_('processNewApplications_: applications シートが存在しません');
    return;
  }
  
  const data = appSheet.getDataRange().getValues();
  const headers = data[0];
  
  // ヘッダーのインデックスを取得
  const idxId = headers.indexOf('id');
  const idxUserId = headers.indexOf('user_id');
  const idxType = headers.indexOf('type');
  const idxTimestamp = headers.indexOf('timestamp');
  const idxStatus = headers.indexOf('status');
  const idxAcceptReject = headers.indexOf('accept_reject');
  const idxProcessed = headers.indexOf('processed');
  
  // 未処理の行を探す
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const processed = row[idxProcessed];
    
    if (processed === true || processed === 'TRUE' || processed === 1) {
      continue; // すでに処理済み
    }
    
    const appId = row[idxId];
    const userId = row[idxUserId];
    const type = row[idxType];
    const timestamp = row[idxTimestamp];
    
    if (!appId || !userId || !type) {
      continue; // 必須項目が空ならスキップ
    }
    
    log_(`processNewApplications_: 申込み処理開始 - appId=${appId}, userId=${userId}, type=${type}`);
    
    // 受付可否の判定
    const acceptReject = judgeApplication_(userId, type, timestamp);
    
    // applications シートに結果を書き込み
    appSheet.getRange(i + 1, idxAcceptReject + 1).setValue(acceptReject);
    appSheet.getRange(i + 1, idxStatus + 1).setValue(acceptReject === 'OK' ? '受付' : '拒否');
    
    if (acceptReject === 'OK') {
      // OK の場合：各種処理
      handleAcceptedApplication_(appId, userId, type, timestamp);
    } else {
      // NG の場合：拒否理由の通知（オプション）
      handleRejectedApplication_(appId, userId, type, acceptReject);
    }
    
    // processed フラグを立てる
    appSheet.getRange(i + 1, idxProcessed + 1).setValue(true);
  }
}

/**
 * 申込み受付可否の判定
 */
function judgeApplication_(userId, type, timestamp) {
  const user = getUser_(userId);
  if (!user) {
    return 'NG_USER_NOT_FOUND';
  }
  
  // 配信停止フラグチェック
  if (user.unsubscribed) {
    return 'NG_UNSUBSCRIBED';
  }
  
  const state = getUserState_(userId);
  const now = new Date();
  
  if (type === APP_TYPE.FREE_READING) {
    // 無料鑑定：登録から7日以内、かつ1人1回
    const registeredAt = new Date(user.registered_at);
    const daysSinceReg = (now - registeredAt) / (1000 * 60 * 60 * 24);
    
    if (daysSinceReg > 7) {
      return 'NG_EXPIRED_7DAYS';
    }
    
    // すでに無料鑑定を受けたかチェック
    if (hasReceivedFreeReading_(userId)) {
      return 'NG_ALREADY_USED';
    }
    
    return 'OK';
    
  } else if (type === APP_TYPE.FREE_CONSULT) {
    // 無料相談：ロック中または無断キャンセル歴がないかチェック
    if (state.consult_locked) {
      return 'NG_CONSULT_LOCKED';
    }
    
    if (state.no_show_flag) {
      return 'NG_NO_SHOW_HISTORY';
    }
    
    return 'OK';
    
  } else if (type === APP_TYPE.PAID_READING) {
    // 有料鑑定：基本的に常に受付可能
    return 'OK';
  }
  
  return 'NG_UNKNOWN_TYPE';
}

/**
 * 受付OKの場合の処理
 */
function handleAcceptedApplication_(appId, userId, type, timestamp) {
  const config = getConfig_();
  const now = new Date();
  
  if (type === APP_TYPE.FREE_READING) {
    // 無料鑑定の場合
    
    // 1. 受付メールを送信キューに追加
    addToSendQueue_(userId, 'tmpl_free_accept', {
      app_id: appId
    }, now);
    
    // 2. 締切を設定（7日後）
    const deadline = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    setDeadline_(userId, 'reading_deadline', deadline);
    
    // 3. 選定通知を正午にスケジュール（翌日または当日）
    const selectionTime = getNextNoonTime_(now);
    addToSendQueue_(userId, 'tmpl_selected_free', {
      app_id: appId
    }, selectionTime);
    
    // 4. 結果メールを夜帯にスケジュール（選定通知の12時間後）
    const resultTime = new Date(selectionTime.getTime() + 12 * 60 * 60 * 1000);
    addToSendQueue_(userId, 'tmpl_free_result', {
      app_id: appId,
      result_url: '{{result_url}}' // 後で差し替え
    }, resultTime);
    
    log_(`handleAcceptedApplication_: 無料鑑定 - userId=${userId}, 選定=${formatDateTime_(selectionTime)}, 結果=${formatDateTime_(resultTime)}`);
    
  } else if (type === APP_TYPE.FREE_CONSULT) {
    // 無料相談の場合
    
    // 1. 候補3つ依頼メールを送信
    addToSendQueue_(userId, 'tmpl_ask3', {
      app_id: appId
    }, now);
    
    // 2. 締切を設定（48時間後）
    const deadline = new Date(now.getTime() + 48 * 60 * 60 * 1000);
    setDeadline_(userId, 'consult_deadline', deadline);
    
    // 3. ステートをロック
    setUserState_(userId, { consult_locked: true });
    
    // 4. 運営への通知も送信キューに追加
    const opsEmail = config.ops_email;
    if (opsEmail) {
      addToSendQueue_(opsEmail, 'ops_consult_request', {
        app_id: appId,
        user_id: userId
      }, now, true); // true = 運営宛
    }
    
    log_(`handleAcceptedApplication_: 無料相談 - userId=${userId}, 締切=${formatDateTime_(deadline)}`);
    
  } else if (type === APP_TYPE.PAID_READING) {
    // 有料鑑定の場合
    
    // 1. 受付メールを送信
    addToSendQueue_(userId, 'tmpl_paid_accept', {
      app_id: appId
    }, now);
    
    log_(`handleAcceptedApplication_: 有料鑑定 - userId=${userId}`);
  }
}

/**
 * 受付NGの場合の処理
 */
function handleRejectedApplication_(appId, userId, type, reason) {
  log_(`handleRejectedApplication_: 拒否 - appId=${appId}, userId=${userId}, reason=${reason}`);
  // 必要に応じて拒否理由を通知するメールを送信
  // （現在は何もしない）
}

// ================================================================================
// 2. 相談決定の処理
// ================================================================================

/**
 * consult_decisions シートの未処理行を確認して、appointments を作成
 */
function processConsultDecisions_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const decisionSheet = ss.getSheetByName('consult_decisions');
  
  if (!decisionSheet) {
    log_('processConsultDecisions_: consult_decisions シートが存在しません');
    return;
  }
  
  const data = decisionSheet.getDataRange().getValues();
  const headers = data[0];
  
  const idxId = headers.indexOf('id');
  const idxUserId = headers.indexOf('user_id');
  const idxRequestId = headers.indexOf('request_id');
  const idxChosenSlot = headers.indexOf('chosen_slot');
  const idxZoomUrl = headers.indexOf('zoom_url');
  const idxZoomPassword = headers.indexOf('zoom_password');
  const idxProcessed = headers.indexOf('processed');
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const processed = row[idxProcessed];
    
    if (processed === true || processed === 'TRUE' || processed === 1) {
      continue;
    }
    
    const decisionId = row[idxId];
    const userId = row[idxUserId];
    const chosenSlot = row[idxChosenSlot];
    const zoomUrl = row[idxZoomUrl];
    const zoomPassword = row[idxZoomPassword];
    
    if (!decisionId || !userId || !chosenSlot) {
      continue;
    }
    
    log_(`processConsultDecisions_: 相談決定処理 - decisionId=${decisionId}, userId=${userId}`);
    
    // appointments に登録
    const apptTime = new Date(chosenSlot);
    const apptId = createAppointment_(userId, apptTime, zoomUrl, zoomPassword);
    
    // 確定通知メールを送信
    addToSendQueue_(userId, 'tmpl_appt_confirm', {
      appt_id: apptId,
      appt_time: formatDateTime_(apptTime),
      zoom_url: zoomUrl,
      zoom_password: zoomPassword
    }, new Date());
    
    // リマインダーをスケジュール
    scheduleReminders_(userId, apptId, apptTime);
    
    // ロック解除は面談後に手動で行う想定
    
    // processed フラグ
    decisionSheet.getRange(i + 1, idxProcessed + 1).setValue(true);
  }
}

/**
 * appointments シートに予約を作成
 */
function createAppointment_(userId, apptTime, zoomUrl, zoomPassword) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const apptSheet = ss.getSheetByName('appointments');
  
  if (!apptSheet) {
    throw new Error('appointments シートが存在しません');
  }
  
  const apptId = 'APPT_' + Utilities.getUuid();
  const now = new Date();
  
  apptSheet.appendRow([
    apptId,
    userId,
    apptTime,
    zoomUrl,
    zoomPassword,
    'scheduled',
    now,
    '', // completed_at
    false // no_show
  ]);
  
  log_(`createAppointment_: 予約作成 - apptId=${apptId}, userId=${userId}, time=${formatDateTime_(apptTime)}`);
  
  return apptId;
}

/**
 * リマインダーをスケジュール
 */
function scheduleReminders_(userId, apptId, apptTime) {
  // 前日10:00
  const rem1Time = new Date(apptTime);
  rem1Time.setDate(rem1Time.getDate() - 1);
  rem1Time.setHours(10, 0, 0, 0);
  
  if (rem1Time > new Date()) {
    addToSendQueue_(userId, 'tmpl_appt_rem1', {
      appt_id: apptId,
      appt_time: formatDateTime_(apptTime)
    }, rem1Time);
  }
  
  // 当日 -2h
  const rem2Time = new Date(apptTime.getTime() - 2 * 60 * 60 * 1000);
  if (rem2Time > new Date()) {
    addToSendQueue_(userId, 'tmpl_appt_rem2', {
      appt_id: apptId,
      appt_time: formatDateTime_(apptTime)
    }, rem2Time);
  }
  
  // 当日 -15m
  const rem3Time = new Date(apptTime.getTime() - 15 * 60 * 1000);
  if (rem3Time > new Date()) {
    addToSendQueue_(userId, 'tmpl_appt_rem3', {
      appt_id: apptId,
      appt_time: formatDateTime_(apptTime)
    }, rem3Time);
  }
  
  log_(`scheduleReminders_: リマインダー設定 - userId=${userId}, apptId=${apptId}`);
}

// ================================================================================
// 3. 予約リマインドの処理（補助）
// ================================================================================

/**
 * 予約リマインドの補助処理
 * 現状は不要（リマインダーは scheduleReminders_ で自動設定される）
 */
function processAppointmentReminders_() {
  // 現状は何もしない
  // 将来的に動的なリマインド調整が必要になった場合はここに実装
}

// ================================================================================
// 4. 送信キューの処理
// ================================================================================

/**
 * send_queue シートを確認して、送信時刻が来たものを送信
 */
function processSendQueue_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const queueSheet = ss.getSheetByName('send_queue');
  const config = getConfig_();
  
  if (!queueSheet) {
    log_('processSendQueue_: send_queue シートが存在しません');
    return;
  }
  
  const data = queueSheet.getDataRange().getValues();
  const headers = data[0];
  
  const idxId = headers.indexOf('id');
  const idxRecipient = headers.indexOf('recipient');
  const idxTemplateId = headers.indexOf('template_id');
  const idxVariables = headers.indexOf('variables');
  const idxScheduledAt = headers.indexOf('scheduled_at');
  const idxStatus = headers.indexOf('status');
  const idxSentAt = headers.indexOf('sent_at');
  const idxErrorMsg = headers.indexOf('error_msg');
  const idxIsOps = headers.indexOf('is_ops');
  
  const now = new Date();
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const status = row[idxStatus];
    
    if (status !== SEND_STATUS.PENDING) {
      continue; // pending 以外はスキップ
    }
    
    const queueId = row[idxId];
    const recipient = row[idxRecipient];
    const templateId = row[idxTemplateId];
    const variablesJson = row[idxVariables];
    const scheduledAt = new Date(row[idxScheduledAt]);
    const isOps = row[idxIsOps] === true || row[idxIsOps] === 'TRUE' || row[idxIsOps] === 1;
    
    // 予定時刻が来ているかチェック
    if (scheduledAt > now) {
      continue; // まだ時刻が来ていない
    }
    
    log_(`processSendQueue_: 送信処理開始 - queueId=${queueId}, recipient=${recipient}, template=${templateId}`);
    
    // freeze_sending チェック（運営宛は除外）
    if (config.freeze_sending && !isOps) {
      log_(`processSendQueue_: freeze_sending が有効なため、送信スキップ - queueId=${queueId}`);
      continue;
    }
    
    try {
      // メール送信
      sendEmail_(recipient, templateId, variablesJson, isOps);
      
      // ステータス更新
      queueSheet.getRange(i + 1, idxStatus + 1).setValue(SEND_STATUS.SENT);
      queueSheet.getRange(i + 1, idxSentAt + 1).setValue(now);
      
      log_(`processSendQueue_: 送信成功 - queueId=${queueId}`);
      
    } catch (e) {
      // エラーの場合
      log_(`processSendQueue_: 送信エラー - queueId=${queueId}, error=${e.toString()}`);
      
      queueSheet.getRange(i + 1, idxStatus + 1).setValue(SEND_STATUS.ERROR);
      queueSheet.getRange(i + 1, idxErrorMsg + 1).setValue(e.toString().substring(0, 500));
    }
  }
}

/**
 * メール送信の実処理
 */
function sendEmail_(recipient, templateId, variablesJson, isOps) {
  const config = getConfig_();
  const template = getTemplate_(templateId);
  
  if (!template) {
    throw new Error('テンプレートが見つかりません: ' + templateId);
  }
  
  // 変数をパース
  let variables = {};
  if (variablesJson && typeof variablesJson === 'string') {
    try {
      variables = JSON.parse(variablesJson);
    } catch (e) {
      log_('sendEmail_: 変数のパースエラー - ' + e.toString());
    }
  } else if (typeof variablesJson === 'object') {
    variables = variablesJson;
  }
  
  // recipient が user_id の場合はメールアドレスに変換
  let toEmail = recipient;
  if (recipient && recipient.indexOf('@') === -1) {
    const user = getUser_(recipient);
    if (user && user.email) {
      toEmail = user.email;
      variables.name = user.name || '';
      variables.email = user.email;
    } else {
      throw new Error('ユーザーのメールアドレスが見つかりません: ' + recipient);
    }
  }
  
  // プレビューモード（運営宛以外）
  if (config.preview_mode && !isOps) {
    toEmail = config.preview_to;
    variables._original_recipient = recipient;
  }
  
  // テンプレート変数を置換
  let subject = replaceVariables_(template.subject, variables);
  let body = replaceVariables_(template.body, variables);
  
  // プレビューモードの場合は件名に[PREVIEW]を追加
  if (config.preview_mode && !isOps) {
    subject = '[PREVIEW] ' + subject;
    body = '[元の宛先: ' + recipient + ']\n\n' + body;
  }
  
  // HTML対応
  const options = {};
  if (template.is_html) {
    options.htmlBody = body;
  }
  
  // 送信
  GmailApp.sendEmail(toEmail, subject, body, options);
  
  log_(`sendEmail_: メール送信完了 - to=${toEmail}, subject=${subject}`);
}

/**
 * テンプレート変数を置換
 */
function replaceVariables_(text, variables) {
  if (!text) return '';
  
  let result = text;
  for (let key in variables) {
    const placeholder = '{{' + key + '}}';
    const value = variables[key] || '';
    result = result.replace(new RegExp(placeholder, 'g'), value);
  }
  
  return result;
}

// ================================================================================
// ユーティリティ関数
// ================================================================================

/**
 * 設定を取得
 */
function getConfig_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const configSheet = ss.getSheetByName('config');
  
  if (!configSheet) {
    // デフォルト設定を返す
    return {
      freeze_all: false,
      freeze_sending: false,
      preview_mode: true,
      preview_to: Session.getActiveUser().getEmail(),
      sender_email: Session.getActiveUser().getEmail(),
      sender_name: 'いずみきょうか',
      ops_email: Session.getActiveUser().getEmail(),
      timezone: TIMEZONE
    };
  }
  
  const data = configSheet.getDataRange().getValues();
  const config = {};
  
  for (let i = 1; i < data.length; i++) {
    const key = data[i][0];
    let value = data[i][1];
    
    // 真偽値に変換
    if (value === 'TRUE' || value === 1 || value === true) {
      value = true;
    } else if (value === 'FALSE' || value === 0 || value === false) {
      value = false;
    }
    
    config[key] = value;
  }
  
  return config;
}

/**
 * ユーザー情報を取得
 */
function getUser_(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const userSheet = ss.getSheetByName('users');
  
  if (!userSheet) return null;
  
  const data = userSheet.getDataRange().getValues();
  const headers = data[0];
  
  const idxId = headers.indexOf('user_id');
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][idxId] === userId) {
      const user = {};
      for (let j = 0; j < headers.length; j++) {
        user[headers[j]] = data[i][j];
      }
      return user;
    }
  }
  
  return null;
}

/**
 * ユーザーステート取得
 */
function getUserState_(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const stateSheet = ss.getSheetByName('states');
  
  if (!stateSheet) {
    return {
      consult_locked: false,
      no_show_flag: false,
      purchased_course: false
    };
  }
  
  const data = stateSheet.getDataRange().getValues();
  const headers = data[0];
  const idxId = headers.indexOf('user_id');
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][idxId] === userId) {
      const state = {};
      for (let j = 0; j < headers.length; j++) {
        state[headers[j]] = data[i][j];
      }
      return state;
    }
  }
  
  // 見つからない場合はデフォルト
  return {
    consult_locked: false,
    no_show_flag: false,
    purchased_course: false
  };
}

/**
 * ユーザーステート設定
 */
function setUserState_(userId, updates) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const stateSheet = ss.getSheetByName('states');
  
  if (!stateSheet) return;
  
  const data = stateSheet.getDataRange().getValues();
  const headers = data[0];
  const idxId = headers.indexOf('user_id');
  
  // 既存行を探す
  for (let i = 1; i < data.length; i++) {
    if (data[i][idxId] === userId) {
      // 更新
      for (let key in updates) {
        const colIndex = headers.indexOf(key);
        if (colIndex >= 0) {
          stateSheet.getRange(i + 1, colIndex + 1).setValue(updates[key]);
        }
      }
      return;
    }
  }
  
  // 見つからない場合は新規行を追加
  const newRow = new Array(headers.length).fill('');
  newRow[idxId] = userId;
  for (let key in updates) {
    const colIndex = headers.indexOf(key);
    if (colIndex >= 0) {
      newRow[colIndex] = updates[key];
    }
  }
  stateSheet.appendRow(newRow);
}

/**
 * 無料鑑定を受けたことがあるかチェック
 */
function hasReceivedFreeReading_(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const readingsSheet = ss.getSheetByName('readings');
  
  if (!readingsSheet) return false;
  
  const data = readingsSheet.getDataRange().getValues();
  const headers = data[0];
  const idxUserId = headers.indexOf('user_id');
  const idxType = headers.indexOf('type');
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][idxUserId] === userId && data[i][idxType] === '無料') {
      return true;
    }
  }
  
  return false;
}

/**
 * 締切を設定
 */
function setDeadline_(userId, deadlineType, deadlineTime) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const deadlineSheet = ss.getSheetByName('deadlines');
  
  if (!deadlineSheet) return;
  
  const data = deadlineSheet.getDataRange().getValues();
  const headers = data[0];
  const idxUserId = headers.indexOf('user_id');
  
  // 既存行を探す
  for (let i = 1; i < data.length; i++) {
    if (data[i][idxUserId] === userId) {
      const colIndex = headers.indexOf(deadlineType);
      if (colIndex >= 0) {
        deadlineSheet.getRange(i + 1, colIndex + 1).setValue(deadlineTime);
      }
      return;
    }
  }
  
  // 見つからない場合は新規行を追加
  const newRow = new Array(headers.length).fill('');
  newRow[idxUserId] = userId;
  const colIndex = headers.indexOf(deadlineType);
  if (colIndex >= 0) {
    newRow[colIndex] = deadlineTime;
  }
  deadlineSheet.appendRow(newRow);
}

/**
 * テンプレート取得
 */
function getTemplate_(templateId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const templateSheet = ss.getSheetByName('email_templates');
  
  if (!templateSheet) return null;
  
  const data = templateSheet.getDataRange().getValues();
  const headers = data[0];
  const idxId = headers.indexOf('template_id');
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][idxId] === templateId) {
      const template = {};
      for (let j = 0; j < headers.length; j++) {
        template[headers[j]] = data[i][j];
      }
      return template;
    }
  }
  
  return null;
}

/**
 * 送信キューに追加
 */
function addToSendQueue_(recipient, templateId, variables, scheduledAt, isOps) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const queueSheet = ss.getSheetByName('send_queue');
  
  if (!queueSheet) {
    throw new Error('send_queue シートが存在しません');
  }
  
  const queueId = 'Q_' + Utilities.getUuid();
  const variablesJson = JSON.stringify(variables);
  const now = new Date();
  
  queueSheet.appendRow([
    queueId,
    recipient,
    templateId,
    variablesJson,
    scheduledAt,
    SEND_STATUS.PENDING,
    now,
    '', // sent_at
    '', // error_msg
    isOps || false
  ]);
  
  log_(`addToSendQueue_: キュー追加 - queueId=${queueId}, recipient=${recipient}, template=${templateId}, scheduled=${formatDateTime_(scheduledAt)}`);
}

/**
 * 次の正午時刻を取得
 */
function getNextNoonTime_(baseTime) {
  const noon = new Date(baseTime);
  noon.setHours(12, 0, 0, 0);
  
  if (noon <= baseTime) {
    // すでに正午を過ぎている場合は翌日の正午
    noon.setDate(noon.getDate() + 1);
  }
  
  return noon;
}

/**
 * 日時をフォーマット
 */
function formatDateTime_(date) {
  if (!date) return '';
  return Utilities.formatDate(date, TIMEZONE, 'yyyy/MM/dd HH:mm');
}

/**
 * ログ出力
 */
function log_(message) {
  const timestamp = Utilities.formatDate(new Date(), TIMEZONE, 'yyyy-MM-dd HH:mm:ss');
  Logger.log(`[${timestamp}] ${message}`);
  
  // logs_今月 シートに記録
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const month = Utilities.formatDate(new Date(), TIMEZONE, 'yyyy-MM');
    const logSheet = ss.getSheetByName(`logs_${month}`);
    
    if (logSheet) {
      logSheet.appendRow([new Date(), message]);
    }
  } catch (e) {
    // ログ記録に失敗しても処理は続行
    Logger.log('ログ記録エラー: ' + e.toString());
  }
}

/**
 * 運営にエラー通知
 */
function notifyOpsError_(error) {
  const config = getConfig_();
  if (!config.ops_email) return;
  
  const subject = '[占いステップ] エラー通知';
  const body = `システムでエラーが発生しました。\n\nエラー内容:\n${error.toString()}\n\nスタックトレース:\n${error.stack || 'なし'}`;
  
  try {
    GmailApp.sendEmail(config.ops_email, subject, body);
  } catch (e) {
    log_('notifyOpsError_: エラー通知の送信に失敗 - ' + e.toString());
  }
}

// ================================================================================
// セットアップ関数
// ================================================================================

/**
 * スプレッドシートの初期構造を作成
 */
function setupSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  log_('setupSheets: スプレッドシート初期化開始');
  
  // 各シートを作成（存在しない場合のみ）
  
  // 1. users
  createSheetIfNotExists_('users', [
    'user_id', 'name', 'email', 'birth_date', 'line_id', 
    'registered_at', 'unsubscribed', 'notes'
  ]);
  
  // 2. applications
  createSheetIfNotExists_('applications', [
    'id', 'user_id', 'type', 'timestamp', 'status', 
    'accept_reject', 'processed', 'notes'
  ]);
  
  // 3. deadlines
  createSheetIfNotExists_('deadlines', [
    'user_id', 'consult_deadline', 'reading_deadline', 'result_scheduled'
  ]);
  
  // 4. states
  createSheetIfNotExists_('states', [
    'user_id', 'consult_locked', 'no_show_flag', 'purchased_course', 
    'last_updated'
  ]);
  
  // 5. readings
  createSheetIfNotExists_('readings', [
    'reading_id', 'user_id', 'type', 'result_url', 'sent_at', 'notes'
  ]);
  
  // 6. email_templates
  createSheetIfNotExists_('email_templates', [
    'template_id', 'name', 'subject', 'body', 'is_html', 'notes'
  ]);
  
  // 7. send_queue
  createSheetIfNotExists_('send_queue', [
    'id', 'recipient', 'template_id', 'variables', 'scheduled_at', 
    'status', 'created_at', 'sent_at', 'error_msg', 'is_ops'
  ]);
  
  // 8. consult_requests
  createSheetIfNotExists_('consult_requests', [
    'request_id', 'user_id', 'slot1', 'slot2', 'slot3', 'received_at', 'notes'
  ]);
  
  // 9. consult_decisions
  createSheetIfNotExists_('consult_decisions', [
    'id', 'user_id', 'request_id', 'chosen_slot', 'zoom_url', 
    'zoom_password', 'decided_at', 'processed'
  ]);
  
  // 10. appointments
  createSheetIfNotExists_('appointments', [
    'appt_id', 'user_id', 'appt_time', 'zoom_url', 'zoom_password', 
    'status', 'created_at', 'completed_at', 'no_show'
  ]);
  
  // 11. links
  createSheetIfNotExists_('links', [
    'link_id', 'name', 'url', 'notes'
  ]);
  
  // 12. config
  createSheetIfNotExists_('config', [
    'key', 'value', 'description'
  ]);
  
  // 13. products
  createSheetIfNotExists_('products', [
    'product_id', 'name', 'price', 'description', 'detail_html', 'image_url', 'active', 'category', 'sort_order', 'is_subscription'
  ]);
  
  // 14. payments
  createSheetIfNotExists_('payments', [
    'payment_id', 'user_id', 'product_id', 'amount', 'paid_at', 'status'
  ]);
  
  // 15. ops_tickets
  createSheetIfNotExists_('ops_tickets', [
    'ticket_id', 'user_id', 'type', 'description', 'status', 'created_at'
  ]);
  
  // 16. kpi_daily
  createSheetIfNotExists_('kpi_daily', [
    'date', 'new_users', 'free_consult_apps', 'free_reading_apps', 
    'paid_reading_apps', 'emails_sent', 'notes'
  ]);
  
  // 17. consents
  createSheetIfNotExists_('consents', [
    'user_id', 'consent_type', 'consented_at', 'ip_address'
  ]);
  
  // 18. ai_prompts（AI鑑定用プロンプト管理）
  createSheetIfNotExists_('ai_prompts', [
    'prompt_id', 'prompt_type', 'product_id', 'title', 'content', 'active', 'sort_order', 'notes'
  ]);
  
  // 19. ai_settings（AI設定管理）
  createSheetIfNotExists_('ai_settings', [
    'setting_key', 'setting_value', 'description'
  ]);
  
  // 20. ai_reading_schedule（AI鑑定スケジュール）
  createSheetIfNotExists_('ai_reading_schedule', [
    'schedule_id', 'user_id', 'app_id', 'type', 'scheduled_at', 'status', 'created_at', 'processed_at', 'reading_id'
  ]);
  
  // 21. form_tokens（フォーム認証トークン）
  createSheetIfNotExists_('form_tokens', [
    'token', 'user_id', 'form_type', 'created_at', 'used_at', 'used'
  ]);
  
  // 22. manual_payments（手動決済記録）
  createSheetIfNotExists_('manual_payments', [
    'name', 'email', 'birth_date', 'product_name', 'amount', 'transaction_id', 'paid_at', 'processed'
  ]);
  
  // 23. subscriptions（サブスク管理）
  createSheetIfNotExists_('subscriptions', [
    'subscription_id', 'user_id', 'product_id', 'status', 'started_at', 'next_billing_date', 'cancelled_at'
  ]);
  
  // 24. monthly_fortunes（月次運勢記録）
  createSheetIfNotExists_('monthly_fortunes', [
    'reading_id', 'user_id', 'fortune_type', 'year', 'month', 'content', 'sent_at', 'tokens_used', 'model'
  ]);
  
  // 25. monthly_fortune_schedule（月次運勢スケジュール）
  createSheetIfNotExists_('monthly_fortune_schedule', [
    'schedule_id', 'user_id', 'fortune_type', 'year', 'month', 'scheduled_at', 'status', 'created_at', 'processed_at', 'reading_id'
  ]);
  
  // 26. monthly_fortune_log（月次運勢処理ログ）
  createSheetIfNotExists_('monthly_fortune_log', [
    'process_date', 'year', 'month', 'simple_count', 'detailed_count', 'status'
  ]);
  
  // 27. logs_今月
  const month = Utilities.formatDate(new Date(), TIMEZONE, 'yyyy-MM');
  createSheetIfNotExists_(`logs_${month}`, [
    'timestamp', 'message'
  ]);
  
  // 28. archive_process_log（アーカイブ処理ログ）
  createSheetIfNotExists_('archive_process_log', [
    'process_date', 'users_processed', 'readings_archived', 'fortunes_archived', 'status'
  ]);
  
  log_('setupSheets: スプレッドシート初期化完了');
  
  // 初期データを投入
  setupInitialData_();
}

/**
 * シートが存在しない場合のみ作成
 */
function createSheetIfNotExists_(sheetName, headers) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    sheet.appendRow(headers);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    log_(`createSheetIfNotExists_: シート作成 - ${sheetName}`);
  } else {
    log_(`createSheetIfNotExists_: シート既存 - ${sheetName}`);
  }
}

/**
 * 初期データの投入
 */
function setupInitialData_() {
  log_('setupInitialData_: 初期データ投入開始');
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // config の初期値
  const configSheet = ss.getSheetByName('config');
  if (configSheet && configSheet.getLastRow() === 1) {
    const userEmail = Session.getActiveUser().getEmail();
    
    configSheet.appendRow(['freeze_all', 'FALSE', '全処理を停止']);
    configSheet.appendRow(['freeze_sending', 'FALSE', 'ユーザー宛送信を停止（運営は許可）']);
    configSheet.appendRow(['preview_mode', 'TRUE', 'プレビューモード（運営宛に転送）']);
    configSheet.appendRow(['preview_to', userEmail, 'プレビューの宛先']);
    configSheet.appendRow(['sender_email', userEmail, '送信元メールアドレス']);
    configSheet.appendRow(['sender_name', 'いずみきょうか', '送信者名']);
    configSheet.appendRow(['ops_email', userEmail, '運営通知先']);
    configSheet.appendRow(['timezone', TIMEZONE, 'タイムゾーン']);
    
    log_('setupInitialData_: config 初期値投入完了');
  }
  
  // email_templates の初期値（最小セット）
  const templateSheet = ss.getSheetByName('email_templates');
  if (templateSheet && templateSheet.getLastRow() === 1) {
    // テンプレートデータを別関数で投入
    setupInitialTemplates_();
  }
  
  // links の初期値
  const linksSheet = ss.getSheetByName('links');
  if (linksSheet && linksSheet.getLastRow() === 1) {
    linksSheet.appendRow(['L9000', '商品ページ（メイン）', 'https://script.google.com/macros/s/YOUR_ID/exec', 'デプロイ後に更新']);
    linksSheet.appendRow(['L9001', '無料相談申込みフォーム', 'https://docs.google.com/forms/d/e/YOUR_ID/viewform', 'Googleフォーム作成後に更新']);
    linksSheet.appendRow(['L9002', '無料鑑定申込みフォーム', 'https://docs.google.com/forms/d/e/YOUR_ID/viewform', 'Googleフォーム作成後に更新']);
    linksSheet.appendRow(['L9003', '有料鑑定フォーム（ベースURL）', 'https://docs.google.com/forms/d/e/YOUR_ID/viewform', 'Googleフォーム作成後に更新']);
    
    log_('setupInitialData_: links 初期値投入完了');
  }
  
  // ai_settings の初期値
  const aiSettingsSheet = ss.getSheetByName('ai_settings');
  if (aiSettingsSheet && aiSettingsSheet.getLastRow() === 1) {
    aiSettingsSheet.appendRow(['default_system_prompt_id', 'SYS_001', 'デフォルトのシステムプロンプトID']);
    aiSettingsSheet.appendRow(['default_temperature', '0.7', '創造性（0.0-2.0）']);
    aiSettingsSheet.appendRow(['default_max_tokens', '2000', 'デフォルトの最大トークン数']);
    aiSettingsSheet.appendRow(['enable_quality_check', 'TRUE', '品質チェックを有効化']);
    aiSettingsSheet.appendRow(['ng_words', '不幸,不運,死ぬ,失敗する,病気になる', 'NGワード（カンマ区切り）']);
    aiSettingsSheet.appendRow(['max_retry_attempts', '3', '品質チェック失敗時のリトライ回数']);
    aiSettingsSheet.appendRow(['min_char_count', '800', '最低文字数']);
    
    log_('setupInitialData_: ai_settings 初期値投入完了');
  }
  
  log_('setupInitialData_: 初期データ投入完了');
}

/**
 * 初期テンプレートの投入
 */
function setupInitialTemplates_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const templateSheet = ss.getSheetByName('email_templates');
  
  if (!templateSheet) return;
  
  const templates = [
    {
      id: 'tmpl_free_accept',
      name: '無料鑑定 受付',
      subject: '【いずみきょうか】無料鑑定のお申し込みを受け付けました',
      body: `{{name}}様

この度は無料鑑定にお申し込みいただき、ありがとうございます。

あなたの運命を読み解く準備をしております。
近日中に選定結果をお知らせいたしますので、楽しみにお待ちください。

ご不明な点がございましたら、お気軽にお問い合わせください。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_selected_free',
      name: '無料鑑定 選定',
      subject: '【いずみきょうか】無料鑑定の選定結果',
      body: `{{name}}様

無料鑑定の選定が完了いたしました。

本日の夜に、あなたの鑑定結果をお送りいたします。
どうぞ楽しみにお待ちください。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_free_result',
      name: '無料鑑定 結果',
      subject: '【いずみきょうか】あなたの鑑定結果をお届けします',
      body: `{{name}}様

お待たせいたしました。
あなたの鑑定結果が完成いたしました。

▼鑑定結果はこちら
{{result_url}}

この結果を受けて、さらに詳しくお話ししたい方は、
無料相談（Zoom 30分）にお申し込みいただけます。

24時間限定のご案内ですので、お早めにどうぞ。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_ask3',
      name: '相談候補3つ依頼',
      subject: '【いずみきょうか】無料相談の日程候補をお送りください',
      body: `{{name}}様

無料相談のお申し込み、ありがとうございます。

48時間以内に、ご都合の良い日時を3つお送りください。
こちらで調整の上、確定日時をご連絡いたします。

▼候補日時の送信はこちら
[フォームURL]

いずみきょうか`,
      is_html: false
    },
    {
      id: 'ops_consult_request',
      name: '運営通知（候補到着）',
      subject: '[運営] 相談候補が届きました',
      body: `無料相談の候補日時が届きました。

ユーザーID: {{user_id}}
申込みID: {{app_id}}

consult_requests シートを確認して、採用日時を consult_decisions に記入してください。`,
      is_html: false
    },
    {
      id: 'tmpl_appt_confirm',
      name: '予約確定通知',
      subject: '【いずみきょうか】無料相談の日時が確定しました',
      body: `{{name}}様

無料相談の日時が確定いたしました。

■ 日時
{{appt_time}}

■ Zoom URL
{{zoom_url}}

■ パスワード
{{zoom_password}}

当日お会いできることを楽しみにしております。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_appt_rem1',
      name: 'リマインド1（前日10時）',
      subject: '【いずみきょうか】明日は無料相談です',
      body: `{{name}}様

明日は無料相談の日です。

■ 日時
{{appt_time}}

お忘れなくご参加ください。
お会いできることを楽しみにしております。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_appt_rem2',
      name: 'リマインド2（当日-2h）',
      subject: '【いずみきょうか】まもなく無料相談が始まります',
      body: `{{name}}様

本日は無料相談の日です。
あと2時間ほどで開始となります。

■ 日時
{{appt_time}}

準備をしてお待ちしております。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_appt_rem3',
      name: 'リマインド3（当日-15m）',
      subject: '【いずみきょうか】15分後に無料相談が始まります',
      body: `{{name}}様

15分後に無料相談が始まります。
Zoom にアクセスしてお待ちください。

■ 日時
{{appt_time}}

お会いできることを楽しみにしております。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_consult_reask',
      name: '全不採用→再提示依頼',
      subject: '【いずみきょうか】別の日時候補をお送りください',
      body: `{{name}}様

お送りいただいた日時候補ですが、
こちらの都合が合わず、調整が難しい状況です。

大変お手数ですが、別の日時候補を3つお送りいただけますでしょうか。

▼候補日時の送信はこちら
[フォームURL]

ご協力をお願いいたします。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_paid_accept',
      name: '有料鑑定 受付',
      subject: '【いずみきょうか】有料鑑定のお申し込みを受け付けました',
      body: `{{name}}様

有料鑑定のお申し込み、ありがとうございます。

鑑定結果は7日以内にお届けいたします。
楽しみにお待ちください。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_paid_form_link',
      name: '有料鑑定フォーム案内',
      subject: '【いずみきょうか】ご相談内容記入のお願い',
      body: `{{name}}様

有料鑑定のお申し込み、誠にありがとうございます。

お支払いが完了いたしました。

次のステップとして、ご相談内容を詳しくお聞かせいただきたく存じます。

▼ご相談内容記入フォーム（1回限り有効）
{{form_url}}

※このフォームは1回のみ回答可能です
※じっくりお考えの上、ご記入ください

鑑定結果は7日以内にメールでお届けします。
楽しみにお待ちください。

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_reading_result',
      name: '鑑定結果送付',
      subject: '【いずみきょうか】あなた専用の鑑定書が完成しました',
      body: `{{name}}様

お待たせいたしました。
あなた専用の鑑定書が完成いたしました。

▼鑑定結果はこちら
{{reading_url}}

じっくりとお読みいただき、今後の人生の参考にしていただければ幸いです。

ご不明な点やさらに詳しくお聞きになりたいことがございましたら、
お気軽にお問い合わせください。

あなたの幸せを心よりお祈りしています✨

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_monthly_simple',
      name: '月次簡易運勢',
      subject: '【いずみきょうか】{{year}}年{{month}}月のあなたの運勢🌙',
      body: `{{name}}様

{{year}}年{{month}}月の運勢をお届けします✨

{{fortune_content}}

━━━━━━━━━━━━━━━━━━

もっと詳しく知りたい方へ🔮

【月次詳細運勢サブスク】
毎月25日に、あなた専用の詳細運勢をお届け

・日別の吉日・厄日カレンダー
・週ごとの詳細な行動アドバイス
・開運アクション10個（日付指定）
・恋愛・仕事・金運の詳細分析

月額 ¥2,980
（個別鑑定より40%以上お得！）

▼詳細はこちら
{{subscription_link}}

いずみきょうか`,
      is_html: false
    },
    {
      id: 'tmpl_monthly_detailed',
      name: '月次詳細運勢（サブスク）',
      subject: '【いずみきょうか】{{year}}年{{month}}月のあなた専用詳細運勢✨',
      body: `{{name}}様

いつもありがとうございます🌙

{{year}}年{{month}}月の、あなた専用の詳細運勢が完成しました。

{{fortune_content}}

この1ヶ月、素晴らしい日々になりますように🌟

ご不明な点がございましたら
いつでもお問い合わせください。

いずみきょうか`,
      is_html: false
    }
  ];
  
  templates.forEach(tmpl => {
    templateSheet.appendRow([
      tmpl.id,
      tmpl.name,
      tmpl.subject,
      tmpl.body,
      tmpl.is_html,
      ''
    ]);
  });
  
  log_('setupInitialTemplates_: テンプレート投入完了 (' + templates.length + '件)');
}

/**
 * トリガーの設定
 */
function setupTriggers() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'tick') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // 新しいトリガーを作成（毎分実行）
  ScriptApp.newTrigger('tick')
    .timeBased()
    .everyMinutes(1)
    .create();
  
  log_('setupTriggers: トリガー設定完了（毎分実行）');
  
  SpreadsheetApp.getUi().alert('トリガー設定完了', '毎分実行のトリガーが設定されました。', SpreadsheetApp.getUi().ButtonSet.OK);
}

/**
 * トリガーの削除
 */
function deleteTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'tick') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  log_('deleteTriggers: トリガー削除完了');
  
  SpreadsheetApp.getUi().alert('トリガー削除完了', 'tick() のトリガーが削除されました。', SpreadsheetApp.getUi().ButtonSet.OK);
}

// ================================================================================
// OpenAI API統合 - AI自動鑑定
// ================================================================================

/**
 * OpenAI APIで鑑定書を生成（スプシ管理版）
 */
function generateReadingWithAI_(user, application) {
  const config = getConfig_();
  const aiSettings = getAISettings_();
  
  const apiKey = config.openai_api_key;
  const model = config.openai_model || 'gpt-4o-mini';
  const temperature = parseFloat(aiSettings.default_temperature) || 0.7;
  const maxTokens = parseInt(aiSettings.default_max_tokens) || 2000;
  
  if (!apiKey) {
    throw new Error('OpenAI API キーが設定されていません');
  }
  
  // システムプロンプトをシートから取得
  const systemPrompt = getSystemPromptFromSheet_();
  
  // ユーザープロンプトをシートから構築
  const userPrompt = buildReadingPromptFromSheet_(user, application);
  
  log_(`generateReadingWithAI_: AI鑑定開始 - user=${user.name}`);
  
  // OpenAI API 呼び出し
  const url = 'https://api.openai.com/v1/chat/completions';
  const payload = {
    model: model,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    temperature: temperature,
    max_tokens: maxTokens
  };
  
  const options = {
    method: 'post',
    headers: {
      'Authorization': 'Bearer ' + apiKey,
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const statusCode = response.getResponseCode();
  
  if (statusCode !== 200) {
    const errorText = response.getContentText();
    log_('generateReadingWithAI_: APIエラー - ' + errorText);
    throw new Error('OpenAI API エラー: ' + statusCode);
  }
  
  const result = JSON.parse(response.getContentText());
  const readingText = result.choices[0].message.content;
  
  // 品質チェック
  if (aiSettings.enable_quality_check) {
    const issues = checkReadingQuality_(readingText, aiSettings);
    if (issues.length > 0) {
      log_(`品質チェック警告: ${issues.join(', ')}`);
    }
  }
  
  log_(`generateReadingWithAI_: AI鑑定完了 - tokens=${result.usage.total_tokens}`);
  
  return {
    text: readingText,
    tokens_used: result.usage.total_tokens,
    model: model
  };
}

/**
 * システムプロンプトを取得（スプシから）
 */
function getSystemPromptFromSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const promptsSheet = ss.getSheetByName('ai_prompts');
  const settingsSheet = ss.getSheetByName('ai_settings');
  
  let defaultId = 'SYS_001';
  if (settingsSheet) {
    const settingsData = settingsSheet.getDataRange().getValues();
    for (let i = 1; i < settingsData.length; i++) {
      if (settingsData[i][0] === 'default_system_prompt_id') {
        defaultId = settingsData[i][1];
        break;
      }
    }
  }
  
  if (!promptsSheet) {
    return 'あなたは経験豊富な占い師です。'; // フォールバック
  }
  
  const data = promptsSheet.getDataRange().getValues();
  const headers = data[0];
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (row[0] === defaultId && row[1] === 'system' && row[5] === true) {
      return row[4].replace(/\\n/g, '\n');
    }
  }
  
  return 'あなたは経験豊富な占い師です。';
}

/**
 * 商品別プロンプトを取得（スプシから）
 */
function getProductPromptFromSheet_(productId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const promptsSheet = ss.getSheetByName('ai_prompts');
  
  if (!promptsSheet) return null;
  
  const data = promptsSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (row[2] === productId && row[1] === 'product' && row[5] === true) {
      return row[4].replace(/\\n/g, '\n');
    }
  }
  
  return null;
}

/**
 * AI設定を取得（スプシから）
 */
function getAISettings_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const settingsSheet = ss.getSheetByName('ai_settings');
  
  const defaults = {
    default_temperature: 0.7,
    default_max_tokens: 2000,
    enable_quality_check: true,
    ng_words: '不幸,不運,死ぬ',
    max_retry_attempts: 3,
    min_char_count: 800
  };
  
  if (!settingsSheet) return defaults;
  
  const data = settingsSheet.getDataRange().getValues();
  const settings = {};
  
  for (let i = 1; i < data.length; i++) {
    const key = data[i][0];
    let value = data[i][1];
    if (value === 'TRUE' || value === true) value = true;
    if (value === 'FALSE' || value === false) value = false;
    settings[key] = value;
  }
  
  return Object.assign(defaults, settings);
}

/**
 * 鑑定用プロンプトを構築（スプシから）
 */
function buildReadingPromptFromSheet_(user, application) {
  const birthDate = new Date(user.birth_date);
  const age = calculateAge_(birthDate);
  const zodiacSign = getZodiacSign_(birthDate);
  const chineseZodiac = getChineseZodiac_(birthDate.getFullYear());
  
  const userInfo = `お名前: ${user.name}様
生年月日: ${formatDate_(birthDate)}
年齢: ${age}歳
星座: ${zodiacSign}
干支: ${chineseZodiac}`;
  
  const consultation = application.consultation_content || '（特になし）';
  const productId = application.product_id || 'PROD_001';
  
  let promptTemplate = getProductPromptFromSheet_(productId);
  
  if (!promptTemplate) {
    promptTemplate = `【基本情報】\n{user_info}\n\n【相談内容】\n{consultation}\n\n詳しく鑑定してください。`;
  }
  
  let prompt = promptTemplate
    .replace(/{user_info}/g, userInfo)
    .replace(/{consultation}/g, consultation)
    .replace(/{name}/g, user.name)
    .replace(/{age}/g, age)
    .replace(/{zodiac_sign}/g, zodiacSign)
    .replace(/{chinese_zodiac}/g, chineseZodiac)
    .replace(/{birth_date}/g, formatDate_(birthDate));
  
  return prompt;
}

/**
 * 年齢計算
 */
function calculateAge_(birthDate) {
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
}

/**
 * 星座を取得
 */
function getZodiacSign_(birthDate) {
  const month = birthDate.getMonth() + 1;
  const day = birthDate.getDate();
  
  if ((month == 3 && day >= 21) || (month == 4 && day <= 19)) return '牡羊座';
  if ((month == 4 && day >= 20) || (month == 5 && day <= 20)) return '牡牛座';
  if ((month == 5 && day >= 21) || (month == 6 && day <= 21)) return '双子座';
  if ((month == 6 && day >= 22) || (month == 7 && day <= 22)) return '蟹座';
  if ((month == 7 && day >= 23) || (month == 8 && day <= 22)) return '獅子座';
  if ((month == 8 && day >= 23) || (month == 9 && day <= 22)) return '乙女座';
  if ((month == 9 && day >= 23) || (month == 10 && day <= 23)) return '天秤座';
  if ((month == 10 && day >= 24) || (month == 11 && day <= 22)) return '蠍座';
  if ((month == 11 && day >= 23) || (month == 12 && day <= 21)) return '射手座';
  if ((month == 12 && day >= 22) || (month == 1 && day <= 19)) return '山羊座';
  if ((month == 1 && day >= 20) || (month == 2 && day <= 18)) return '水瓶座';
  return '魚座';
}

/**
 * 干支を取得
 */
function getChineseZodiac_(year) {
  const animals = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
  return animals[(year - 4) % 12];
}

/**
 * 日付フォーマット
 */
function formatDate_(date) {
  return Utilities.formatDate(date, TIMEZONE, 'yyyy年M月d日');
}

/**
 * 品質チェック
 */
function checkReadingQuality_(readingText, aiSettings) {
  const issues = [];
  const minChars = parseInt(aiSettings.min_char_count) || 800;
  
  if (readingText.length < minChars) {
    issues.push(`文字数不足（${readingText.length}文字 < ${minChars}文字）`);
  }
  
  const ngWordsStr = aiSettings.ng_words || '';
  const ngWords = ngWordsStr.split(',').map(w => w.trim()).filter(w => w);
  
  ngWords.forEach(word => {
    if (readingText.includes(word)) {
      issues.push(`NGワード: ${word}`);
    }
  });
  
  return issues;
}

/**
 * 鑑定書をHTML形式に変換
 */
function formatReadingAsHTML_(readingText, user) {
  let html = `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>鑑定書 - ${user.name}様</title>
  <style>
    body{font-family:'Hiragino Sans',Meiryo,sans-serif;max-width:800px;margin:0 auto;padding:40px 20px;line-height:1.8;color:#333;background:#f5f5f5}
    .container{background:#fff;padding:40px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.1)}
    h1{text-align:center;color:#667eea;border-bottom:3px solid #667eea;padding-bottom:20px;margin-bottom:30px}
    h2{color:#667eea;margin-top:30px;margin-bottom:15px;border-left:5px solid #667eea;padding-left:15px}
    h3{color:#555;margin-top:20px;margin-bottom:10px}
    p{margin-bottom:15px}
    .info{background:#f8f9fa;padding:20px;border-radius:5px;margin-bottom:30px}
    .footer{text-align:center;margin-top:50px;padding-top:20px;border-top:1px solid #ddd;color:#999;font-size:14px}
  </style>
</head>
<body>
  <div class="container">
    <h1>🔮 鑑定書</h1>
    <div class="info">
      <strong>お名前:</strong> ${user.name}様<br>
      <strong>生年月日:</strong> ${formatDate_(new Date(user.birth_date))}<br>
      <strong>鑑定日:</strong> ${formatDate_(new Date())}
    </div>
    <div class="content">
      ${convertMarkdownToHTML_(readingText)}
    </div>
    <div class="footer">
      <p>いずみきょうか 鑑定</p>
      <p>この鑑定書はあなた専用に作成されたものです。</p>
    </div>
  </div>
</body>
</html>`;
  
  return html;
}

/**
 * Markdown風テキストをHTMLに変換
 */
function convertMarkdownToHTML_(text) {
  text = text.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  text = text.replace(/^# (.+)$/gm, '<h2>$1</h2>');
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  
  text = text.split('\n\n').map(para => {
    if (para.trim() && !para.startsWith('<h')) {
      return '<p>' + para.trim() + '</p>';
    }
    return para;
  }).join('\n');
  
  return text;
}

/**
 * 鑑定書をGoogle Driveに保存
 */
function saveReadingToDrive_(html, user, readingId) {
  const folderName = '占い鑑定書';
  let folder;
  
  const folders = DriveApp.getFoldersByName(folderName);
  if (folders.hasNext()) {
    folder = folders.next();
  } else {
    folder = DriveApp.createFolder(folderName);
  }
  
  const fileName = `鑑定書_${user.name}_${readingId}.html`;
  const blob = Utilities.newBlob(html, 'text/html', fileName);
  const file = folder.createFile(blob);
  
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  
  return {
    file_id: file.getId(),
    url: file.getUrl(),
    file_name: fileName
  };
}

/**
 * AI鑑定を実行して送信
 */
function executeAIReading_(userId, appId) {
  const user = getUser_(userId);
  const application = getApplication_(appId);
  
  if (!user || !application) {
    throw new Error('データが見つかりません');
  }
  
  log_(`executeAIReading_: AI生成開始 - user=${user.name}`);
  
  // AI鑑定生成
  const result = generateReadingWithAI_(user, application);
  
  // HTMLフォーマット
  const html = formatReadingAsHTML_(result.text, user);
  
  // Google Driveに保存
  const readingId = 'READ_' + Utilities.getUuid();
  const fileInfo = saveReadingToDrive_(html, user, readingId);
  
  // readings シートに記録
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const readingsSheet = ss.getSheetByName('readings');
  readingsSheet.appendRow([
    readingId,
    userId,
    application.type || '有料鑑定',
    fileInfo.url,
    new Date(),
    result.tokens_used,
    result.model,
    fileInfo.file_id,
    'completed'
  ]);
  
  // メール送信キューに追加
  addToSendQueue_(userId, 'tmpl_reading_result', {
    name: user.name,
    reading_url: fileInfo.url
  }, new Date());
  
  log_(`executeAIReading_: 完了 - readingId=${readingId}`);
  
  return readingId;
}

/**
 * application情報を取得
 */
function getApplication_(appId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const appSheet = ss.getSheetByName('applications');
  
  if (!appSheet) return null;
  
  const data = appSheet.getDataRange().getValues();
  const headers = data[0];
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === appId) {
      const app = {};
      for (let j = 0; j < headers.length; j++) {
        app[headers[j]] = data[i][j];
      }
      return app;
    }
  }
  
  return null;
}

/**
 * AI鑑定をスケジュール
 */
function scheduleAIReading_(userId, appId, type, scheduledTime) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let scheduleSheet = ss.getSheetByName('ai_reading_schedule');
  
  if (!scheduleSheet) {
    scheduleSheet = ss.insertSheet('ai_reading_schedule');
    scheduleSheet.appendRow(['schedule_id', 'user_id', 'app_id', 'type', 'scheduled_at', 'status', 'created_at', 'processed_at', 'reading_id']);
  }
  
  const scheduleId = 'SCHED_' + Utilities.getUuid();
  scheduleSheet.appendRow([scheduleId, userId, appId, type, scheduledTime, 'pending', new Date(), '', '']);
  
  log_(`scheduleAIReading_: スケジュール追加 - ${scheduleId}`);
}

/**
 * スケジュールされたAI鑑定を処理
 */
function processScheduledAIReadings_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const scheduleSheet = ss.getSheetByName('ai_reading_schedule');
  
  if (!scheduleSheet) return;
  
  const data = scheduleSheet.getDataRange().getValues();
  if (data.length <= 1) return;
  
  const now = new Date();
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (row[5] !== 'pending') continue;
    if (new Date(row[4]) > now) continue;
    
    try {
      const readingId = executeAIReading_(row[1], row[2]);
      scheduleSheet.getRange(i + 1, 6).setValue('completed');
      scheduleSheet.getRange(i + 1, 8).setValue(now);
      scheduleSheet.getRange(i + 1, 9).setValue(readingId);
    } catch (error) {
      log_('processScheduledAIReadings_: エラー - ' + error.toString());
      scheduleSheet.getRange(i + 1, 6).setValue('error');
    }
  }
}

// ================================================================================
// PayPal決済 & 商品ページ
// ================================================================================

/**
 * Webアプリのエントリーポイント（GET）
 */
function doGet(e) {
  const page = e.parameter.page || 'products';
  
  if (page === 'products') {
    return renderProductsPage_();
  } else if (page === 'product') {
    return renderProductDetailPage_(e.parameter.id);
  } else if (page === 'complete') {
    return renderCompletePage_();
  }
  
  return renderProductsPage_();
}

/**
 * Webhook受信（POST）
 */
function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    
    if (payload.type === 'payment_completed') {
      handlePayPalPayment_(payload);
    }
    
    return ContentService.createTextOutput(JSON.stringify({status: 'success'})).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    log_('doPost: エラー - ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({status: 'error', message: error.toString()})).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * PayPal決済完了処理
 */
function handlePayPalPayment_(payload) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const user = payload.user;
  const product = payload.product;
  const paypal = payload.paypal;
  
  // ユーザー登録
  let userId = getUserByEmail_(user.email);
  if (!userId) {
    userId = 'USER_' + Utilities.getUuid();
    ss.getSheetByName('users').appendRow([
      userId, user.name, user.email, user.birth_date, '', new Date(), false, 'PayPal決済'
    ]);
  }
  
  // 決済記録
  const paymentId = 'PAY_' + paypal.order_id;
  ss.getSheetByName('payments').appendRow([
    paymentId, userId, product.id, product.price, new Date(), 'completed', paypal.payer_email, paypal.order_id, JSON.stringify(paypal)
  ]);
  
  // フォームトークン生成
  const token = generateFormToken_(userId, '有料鑑定');
  const formURL = generatePaidFormURL_(token);
  
  // メール送信（フォームURL案内）
  addToSendQueue_(userId, 'tmpl_paid_form_link', {
    name: user.name,
    form_url: formURL
  }, new Date());
  
  // サブスク商品の場合、subscriptions に登録
  const productData = getProduct_(product.id);
  if (productData && productData.is_subscription === true) {
    registerSubscription_(userId, product.id);
    log_('handlePayPalPayment_: サブスク登録 - ' + userId);
  }
  
  // 運営通知
  const config = getConfig_();
  if (config.ops_email) {
    const noticeType = productData && productData.is_subscription ? '[サブスク契約]' : '[決済完了]';
    GmailApp.sendEmail(config.ops_email, noticeType + ' 有料鑑定',
      `決済完了\nユーザー: ${user.name}\n金額: ¥${product.price}\n商品: ${product.name}\nPayPal ID: ${paypal.order_id}`);
  }
  
  log_('handlePayPalPayment_: 決済処理完了 - ' + paymentId);
}

/**
 * 商品ページレンダリング
 */
function renderProductsPage_() {
  const products = getActiveProducts_();
  const config = getConfig_();
  
  let html = HtmlService.createTemplateFromFile('ProductsPage');
  html.products = products;
  html.config = config;
  
  return html.evaluate().setTitle('有料鑑定 - いずみきょうか');
}

/**
 * アクティブな商品を取得
 */
function getActiveProducts_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const productSheet = ss.getSheetByName('products');
  
  if (!productSheet) return [];
  
  const data = productSheet.getDataRange().getValues();
  const headers = data[0];
  const products = [];
  
  for (let i = 1; i < data.length; i++) {
    const product = {};
    for (let j = 0; j < headers.length; j++) {
      product[headers[j]] = data[i][j];
    }
    if (product.active === true || product.active === 'TRUE') {
      products.push(product);
    }
  }
  
  products.sort((a, b) => (a.sort_order || 999) - (b.sort_order || 999));
  return products;
}

// ================================================================================
// フォームトークン認証（1回限り制御）
// ================================================================================

/**
 * フォームトークン生成
 */
function generateFormToken_(userId, formType) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let tokenSheet = ss.getSheetByName('form_tokens');
  
  if (!tokenSheet) {
    tokenSheet = ss.insertSheet('form_tokens');
    tokenSheet.appendRow(['token', 'user_id', 'form_type', 'created_at', 'used_at', 'used']);
  }
  
  const token = Utilities.getUuid();
  tokenSheet.appendRow([token, userId, formType, new Date(), '', false]);
  
  log_(`generateFormToken_: トークン生成 - ${token}`);
  return token;
}

/**
 * トークン検証
 */
function validateFormToken_(token, formType) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tokenSheet = ss.getSheetByName('form_tokens');
  
  if (!tokenSheet) return false;
  
  const data = tokenSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === token && data[i][2] === formType && data[i][5] === false) {
      // 使用済みにマーク
      tokenSheet.getRange(i + 1, 5).setValue(new Date());
      tokenSheet.getRange(i + 1, 6).setValue(true);
      return true;
    }
  }
  
  return false;
}

/**
 * 有料鑑定フォームURL生成
 */
function generatePaidFormURL_(token) {
  const baseURL = getLink_('L9003');
  // ↓ entry.xxxxxxx は実際のフォームフィールドIDに置き換え
  return baseURL + '?entry.123456789=' + encodeURIComponent(token);
}

/**
 * リンク取得
 */
function getLink_(linkId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const linksSheet = ss.getSheetByName('links');
  
  if (!linksSheet) return '';
  
  const data = linksSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === linkId) {
      return data[i][2];
    }
  }
  
  return '';
}

// ================================================================================
// Googleフォーム送信時の処理
// ================================================================================

/**
 * 無料鑑定フォーム送信時
 */
function onFreeReadingFormSubmit(e) {
  try {
    const response = e.namedValues;
    const name = response['お名前'][0];
    const email = response['メールアドレス'][0];
    const birthDate = response['生年月日'][0];
    const consultation = response['どのようなことを知りたいですか？'][0];
    
    // ユーザー登録
    let userId = getUserByEmail_(email);
    if (!userId) {
      userId = 'USER_' + Utilities.getUuid();
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      ss.getSheetByName('users').appendRow([userId, name, email, birthDate, '', new Date(), false, '無料鑑定フォーム']);
    }
    
    // 申込み記録
    const appId = 'APP_' + Utilities.getUuid();
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    ss.getSheetByName('applications').appendRow([
      appId, userId, '無料鑑定', new Date(), '', '', false, '無料鑑定フォーム', consultation, 'FREE_001'
    ]);
    
    log_('onFreeReadingFormSubmit: 申込み記録 - ' + appId);
  } catch (error) {
    log_('onFreeReadingFormSubmit: エラー - ' + error.toString());
  }
}

/**
 * 有料鑑定フォーム送信時（トークン検証）
 */
function onPaidReadingFormSubmit(e) {
  try {
    const response = e.namedValues;
    const token = response['認証トークン'][0];
    const name = response['お名前'][0];
    const email = response['メールアドレス'][0];
    const consultation = response['ご相談内容'][0];
    
    // トークン検証
    if (!validateFormToken_(token, '有料鑑定')) {
      log_('onPaidReadingFormSubmit: 無効なトークン - ' + token);
      return;
    }
    
    // ユーザーID取得（トークンから）
    const userId = getUserIdFromToken_(token);
    
    // applications シートの該当行を更新（consultation_content）
    updateApplicationConsultation_(userId, consultation);
    
    // AI鑑定をスケジュール（翌日）
    const application = getLatestApplication_(userId);
    if (application) {
      const readingTime = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
      scheduleAIReading_(userId, application.id, '有料鑑定', readingTime);
    }
    
    log_('onPaidReadingFormSubmit: 相談内容記録 - ' + userId);
  } catch (error) {
    log_('onPaidReadingFormSubmit: エラー - ' + error.toString());
  }
}

/**
 * 無料相談フォーム送信時
 */
function onConsultFormSubmit(e) {
  try {
    const response = e.namedValues;
    const name = response['お名前'][0];
    const email = response['メールアドレス'][0];
    const slot1 = response['候補日時 第1希望'][0];
    const slot2 = response['候補日時 第2希望'][0];
    const slot3 = response['候補日時 第3希望'][0];
    const consultation = response['ご相談内容'] ? response['ご相談内容'][0] : '';
    
    // ユーザー登録
    let userId = getUserByEmail_(email);
    if (!userId) {
      userId = 'USER_' + Utilities.getUuid();
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      ss.getSheetByName('users').appendRow([userId, name, email, '', '', new Date(), false, '無料相談フォーム']);
    }
    
    // consult_requests に記録
    const requestId = 'REQ_' + Utilities.getUuid();
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    ss.getSheetByName('consult_requests').appendRow([requestId, userId, slot1, slot2, slot3, new Date(), consultation]);
    
    // 運営に通知
    const config = getConfig_();
    if (config.ops_email) {
      GmailApp.sendEmail(config.ops_email, '[無料相談] 候補日時到着',
        `ユーザー: ${name}\n候補1: ${slot1}\n候補2: ${slot2}\n候補3: ${slot3}\n\nconsult_decisions シートに記入してください。`);
    }
    
    log_('onConsultFormSubmit: 候補記録 - ' + requestId);
  } catch (error) {
    log_('onConsultFormSubmit: エラー - ' + error.toString());
  }
}

/**
 * トークンからユーザーIDを取得
 */
function getUserIdFromToken_(token) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tokenSheet = ss.getSheetByName('form_tokens');
  
  if (!tokenSheet) return null;
  
  const data = tokenSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === token) {
      return data[i][1];
    }
  }
  
  return null;
}

/**
 * applications の相談内容を更新
 */
function updateApplicationConsultation_(userId, consultation) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const appSheet = ss.getSheetByName('applications');
  
  if (!appSheet) return;
  
  const data = appSheet.getDataRange().getValues();
  const headers = data[0];
  const idxUserId = headers.indexOf('user_id');
  const idxConsultation = headers.indexOf('consultation_content');
  
  for (let i = data.length - 1; i >= 1; i--) {
    if (data[i][idxUserId] === userId) {
      appSheet.getRange(i + 1, idxConsultation + 1).setValue(consultation);
      break;
    }
  }
}

/**
 * 最新の申込みを取得
 */
function getLatestApplication_(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const appSheet = ss.getSheetByName('applications');
  
  if (!appSheet) return null;
  
  const data = appSheet.getDataRange().getValues();
  const headers = data[0];
  
  for (let i = data.length - 1; i >= 1; i--) {
    if (data[i][headers.indexOf('user_id')] === userId) {
      const app = {};
      for (let j = 0; j < headers.length; j++) {
        app[headers[j]] = data[i][j];
      }
      return app;
    }
  }
  
  return null;
}

/**
 * メールアドレスでユーザーIDを取得
 */
function getUserByEmail_(email) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const userSheet = ss.getSheetByName('users');
  
  if (!userSheet) return null;
  
  const data = userSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][2] === email) {
      return data[i][0];
    }
  }
  
  return null;
}

/**
 * LINE IDでユーザーIDを取得
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
    const name = data[i][1];
    if (name === productName || productName.includes(name) || name.includes(productName)) {
      return data[i][0];
    }
  }
  
  return 'PROD_001'; // デフォルト
}

// ================================================================================
// 手動決済記録の処理（プロライン無料版用）
// ================================================================================

/**
 * manual_payments シートを確認して処理
 */
function processManualPayments_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const manualSheet = ss.getSheetByName('manual_payments');
  
  if (!manualSheet) return;
  
  const data = manualSheet.getDataRange().getValues();
  if (data.length <= 1) return;
  
  const headers = data[0];
  const idxName = headers.indexOf('name');
  const idxEmail = headers.indexOf('email');
  const idxBirthDate = headers.indexOf('birth_date');
  const idxProductName = headers.indexOf('product_name');
  const idxAmount = headers.indexOf('amount');
  const idxTransactionId = headers.indexOf('transaction_id');
  const idxProcessed = headers.indexOf('processed');
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const processed = row[idxProcessed];
    
    if (processed === true || processed === 'TRUE' || processed === 1) {
      continue;
    }
    
    const userName = row[idxName];
    const userEmail = row[idxEmail];
    const birthDate = row[idxBirthDate];
    const productName = row[idxProductName];
    const amount = row[idxAmount];
    const transactionId = row[idxTransactionId];
    
    if (!userName || !userEmail || !productName) {
      continue;
    }
    
    log_(`processManualPayments_: 手動決済処理開始 - ${userName}`);
    
    try {
      // データ作成
      const payload = {
        type: 'payment_completed',
        user: { name: userName, email: userEmail, birth_date: birthDate },
        product: { 
          id: getProductIdByName_(productName),
          name: productName,
          price: amount
        },
        paypal: { order_id: transactionId || 'MANUAL_' + new Date().getTime() }
      };
      
      // 既存の処理を実行
      handlePayPalPayment_(payload);
      
      // processed フラグ
      manualSheet.getRange(i + 1, idxProcessed + 1).setValue(true);
      
      log_(`processManualPayments_: 処理完了 - ${userName}`);
      
    } catch (error) {
      log_(`processManualPayments_: エラー - ${error.toString()}`);
      // エラーでもprocessedは立てない（再試行のため）
    }
  }
}

/**
 * 手動決済記録用の補助関数（Apps Scriptエディタから実行）
 */
function recordPaymentManually() {
  const ui = SpreadsheetApp.getUi();
  
  const userName = ui.prompt('お名前を入力').getResponseText();
  const userEmail = ui.prompt('メールアドレスを入力').getResponseText();
  const birthDate = ui.prompt('生年月日（YYYY-MM-DD）').getResponseText();
  const productName = ui.prompt('商品名（例：有料鑑定（基本））').getResponseText();
  const amount = ui.prompt('金額（例：5000）').getResponseText();
  const transactionId = ui.prompt('PayPal取引ID').getResponseText();
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let manualSheet = ss.getSheetByName('manual_payments');
  
  if (!manualSheet) {
    manualSheet = ss.insertSheet('manual_payments');
    manualSheet.appendRow(['name', 'email', 'birth_date', 'product_name', 'amount', 'transaction_id', 'paid_at', 'processed']);
  }
  
  manualSheet.appendRow([
    userName, userEmail, birthDate, productName, parseInt(amount), transactionId, new Date(), false
  ]);
  
  ui.alert('記録完了', '1分以内に自動処理されます。', ui.ButtonSet.OK);
}

// ================================================================================
// 月次運勢配信システム
// ================================================================================

/**
 * 月次運勢配信の処理（毎月25～30日に実行）
 */
function processMonthlyFortuneDistribution_() {
  const now = new Date();
  const today = now.getDate();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  
  // 25日～30日の期間のみ実行
  if (today < 25 || today > 30) {
    return;
  }
  
  // 今日すでに処理済みかチェック
  if (isMonthlyFortuneProcessedToday_()) {
    return;
  }
  
  log_('processMonthlyFortuneDistribution_: 月次運勢配信開始');
  
  // 1. サブスク契約者の確認・課金（25日のみ）
  if (today === 25) {
    processSubscriptionBilling_();
  }
  
  // 2. 配信対象者を取得
  const subscribers = getActiveSubscribers_();
  const allUsers = getAllEmailUsers_();
  const nonSubscribers = allUsers.filter(user => {
    return !subscribers.find(sub => sub.user_id === user.user_id);
  });
  
  // 3. 優先度1: サブスク契約者に詳細運勢配信
  distributeDetailedFortune_(subscribers, year, month + 1);
  
  // 4. 優先度2: 非契約者に簡易運勢配信
  distributeSimpleFortune_(nonSubscribers, year, month + 1);
  
  // 5. 今日の処理完了フラグ
  markMonthlyFortuneProcessed_();
  
  log_('processMonthlyFortuneDistribution_: 配信スケジュール完了');
}

/**
 * 今日すでに処理済みかチェック
 */
function isMonthlyFortuneProcessedToday_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let processLog = ss.getSheetByName('monthly_fortune_log');
  
  if (!processLog) {
    processLog = ss.insertSheet('monthly_fortune_log');
    processLog.appendRow(['process_date', 'year', 'month', 'simple_count', 'detailed_count', 'status']);
    return false;
  }
  
  const data = processLog.getDataRange().getValues();
  const today = Utilities.formatDate(new Date(), TIMEZONE, 'yyyy-MM-dd');
  
  for (let i = 1; i < data.length; i++) {
    const processDate = Utilities.formatDate(new Date(data[i][0]), TIMEZONE, 'yyyy-MM-dd');
    if (processDate === today && data[i][5] === 'completed') {
      return true;
    }
  }
  
  return false;
}

/**
 * 処理完了をマーク
 */
function markMonthlyFortuneProcessed_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let processLog = ss.getSheetByName('monthly_fortune_log');
  
  const now = new Date();
  const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  
  processLog.appendRow([now, nextMonth.getFullYear(), nextMonth.getMonth() + 1, 0, 0, 'completed']);
}

/**
 * サブスク契約者を取得
 */
function getActiveSubscribers_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let subSheet = ss.getSheetByName('subscriptions');
  
  if (!subSheet) {
    subSheet = ss.insertSheet('subscriptions');
    subSheet.appendRow(['subscription_id', 'user_id', 'product_id', 'status', 'started_at', 'next_billing_date', 'cancelled_at']);
    return [];
  }
  
  const data = subSheet.getDataRange().getValues();
  const subscribers = [];
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (row[3] === 'active') {
      const user = getUser_(row[1]);
      if (user) {
        subscribers.push({ subscription_id: row[0], user_id: row[1], user: user });
      }
    }
  }
  
  return subscribers;
}

/**
 * 全メール登録ユーザーを取得
 */
function getAllEmailUsers_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const userSheet = ss.getSheetByName('users');
  
  if (!userSheet) return [];
  
  const data = userSheet.getDataRange().getValues();
  const users = [];
  
  for (let i = 1; i < data.length; i++) {
    const email = data[i][2];
    const unsubscribed = data[i][6];
    
    if (email && !unsubscribed) {
      users.push({
        user_id: data[i][0],
        name: data[i][1],
        email: data[i][2],
        birth_date: data[i][3]
      });
    }
  }
  
  return users;
}

/**
 * 詳細運勢配信（サブスク）
 */
function distributeDetailedFortune_(subscribers, year, month) {
  const now = new Date();
  
  subscribers.forEach((subscriber, index) => {
    // 0〜6時間後にランダム分散
    const scheduledTime = new Date(now.getTime() + (index % 12) * 30 * 60 * 1000);
    scheduleMonthlyFortune_(subscriber.user_id, 'detailed', year, month, scheduledTime);
  });
  
  log_(`distributeDetailedFortune_: ${subscribers.length}件スケジュール`);
}

/**
 * 簡易運勢配信（全員）
 */
function distributeSimpleFortune_(users, year, month) {
  const now = new Date();
  const today = now.getDate();
  const daysLeft = Math.max(1, 31 - today);
  const usersPerDay = Math.ceil(users.length / daysLeft);
  
  users.forEach((user, index) => {
    const dayOffset = Math.floor(index / usersPerDay);
    const scheduledTime = new Date(now.getTime() + dayOffset * 24 * 60 * 60 * 1000 + (Math.random() * 12) * 60 * 60 * 1000);
    
    scheduleMonthlyFortune_(user.user_id, 'simple', year, month, scheduledTime);
  });
  
  log_(`distributeSimpleFortune_: ${users.length}件スケジュール`);
}

/**
 * 月次運勢をスケジュール
 */
function scheduleMonthlyFortune_(userId, fortuneType, year, month, scheduledTime) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let scheduleSheet = ss.getSheetByName('monthly_fortune_schedule');
  
  if (!scheduleSheet) {
    scheduleSheet = ss.insertSheet('monthly_fortune_schedule');
    scheduleSheet.appendRow(['schedule_id', 'user_id', 'fortune_type', 'year', 'month', 'scheduled_at', 'status', 'created_at', 'processed_at', 'reading_id']);
  }
  
  const scheduleId = 'MF_' + Utilities.getUuid();
  scheduleSheet.appendRow([scheduleId, userId, fortuneType, year, month, scheduledTime, 'pending', new Date(), '', '']);
}

/**
 * スケジュールされた月次運勢を処理
 */
function processMonthlyFortuneSchedule_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const scheduleSheet = ss.getSheetByName('monthly_fortune_schedule');
  
  if (!scheduleSheet) return;
  
  const data = scheduleSheet.getDataRange().getValues();
  if (data.length <= 1) return;
  
  const now = new Date();
  let processedCount = 0;
  const maxPerTick = 5;
  
  for (let i = 1; i < data.length; i++) {
    if (processedCount >= maxPerTick) break;
    
    const row = data[i];
    if (row[6] !== 'pending') continue;
    if (new Date(row[5]) > now) continue;
    
    try {
      const readingId = generateMonthlyFortune_(row[1], row[2], row[3], row[4]);
      scheduleSheet.getRange(i + 1, 7).setValue('completed');
      scheduleSheet.getRange(i + 1, 9).setValue(now);
      scheduleSheet.getRange(i + 1, 10).setValue(readingId);
      processedCount++;
    } catch (error) {
      log_('processMonthlyFortuneSchedule_: エラー - ' + error.toString());
      scheduleSheet.getRange(i + 1, 7).setValue('error');
    }
  }
}

/**
 * 月次運勢を生成して送信
 */
function generateMonthlyFortune_(userId, fortuneType, year, month) {
  const user = getUser_(userId);
  if (!user) throw new Error('ユーザーが見つかりません');
  
  log_(`generateMonthlyFortune_: 生成開始 - ${user.name}, ${fortuneType}`);
  
  // プロンプト構築
  const prompt = buildMonthlyFortunePrompt_(user, fortuneType, year, month);
  const maxTokens = fortuneType === 'detailed' ? 2500 : 600;
  
  // AI生成
  const result = callOpenAI_(prompt, maxTokens);
  
  // 記録
  const readingId = `MF_${year}_${month}_${fortuneType}_${userId}`;
  recordMonthlyFortune_(userId, readingId, fortuneType, year, month, result);
  
  // メール送信
  sendMonthlyFortuneEmail_(user, fortuneType, year, month, result.text);
  
  log_(`generateMonthlyFortune_: 完了 - ${readingId}`);
  
  return readingId;
}

/**
 * 月次運勢プロンプト構築
 */
function buildMonthlyFortunePrompt_(user, fortuneType, year, month) {
  const birthDate = new Date(user.birth_date);
  const userInfo = `お名前: ${user.name}様
生年月日: ${formatDate_(birthDate)}
星座: ${getZodiacSign_(birthDate)}
干支: ${getChineseZodiac_(birthDate.getFullYear())}`;
  
  const promptId = fortuneType === 'detailed' ? 'MONTHLY_DETAIL' : 'MONTHLY_SIMPLE';
  let template = getMonthlyFortunePromptTemplate_(promptId);
  
  if (!template) {
    template = fortuneType === 'detailed' 
      ? `{name}様の{year}年{month}月の詳細運勢を占ってください。`
      : `{name}様の{year}年{month}月の簡易運勢を占ってください。吉日と厄日を示してください。`;
  }
  
  // 詳細版の場合、簡易版の内容を参照
  let simpleFortune = '';
  if (fortuneType === 'detailed') {
    simpleFortune = getSimpleFortune_(user.user_id, year, month);
    if (simpleFortune) {
      template += `\n\n【この方への簡易運勢（参考）】\n${simpleFortune}\n\n上記の簡易運勢と矛盾しないように、さらに詳しく占ってください。`;
    }
  }
  
  return template
    .replace(/{user_info}/g, userInfo)
    .replace(/{name}/g, user.name)
    .replace(/{year}/g, year)
    .replace(/{month}/g, month);
}

/**
 * 月次運勢プロンプトテンプレート取得
 */
function getMonthlyFortunePromptTemplate_(promptId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const promptsSheet = ss.getSheetByName('ai_prompts');
  
  if (!promptsSheet) return null;
  
  const data = promptsSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === promptId && data[i][5] === true) {
      return data[i][4].replace(/\\n/g, '\n');
    }
  }
  
  return null;
}

/**
 * 簡易運勢を取得
 */
function getSimpleFortune_(userId, year, month) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const fortuneSheet = ss.getSheetByName('monthly_fortunes');
  
  if (!fortuneSheet) return '';
  
  const data = fortuneSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][1] === userId && data[i][2] === 'simple' && 
        data[i][3] === year && data[i][4] === month) {
      return data[i][5];
    }
  }
  
  return '';
}

/**
 * OpenAI API呼び出し（汎用）
 */
function callOpenAI_(prompt, maxTokens) {
  const config = getConfig_();
  const aiSettings = getAISettings_();
  const apiKey = config.openai_api_key;
  const model = config.openai_model || 'gpt-4o-mini';
  
  const systemPrompt = getSystemPromptFromSheet_();
  
  const url = 'https://api.openai.com/v1/chat/completions';
  const payload = {
    model: model,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: prompt }
    ],
    temperature: parseFloat(aiSettings.default_temperature) || 0.7,
    max_tokens: maxTokens
  };
  
  const options = {
    method: 'post',
    headers: {
      'Authorization': 'Bearer ' + apiKey,
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const statusCode = response.getResponseCode();
  
  if (statusCode !== 200) {
    throw new Error('OpenAI API エラー: ' + statusCode);
  }
  
  const result = JSON.parse(response.getContentText());
  
  return {
    text: result.choices[0].message.content,
    tokens_used: result.usage.total_tokens,
    model: model
  };
}

/**
 * 月次運勢を記録
 */
function recordMonthlyFortune_(userId, readingId, fortuneType, year, month, result) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let fortuneSheet = ss.getSheetByName('monthly_fortunes');
  
  if (!fortuneSheet) {
    fortuneSheet = ss.insertSheet('monthly_fortunes');
    fortuneSheet.appendRow(['reading_id', 'user_id', 'fortune_type', 'year', 'month', 'content', 'sent_at', 'tokens_used', 'model']);
  }
  
  fortuneSheet.appendRow([readingId, userId, fortuneType, year, month, result.text, new Date(), result.tokens_used, result.model]);
}

/**
 * 月次運勢メール送信
 */
function sendMonthlyFortuneEmail_(user, fortuneType, year, month, fortuneText) {
  if (fortuneType === 'detailed') {
    addToSendQueue_(user.user_id, 'tmpl_monthly_detailed', {
      name: user.name,
      year: year,
      month: month,
      fortune_content: fortuneText
    }, new Date());
  } else {
    addToSendQueue_(user.user_id, 'tmpl_monthly_simple', {
      name: user.name,
      year: year,
      month: month,
      fortune_content: fortuneText,
      subscription_link: getLink_('L9000')
    }, new Date());
  }
}

/**
 * サブスク課金処理
 */
function processSubscriptionBilling_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const subSheet = ss.getSheetByName('subscriptions');
  
  if (!subSheet) return;
  
  const data = subSheet.getDataRange().getValues();
  const now = new Date();
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (row[3] === 'active') {
      const nextBillingDate = new Date(now.getFullYear(), now.getMonth() + 1, 25);
      subSheet.getRange(i + 1, 6).setValue(nextBillingDate);
      
      log_(`processSubscriptionBilling_: サブスク課金予定 - ${row[1]}, 次回: ${formatDateTime_(nextBillingDate)}`);
    }
  }
}

/**
 * サブスク登録
 */
function registerSubscription_(userId, productId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let subSheet = ss.getSheetByName('subscriptions');
  
  if (!subSheet) {
    subSheet = ss.insertSheet('subscriptions');
    subSheet.appendRow(['subscription_id', 'user_id', 'product_id', 'status', 'started_at', 'next_billing_date', 'cancelled_at']);
  }
  
  // 既存チェック
  const data = subSheet.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (data[i][1] === userId && data[i][2] === productId) {
      subSheet.getRange(i + 1, 4).setValue('active');
      return;
    }
  }
  
  // 新規登録
  const subId = 'SUB_' + Utilities.getUuid();
  const now = new Date();
  const nextBillingDate = new Date(now.getFullYear(), now.getMonth() + 1, 25);
  
  subSheet.appendRow([subId, userId, productId, 'active', now, nextBillingDate, '']);
  
  log_(`registerSubscription_: サブスク登録 - ${subId}`);
}

/**
 * サブスク解約
 */
function cancelSubscription(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const subSheet = ss.getSheetByName('subscriptions');
  
  if (!subSheet) return;
  
  const data = subSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][1] === userId && data[i][3] === 'active') {
      subSheet.getRange(i + 1, 4).setValue('cancelled');
      subSheet.getRange(i + 1, 7).setValue(new Date());
      break;
    }
  }
}

// ================================================================================
// アーカイブシステム（個人別管理・データ軽量化）
// ================================================================================

/**
 * 個人別アーカイブ処理（毎月15日に実行）
 */
function processArchiveOn15th_() {
  const now = new Date();
  const today = now.getDate();
  
  // 15日のみ実行
  if (today !== 15) {
    return;
  }
  
  // 今日すでに処理済みかチェック
  if (isArchiveProcessedToday_()) {
    return;
  }
  
  log_('processArchiveOn15th_: 個人別アーカイブ開始');
  
  // 1. ユーザーごとのデータをアーカイブ
  archiveUserDataIndividually_();
  
  // 2. システムログのアーカイブ
  archiveSystemLogs_();
  
  // 3. 処理完了フラグ
  markArchiveProcessed_();
  
  // 4. 運営に通知
  notifyArchiveCompleted_();
  
  log_('processArchiveOn15th_: アーカイブ完了');
}

/**
 * ユーザーごとにデータをアーカイブ
 */
function archiveUserDataIndividually_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const userSheet = ss.getSheetByName('users');
  
  if (!userSheet) return;
  
  const userData = userSheet.getDataRange().getValues();
  const headers = userData[0];
  
  let usersProcessed = 0;
  let readingsArchived = 0;
  let fortunesArchived = 0;
  
  // 各ユーザーごとに処理（最大50人/回）
  const maxUsersPerRun = 50;
  
  for (let i = 1; i < Math.min(userData.length, maxUsersPerRun + 1); i++) {
    const userId = userData[i][0];
    
    if (!userId) continue;
    
    try {
      // 個人別アーカイブシート作成・更新
      const result = createOrUpdateUserArchive_(userId);
      
      readingsArchived += result.readingsCount;
      fortunesArchived += result.fortunesCount;
      
      // 鑑定回数を集計
      const counts = calculateUserReadingCounts_(userId);
      
      // usersシートに記録
      updateUserStats_(userSheet, i + 1, counts, result.archiveSheetId);
      
      usersProcessed++;
      
    } catch (error) {
      log_('archiveUserDataIndividually_: エラー - ' + userId + ': ' + error.toString());
    }
  }
  
  log_(`archiveUserDataIndividually_: ${usersProcessed}人処理, 鑑定${readingsArchived}件, 運勢${fortunesArchived}件アーカイブ`);
}

/**
 * 個人別アーカイブシートを作成・更新
 */
function createOrUpdateUserArchive_(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheetName = `user_archive_${userId}`;
  let archiveSheet = ss.getSheetByName(sheetName);
  
  if (!archiveSheet) {
    archiveSheet = ss.insertSheet(sheetName);
    archiveSheet.appendRow(['date', 'type', 'result_url', 'tokens_used', 'status', 'notes']);
    archiveSheet.hideSheet(); // 非表示にして整理
  }
  
  // 3ヶ月以上前のデータを取得
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
  if (readingsData.length > 0) {
    deleteOldReadings_(userId, threeMonthsAgo);
  }
  
  if (fortunesData.length > 0) {
    deleteOldMonthlyFortunes_(userId, threeMonthsAgo);
  }
  
  return {
    archiveSheetId: archiveSheet.getSheetId(),
    readingsCount: readingsData.length,
    fortunesCount: fortunesData.length
  };
}

/**
 * 鑑定回数を集計
 */
function calculateUserReadingCounts_(userId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  let countFree = 0;
  let countPaid = 0;
  let countMonthly = 0;
  let lastReadingDate = null;
  
  // readingsシート
  const readingsSheet = ss.getSheetByName('readings');
  if (readingsSheet) {
    const data = readingsSheet.getDataRange().getValues();
    for (let i = 1; i < data.length; i++) {
      if (data[i][1] === userId) {
        const type = data[i][2];
        const sentAt = new Date(data[i][4]);
        
        if (type && type.includes('無料')) countFree++;
        else if (type && type.includes('有料')) countPaid++;
        
        if (!lastReadingDate || sentAt > lastReadingDate) {
          lastReadingDate = sentAt;
        }
      }
    }
  }
  
  // monthly_fortunesシート
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
      
      if (type && type.includes('無料')) countFree++;
      else if (type && type.includes('有料')) countPaid++;
      else if (type && type.includes('月次')) countMonthly++;
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

/**
 * usersシートの統計情報を更新
 */
function updateUserStats_(userSheet, rowIndex, counts, archiveSheetId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const headers = userSheet.getRange(1, 1, 1, userSheet.getLastColumn()).getValues()[0];
  
  // 列を取得または追加
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

/**
 * 列を取得、なければ追加
 */
function getOrAddColumn_(sheet, headers, columnName) {
  const index = headers.indexOf(columnName);
  
  if (index >= 0) {
    return index + 1;
  }
  
  const newColIndex = headers.length + 1;
  sheet.getRange(1, newColIndex).setValue(columnName);
  
  return newColIndex;
}

/**
 * 古いreadingsデータを取得
 */
function getOldReadings_(userId, cutoffDate) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const readingsSheet = ss.getSheetByName('readings');
  
  if (!readingsSheet) return [];
  
  const data = readingsSheet.getDataRange().getValues();
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
          tokens_used: data[i][5] || 0
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
          tokens_used: data[i][7] || 0
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
  const keepRows = [data[0]];
  
  for (let i = 1; i < data.length; i++) {
    const rowUserId = data[i][1];
    const sentAt = new Date(data[i][4]);
    
    if (rowUserId !== userId || sentAt >= cutoffDate) {
      keepRows.push(data[i]);
    }
  }
  
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
  const today = Utilities.formatDate(new Date(), TIMEZONE, 'yyyy-MM-dd');
  
  for (let i = 1; i < data.length; i++) {
    const processDate = Utilities.formatDate(new Date(data[i][0]), TIMEZONE, 'yyyy-MM-dd');
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
  const archiveDate = Utilities.formatDate(lastMonth, TIMEZONE, 'yyyy-MM');
  
  const currentLogSheet = ss.getSheetByName(`logs_${archiveDate}`);
  
  if (!currentLogSheet) return;
  
  const archiveSheetName = `archive_logs_${archiveDate}`;
  let archiveSheet = ss.getSheetByName(archiveSheetName);
  
  if (!archiveSheet) {
    archiveSheet = currentLogSheet.copyTo(ss);
    archiveSheet.setName(archiveSheetName);
    archiveSheet.hideSheet();
    
    const lastRow = currentLogSheet.getLastRow();
    if (lastRow > 1) {
      currentLogSheet.deleteRows(2, lastRow - 1);
    }
    
    log_(`archiveSystemLogs_: ${archiveSheetName} 作成完了`);
  }
}

/**
 * アーカイブ完了通知
 */
function notifyArchiveCompleted_() {
  const config = getConfig_();
  if (!config.ops_email) return;
  
  const now = new Date();
  const subject = `[占いシステム] 個人別アーカイブ完了（毎月15日）`;
  const body = `個人別データアーカイブが完了しました。\n\n・3ヶ月以上前のデータを個人別アーカイブシートに移動\n・usersシートに鑑定回数を集計\n・個人別アーカイブへのリンクを設定\n\nusersシートを確認してください。`;
  
  GmailApp.sendEmail(config.ops_email, subject, body);
}

/**
 * 手動アーカイブ実行（Apps Scriptエディタから）
 */
function runArchiveNow() {
  const ui = SpreadsheetApp.getUi();
  const result = ui.alert(
    '個人別アーカイブ実行',
    '3ヶ月以上前のデータを個人別にアーカイブします。よろしいですか？',
    ui.ButtonSet.YES_NO
  );
  
  if (result === ui.Button.YES) {
    archiveUserDataIndividually_();
    archiveSystemLogs_();
    
    ui.alert('アーカイブ完了', '個人別アーカイブが完了しました。usersシートを確認してください。', ui.ButtonSet.OK);
  }
}

