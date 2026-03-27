# PR 資料強制收集機制 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 MP-Box-repo 的 PR 流程中，自動關聯 Issue 並強制要求填寫測試方式。

**Architecture:** 新增 PR Template 預填測試方式欄位；新增 `pr-validate` GitHub Actions workflow，於 PR 開啟或更新時自動從分支名稱解析 Issue 編號並注入 `Closes #XX`，同時驗證測試方式區塊是否填寫。Branch Protection 最後手動在 GitHub UI 設定。

**Tech Stack:** GitHub Actions, `actions/github-script@v7`（內建 `@octokit/rest`）, JavaScript（workflow script inline）

---

## File Structure

| 動作 | 路徑 | 說明 |
|------|------|------|
| 新增 | `.github/pull_request_template.md` | PR 開啟時自動帶入的模板 |
| 新增 | `.github/workflows/pr-validate.yml` | PR 驗證 workflow |

---

### Task 1：新增 PR Template

**Files:**
- Create: `.github/pull_request_template.md`

- [ ] **Step 1：建立 PR Template 檔案**

內容如下（完整貼上）：

```markdown
## 測試方式
<!-- 請描述你如何驗證這個變更，不可留空 -->
```

- [ ] **Step 2：Commit 並 push**

```bash
git add .github/pull_request_template.md
git commit -m "feat: add PR template with testing section"
git push
```

- [ ] **Step 3：驗證模板生效**

到 GitHub 開一個 PR（任意分支），確認 PR body 自動帶入「## 測試方式」區塊。

---

### Task 2：建立 pr-validate workflow 骨架

**Files:**
- Create: `.github/workflows/pr-validate.yml`

- [ ] **Step 1：建立 workflow 檔案（骨架，無邏輯）**

```yaml
name: PR Validate

on:
  pull_request:
    types: [opened, edited, synchronize]

permissions:
  pull-requests: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Echo trigger
        run: echo "PR validate triggered for branch ${{ github.head_ref }}"
```

- [ ] **Step 2：Commit 並 push**

```bash
git add .github/workflows/pr-validate.yml
git commit -m "feat: add pr-validate workflow skeleton"
git push
```

- [ ] **Step 3：驗證 workflow 出現在 GitHub**

到 GitHub 該 repo 開一個 PR，進入 PR 頁面的 **Checks** tab，確認出現 `PR Validate` job 且成功執行（顯示 echo 輸出）。

---

### Task 3：自動注入 Closes #XX

**Files:**
- Modify: `.github/workflows/pr-validate.yml`

- [ ] **Step 1：替換 `Echo trigger` step 為自動注入邏輯**

將 `pr-validate.yml` 的 `steps` 區塊改為：

```yaml
    steps:
      - name: Auto-inject Closes reference
        uses: actions/github-script@v7
        with:
          script: |
            const branchName = context.payload.pull_request.head.ref;
            const match = branchName.match(/^issue-(\d+)/);

            if (!match) {
              console.log('分支名稱不符合 issue-{number} 格式，略過自動注入。');
              return;
            }

            const issueNumber = match[1];
            const closesRef = `Closes #${issueNumber}`;
            let body = context.payload.pull_request.body || '';

            if (body.includes(closesRef)) {
              console.log(`"${closesRef}" 已存在，略過。`);
              return;
            }

            body = body.trimEnd() + `\n\n${closesRef}`;
            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.payload.pull_request.number,
              body: body
            });
            console.log(`已自動注入 "${closesRef}" 至 PR body。`);
```

完整檔案此時應為：

```yaml
name: PR Validate

on:
  pull_request:
    types: [opened, edited, synchronize]

permissions:
  pull-requests: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Auto-inject Closes reference
        uses: actions/github-script@v7
        with:
          script: |
            const branchName = context.payload.pull_request.head.ref;
            const match = branchName.match(/^issue-(\d+)/);

            if (!match) {
              console.log('分支名稱不符合 issue-{number} 格式，略過自動注入。');
              return;
            }

            const issueNumber = match[1];
            const closesRef = `Closes #${issueNumber}`;
            let body = context.payload.pull_request.body || '';

            if (body.includes(closesRef)) {
              console.log(`"${closesRef}" 已存在，略過。`);
              return;
            }

            body = body.trimEnd() + `\n\n${closesRef}`;
            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.payload.pull_request.number,
              body: body
            });
            console.log(`已自動注入 "${closesRef}" 至 PR body。`);
```

- [ ] **Step 2：Commit 並 push**

```bash
git add .github/workflows/pr-validate.yml
git commit -m "feat: auto-inject Closes reference from branch name"
git push
```

- [ ] **Step 3：驗證自動注入**

1. 到 MP-Box-repo 開一個 Issue（隨便寫什麼）
2. 等 `issue-create-branch` workflow 自動建立分支（格式 `issue-{number}-xxx`）
3. 在該分支上 push 任意 commit，然後開 PR
4. 確認 PR body 自動出現 `Closes #{issue number}`
5. 確認 GitHub **Checks** tab 的 `Auto-inject Closes reference` step 顯示綠燈

---

### Task 4：驗證測試方式區塊

**Files:**
- Modify: `.github/workflows/pr-validate.yml`

- [ ] **Step 1：在 workflow 新增驗證 step**

在 `pr-validate.yml` 的 `steps` 底部追加（`Auto-inject Closes reference` step 之後）：

```yaml
      - name: Validate testing section
        uses: actions/github-script@v7
        with:
          script: |
            let body = context.payload.pull_request.body || '';

            // 移除 HTML 註解
            body = body.replace(/<!--[\s\S]*?-->/g, '');

            // 找到「測試方式」區塊的內容（到下一個 ## 或結尾為止）
            const match = body.match(/##\s*測試方式([\s\S]*?)(?=\n##|$)/);

            if (!match) {
              core.setFailed('PR body 缺少「## 測試方式」區塊，請依照 PR 模板填寫。');
              return;
            }

            const content = match[1].trim();

            if (!content) {
              core.setFailed('「測試方式」不得為空，請描述你如何驗證這個變更。');
              return;
            }

            console.log('測試方式驗證通過。');
```

完整 `pr-validate.yml` 此時應為：

```yaml
name: PR Validate

on:
  pull_request:
    types: [opened, edited, synchronize]

permissions:
  pull-requests: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Auto-inject Closes reference
        uses: actions/github-script@v7
        with:
          script: |
            const branchName = context.payload.pull_request.head.ref;
            const match = branchName.match(/^issue-(\d+)/);

            if (!match) {
              console.log('分支名稱不符合 issue-{number} 格式，略過自動注入。');
              return;
            }

            const issueNumber = match[1];
            const closesRef = `Closes #${issueNumber}`;
            let body = context.payload.pull_request.body || '';

            if (body.includes(closesRef)) {
              console.log(`"${closesRef}" 已存在，略過。`);
              return;
            }

            body = body.trimEnd() + `\n\n${closesRef}`;
            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.payload.pull_request.number,
              body: body
            });
            console.log(`已自動注入 "${closesRef}" 至 PR body。`);

      - name: Validate testing section
        uses: actions/github-script@v7
        with:
          script: |
            let body = context.payload.pull_request.body || '';

            // 移除 HTML 註解
            body = body.replace(/<!--[\s\S]*?-->/g, '');

            // 找到「測試方式」區塊的內容（到下一個 ## 或結尾為止）
            const match = body.match(/##\s*測試方式([\s\S]*?)(?=\n##|$)/);

            if (!match) {
              core.setFailed('PR body 缺少「## 測試方式」區塊，請依照 PR 模板填寫。');
              return;
            }

            const content = match[1].trim();

            if (!content) {
              core.setFailed('「測試方式」不得為空，請描述你如何驗證這個變更。');
              return;
            }

            console.log('測試方式驗證通過。');
```

- [ ] **Step 2：Commit 並 push**

```bash
git add .github/workflows/pr-validate.yml
git commit -m "feat: validate testing section in PR body"
git push
```

- [ ] **Step 3：測試場景一 — 測試方式為空**

1. 開一個 PR，PR body 只填：
   ```
   ## 測試方式
   ```
   （沒有其他內容）
2. 確認 GitHub Checks 的 `Validate testing section` 失敗，顯示訊息：
   `「測試方式」不得為空，請描述你如何驗證這個變更。`

- [ ] **Step 4：測試場景二 — 只有 HTML 註解**

1. 編輯同一個 PR body 為：
   ```
   ## 測試方式
   <!-- 請描述你如何驗證這個變更，不可留空 -->
   ```
2. 確認 check 仍然失敗（HTML 註解不算內容）。

- [ ] **Step 5：測試場景三 — 正確填寫**

1. 編輯 PR body 為：
   ```
   ## 測試方式
   執行 python second.py，確認輸出 Hello 和 Goodbye 兩行。
   ```
2. 確認 check 通過，顯示綠燈。

---

### Task 5：設定 Branch Protection（手動）

**Files:** 無（GitHub UI 操作）

- [ ] **Step 1：進入 Branch Protection 設定**

到 GitHub：`MPinfo-Co/MP-Box-repo` > **Settings** > **Branches** > **Add branch ruleset**（或 Add rule）

- [ ] **Step 2：設定規則**

- Branch name pattern：`main`
- 勾選 **Require status checks to pass before merging**
- 搜尋並加入 `validate`（對應 job name）作為 required check
- 勾選 **Require branches to be up to date before merging**（建議）

- [ ] **Step 3：儲存並驗證**

1. 開一個測試 PR，測試方式留空
2. 確認 GitHub 的 **Merge** 按鈕呈灰色且顯示 `Required status checks have not passed`

---

## 驗收清單

- [ ] 開 PR 時 body 自動帶入「## 測試方式」模板
- [ ] 從 `issue-{number}-xxx` 分支開 PR，body 自動出現 `Closes #{number}`
- [ ] 從非 `issue-` 開頭的分支開 PR，不會注入 `Closes`，但驗證仍執行
- [ ] 測試方式留空 → check 失敗
- [ ] 測試方式只有 HTML 註解 → check 失敗
- [ ] 測試方式有實際文字 → check 通過
- [ ] Branch Protection 設定後，check 未通過時無法 merge
