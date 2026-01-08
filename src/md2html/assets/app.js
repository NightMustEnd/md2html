// サイドバーの開閉
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebarOpenBtn = document.getElementById('sidebarOpenBtn');

if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });
}

if (sidebarOpenBtn) {
    sidebarOpenBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
    });
}

// テーマ切替
const themeToggle = document.getElementById('themeToggle');
const currentTheme = localStorage.getItem('theme') || 'light';

// 初期テーマを適用
document.documentElement.setAttribute('data-theme', currentTheme);
updateThemeIcon(currentTheme);

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const newTheme = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    if (themeToggle) {
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// 検索機能
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');

if (searchInput && window.__SEARCH_INDEX__) {
    let searchTimeout;

    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim().toLowerCase();

        if (query.length === 0) {
            searchResults.classList.remove('active');
            searchResults.innerHTML = '';
            return;
        }

        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 200);
    });

    function performSearch(query) {
        const results = [];
        const keywords = query.split(/\s+/);

        window.__SEARCH_INDEX__.forEach(page => {
            const titleMatch = page.title.toLowerCase().includes(query);
            const contentMatch = page.content.toLowerCase().includes(query);

            if (titleMatch || contentMatch) {
                // スコア計算（タイトルマッチの方が高スコア）
                let score = 0;
                if (titleMatch) score += 10;
                if (contentMatch) score += 1;

                // キーワードごとのマッチ数
                keywords.forEach(keyword => {
                    const titleCount = (page.title.toLowerCase().match(new RegExp(keyword, 'g')) || []).length;
                    const contentCount = (page.content.toLowerCase().match(new RegExp(keyword, 'g')) || []).length;
                    score += titleCount * 5 + contentCount;
                });

                // スニペット生成
                const snippet = generateSnippet(page.content, query);

                results.push({
                    title: page.title,
                    url: page.url,
                    snippet: snippet,
                    score: score
                });
            }
        });

        // スコアでソート
        results.sort((a, b) => b.score - a.score);

        displaySearchResults(results.slice(0, 10)); // 上位10件
    }

    function generateSnippet(text, query) {
        const index = text.toLowerCase().indexOf(query.toLowerCase());
        if (index === -1) {
            return text.substring(0, 100) + '...';
        }

        const start = Math.max(0, index - 50);
        const end = Math.min(text.length, index + query.length + 50);
        let snippet = text.substring(start, end);

        if (start > 0) snippet = '...' + snippet;
        if (end < text.length) snippet = snippet + '...';

        // クエリをハイライト
        const regex = new RegExp(`(${query})`, 'gi');
        snippet = snippet.replace(regex, '<mark>$1</mark>');

        return snippet;
    }

    function displaySearchResults(results) {
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-result-item">検索結果が見つかりませんでした</div>';
            searchResults.classList.add('active');
            return;
        }

        searchResults.innerHTML = results.map(result => `
            <div class="search-result-item" onclick="window.location.href='${result.url}'">
                <div class="search-result-title">${result.title}</div>
                <div class="search-result-snippet">${result.snippet}</div>
            </div>
        `).join('');

        searchResults.classList.add('active');
    }

    // 検索結果外をクリックで閉じる
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('active');
        }
    });
}

// コードコピー機能
function copyCode(button) {
    const codeBlock = button.nextElementSibling;
    const code = codeBlock.querySelector('code');

    if (!code) return;

    const text = code.textContent || code.innerText;

    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.style.backgroundColor = '#4caf50';
        button.style.color = 'white';

        setTimeout(() => {
            button.textContent = originalText;
            button.style.backgroundColor = '';
            button.style.color = '';
        }, 2000);
    }).catch(err => {
        console.error('コピーに失敗しました:', err);
        button.textContent = 'Error';
        setTimeout(() => {
            button.textContent = 'Copy';
        }, 2000);
    });
}

// ページ読み込み時に現在のセクションをハイライト
window.addEventListener('load', () => {
    const hash = window.location.hash;
    if (hash) {
        const element = document.querySelector(hash);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            // TOCの該当リンクをハイライト
            const tocLink = document.querySelector(`.toc a[href="${hash}"]`);
            if (tocLink) {
                tocLink.style.color = 'var(--link-color)';
                tocLink.style.fontWeight = '600';
            }
        }
    }
});

// スクロール時に現在のセクションをハイライト
let currentSection = '';
window.addEventListener('scroll', () => {
    const headings = document.querySelectorAll('.content h1[id], .content h2[id], .content h3[id]');
    let found = false;

    headings.forEach(heading => {
        const rect = heading.getBoundingClientRect();
        if (rect.top <= 100 && !found) {
            const id = heading.id;
            if (id !== currentSection) {
                currentSection = id;

                // TOCのリンクを更新
                document.querySelectorAll('.toc a').forEach(link => {
                    link.style.color = '';
                    link.style.fontWeight = '';
                });

                const tocLink = document.querySelector(`.toc a[href="#${id}"]`);
                if (tocLink) {
                    tocLink.style.color = 'var(--link-color)';
                    tocLink.style.fontWeight = '600';
                }
            }
            found = true;
        }
    });
});
