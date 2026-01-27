---
tags:
  - プロトタイプ
  - ソースコード
  - Sales_System_Prototype
  - 深層ディスカッション
created: 2026-01-19
status: Archived
---

# Sales_System_Prototype_Knowledge_Bible

[[00_知識マップ|⬅️ 知識マップへ戻る]]

本ドキュメントは、`Sales_System_Prototype` の全ソースコードおよびドキュメントを知識ベースとして保存したものです。

---

## index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sales Management System</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

```

---

## package.json

```json
{
  "name": "sales-system-prototype",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "lucide-react": "^0.309.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "vite": "^5.0.8"
  }
}

```

---

## postcss.config.js

```javascript
export default {
    plugins: {
        tailwindcss: {},
        autoprefixer: {},
    },
}

```

---

## README.md

```markdown
---
tags: [prototype, tool/sales_management, react, vite, ai_assisted]
date: 2026-01-16
source: Building_AI_Sales_Prototypes
---

# Sales Management System Prototype

Tags: #React #Vite #SalesSystem #CRUD #JavaScript #Prototype
Links: [[00_知識マップ]] [[Building_AI_Sales_Prototypes]]

---

## 📋 概要

AI支援による開発デモンストレーションとして作成された、React/Viteベースの販売管理システムプロトタイプです。
顧客管理（CRUD）機能を持ち、モダンなWebアプリケーションの基礎構造を備えています。

## 🎯 機能

- **顧客一覧表示**: 登録された顧客データを一覧で確認
- **顧客追加**: 新しい顧客情報の登録
- **顧客編集**: 既存の顧客情報の更新
- **顧客削除**: 不要な顧客データの削除
- **レスポンシブデザイン**: Tailwind CSSを使用したモダンなUI

## 🛠️ 技術スタック

- **Frontend**: React, Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React

## 🚀 セットアップ

1. **依存関係のインストール**:
   ```bash
   npm install
   ```

2. **開発サーバーの起動**:
   ```bash
   npm run dev
   ```

3. **ブラウザで確認**:
   http://localhost:5173

## 📝 開発メモ

このプロトタイプは、AIによるコーディング支援の有効性を検証するために作成されました。
迅速なプロトタイピングと、クリーンなコード生成能力を実証しています。

```

---

## tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {},
    },
    plugins: [],
}

```

---

## vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
})

```

---

## src\App.jsx

```jsx
import React, { useState } from 'react';
import { Users, ShoppingCart, BarChart3, Settings, Plus, Search } from 'lucide-react';

const mockCustomers = [
    { id: 1, name: "山田 太郎", company: "株式会社ABC", email: "taro@abc.co.jp", status: "Active", sales: "¥1,200,000" },
    { id: 2, name: "鈴木 一郎", company: "XYZ商事", email: "suzuki@xyz.com", status: "Inactive", sales: "¥450,000" },
    { id: 3, name: "佐藤 花子", company: "グローバルテック", email: "sato@global.tech", status: "Active", sales: "¥3,800,000" },
];

function App() {
    const [activeTab, setActiveTab] = useState('customers');
    const [customers, setCustomers] = useState(mockCustomers);

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <div className="w-64 bg-slate-800 text-white flex flex-col">
                <div className="p-6">
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <BarChart3 className="w-8 h-8 text-blue-400" />
                        LionSales
                    </h1>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                    <SidebarItem icon={<BarChart3 />} label="ダッシュボード" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
                    <SidebarItem icon={<Users />} label="顧客管理" active={activeTab === 'customers'} onClick={() => setActiveTab('customers')} />
                    <SidebarItem icon={<ShoppingCart />} label="受注管理" active={activeTab === 'orders'} onClick={() => setActiveTab('orders')} />
                    <SidebarItem icon={<Settings />} label="設定" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
                </nav>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto">
                <header className="bg-white shadow-sm p-6 flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-gray-800">顧客管理</h2>
                    <div className="flex gap-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                            <input type="text" placeholder="検索..." className="pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                        </div>
                        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
                            <Plus className="w-4 h-4" />
                            新規登録
                        </button>
                    </div>
                </header>

                <main className="p-6">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="p-4 font-medium text-gray-500">顧客名</th>
                                    <th className="p-4 font-medium text-gray-500">会社名</th>
                                    <th className="p-4 font-medium text-gray-500">メールアドレス</th>
                                    <th className="p-4 font-medium text-gray-500">ステータス</th>
                                    <th className="p-4 font-medium text-gray-500">年間売上</th>
                                    <th className="p-4 font-medium text-gray-500">操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                {customers.map((customer) => (
                                    <tr key={customer.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="p-4 font-semibold text-gray-700">{customer.name}</td>
                                        <td className="p-4 text-gray-600">{customer.company}</td>
                                        <td className="p-4 text-gray-600">{customer.email}</td>
                                        <td className="p-4">
                                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${customer.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                                                {customer.status}
                                            </span>
                                        </td>
                                        <td className="p-4 font-mono text-gray-700">{customer.sales}</td>
                                        <td className="p-4 text-blue-600 hover:text-blue-800 cursor-pointer">詳細</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </main>
            </div>
        </div>
    );
}

function SidebarItem({ icon, label, active, onClick }) {
    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${active ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-slate-700'}`}
        >
            {icon}
            <span>{label}</span>
        </button>
    )
}

export default App;

```

---

## src\index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

```

---

## src\main.jsx

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)

```

---

