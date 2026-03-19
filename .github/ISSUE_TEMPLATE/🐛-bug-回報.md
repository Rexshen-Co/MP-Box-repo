---
name: "\U0001F41B Bug 回報"
about: 建立一個 Bug 回報以協助我們改善專案
title: ''
labels: bug
assignees: ''
type: Bug

---

body:
  - type: markdown
    attributes:
      value: |
        感謝您抽空回報這個問題！
  - type: textarea
    id: what-happened
    attributes:
      label: 發生了什麼事？
      description: 請詳細描述您遇到的問題，以及您原本預期的結果。
      placeholder: 請告訴我們您看到了什麼...
    validations:
      required: true
  - type: dropdown
    id: browsers
    attributes:
      label: 您使用的瀏覽器？
      multiple: true
      options:
        - Chrome
        - Firefox
        - Safari
        - Edge
  - type: textarea
    id: logs
    attributes:
      label: 相關的 Log 記錄
      description: 請貼上任何相關的錯誤訊息或 Log。
      render: shell
