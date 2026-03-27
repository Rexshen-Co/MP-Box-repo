# PR 資料強制收集機制 — 設計文件

**日期：** 2026-03-27
**範圍：** MPinfo-Co/MP-Box-repo（測試），通過後複製至 P1-code 等下游 repo

---

## 背景

MP-Box 已有 Issue 開立時自動建立分支的機制（`issue-create-branch.yml`），分支命名為 `issue-{number}-{slug}`。目前開 PR 時沒有強制收集任何資訊，也沒有自動關聯 Issue。

---

## 目標

1. PR 開啟時，自動從分支名稱解析 Issue 編號，並在 PR body 補上 `Closes #XX`
2. 強制要求填寫「測試方式」，未填則 CI check 失敗，無法 merge

---

## 新增檔案

### 1. `.github/pull_request_template.md`

PR 開啟時自動帶入的模板，只保留需人工填寫的欄位：

```markdown
## 測試方式
<!-- 請描述你如何驗證這個變更，不可留空 -->
```

### 2. `.github/workflows/pr-validate.yml`

**觸發條件：** `pull_request` 事件，types: `[opened, edited, synchronize]`

**步驟一：自動補上 Closes #XX**
- 從 `github.head_ref`（分支名稱）以 regex `^issue-(\d+)` 解析 Issue 編號
- 若 PR body 尚未包含 `Closes #XX`，透過 GitHub API 更新 PR body 補上
- 若分支名稱不符合命名規則（非 `issue-` 開頭），跳過此步驟

**步驟二：驗證測試方式**
- 讀取 PR body，檢查「測試方式」區塊是否有實際文字內容
- 空白、純 HTML 註解（`<!-- ... -->`）視為未填寫
- 驗證失敗 → exit 1，check 標紅，顯示提示訊息

**所需權限：** `pull-requests: write`（用於更新 PR body）

### 3. GitHub UI Branch Protection（手動設定，最後一步）

路徑：repo Settings > Branches > Add rule，規則套用於 `main`：

- 勾選 **Require status checks to pass before merging**
- 加入 `pr-validate` 作為 required check

---

## 資料流

```
開 PR（從 issue-22-xxx 分支）
  └─ pr-validate workflow 觸發
       ├─ 解析分支名稱 → 補上 Closes #22
       └─ 驗證測試方式是否填寫
            ├─ 通過 → check 綠燈 → 可 merge
            └─ 失敗 → check 紅燈 → 無法 merge（Branch Protection 擋住）
```

---

## 複製至下游 repo 的步驟

測試通過後，將以下兩個檔案複製至各下游 repo：
- `.github/pull_request_template.md`
- `.github/workflows/pr-validate.yml`

並在各 repo 的 GitHub UI 設定 Branch Protection。

---

## 已知限制

- 若 PR 從非 `issue-` 開頭的分支建立（如 `testPR`），不會自動補 `Closes #XX`，但測試方式驗證仍會執行
- Branch Protection 需手動在 GitHub UI 設定，無法透過 workflow 自動化
