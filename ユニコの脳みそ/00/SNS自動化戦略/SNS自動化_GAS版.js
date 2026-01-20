/**
 * SNS自動化システム v3.3 (Date & Time Edition)
 * 
 * 【v3.3の進化点: 日時自動計算】
 * - キャンペーン作成時に「開始日」を指定できるようになりました。
 * - AIが「朝・昼・夜」の投稿タイミングを提案し、GASが「2024/05/01 07:00」のような正確な日時を自動計算します。
 * - これにより、Pythonロボットが迷わず予約投稿できるようになります。
 */

// ==========================================
// ★世界観設定 (魂の代弁者)
// ==========================================
const PERSONA_SETTING = `
あなたは「人間の心の闇と光」を知り尽くした、魂の代弁者です。
ターゲット：30代〜40代の、過去の恋愛に執着し、誰にも言えない孤独を抱える女性。

【絶対ルール】
・表面的な共感ではなく、「深夜2時に彼のアカウントを監視してしまう」ような具体的な痛みをえぐる。
・綺麗なアドバイスはいらない。読者の「影（嫉妬・執着）」を肯定し、寄り添う。
・口調：静かで深く、心に染み入るトーン。「〜だよね」「〜してない？」
`;

// ==========================================
// メイン処理
// ==========================================

function onOpen() {
    const ui = SpreadsheetApp.getUi();
    ui.createMenu('SNS自動化')
        .addItem('1. 初期設定: APIキー登録', 'setApiKey')
        .addSeparator()
        .addItem('2. キャンペーン自動作成 (日時計算付)', 'createCampaign')
        .addItem('3. 投稿生成を実行 (記事作成)', 'generateContent')
        .addSeparator()
        .addItem('4. Python連携: CSV書き出し', 'exportToCsv')
        .addToUi();
}

/**
 * 2. キャンペーン作成 (日時計算機能付き)
 */
function createCampaign() {
    const apiKey = getApiKey();
    if (!apiKey) { setApiKey(); return; }

    const ui = SpreadsheetApp.getUi();

    // Q1. ゴール
    const goalResponse = ui.prompt('ステップ1: ゴール設定',
        'このキャンペーンの最終目的は何ですか？\n(例: LINE登録増加)', ui.ButtonSet.OK_CANCEL);
    if (goalResponse.getSelectedButton() != ui.Button.OK) return;
    const finalGoal = goalResponse.getResponseText();

    // Q2. 期間
    const daysResponse = ui.prompt('ステップ2: 期間設定',
        '何日間のキャンペーンにしますか？(数字のみ)', ui.ButtonSet.OK_CANCEL);
    if (daysResponse.getSelectedButton() != ui.Button.OK) return;
    const days = parseInt(daysResponse.getResponseText());
    if (isNaN(days)) { ui.alert('エラー', '数字で入力してください', ui.ButtonSet.OK); return; }

    // Q3. 開始日 (v3.3新機能)
    const todayStr = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy/MM/dd");
    const dateResponse = ui.prompt('ステップ3: 開始日設定',
        `いつから投稿を開始しますか？(yyyy/MM/dd形式)\n例: ${todayStr}`, ui.ButtonSet.OK_CANCEL);
    if (dateResponse.getSelectedButton() != ui.Button.OK) return;

    let startDateStr = dateResponse.getResponseText().trim();
    if (!startDateStr) startDateStr = todayStr;
    const startDate = new Date(startDateStr);
    if (isNaN(startDate.getTime())) { ui.alert('エラー', '日付形式が正しくありません', ui.ButtonSet.OK); return; }

    // シート初期化
    setupSheet(true);

    const sheet = SpreadsheetApp.getActiveSheet();
    sheet.getRange(2, 1).setValue('戦略とスケジュールを構築中...');

    try {
        const strategy = callOpenAIForStrategy(apiKey, finalGoal, days);

        // (A) 戦略データ受け取り
        if (strategy && strategy.length > 0) {
            const rows = [];

            // (B) 日時の計算処理
            for (let i = 0; i < strategy.length; i++) {
                const item = strategy[i];

                // Day番号から日付を計算
                // item.day = 1 なら startDateと同じ日
                const targetDate = new Date(startDate);
                targetDate.setDate(startDate.getDate() + (item.day - 1));

                // Timeから時間を設定
                // Morning=07:00, Noon=12:00, Night=19:00 と仮定
                let timeStr = "19:00"; // デフォルト
                if (item.time === "Morning") timeStr = "07:00";
                if (item.time === "Noon") timeStr = "12:00";
                if (item.time === "Night") timeStr = "19:00";

                const dateString = Utilities.formatDate(targetDate, Session.getScriptTimeZone(), "yyyy/MM/dd");
                const fullDateTime = `${dateString} ${timeStr}`; // 2024/05/01 19:00

                // 行データ作成
                // [Topic, Type, Goal, Generated Content, Image Prompt, Status, Scheduled Time]
                rows.push([item.topic, item.type, item.goal, "", "", "", fullDateTime]);
            }

            sheet.getRange(2, 1, rows.length, 7).setValues(rows);
            ui.alert('完了', `${days}日間 (${rows.length}投稿) のスケジュールを作成しました。\nG列に予約日時が入っています。確認してください。`, ui.ButtonSet.OK);
        }
    } catch (e) {
        ui.alert('エラー', '戦略作成に失敗しました: ' + e.message, ui.ButtonSet.OK);
    }
}

/**
 * 戦略AI (時間帯を指定させる)
 */
function callOpenAIForStrategy(apiKey, finalGoal, days) {
    const url = 'https://api.openai.com/v1/chat/completions';

    const systemPrompt = `
あなたはSNSマーケティング・ストラテジストです。
クライアントの「最終ゴール」を達成するために、${days}日間で【最大の結果】を出すためのスパルタ投稿スケジュールを立案してください。

# 6ステップ教育理論
1. Problem (問題提起) -> 信頼構築
2. Agitation (常識破壊) -> 興味付け
3. Solution (解決策) -> 教育
4. Trust (信頼) -> 権威付け
5. Proof (証拠) -> 不安払拭
6. Offer (オファー) -> 行動

上記を意識し、1日複数回投稿（Morning/Noon/Night）を組み合わせてください。

# 出力フォーマット (JSON配列)
{
  "plan": [
    { "day": 1, "time": "Morning", "goal": "常識破壊", "type": "Feed", "topic": "なぜ復縁できないのか？" },
    { "day": 1, "time": "Night", "goal": "信頼構築", "type": "Story", "topic": "辛いよねアンケート" },
    ...
  ]
}
※ "time" は必ず [Morning, Noon, Night] のいずれか。
`;

    const payload = {
        model: 'gpt-4o',
        messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: `最終ゴール: ${finalGoal}\n期間: ${days}日間` }
        ],
        response_format: { type: "json_object" }
    };

    const options = {
        method: 'post',
        contentType: 'application/json',
        headers: { 'Authorization': 'Bearer ' + apiKey },
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
    };

    const response = UrlFetchApp.fetch(url, options);
    const json = JSON.parse(response.getContentText());
    if (json.error) throw new Error(json.error.message);

    return JSON.parse(json.choices[0].message.content).plan;
}

/**
 * 3. 投稿生成 (変更なし、列ズレのみ対応)
 */
function generateContent() {
    const apiKey = getApiKey();
    if (!apiKey) { setApiKey(); return; }

    const sheet = SpreadsheetApp.getActiveSheet();
    const lastRow = sheet.getLastRow();
    if (lastRow < 2) return;

    // 今度は7列取得
    const range = sheet.getRange(2, 1, lastRow - 1, 7);
    const data = range.getValues();
    let processedCount = 0;

    for (let i = 0; i < data.length; i++) {
        const row = data[i];
        const topic = row[0];
        const type = row[1];
        const goal = row[2];
        const status = row[5];

        if (topic !== '' && status === '' && row[3] === '') {
            try {
                const result = callOpenAIForContent(apiKey, topic, type, goal);
                sheet.getRange(i + 2, 4).setValue(result.caption);
                sheet.getRange(i + 2, 5).setValue(result.image_prompt);
                sheet.getRange(i + 2, 6).setValue('Done');
                processedCount++;
            } catch (e) {
                sheet.getRange(i + 2, 6).setValue('Error: ' + e.message);
            }
        }
    }

    if (processedCount > 0) browserMsg('完了', processedCount + '件生成しました。');
}

/**
 * AI記事執筆 (変更なし)
 */
function callOpenAIForContent(apiKey, topic, type, goal) {
    const url = 'https://api.openai.com/v1/chat/completions';

    let goalInstruction = "";
    if (goal === '信頼構築') goalInstruction = "読者に『私の気持ちを分かってくれている』と深く共感させてください。売り込みは一切禁止。";
    if (goal === '常識破壊') goalInstruction = "読者が信じている間違った常識（例: 冷却期間が必要など）を否定し、衝撃を与えてください。";
    if (goal === 'ノウハウ') goalInstruction = "具体的で役立つ手順を教えてください。信頼を積み上げるフェーズです。";
    if (goal === 'LINE誘導' || goal === '販売') goalInstruction = "★最重要★ 今回は教育の締めくくりです。これまでの回答が『プロフのリンク』にあることを強く訴求し、クリックさせることが唯一の目的です。";

    let typeInstruction = "";
    if (type === 'Feed') {
        typeInstruction = `
# 形式: Instagramフィード (画像1枚 + キャプション)
# コンテンツ作成の極意:
1. 【Problem (痛み)】: 誰もが隠している「惨めな本音」や「執着」を具体的に描写。
2. 【Agitation (煽り)】: その感情を否定せず、魂の叫びとして肯定する。
3. 【Solution (救済)】: 常識とは違う、あなただけの新しい視点を与える。
4. 【Action (結び)】: 静かに、しかし力強く保存・行動を促す。
    `;
    } else if (type === 'Reel') {
        typeInstruction = `
# 形式: Instagramリール台本 (テンポ重視・ビジュアルノベル風)
# コンテンツ作成の極意:
1. 【Hook】: 0.1秒で手を止めさせる衝撃的な一言。
2. 【Body】: 淡々と核心を突くナレーション。
3. 【Conclusion】: 余韻を残し、続きはキャプションへ誘導。
※ 画像プロンプトは各シーン(Scene 1, Scene 2...)ごとに詳細に出力。
    `;
    } else if (type === 'Story') {
        typeInstruction = `
# 形式: Instagramストーリーズ (対話型セラピー)
# コンテンツ作成の極意:
1. 【Slide 1】: 踏み込んだ2択アンケート (テーマに関連するもの必須)。
2. 【Slide 2】: 回答への深い共感とバリデーション。
3. 【Slide 3】: DMやリンクへのさりげない導線。
※ 画像プロンプトは3枚分出力。
    `;
    }

    const systemPrompt = `
${PERSONA_SETTING}

目的: 【${goal}】
${goalInstruction}

形式: ${type}
入力テーマ: ${topic}

${typeInstruction}

# 出力フォーマット (JSON)
{
  "caption": "本文(リールは台本)",
  "image_prompt": "画像指示(複数可)"
}
`;

    const payload = {
        model: 'gpt-4o-mini',
        messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: topic }
        ],
        response_format: { type: "json_object" }
    };

    const options = {
        method: 'post',
        contentType: 'application/json',
        headers: { 'Authorization': 'Bearer ' + apiKey },
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
    };

    const response = UrlFetchApp.fetch(url, options);
    const json = JSON.parse(response.getContentText());
    if (json.error) throw new Error(json.error.message);
    return JSON.parse(json.choices[0].message.content);
}

/**
 * 4. CSV出力 (日時列を追加)
 */
function exportToCsv() {
    const sheet = SpreadsheetApp.getActiveSheet();
    const lastRow = sheet.getLastRow();

    if (lastRow < 2) {
        Browser.msgBox("エラー", "データがありません。", Browser.Buttons.OK);
        return;
    }

    // 7列取得
    const data = sheet.getRange(2, 1, lastRow - 1, 7).getValues();

    let csvContent = "file_name,scheduled_time,caption,type,image_prompt\n";

    for (let i = 0; i < data.length; i++) {
        const row = data[i];
        const generatedContent = row[3];
        const type = row[1];
        const prompt = row[4];
        const scheduledTime = row[6]; // G列

        if (!generatedContent) continue;

        // 日付フォーマット調整 (YYYY-MM-DD HH:mm:ss形式が安全)
        let timeStr = "";
        if (scheduledTime instanceof Date) {
            timeStr = Utilities.formatDate(scheduledTime, Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
        } else {
            timeStr = String(scheduledTime);
        }

        const fileName = `image_${('00' + (i + 1)).slice(-3)}.jpg`;

        const escapedCaption = `"${generatedContent.replace(/"/g, '""')}"`;
        const escapedPrompt = `"${prompt.replace(/"/g, '""')}"`;

        csvContent += `${fileName},${timeStr},${escapedCaption},${type},${escapedPrompt}\n`;
    }

    const folder = DriveApp.getRootFolder();
    const fileNameFull = `sns_schedule_${new Date().getTime()}.csv`;
    const file = folder.createFile(fileNameFull, csvContent, MimeType.CSV);

    SpreadsheetApp.getUi().showModalDialog(HtmlService.createHtmlOutput(`
    <p>スケジュール付きCSVを作成しました！</p>
    <p><a href="${file.getUrl()}" target="_blank">${fileNameFull}</a></p>
    <p>これをPythonツールに読み込ませれば、指定日時に自動投稿予約されます。</p>
  `).setWidth(400).setHeight(300), "出力完了");
}

// --- Helper Functions ---
function setApiKey() {
    const ui = SpreadsheetApp.getUi();
    const r = ui.prompt('OpenAI API Key', 'sk-...', ui.ButtonSet.OK_CANCEL);
    if (r.getSelectedButton() == ui.Button.OK) PropertiesService.getScriptProperties().setProperty('OPENAI_API_KEY', r.getResponseText().trim());
}
function getApiKey() { return PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY'); }
function browserMsg(t, m) { Browser.msgBox(t, m, Browser.Buttons.OK); }
function setupSheet(force = false) {
    const sheet = SpreadsheetApp.getActiveSheet();
    if (!force && sheet.getLastRow() > 1) {
        const check = Browser.msgBox('確認', 'シートを初期化すると今のデータが消えます。よろしいですか？', Browser.Buttons.YES_NO);
        if (check == 'no') return;
    }
    sheet.clear();
    // v3.3: Scheduled Time (7列目) を追加
    const headers = ['Topic (テーマ)', 'Type (タイプ)', 'Goal (目的)', 'Generated Content', 'Image Prompt', 'Status', 'Scheduled Time (予約日時)'];
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#d9e1f2');
    sheet.setColumnWidth(1, 200); sheet.setColumnWidth(4, 350); sheet.setColumnWidth(7, 150);
    const typeRule = SpreadsheetApp.newDataValidation().requireValueInList(['Feed', 'Reel', 'Story'], true).build();
    sheet.getRange(2, 2, 999, 1).setDataValidation(typeRule);
    const goalRule = SpreadsheetApp.newDataValidation().requireValueInList(['信頼構築', '常識破壊', 'ノウハウ', 'LINE誘導', '販売'], true).build();
    sheet.getRange(2, 3, 999, 1).setDataValidation(goalRule);
}
