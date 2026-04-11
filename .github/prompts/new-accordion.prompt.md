---
mode: agent
description: "Add a new accordion section to a company panel in portfolio_showcase.html"
---

Add a new accordion section to the **${input:company}** panel in `portfolio_showcase.html`.

- Accordion group ID: `${input:accordionGroupId}` (e.g. `witheritelawSections`, `aaSections`, `citiSections`)
- New collapse ID: `${input:collapseId}` — must be unique across the entire file
- Emoji: ${input:emoji}
- Title: **${input:title}**
- Content: ${input:content}

Use this exact structure:
```html
<div class="pt-acc-item">
  <button class="pt-acc-header" type="button"
          data-bs-toggle="collapse" data-bs-target="#${input:collapseId}"
          aria-expanded="false" aria-controls="${input:collapseId}">
    <span>${input:emoji}</span> ${input:title}
    <i class="fas fa-chevron-down pt-acc-chevron"></i>
  </button>
  <div id="${input:collapseId}" class="collapse" data-bs-parent="#${input:accordionGroupId}">
    <div class="pt-acc-body">
      <p>${input:content}</p>
    </div>
  </div>
</div>
```

Insert it before the closing `</div><!-- /${input:accordionGroupId} -->` comment.
Do not change any other accordion items.
