
// ========================================
// n8n Codeノード用: Unico Brain版 (SNS運用代行)
// ========================================

/*
  【概要】
  スプレッドシートから取得した「フック」「構成」「トーン」をランダムに組み合わせ、
  LLMへの指示（User Prompt）を生成するロジックです。

  【入力】
  - Get Hooks (Node)
  - Get Structures (Node)
  - Get Tones (Node)
*/

// -------- Utils --------
const hasOwn = (o, k) => o && Object.prototype.hasOwnProperty.call(o, k);
const get = (o, k, d = '') => (hasOwn(o, k) && String(o[k]).trim() !== '' ? o[k] : d);
const pickOne = (arr) => arr[Math.floor(Math.random() * arr.length)];

// -------- Type Definitions & Weighting --------
const TYPE_KEYS = ['投稿タイプ', 'タイプ', '種別', 'postType'];

// 投稿タイプの重み付け（バランスの良い運用のため）
const POST_TYPE_WEIGHTS = [
  { t: '価値提供', w: 0.40 }, // お役立ち情報
  { t: 'ノウハウ系', w: 0.20 }, // 具体的な手法
  { t: '共感・感情タイプ', w: 0.15 }, // ストーリー
  { t: '商品訴求', w: 0.10 }, // セールス
  { t: 'ソフトCTA', w: 0.10 }, // 誘導
  { t: '問いかけ', w: 0.05 }, // インタラクション
];

// 重み付きランダム選択関数
function pickWeighted(options) {
  const sum = options.reduce((s, o) => s + (o.w ?? 0), 0);
  const r = Math.random() * sum;
  let acc = 0;
  for (const o of options) {
    acc += o.w;
    if (r <= acc) return o.t;
  }
  return options[0].t;
}

// -------- Data Normalization (Spreadsheet to Object) --------
// ※シートの列名が多少揺れても吸収できるように正規化
const normalize = (r, type) => {
  // 簡易的な正規化ロジック
  const vals = Object.values(r);
  const template = vals.find(v => v.length > 10 && (v.includes('【') || v.includes('「')));
  const name = vals.find(v => v.length < 20 && v !== template);
  return {
    template: template || "",
    name: name || type
  };
};

// -------- Main Logic --------

// 1. Get Data from Previous Nodes
// ※n8nのノード名と一致させる必要があります
const structuresRaw = $('Get Structures').all().map(i => i.json);
const hooksRaw = $('Get Hooks').all().map(i => i.json);
const tonesRaw = $('Get Tones').all().map(i => i.json);

if (!structuresRaw.length || !hooksRaw.length || !tonesRaw.length) {
  throw new Error('スプレッドシートのデータが取得できませんでした。');
}

// 2. Select Post Type
const g = $getWorkflowStaticData('global');
const lastType = g.lastPostType || null;
// 同じタイプが連続しないように調整（簡易版）
let postType = pickWeighted(POST_TYPE_WEIGHTS);
if (postType === lastType) postType = pickWeighted(POST_TYPE_WEIGHTS);
g.lastPostType = postType;

// 3. Pick Patterns Randomly
const structure = pickOne(structuresRaw);
const hook = pickOne(hooksRaw);
const tone = pickOne(tonesRaw);

// 4. Define Products (SNS運用代行サービスの例)
// ※必要に応じて書き換えてください
const products = [
  'SNS運用代行「ユニコ・エージェンシー」',
  '最短で1万フォロワーを目指す「ロードマップ講座」',
  'クリック率を3倍にする「ライティング・テンプレート」',
  '全自動収益化システム構築コンサル',
];

const selectedProduct = pickOne(products);

// 5. Construct User Prompt (The "Chat Input")
const promptDetail = `
【今回の投稿テーマ】: ${postType}
【使用する構成】: ${structure['構成テンプレート'] || structure['構成名']}
【使用するフック】: ${hook['フックテンプレート'] || hook['フック名']}
【使用するトーン】: ${tone['トーン指示'] || tone['トーン名']}
【訴求する商品（必要な場合）】: ${selectedProduct}

## 指示
上記の「構成」と「フック」の型を厳守し、「トーン」の口調で、SNS（Threads/Instagram）用の投稿本文を作成してください。
読者が思わず保存したくなるような、有益かつ感情を揺さぶる内容にしてください。
`;

// 6. Context Selection for System Prompt (Optional)
// JSON側のSystem Promptが固定の場合は無視されますが、動的変更用に残します
let context = "content_creation";
if (postType === '商品訴求') context = "closer";

// 7. Output
return [{
  json: {
    chatInput: promptDetail,
    selectedProduct: selectedProduct,
    // knowledgeModules: `
    //   - Vol.10 (Use "Us vs Them" narrative & Jargon)
    //   - Vol.11 (Emotional Triggers: Curiosity & Urgency)
    //   - Vol.12 (Social Proof: Testimonials & Authority)
    //   - Vol.13 (Scarcity & Exclusivity)
    //   - Vol.14 (Viral Science: "Noise" hook & "Incompleteness" loop)
    //   Constraint: Create high-engagement posts that trigger Dopamine & Belongingness.
    // `,
    postType: postType,
    context: context,
    timestamp: new Date().toISOString()
  }
}];
```
