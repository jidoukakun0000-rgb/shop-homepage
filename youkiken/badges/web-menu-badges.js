const TAG_ORDER = ["名物", "人気", "特盛可", "持帰"];

const BADGES = {
  特盛可: { label: "特盛可", className: "menu-badge menu-badge--extra-large" },
  持帰: { label: "持帰", className: "menu-badge menu-badge--takeout" },
};

export function orderedTags(tags = []) {
  return [...tags].sort((a, b) => {
    const ai = TAG_ORDER.indexOf(a);
    const bi = TAG_ORDER.indexOf(b);
    return (ai < 0 ? TAG_ORDER.length : ai) - (bi < 0 ? TAG_ORDER.length : bi);
  });
}

export function renderMenuBadges(tags = []) {
  const fragment = document.createDocumentFragment();

  for (const tag of orderedTags(tags)) {
    const definition = BADGES[tag];
    if (!definition) continue; // 「名物」「人気」は既存タグ表示を使用

    const badge = document.createElement("span");
    badge.className = definition.className;
    badge.textContent = definition.label;
    badge.setAttribute("aria-label", definition.label === "持帰" ? "持ち帰り可" : "特盛可");
    fragment.append(badge);
  }

  return fragment;
}

// menu.json 例:
// { "name": "チャーシューメン", "tags": ["人気", "持帰", "特盛可"], "price": 1100 }
// DOM順: name → existingTags → renderMenuBadges(tags) → price
