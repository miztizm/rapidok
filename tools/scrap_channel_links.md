# 📡 TikTok Video Scraper - Browser Console Tool

> **Part of the Rapidok Schema** - Extract video IDs from any TikTok profile without rate limits or API restrictions.

## 🎯 What This Does

This browser console script extracts **all video IDs** from a TikTok user's profile by:
- **Intercepting TikTok's API calls** (captures data as you scroll)
- **DOM mutation observation** (detects new videos loaded dynamically)
- **Smart auto-scrolling** (automatically loads the entire feed)
- **Username auto-detection** (no manual configuration needed)

**Use Case**: When you need to bulk download from a profile but want to generate the URL list first, or when TikTok's web interface doesn't expose all videos through their official API.

---

## 🚀 Quick Start

### Step 1: Navigate to Target Profile
```
https://www.tiktok.com/@username
```
Open any TikTok profile in your browser (Chrome, Firefox, Edge recommended).

### Step 2: Open Developer Console
- **Windows/Linux**: `F12` or `Ctrl + Shift + J`
- **Mac**: `Cmd + Option + J`

### Step 3: Paste the Script
Copy the entire JavaScript code below and paste it into the console, then press `Enter`.

### Step 4: Start Collection
```javascript
rapidok.start()
```

The scraper will:
1. Auto-detect the username
2. Begin scrolling the page automatically
3. Intercept API responses
4. Extract video IDs in real-time
5. Stop when no new content is detected (after 5 scroll attempts)

### Step 5: Get Results
Once stopped, the script automatically:
- ✅ Copies **full video URLs** to your clipboard
- ✅ Displays all video IDs in the console
- ✅ Shows collection statistics

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `rapidok.start()` | ▶ Start auto-scrolling and video collection |
| `rapidok.stop()` | ⏹ Stop collection and dump results |
| `rapidok.dump()` | 📊 Display all collected videos and stats |
| `rapidok.count()` | 🔢 Show total video count |
| `rapidok.videos()` | 📋 List all video IDs (array format) |
| `rapidok.urls()` | 🔗 List all full video URLs |
| `rapidok.clear()` | 🔄 Reset collection (start over) |
| `rapidok.stats()` | 📈 Show detailed statistics |

---

## 🛠️ How It Works

### **1. Username Detection**
Automatically extracts the username from:
- URL path (`/@username`)
- Page DOM elements
- React internal state
- Fallback to `@unknown` if detection fails

### **2. API Interception**
Patches `window.fetch()` to capture TikTok's internal API responses containing video metadata. This is **non-invasive** and doesn't modify TikTok's functionality.

### **3. DOM Mutation Observer**
Watches for new `<a>` tags with `/video/` hrefs as TikTok's infinite scroll loads content. Extracts video IDs immediately when they appear.

### **4. Smart Auto-Scroll**
- Scrolls by `window.innerHeight` every 2 seconds
- Detects when page height stops increasing
- Stops after 5 consecutive "no new content" detections
- Prevents infinite loops on short profiles

### **5. Deduplication**
Uses a `Set()` to track seen video IDs, preventing duplicates from API/DOM overlap.

---

## 📊 Output Format

### Console Output
```
════════════════════════════════════════════════
🎬 TIKTOK RAPIDOK - FINAL RESULTS
════════════════════════════════════════════════

📊 Statistics:
   Total Videos: 152
   From API Calls: 8
   From DOM Scan: 144
   Scroll Iterations: 23
   Username: @miztizm

────────────────────────────────────────────────
📋 VIDEO IDS (Plain Text - Copy Below):
7563194740645154070
7507925100570660118
7503421463131737366
...

🔗 FULL VIDEO URLS (Plain Text - Copy Below):
https://www.tiktok.com/@miztizm/video/7563194740645154070
https://www.tiktok.com/@miztizm/video/7507925100570660118
https://www.tiktok.com/@miztizm/video/7503421463131737366
...

✅ Video URLs auto-copied to clipboard!
════════════════════════════════════════════════
```

### Clipboard Contents
Full URLs are automatically copied to your clipboard—ready to paste into `links.txt` for Rapidok batch downloads.

---

## 💡 Usage Examples

### Example 1: Quick Extract & Download
```javascript
// In browser console on profile page
rapidok.start()

// Wait for completion (auto-stops)
// URLs are now in clipboard

// Then in terminal
python run.py --links urls.txt --workers 2 --delay 3
```

### Example 2: Manual Control
```javascript
// Start collection
rapidok.start()

// Check progress
rapidok.count()  // Shows: Total: 47

// Stop early if needed
rapidok.stop()

// Review results
rapidok.dump()
```

### Example 3: Resume After Browser Refresh
```javascript
// If you accidentally refresh, re-run the script
// Then manually scroll a bit to trigger API calls
// The script will collect as you browse
rapidok.count()  // Check what's been collected
```

---

## ⚠️ Important Notes

### **Rate Limiting**
- This script **does NOT bypass** TikTok's rate limits
- It only extracts URLs visible through normal browsing
- Use the extracted URLs with Rapidok's `--delay` and `--throttle-rate` options

### **Browser Compatibility**
- ✅ Chrome/Chromium (Recommended)
- ✅ Firefox
- ✅ Edge
- ⚠️ Safari (may have clipboard API restrictions)

### **Limitations**
- Only works on public profiles
- Private/restricted accounts will show limited videos
- TikTok may lazy-load videos differently based on region/account status
- Maximum ~2000-3000 videos per session (TikTok's infinite scroll limit)

### **Ethical Use**
This tool is for **archival and research purposes**. Respect:
- Platform Terms of Service
- Content creator rights
- Copyright and intellectual property laws
- Privacy and data protection regulations

---

## 🔧 Troubleshooting

**Q: Script stops too early**  
A: TikTok's infinite scroll may pause. Manually scroll a bit, then run `rapidok.start()` again.

**Q: No videos detected**  
A: Ensure you're on a profile page (`/@username`), not the homepage. Refresh and retry.

**Q: Duplicate IDs in output**  
A: The script auto-deduplicates. If you see duplicates, they're from different collection runs. Use `rapidok.clear()` before starting.

**Q: Clipboard copy failed**  
A: Some browsers restrict clipboard access. Manually copy from console output.

**Q: Wrong username detected**  
A: Manually set with: `rapidok.username = 'correctname'` before running `rapidok.dump()`.

---

## 🔗 Integration with Rapidok

### Workflow
1. **Extract URLs** (this script) → Generates `urls.txt`
2. **Download Videos** (Rapidok) → Process with rate limiting
3. **Archive** → Organized by creator, with metadata

### Example Pipeline
```bash
# 1. Extract URLs in browser (paste script in console)
rapidok.start()
# Wait for completion, URLs copied to clipboard

# 2. Save to file
# Paste clipboard contents into urls.txt

# 3. Download with Rapidok
python run.py --links urls.txt --workers 2 --delay 3 --save-metadata

# 4. Result: All videos downloaded to downloads/@username/
```

---

## 📜 The Code

```javascript
// ==== TIKTOK VIDEO SCRAPER v2.1 - COMPLETE & FINAL ====
// Features: Auto-detects username, MutationObserver, API interception, smart scrolling

console.clear();
console.log('%c🚀 TikTok Feed Scraper v2.1 - PRODUCTION READY', 'color: #00ff00; font-size: 16px; font-weight: bold;');

window.rapidok = {
    allVideos: [],
    seenIds: new Set(),
    apiCount: 0,
    domCount: 0,
    isRunning: false,
    scrollCount: 0,
    observer: null,
    mutationObserver: null,
    username: null
};

const collector = window.rapidok;

// ===== EXTRACT USERNAME FROM PAGE =====
function detectUsername() {
    // Method 1: From URL path
    const urlMatch = window.location.pathname.match(/@([a-zA-Z0-9._-]+)/);
    if (urlMatch) {
        collector.username = urlMatch[1];
        console.log(`%c✓ Username detected from URL: @${collector.username}`, 'color: #00ff00;');
        return collector.username;
    }
    
    // Method 2: From profile link in page
    const profileLink = document.querySelector('a[href*="/@"]');
    if (profileLink) {
        const match = profileLink.href.match(/@([a-zA-Z0-9._-]+)/);
        if (match) {
            collector.username = match[1];
            console.log(`%c✓ Username detected from page link: @${collector.username}`, 'color: #00ff00;');
            return collector.username;
        }
    }
    
    // Method 3: From React props (TikTok stores data here)
    try {
        const scripts = document.querySelectorAll('script');
        for (let script of scripts) {
            if (script.textContent.includes('uniqueId')) {
                const match = script.textContent.match(/"uniqueId":"([^"]+)"/);
                if (match) {
                    collector.username = match[1];
                    console.log(`%c✓ Username detected from page data: @${collector.username}`, 'color: #00ff00;');
                    return collector.username;
                }
            }
        }
    } catch (e) {}
    
    // Fallback
    collector.username = 'unknown';
    console.log(`%c⚠ Username not detected, using @unknown`, 'color: #ffaa00;');
    return 'unknown';
}

// ===== MUTATION OBSERVER: Detects new DOM elements =====
function setupMutationObserver() {
    const config = { 
        childList: true, 
        subtree: true, 
        attributes: true,
        attributeFilter: ['href', 'data-video-id']
    };
    
    const callback = (mutations) => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) {
                        extractVideoIDs(node);
                    }
                });
            }
        });
    };
    
    collector.mutationObserver = new MutationObserver(callback);
    collector.mutationObserver.observe(document.body, config);
    console.log('%c✓ MutationObserver: Watching for new DOM elements', 'color: #00ccff;');
}

// ===== EXTRACT VIDEO IDS FROM ANY ELEMENT =====
function extractVideoIDs(element) {
    let foundCount = 0;
    
    const links = element.querySelectorAll ? element.querySelectorAll('a[href*="/video/"], [data-video-id]') : [];
    
    links.forEach(link => {
        let id = null;
        
        // Extract from href
        if (link.href && link.href.includes('/video/')) {
            const match = link.href.match(/\/video\/(\d+)/);
            if (match) id = match[1];
        }
        
        // Extract from data attribute
        if (!id && link.dataset.videoId) {
            id = link.dataset.videoId;
        }
        
        if (id && !collector.seenIds.has(id)) {
            collector.seenIds.add(id);
            collector.allVideos.push(id);
            foundCount++;
            console.log(`%c✓ [VIDEO] ${id}`, 'color: #ffff00; font-size: 11px;');
        }
    });
    
    if (foundCount > 0) {
        collector.domCount++;
        console.log(`%c+${foundCount} videos | Total: ${collector.allVideos.length}`, 'color: #00ccff;');
    }
}

// ===== INTERCEPT FETCH API =====
function setupFetchInterception() {
    const origFetch = window.fetch;
    
    window.fetch = function(...args) {
        const [resource] = args;
        const promise = origFetch.apply(this, args);
        
        promise.then(response => {
            const url = typeof resource === 'string' ? resource : resource.url;
            
            if (url && (url.includes('/api/') && url.includes('item_list') || url.includes('feed'))) {
                response.clone().json().then(data => {
                    if (data?.itemList && Array.isArray(data.itemList)) {
                        let newCount = 0;
                        data.itemList.forEach(item => {
                            if (item.id && !collector.seenIds.has(item.id)) {
                                collector.seenIds.add(item.id);
                                collector.allVideos.push(item.id);
                                newCount++;
                            }
                        });
                        
                        if (newCount > 0) {
                            collector.apiCount++;
                            console.log(`%c📡 API #${collector.apiCount}: +${newCount} videos (Total: ${collector.allVideos.length})`, 'color: #00ff88; font-weight: bold;');
                        }
                    }
                }).catch(() => {});
            }
        });
        
        return promise;
    };
    
    console.log('%c✓ Fetch API intercepted', 'color: #00ccff;');
}

// ===== SMART AUTO-SCROLL =====
function startSmartScrolling() {
    if (collector.isRunning) {
        console.warn('Already running!');
        return;
    }
    
    collector.isRunning = true;
    console.log('%c▶ SMART AUTO-SCROLL STARTED', 'color: #00ff00; font-weight: bold; font-size: 14px;');
    
    let lastHeight = document.body.scrollHeight;
    let consecutiveNoChange = 0;
    
    const scrollTimer = setInterval(() => {
        const currentHeight = document.body.scrollHeight;
        
        window.scrollBy(0, window.innerHeight);
        collector.scrollCount++;
        
        if (currentHeight === lastHeight) {
            consecutiveNoChange++;
            console.log(`%c⬆ No new content (${consecutiveNoChange}x)`, 'color: #ff9900;');
            
            if (consecutiveNoChange >= 5) {
                console.log('%c🛑 No new content after 5 attempts - STOPPING', 'color: #ff0000; font-weight: bold;');
                stopScrolling();
                return;
            }
        } else {
            consecutiveNoChange = 0;
            lastHeight = currentHeight;
            console.log(`%c⬇ Scroll #${collector.scrollCount} | Videos: ${collector.allVideos.length}`, 'color: #999;');
        }
    }, 2000);
    
    window.rapidok.scrollTimer = scrollTimer;
}

function stopScrolling() {
    clearInterval(window.rapidok.scrollTimer);
    collector.isRunning = false;
    console.log('%c⏹ STOPPED', 'color: #ff0000; font-weight: bold;');
    setTimeout(() => dumpResults(), 1000);
}

// ===== INITIAL SCAN =====
function scanExistingVideos() {
    console.log('%c🔍 Initial scan of visible videos...', 'color: #00ccff;');
    extractVideoIDs(document.body);
}

// ===== DUMP RESULTS WITH CORRECT URLS =====
function dumpResults() {
    console.log('\n%c════════════════════════════════════════════════', 'color: #00ff00; font-weight: bold;');
    console.log('%c🎬 TIKTOK RAPIDOK - FINAL RESULTS', 'color: #ffff00; font-size: 16px; font-weight: bold;');
    console.log('%c════════════════════════════════════════════════', 'color: #00ff00; font-weight: bold;');
    console.log(`
📊 Statistics:
   Total Videos: ${collector.allVideos.length}
   From API Calls: ${collector.apiCount}
   From DOM Scan: ${collector.domCount}
   Scroll Iterations: ${collector.scrollCount}
   Username: @${collector.username}
    `);
    console.log('%c────────────────────────────────────────────────', 'color: #00ff00;');
    
    // Video IDs only
    console.log('%c📋 VIDEO IDS (Plain Text - Copy Below):', 'color: #ffff00; font-weight: bold; font-size: 13px;');
    console.log(collector.allVideos.join('\n'));
    
    console.log('\n');
    
    // Full URLs with correct username
    const urls = collector.allVideos.map(id => `https://www.tiktok.com/@${collector.username}/video/${id}`).join('\n');
    console.log('%c🔗 FULL VIDEO URLS (Plain Text - Copy Below):', 'color: #ffff00; font-weight: bold; font-size: 13px;');
    console.log(urls);
    
    console.log('\n%c════════════════════════════════════════════════\n', 'color: #00ff00; font-weight: bold;');
    
    // Copy to clipboard
    try {
        navigator.clipboard.writeText(urls);
        console.log('%c✅ Video URLs auto-copied to clipboard!', 'color: #00ff00; font-weight: bold;');
    } catch (e) {
        console.warn('Clipboard copy failed, copy manually from above');
    }
}

// ===== PUBLIC COMMANDS =====
console.log(`%c
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RAPIDOK - TIKTOK VIDEO SCRAPER COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

rapidok.start()          ▶ Start auto-scrolling & collection
rapidok.stop()           ⏹ Stop and dump results
rapidok.dump()           📊 Show current results
rapidok.count()          🔢 Show total count
rapidok.videos()         📋 Show all video IDs
rapidok.urls()           🔗 Show all video URLs
rapidok.clear()          🔄 Reset collection
rapidok.stats()          📈 Show full statistics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    `, 'color: #00ccff; font-family: monospace; font-size: 12px;');

window.rapidok.start = startSmartScrolling;
window.rapidok.stop = stopScrolling;
window.rapidok.dump = dumpResults;
window.rapidok.count = () => console.log(`%cTotal: ${collector.allVideos.length}`, 'color: #00ff00; font-weight: bold;');
window.rapidok.videos = () => console.log(collector.allVideos);
window.rapidok.urls = () => {
    const urls = collector.allVideos.map(id => `https://www.tiktok.com/@${collector.username}/video/${id}`);
    console.log(urls.join('\n'));
};
window.rapidok.clear = () => {
    collector.allVideos = [];
    collector.seenIds.clear();
    console.log('%c🔄 Collection cleared', 'color: #ff0000;');
};
window.rapidok.stats = () => console.log({
    totalVideos: collector.allVideos.length,
    fromAPI: collector.apiCount,
    fromDOM: collector.domCount,
    scrolls: collector.scrollCount,
    username: collector.username
});

// ===== INITIALIZE =====
console.log('%c✓ Setup complete!', 'color: #00ff00; font-weight: bold;');
detectUsername();
setupMutationObserver();
setupFetchInterception();
scanExistingVideos();
console.log(`%c✓ Ready! Type: rapidok.start() to begin scanning`, 'color: #00ff00; font-weight: bold; font-size: 14px;');
```

---

**Stay paranoid. Stay persistent. Stay free.**

---

*Part of the [Rapidok](https://github.com/miztizm/rapidok) toolkit*
