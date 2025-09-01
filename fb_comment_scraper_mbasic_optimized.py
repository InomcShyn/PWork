# fb_comment_scraper_mbasic_optimized.py
# Phiên bản tối ưu hóa đặc biệt cho mbasic.facebook.com
import time, random, threading, re, requests, pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ----------------------------
# Helper utils
# ----------------------------
def parse_cookies_to_list(cookie_str):
    cookies_list = []
    for pair in cookie_str.split(';'):
        pair = pair.strip()
        if '=' in pair:
            name, value = pair.split('=', 1)
            cookies_list.append({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com'})
    return cookies_list

def parse_cookies_to_dict(cookie_str):
    d = {}
    for pair in cookie_str.split(';'):
        pair = pair.strip()
        if '=' in pair:
            name, value = pair.split('=', 1)
            d[name.strip()] = value.strip()
    return d

def ensure_mbasic_url(url):
    if "mbasic.facebook.com" in url:
        return url
    url = url.replace("www.facebook.com", "mbasic.facebook.com")
    url = url.replace("m.facebook.com", "mbasic.facebook.com")
    return url

def try_resolve_numeric_uid(profile_href, cookies_dict, timeout=6):
    if not profile_href:
        return None
    try:
        href = profile_href.replace("www.facebook.com", "mbasic.facebook.com")
        r = requests.get(href, cookies=cookies_dict, timeout=timeout, allow_redirects=True)
        html = r.text
        m = re.search(r"profile\.php\?id=(\d+)", html)
        if m: return m.group(1)
        m2 = re.search(r'"entity_id":"(\d+)"', html)
        if m2: return m2.group(1)
        parts = profile_href.rstrip('/').split('/')
        if parts: return parts[-1]
    except:
        return None
    return None

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove Facebook-specific UI elements
    text = re.sub(r'\b(Like|Reply|Share|Comment|Translate|See translation|Hide|Report|Block)\b', '', text)
    text = re.sub(r'\b(Thích|Phản hồi|Chia sẻ|Bình luận|Dịch|Ẩn|Báo cáo|Chặn)\b', '', text)
    text = re.sub(r'\b(\d+\s*(minutes?|hours?|days?|seconds?|phút|giờ|ngày|giây)\s*ago|trước)\b', '', text)
    text = re.sub(r'\b(Top fan|Most relevant|Newest|All comments|Fan hàng đầu|Liên quan nhất|Mới nhất|Tất cả bình luận)\b', '', text)
    return text.strip()

# ----------------------------
# Mbasic-Optimized Comment Scraper
# ----------------------------
class FacebookMbasicOptimizedScraper:
    def __init__(self, cookie_str, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Use mobile user agent for better mbasic compatibility
        options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; SM-G973F) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36")
        options.add_argument("window-size=414,896")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.cookie_str = cookie_str or ""
        self.cookies_list = parse_cookies_to_list(self.cookie_str)
        self.cookies_dict = parse_cookies_to_dict(self.cookie_str)
        self.current_comments = []
        
        if self.cookies_list:
            self._login_with_cookies()

    def _login_with_cookies(self):
        self.driver.get("https://mbasic.facebook.com")
        time.sleep(3)
        for c in self.cookies_list:
            cookie = c.copy()
            cookie.pop('sameSite', None)
            cookie.pop('httpOnly', None)
            cookie.pop('secure', None)
            cookie.setdefault('domain', '.facebook.com')
            try:
                self.driver.add_cookie(cookie)
            except: pass
        self.driver.get("https://mbasic.facebook.com")
        time.sleep(4)

    def load_post(self, post_url):
        self.post_url = ensure_mbasic_url(post_url)
        print(f"Loading post: {self.post_url}")
        
        try:
            self.driver.get(self.post_url)
            time.sleep(6)
            
            current_url = self.driver.current_url
            print(f"Current URL after load: {current_url}")
            
            # Check accessibility
            page_title = self.driver.title
            print(f"Page title: {page_title}")
            
            if "Log in" in page_title or "Login" in page_title or "Đăng nhập" in page_title:
                print("ERROR: Not logged in! Check your cookies.")
                return False
            
            # Check if we can see comments section
            try:
                comments_section = self.driver.find_element(By.XPATH, "//*[contains(text(),'Comment') or contains(text(),'Bình luận')]")
                print("✓ Comments section found")
            except:
                print("⚠ Comments section not immediately visible")
            
            return True
                
        except Exception as e:
            print(f"Error loading post: {e}")
            return False

    def smart_expand_comments(self, max_rounds=50):
        """Intelligent comment expansion specifically for mbasic"""
        print("=== SMART COMMENT EXPANSION FOR MBASIC ===")
        
        round_count = 0
        consecutive_no_expansion = 0
        total_clicks = 0
        
        while round_count < max_rounds and consecutive_no_expansion < 6:
            round_count += 1
            expanded_this_round = False
            print(f"\n--- Expansion Round {round_count} ---")
            
            # Scroll strategy: scroll down then up to trigger loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Mbasic-specific expand link patterns
            mbasic_expand_patterns = [
                # English patterns
                "//a[contains(text(),'View more comments')]",
                "//a[contains(text(),'View previous comments')]",
                "//a[contains(text(),'View more replies')]", 
                "//a[contains(text(),'View replies')]",
                "//a[contains(text(),'Show more')]",
                "//a[contains(text(),'See more')]",
                "//a[contains(text(),'More comments')]",
                "//a[contains(text(),'Load more')]",
                
                # Vietnamese patterns
                "//a[contains(text(),'Xem thêm bình luận')]",
                "//a[contains(text(),'Xem bình luận trước')]",
                "//a[contains(text(),'Xem thêm phản hồi')]",
                "//a[contains(text(),'Xem phản hồi')]",
                "//a[contains(text(),'Hiển thị thêm')]",
                "//a[contains(text(),'Xem thêm')]",
                "//a[contains(text(),'Tải thêm')]",
                
                # Href-based patterns (more reliable)
                "//a[contains(@href,'comment_id') and contains(@href,'view')]",
                "//a[contains(@href,'reply_comment_id')]",
                "//a[contains(@href,'comment') and (contains(text(),'View') or contains(text(),'Xem'))]",
                "//a[contains(@href,'comment') and (contains(text(),'more') or contains(text(),'thêm'))]",
                
                # Generic but filtered
                "//a[contains(@href,'facebook.com') and (contains(text(),'View') or contains(text(),'Show') or contains(text(),'Xem'))]",
                
                # Fallback: any clickable element with expand text
                "//*[self::a or self::span or self::div][contains(text(),'View more') or contains(text(),'Xem thêm')]",
            ]
            
            all_expand_links = []
            for pattern in mbasic_expand_patterns:
                try:
                    links = self.driver.find_elements(By.XPATH, pattern)
                    all_expand_links.extend(links)
                except Exception as e:
                    print(f"Pattern failed: {pattern[:50]}... - {e}")
                    continue
            
            # Remove duplicates and filter
            unique_links = []
            seen_locations = set()
            
            for link in all_expand_links:
                try:
                    if not link.is_displayed():
                        continue
                        
                    location = link.location
                    text = link.text.strip()
                    href = link.get_attribute('href') or ''
                    
                    # Create unique identifier
                    unique_id = f"{location['x']}_{location['y']}_{text[:30]}"
                    
                    if unique_id not in seen_locations:
                        seen_locations.add(unique_id)
                        unique_links.append((link, text, href))
                        
                except:
                    continue
            
            print(f"Found {len(unique_links)} unique expand links")
            
            # Click links with priority system
            for i, (link, text, href) in enumerate(unique_links):
                try:
                    # Priority system: comment links > reply links > generic
                    priority = 0
                    if 'comment' in href.lower(): priority += 3
                    if 'reply' in href.lower(): priority += 2
                    if any(word in text.lower() for word in ['view', 'xem', 'more', 'thêm']): priority += 1
                    
                    print(f"  Link {i+1}: '{text[:40]}' (priority: {priority})")
                    
                    if priority < 1:
                        print(f"    Skipping low priority link")
                        continue
                    
                    # Scroll to link
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    time.sleep(1.5)
                    
                    # Try clicking
                    clicked = False
                    try:
                        # Method 1: Regular click
                        link.click()
                        clicked = True
                    except:
                        try:
                            # Method 2: JavaScript click
                            self.driver.execute_script("arguments[0].click();", link)
                            clicked = True
                        except:
                            try:
                                # Method 3: Navigate to href
                                if href and 'facebook.com' in href:
                                    self.driver.get(href)
                                    clicked = True
                            except:
                                continue
                    
                    if clicked:
                        print(f"    ✓ Successfully clicked: '{text[:40]}'")
                        expanded_this_round = True
                        total_clicks += 1
                        time.sleep(random.uniform(4, 7))  # Longer wait for loading
                        
                        # Check if page changed significantly (new comments loaded)
                        try:
                            current_comment_count = len(self.driver.find_elements(By.XPATH, "//div[h3//a[contains(@href,'profile.php')]]"))
                            print(f"    Current comment elements visible: {current_comment_count}")
                        except:
                            pass
                    
                except Exception as e:
                    print(f"    Failed to click link {i+1}: {e}")
                    continue
            
            if expanded_this_round:
                consecutive_no_expansion = 0
                print(f"✓ Round {round_count} successful - {total_clicks} total clicks so far")
            else:
                consecutive_no_expansion += 1
                print(f"✗ Round {round_count} - no expansion ({consecutive_no_expansion}/6)")
        
        print(f"=== EXPANSION COMPLETE === (Total clicks: {total_clicks})")
        
        # Final loading sequence
        print("Final loading sequence...")
        for i in range(12):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            if i % 3 == 0:
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)

    def analyze_comment_hierarchy(self, element):
        """Analyze element to determine if it's a main comment or reply"""
        try:
            element_html = element.get_attribute('outerHTML')
            
            # Method 1: Check for mbasic-specific reply indicators
            reply_indicators = [
                'margin-left:',
                'padding-left:',
                'style="margin-left:',
                'style="padding-left:',
            ]
            
            has_indentation = any(indicator in element_html for indicator in reply_indicators)
            
            # Extract indentation value if present
            indentation_level = 0
            margin_match = re.search(r'margin-left:\s*(\d+)', element_html)
            padding_match = re.search(r'padding-left:\s*(\d+)', element_html)
            
            if margin_match:
                indentation_level = max(indentation_level, int(margin_match.group(1)))
            if padding_match:
                indentation_level = max(indentation_level, int(padding_match.group(1)))
            
            # Method 2: Check ancestor structure
            try:
                # Count how many comment-like ancestors this element has
                comment_ancestors = element.find_elements(By.XPATH, 
                    "./ancestor::div[h3//a[contains(@href,'profile.php')] or h3//a[contains(@href,'user.php')]]")
                ancestor_comment_count = len(comment_ancestors)
            except:
                ancestor_comment_count = 0
            
            # Method 3: Check position relative to other comments
            try:
                # Find previous sibling elements that look like comments
                prev_siblings = element.find_elements(By.XPATH, "./preceding-sibling::div")
                following_siblings = element.find_elements(By.XPATH, "./following-sibling::div")
            except:
                prev_siblings = []
                following_siblings = []
            
            # Decision logic for mbasic
            is_reply = False
            
            # Strong indicators of reply
            if indentation_level > 15:  # Significant indentation
                is_reply = True
            elif ancestor_comment_count > 1:  # Nested within another comment
                is_reply = True
            elif has_indentation and len(prev_siblings) > 0:  # Indented and has preceding content
                is_reply = True
            
            comment_type = "Reply" if is_reply else "Comment"
            
            print(f"    Hierarchy analysis: indent={indentation_level}px, ancestors={ancestor_comment_count}, "
                  f"has_indent={has_indentation} -> {comment_type}")
            
            return comment_type
            
        except Exception as e:
            print(f"    Error in hierarchy analysis: {e}")
            return "Comment"

    def extract_mbasic_comment_data(self, element):
        """Extract comment data optimized for mbasic structure"""
        try:
            # Get full text
            full_text = element.text.strip()
            if not full_text or len(full_text) < 3:
                return None
            
            print(f"  Processing mbasic element: '{full_text[:80]}...'")
            
            # Extract name from h3 > a structure (mbasic standard)
            username = "Unknown"
            profile_href = None
            
            try:
                # Primary method: h3 > a structure
                name_link = element.find_element(By.XPATH, ".//h3/a")
                username = name_link.text.strip()
                profile_href = name_link.get_attribute('href')
                print(f"    Found name via h3/a: '{username}'")
                
            except:
                try:
                    # Fallback: any profile link
                    profile_links = element.find_elements(By.XPATH, ".//a[contains(@href,'profile.php') or contains(@href,'user.php')]")
                    if profile_links:
                        username = profile_links[0].text.strip()
                        profile_href = profile_links[0].get_attribute('href')
                        print(f"    Found name via profile link: '{username}'")
                except:
                    pass
            
            # Extract content by removing UI elements and name
            content = full_text
            
            # Remove username from content
            if username != "Unknown":
                # Try different removal strategies
                content = re.sub(rf'^.*?{re.escape(username)}\s*', '', content, count=1).strip()
            
            # Remove timestamp patterns
            content = re.sub(r'^\d+\s*(min|hour|day|sec|phút|giờ|ngày|giây).*?(ago|trước)\s*', '', content).strip()
            
            # Remove UI elements
            content = clean_text(content)
            
            # Remove action words that might remain
            action_patterns = [
                r'^(Like|Reply|Share|Comment|Thích|Phản hồi|Chia sẻ|Bình luận)\s*',
                r'\s*(Like|Reply|Share|Comment|Thích|Phản hồi|Chia sẻ|Bình luận)$',
            ]
            
            for pattern in action_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE).strip()
            
            # Final validation
            if len(content) < 5:
                print(f"    Content too short: '{content}'")
                return None
            
            # Skip if content is just UI elements
            if re.match(r'^(Like|Reply|Share|Comment|Thích|Phản hồi|Chia sẻ|Bình luận|\d+\s*(min|hour|day)).*$', 
                       content, re.IGNORECASE):
                print(f"    Skipping UI-only content: '{content}'")
                return None
            
            # Determine comment type
            comment_type = self.analyze_comment_hierarchy(element)
            
            print(f"    ✓ Valid {comment_type.lower()}: '{username}' - '{content[:60]}...'")
            
            return {
                'username': username,
                'content': content,
                'profile_href': profile_href,
                'comment_type': comment_type,
                'element': element
            }
            
        except Exception as e:
            print(f"  Error extracting mbasic comment data: {e}")
            return None

    def scrape_all_comments(self, limit=0, resolve_uid=True, progress_callback=None):
        print("=== STARTING MBASIC-OPTIMIZED SCRAPING ===")
        
        # Expand all comments first
        self.smart_expand_comments()
        
        comments = []
        seen_content = set()
        self.current_comments = comments
        
        # Save page for debugging
        try:
            with open("/workspace/debug_mbasic_expanded.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("Saved page source to debug_mbasic_expanded.html")
        except:
            pass

        # Mbasic-specific comment selectors (ordered by reliability)
        mbasic_selectors = [
            # Most reliable: elements with h3 containing profile links
            "//div[h3/a[contains(@href,'profile.php')]]",
            "//div[h3/a[contains(@href,'user.php')]]",
            
            # Secondary: any div with profile links and substantial text
            "//div[.//a[contains(@href,'profile.php')] and string-length(normalize-space(text())) > 20]",
            "//div[.//a[contains(@href,'user.php')] and string-length(normalize-space(text())) > 20]",
            
            # Tertiary: content-based detection
            "//div[h3 and string-length(normalize-space(text())) > 30]",
            "//div[.//strong and string-length(normalize-space(text())) > 25]",
            
            # Last resort: any substantial text with some structure
            "//div[string-length(normalize-space(text())) > 40 and (.//a or .//strong or .//b)]",
        ]

        all_elements = []
        
        # Collect elements with deduplication
        for i, selector in enumerate(mbasic_selectors):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                print(f"Mbasic selector {i+1}: Found {len(elements)} elements")
                
                for elem in elements:
                    try:
                        # Use location and size for deduplication
                        location = elem.location
                        size = elem.size
                        unique_key = f"{location['x']},{location['y']},{size['width']},{size['height']}"
                        
                        # Check if already added
                        if not any(hasattr(existing, '_unique_key') and existing._unique_key == unique_key 
                                  for existing in all_elements):
                            elem._unique_key = unique_key
                            all_elements.append(elem)
                    except:
                        # If location check fails, add anyway but mark as potential duplicate
                        all_elements.append(elem)
                        
            except Exception as e:
                print(f"Mbasic selector {i+1} failed: {e}")
                continue

        print(f"Total unique elements to process: {len(all_elements)}")

        # Process elements
        for i, element in enumerate(all_elements):
            try:
                if limit and len(comments) >= limit:
                    break

                print(f"\n--- Processing element {i+1}/{len(all_elements)} ---")
                
                # Extract comment data
                comment_data = self.extract_mbasic_comment_data(element)
                
                if not comment_data:
                    continue
                
                # Enhanced deduplication
                content_key = comment_data['content'].lower().strip()[:100]
                username_key = comment_data['username'].lower().strip()
                full_key = f"{username_key}_{content_key}"
                
                if full_key in seen_content:
                    print("    Skipping: duplicate content")
                    continue
                seen_content.add(full_key)
                
                # Resolve UID
                uid = "Unknown"
                if resolve_uid and comment_data['profile_href']:
                    try:
                        uid = try_resolve_numeric_uid(comment_data['profile_href'], self.cookies_dict)
                        if not uid:
                            uid = "Unknown"
                    except:
                        uid = "Unknown"
                
                # Create final comment object
                final_comment = {
                    "Type": comment_data['comment_type'],
                    "UID": uid,
                    "Name": comment_data['username'],
                    "Content": comment_data['content'],
                    "ProfileLink": comment_data['profile_href'] or "",
                    "ContentLength": len(comment_data['content']),
                    "ProcessedIndex": len(comments)
                }
                
                comments.append(final_comment)
                
                print(f"  ✓ ADDED {comment_data['comment_type'].upper()} #{len(comments)}")
                print(f"    Name: {comment_data['username']}")
                print(f"    Content: {comment_data['content'][:80]}...")
                
                if progress_callback:
                    progress_callback(len(comments))
                    
            except Exception as e:
                print(f"  Error processing element {i}: {e}")
                continue

        print(f"\n=== MBASIC SCRAPING COMPLETE ===")
        print(f"Total items extracted: {len(comments)}")
        
        # Final statistics
        comments_count = len([c for c in comments if c['Type'] == 'Comment'])
        replies_count = len([c for c in comments if c['Type'] == 'Reply'])
        print(f"Main Comments: {comments_count}")
        print(f"Replies: {replies_count}")
        
        # Sort: main comments first, then replies
        comments.sort(key=lambda x: (x['Type'] == 'Reply', x['ProcessedIndex']))
        
        return comments

    def close(self):
        try: 
            self.driver.quit()
        except: 
            pass

# ----------------------------
# Enhanced GUI with Progress Bar
# ----------------------------
class FBCommentMbasicGUI:
    def __init__(self, root):
        self.root = root
        root.title("FB Mbasic Comment Scraper - OPTIMIZED VERSION")
        root.geometry("1000x750")

        # Main frame with scrollbar
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Title
        title_label = tk.Label(main_frame, text="Facebook Comment Scraper - Mbasic Optimized", 
                              font=("Arial", 14, "bold"), fg="#1877f2")
        title_label.pack(pady=(0,10))

        # URL input
        url_frame = tk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(url_frame, text="Link bài viết Facebook:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.entry_url = tk.Entry(url_frame, width=120, font=("Arial", 9))
        self.entry_url.pack(fill=tk.X, pady=(2,0))

        # Cookie input
        cookie_frame = tk.Frame(main_frame)
        cookie_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(cookie_frame, text="Cookie (copy từ browser):", font=("Arial", 10, "bold")).pack(anchor="w")
        self.txt_cookie = tk.Text(cookie_frame, height=6, width=120, font=("Arial", 8))
        self.txt_cookie.pack(fill=tk.X, pady=(2,0))

        # Options frame
        options_frame = tk.LabelFrame(main_frame, text="Tùy chọn", font=("Arial", 10, "bold"))
        options_frame.pack(fill=tk.X, pady=(0,10))
        
        opt_row1 = tk.Frame(options_frame)
        opt_row1.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(opt_row1, text="Giới hạn số lượng (0 = tất cả):").pack(side=tk.LEFT)
        self.entry_limit = tk.Entry(opt_row1, width=10)
        self.entry_limit.insert(0, "0")
        self.entry_limit.pack(side=tk.LEFT, padx=(5,20))

        self.headless_var = tk.BooleanVar(value=True)
        tk.Checkbutton(opt_row1, text="Chạy ẩn (headless)", variable=self.headless_var).pack(side=tk.LEFT, padx=(0,20))

        self.resolve_uid_var = tk.BooleanVar(value=True)
        tk.Checkbutton(opt_row1, text="Lấy UID", variable=self.resolve_uid_var).pack(side=tk.LEFT)

        # File output
        file_frame = tk.LabelFrame(main_frame, text="File xuất dữ liệu", font=("Arial", 10, "bold"))
        file_frame.pack(fill=tk.X, pady=(0,10))
        
        file_input_frame = tk.Frame(file_frame)
        file_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.entry_file = tk.Entry(file_input_frame, width=100, font=("Arial", 9))
        self.entry_file.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(file_input_frame, text="Chọn...", command=self.choose_file).pack(side=tk.RIGHT, padx=(5,0))

        # Status and progress
        status_frame = tk.LabelFrame(main_frame, text="Trạng thái", font=("Arial", 10, "bold"))
        status_frame.pack(fill=tk.X, pady=(0,10))
        
        self.lbl_status = tk.Label(status_frame, text="Sẵn sàng - Phiên bản tối ưu cho mbasic", 
                                  fg="blue", font=("Arial", 10))
        self.lbl_status.pack(padx=10, pady=5)

        self.lbl_progress = tk.Label(status_frame, text="Comments: 0 | Replies: 0", 
                                   fg="green", font=("Arial", 10))
        self.lbl_progress.pack(padx=10, pady=(0,5))

        # Progress bar
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(0,5))

        # Control buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.btn_start = tk.Button(button_frame, text="🚀 Bắt đầu scrape", bg="#28a745", fg="white", 
                                  command=self.start_scrape_thread, font=("Arial", 11, "bold"),
                                  height=2, width=20)
        self.btn_start.pack(side=tk.LEFT, padx=(0,10))

        self.btn_stop = tk.Button(button_frame, text="⏹ Dừng", bg="#dc3545", fg="white", 
                                 command=self.stop_scrape, state=tk.DISABLED,
                                 font=("Arial", 11, "bold"), height=2, width=15)
        self.btn_stop.pack(side=tk.LEFT)

        self.progress_var = tk.IntVar(value=0)
        self.progress_label = tk.Label(button_frame, textvariable=self.progress_var, 
                                     fg="green", font=("Arial", 12, "bold"))
        self.progress_label.pack(side=tk.RIGHT)

        # Instructions
        instructions = tk.Text(main_frame, height=4, wrap=tk.WORD, font=("Arial", 8))
        instructions.pack(fill=tk.X, pady=(10,0))
        instructions.insert(tk.END, 
            "HƯỚNG DẪN:\n"
            "1. Dán link bài viết Facebook (sẽ tự chuyển sang mbasic)\n"
            "2. Dán cookie từ browser (F12 > Application > Cookies > facebook.com)\n"
            "3. Chọn file Excel để lưu kết quả\n"
            "4. Click 'Bắt đầu scrape' và chờ kết quả\n"
            "PHIÊN BẢN NÀY ĐÃ ĐƯỢC TỐI ƯU HÓA ĐỂ LẤY NHIỀU COMMENT HƠN VÀ PHÂN BIỆT CHÍNH XÁC COMMENT/REPLY!")
        instructions.config(state=tk.DISABLED)

        self._scrape_thread = None
        self._stop_flag = False
        self.scraper = None
        self.current_comments = []

    def choose_file(self):
        f = filedialog.asksaveasfilename(
            defaultextension=".xlsx", 
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Chọn file để lưu kết quả"
        )
        if f:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, f)

    def start_scrape_thread(self):
        url = self.entry_url.get().strip()
        cookie_str = self.txt_cookie.get("1.0", tk.END).strip()
        file_out = self.entry_file.get().strip() or "fb_comments_mbasic_optimized.xlsx"
        
        if not url:
            messagebox.showerror("Thiếu thông tin", "Vui lòng nhập link bài viết Facebook.")
            return
        
        if not cookie_str:
            messagebox.showwarning("Cảnh báo", "Không có cookie. Có thể chỉ lấy được comment public.")
        
        try: 
            limit = int(self.entry_limit.get().strip())
        except: 
            limit = 0

        self._stop_flag = False
        self.progress_var.set(0)
        self.current_comments = []
        self.progress_bar.start()
        
        self.lbl_status.config(text="Đang khởi động scraper tối ưu...", fg="orange")
        self.lbl_progress.config(text="Comments: 0 | Replies: 0")
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        self._scrape_thread = threading.Thread(target=self._scrape_worker, 
                                             args=(url, cookie_str, file_out, limit, 
                                                   self.headless_var.get(), self.resolve_uid_var.get()))
        self._scrape_thread.daemon = True
        self._scrape_thread.start()

    def stop_scrape(self):
        self._stop_flag = True
        self.lbl_status.config(text="Đang dừng...", fg="red")
        self.btn_stop.config(state=tk.DISABLED)

    def _progress_cb(self, count):
        self.progress_var.set(count)
        
        # Update comment/reply counts in real-time
        comments_count = len([c for c in self.current_comments if c.get('Type') == 'Comment'])
        replies_count = len([c for c in self.current_comments if c.get('Type') == 'Reply'])
        self.lbl_progress.config(text=f"Comments: {comments_count} | Replies: {replies_count}")
        
        self.lbl_status.config(text=f"Đã xử lý {count} items...", fg="green")
        self.root.update_idletasks()

    def _scrape_worker(self, url, cookie_str, file_out, limit, headless, resolve_uid):
        try:
            self.lbl_status.config(text="Khởi tạo Chrome driver...", fg="orange")
            self.scraper = FacebookMbasicOptimizedScraper(cookie_str, headless=headless)
            
            if self._stop_flag: return
            
            self.lbl_status.config(text="Đang tải trang bài viết...", fg="orange")
            success = self.scraper.load_post(url)
            
            if not success:
                self.lbl_status.config(text="❌ Lỗi: Không thể tải bài viết hoặc không đăng nhập", fg="red")
                messagebox.showerror("Lỗi", "Không thể tải bài viết. Kiểm tra:\n• Cookie có đúng?\n• Link có đúng?\n• Bài viết có public?")
                return
                
            if self._stop_flag: return
            
            self.lbl_status.config(text="Đang mở rộng tất cả comment và reply...", fg="orange")
            
            # Set up progress callback
            def progress_wrapper(count):
                self.current_comments = self.scraper.current_comments
                self._progress_cb(count)
            
            comments = self.scraper.scrape_all_comments(
                limit=limit, 
                resolve_uid=resolve_uid, 
                progress_callback=progress_wrapper
            )
            
            if self._stop_flag: return
            
            self.lbl_status.config(text="Đang lưu dữ liệu vào Excel...", fg="orange")
            
            if comments:
                # Create DataFrame
                df = pd.DataFrame(comments)
                if not file_out.lower().endswith(".xlsx"):
                    file_out += ".xlsx"
                
                # Clean up columns for export
                if 'ProcessedIndex' in df.columns:
                    df = df.drop('ProcessedIndex', axis=1)
                
                # Reorder columns
                column_order = ['Type', 'Name', 'UID', 'Content', 'ContentLength', 'ProfileLink']
                df = df[[col for col in column_order if col in df.columns]]
                
                # Save to Excel with formatting
                with pd.ExcelWriter(file_out, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Comments', index=False)
                    
                    # Get worksheet for formatting
                    worksheet = writer.sheets['Comments']
                    
                    # Auto-adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        
                        adjusted_width = min(max_length + 2, 50)  # Cap at 50 chars
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                comments_count = len([c for c in comments if c['Type'] == 'Comment'])
                replies_count = len([c for c in comments if c['Type'] == 'Reply'])
                
                success_msg = f"✅ HOÀN THÀNH! {comments_count} comments + {replies_count} replies"
                self.lbl_status.config(text=success_msg, fg="green")
                self.lbl_progress.config(text=f"Final: Comments: {comments_count} | Replies: {replies_count}")
                
                # Show detailed results
                messagebox.showinfo("Hoàn thành thành công!", 
                                  f"🎉 Đã lấy thành công:\n\n"
                                  f"📝 {comments_count} comment chính\n"
                                  f"💬 {replies_count} reply\n"
                                  f"📊 Tổng cộng: {len(comments)} items\n\n"
                                  f"💾 Đã lưu tại: {file_out}\n\n"
                                  f"✨ Phiên bản này đã được tối ưu hóa để:\n"
                                  f"• Lấy nhiều comment hơn\n"
                                  f"• Phân biệt chính xác comment/reply\n"
                                  f"• Xử lý tốt hơn với mbasic Facebook")
            else:
                error_msg = "❌ Không tìm thấy comment nào"
                self.lbl_status.config(text=error_msg, fg="red")
                messagebox.showwarning("Không có dữ liệu", 
                                     "❌ Không tìm thấy comment nào!\n\n"
                                     "🔍 Kiểm tra:\n"
                                     "• Cookie có đúng và còn hạn?\n"
                                     "• Bài viết có public hoặc bạn có quyền xem?\n"
                                     "• Bài viết có comment nào không?\n"
                                     "• Kiểm tra file debug_mbasic_expanded.html")
                
        except Exception as e:
            error_msg = f"❌ Lỗi: {str(e)[:80]}..."
            self.lbl_status.config(text=error_msg, fg="red")
            print(f"Detailed error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi hệ thống", f"❌ Có lỗi xảy ra:\n\n{str(e)}\n\nKiểm tra console để xem chi tiết.")
        finally:
            self.progress_bar.stop()
            if self.scraper: 
                self.scraper.close()
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FBCommentMbasicGUI(root)
    root.mainloop()