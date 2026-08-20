# AOT PrimaryNav — Accessible Keyboard Pattern

**Date:** 2026-07-28
**Component:** `src/components/shell/PrimaryNav.astro`
**Strategy:** Kadence is being phased out; this is the Astro-native replacement nav.

## Key A11y Features

- `<nav aria-label="Primary navigation" role="menubar">` — landmark + ARIA menubar role
- `aria-current="page"` on active route (uses `Astro.url.pathname`)
- `aria-expanded` + `aria-haspopup` on dropdown triggers
- `role="menuitem"` on all nav links within the menubar
- `role="none"` on `<li>` elements (required when parent is `role="menubar"`)
- Mobile toggle: `aria-controls`, `aria-expanded`, 44×44px touch target
- Keyboard navigation: ArrowDown opens dropdown/focuses first item, Escape closes menu
- Focus management: returns focus to toggle when menu closes
- Click-outside closes menu
- `@media (hover: hover)` query: hover-based dropdowns on desktop only

## HTML Pattern

```astro
<nav class="aot-primary-nav" aria-label="Primary navigation" id="site-navigation" data-aot-nav>
  <button class="nav-toggle" type="button" aria-controls="nav-menu" aria-expanded="false"
          aria-label="Toggle navigation menu" data-nav-toggle>
    <span class="nav-toggle-bar" aria-hidden="true"></span>...
  </button>
  <ul class="nav-menu" id="nav-menu" role="menubar" data-nav-menu>
    {#each nav as item}
    <li class:list={["nav-item", item.children?.length && "has-dropdown"]} role="none">
      <a href={item.href} class="nav-link" role="menuitem"
         aria-current={currentPath === item.href ? "page" : undefined}
         {...(hasChildren ? {"aria-haspopup":"true","aria-expanded":"false"} : {})}>
        {item.label}
      </a>
      {#if hasChildren}
      <ul class="nav-dropdown" role="menu" aria-label="{item.label} submenu">
        <!-- dropdown items -->
      </ul>
      {/if}
    </li>
    {/each}
  </ul>
</nav>
```

## JavaScript Pattern

```js
// Mobile toggle
toggle.addEventListener('click', () => {
  isExpanded ? closeMenu() : openMenu();
});

// Escape closes
nav.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && menu.classList.contains('is-open')) closeMenu();
});

// ArrowDown opens dropdown
link.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    link.setAttribute('aria-expanded', 'true');
    submenu.classList.add('is-open');
    submenu.querySelector('.nav-dropdown-link')?.focus();
  }
});

// Click outside closes
document.addEventListener('click', (e) => {
  if (!nav.contains(e.target)) closeMenu();
});
```

## CSS Notes

- Desktop: `display: flex` on `.nav-menu` (horizontal)
- Mobile: `display: none` by default, `display: flex` when `.is-open`
- `@media (hover: hover)` — hover-based dropdowns disabled on touch devices
- `.sr-only` utility class for visually-hidden labels

## Accessibility Checklist

- [x] Landmarks: `<header role="banner">`, `<nav aria-label>`, `<main id="main">`, `<footer role="contentinfo">`
- [x] Skip link: `<a class="skip-link" href="#main">`
- [x] `aria-current="page"` on active nav item
- [x] Mobile toggle: `aria-expanded`, `aria-controls`, 44×44px target
- [x] Keyboard: Tab, ArrowDown, Escape, focus trapping
- [x] `role="menubar"` / `role="menuitem"` / `role="none"` on `<li>`
- [x] `role="list"` on `<ul>` inside nav (screen reader list semantics)
- [x] `aria-haspopup` + `aria-expanded` on dropdown triggers
- [x] Grandchild submenu support
