/* ==========================================================================
   极简个人博客交互脚本 (main.js)
   负责：1. 深浅色主题持久化切换  2. 首页时间线分类筛选  3. 代码块一键复制
   ========================================================================== */

(function () {
  const THEME_KEY = "blog-theme-preference";

  // 初始化主题（优先读取本地存储，其次跟随系统偏好）
  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    const prefersDark =
      window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = saved ? saved === "dark" : prefersDark;
    document.documentElement.classList.toggle("dark", isDark);
    updateThemeButtonText(isDark);
  }

  function updateThemeButtonText(isDark) {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;
    btn.textContent = isDark ? "浅色模式" : "深色模式";
    btn.setAttribute("aria-pressed", String(isDark));
  }

  function bindThemeToggle() {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const nextDark = !document.documentElement.classList.contains("dark");
      document.documentElement.classList.toggle("dark", nextDark);
      localStorage.setItem(THEME_KEY, nextDark ? "dark" : "light");
      updateThemeButtonText(nextDark);
    });
  }

  // 首页时间线分类筛选
  function bindCategoryFilter() {
    const filterButtons = document.querySelectorAll("[data-filter]");
    const items = document.querySelectorAll(".timeline-item");
    const yearGroups = document.querySelectorAll(".year-group");
    const countEl = document.getElementById("visibleCount");

    if (!filterButtons.length || !items.length) return;

    filterButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const category = btn.getAttribute("data-filter");

        filterButtons.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");

        let visibleTotal = 0;

        items.forEach((item) => {
          const itemCat = item.getAttribute("data-category");
          const match = category === "all" || itemCat === category;
          item.style.display = match ? "" : "none";
          if (match) visibleTotal += 1;
        });

        // 若某一年份下没有可见文章，隐藏该年份分组
        yearGroups.forEach((group) => {
          const hasVisible = Array.from(group.querySelectorAll(".timeline-item")).some(
            (el) => el.style.display !== "none"
          );
          group.style.display = hasVisible ? "" : "none";
        });

        if (countEl) {
          countEl.textContent = `${visibleTotal} 篇文章`;
        }
      });
    });
  }

  // 文章页代码块一键复制
  function bindCodeCopy() {
    const buttons = document.querySelectorAll(".copy-btn");
    buttons.forEach((btn) => {
      btn.addEventListener("click", async () => {
        const block = btn.closest(".code-block");
        const codeEl = block ? block.querySelector("pre code") : null;
        if (!codeEl) return;

        const text = codeEl.innerText;
        try {
          await navigator.clipboard.writeText(text);
        } catch {
          const textarea = document.createElement("textarea");
          textarea.value = text;
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand("copy");
          document.body.removeChild(textarea);
        }

        const original = btn.textContent;
        btn.textContent = "已复制";
        setTimeout(() => {
          btn.textContent = original;
        }, 1600);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    bindThemeToggle();
    bindCategoryFilter();
    bindCodeCopy();
  });
})();
