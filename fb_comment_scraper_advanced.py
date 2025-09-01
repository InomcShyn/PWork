# fb_comment_scraper_advanced.py
import time, random, threading, re, requests, pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
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
    text = re.sub(r'\b(\d+\s*(minutes?|hours?|days?|seconds?)\s*ago)\b', '', text)
    text = re.sub(r'\b(Top fan|Most relevant|Newest|All comments)\b', '', text)
    return text.strip()

# ----------------------------
# Advanced Comment Scraper
# ----------------------------
class FacebookAdvancedScraper:
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
        options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) "
                             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1")
        options.add_argument("window-size=375,812")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.cookie_str = cookie_str or ""
        self.cookies_list = parse_cookies_to_list(self.cookie_str)
        self.cookies_dict = parse_cookies_to_dict(self.cookie_str)
        self.is_mobile_version = False
        
        if self.cookies_list:
            self._login_with_cookies()

    def _login_with_cookies(self):
        self.driver.get("https://mbasic.facebook.com")
        time.sleep(2)
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
        time.sleep(3)

    def load_post(self, post_url):
        self.post_url = ensure_mbasic_url(post_url)
        print(f"Loading post: {self.post_url}")
        
        try:
            self.driver.get(self.post_url)
            time.sleep(5)
            
            current_url = self.driver.current_url
            print(f"Current URL after load: {current_url}")
            
            # Detect Facebook version
            if "m.facebook.com" in current_url:
                print("On mobile version (m.facebook.com)")
                self.is_mobile_version = True
            elif "mbasic.facebook.com" in current_url:
                print("On mbasic version")
                self.is_mobile_version = False
            
            # Check accessibility
            page_title = self.driver.title
            print(f"Page title: {page_title}")
            
            if "Log in" in page_title or "Login" in page_title:
                print("ERROR: Not logged in! Check your cookies.")
                return False
            
            return True
                
        except Exception as e:
            print(f"Error loading post: {e}")
            return False

    def expand_all_comments_and_replies(self, max_attempts=100):
        print("=== EXPANDING COMMENTS & REPLIES ===")
        attempts = 0
        while attempts < max_attempts:
            expanded = False
            attempts += 1
            print(f"[Attempt {attempts}] scrolling and checking for expand links...")

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3))

            expand_links = self.driver.find_elements(
                By.XPATH,
                "//a[contains(text(),'View more comments') or "
                "contains(text(),'View previous comments') or "
                "contains(text(),'View more replies') or "
                "contains(text(),'Show more') or "
                "contains(text(),'See more')]"
            )

            for link in expand_links:
                try:
                    if link.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].click();", link)
                        print(f"✓ Clicked expand link: {link.text.strip()}")
                        expanded = True
                        time.sleep(random.uniform(2, 3))
                except:
                    continue

            if not expanded:
                print("No more expand links found.")
                break

        print("=== EXPANSION DONE ===")
    
        # Final scroll to make sure everything is loaded
        for i in range(5):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    def detect_comment_hierarchy(self, element):
        """Detect if this is a main comment or a reply based on HTML structure"""
        try:
            # Method 1: Check for specific reply indicators in HTML structure
            parent_html = element.get_attribute("outerHTML")
            
            # Look for reply-specific patterns
            if any(pattern in parent_html.lower() for pattern in [
                'data-ft.*"reply"', 'reply_comment', 'nested_comment', 
                'child_comment', '_2a_i', '_2a_j'
            ]):
                return "Reply", 2
            
            # Method 2: Check nesting level by counting parent divs
            nesting_level = 0
            current = element
            
            while nesting_level < 10:  # Prevent infinite loops
                try:
                    current = current.find_element(By.XPATH, "..")
                    if current.tag_name == 'body':
                        break
                    
                    # Check for comment container indicators
                    class_attr = current.get_attribute("class") or ""
                    data_ft = current.get_attribute("data-ft") or ""
                    
                    if any(indicator in class_attr.lower() for indicator in [
                        'comment', 'reply', 'nested'
                    ]) or 'comment' in data_ft:
                        nesting_level += 1
                        
                except:
                    break
            
            # Method 3: Check indentation/margin styles
            try:
                style = element.get_attribute("style") or ""
                computed_style = self.driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).marginLeft;", element
                )
                
                if computed_style and computed_style != '0px':
                    margin_value = int(re.findall(r'\d+', computed_style)[0]) if re.findall(r'\d+', computed_style) else 0
                    if margin_value > 20:  # Significant left margin indicates reply
                        return "Reply", nesting_level + 1
            except:
                pass
            
            # Decision logic
            if nesting_level >= 2:
                return "Reply", nesting_level
            else:
                return "Comment", nesting_level
                
        except Exception as e:
            print(f"  Error detecting hierarchy: {e}")
            return "Comment", 0

    def extract_name_and_content(self, element):
        """Improved name and content extraction with better separation"""
        try:
            full_text = element.text.strip()
            if not full_text:
                return "Unknown", "", None
            
            print(f"  Processing element with text: '{full_text[:100]}...'")
            
            # Strategy 1: Find the commenter's name (usually in H3 or strong link)
            username = "Unknown"
            profile_href = None
            
            # Priority 1: H3 with link (most reliable)
            h3_links = element.find_elements(By.XPATH, ".//h3//a[@href]")
            if h3_links:
                first_link = h3_links[0]
                link_text = first_link.text.strip()
                link_href = first_link.get_attribute("href")
                
                if (link_text and len(link_text) < 80 and 
                    ('profile.php' in link_href or 'user.php' in link_href or 'facebook.com/' in link_href)):
                    username = link_text
                    profile_href = link_href
                    print(f"  Found H3 name: '{username}'")
            
            # Priority 2: Strong tags with links
            if username == "Unknown":
                strong_links = element.find_elements(By.XPATH, ".//strong//a[@href] | .//b//a[@href]")
                for link in strong_links[:2]:
                    try:
                        link_text = link.text.strip()
                        link_href = link.get_attribute("href")
                        if (link_text and len(link_text) < 80 and 
                            ('profile.php' in link_href or 'facebook.com/' in link_href)):
                            username = link_text
                            profile_href = link_href
                            print(f"  Found strong name: '{username}'")
                            break
                    except:
                        continue
            
            # Priority 3: Any profile link
            if username == "Unknown":
                all_links = element.find_elements(By.XPATH, ".//a[@href]")
                for link in all_links[:5]:
                    try:
                        link_text = link.text.strip()
                        link_href = link.get_attribute("href")
                        
                        if (link_text and len(link_text) < 80 and len(link_text) > 2 and
                            ('profile.php' in link_href or 'user.php' in link_href) and
                            not any(skip in link_text.lower() for skip in ['like', 'reply', 'share', 'comment'])):
                            username = link_text
                            profile_href = link_href
                            print(f"  Found profile name: '{username}'")
                            break
                    except:
                        continue
            
            # Strategy 2: Extract comment content more precisely
            content = ""
            
            # Method 1: Look for content in text nodes that aren't the name
            try:
                # Get all text content
                all_text_elements = element.find_elements(By.XPATH, ".//*[text()]")
                content_candidates = []
                
                for text_elem in all_text_elements:
                    try:
                        text_content = text_elem.text.strip()
                        
                        # Skip if it's the username or UI elements
                        if (text_content and text_content != username and 
                            len(text_content) > 15 and
                            not any(ui in text_content for ui in ['Like', 'Reply', 'Share', 'Comment']) and
                            not re.match(r'^\d+\s*(minutes?|hours?|days?)\s*ago$', text_content)):
                            content_candidates.append(text_content)
                    except:
                        continue
                
                # Choose the longest meaningful content
                if content_candidates:
                    content = max(content_candidates, key=len)
                    print(f"  Found content candidate: '{content[:50]}...'")
                    
            except Exception as e:
                print(f"  Error in content extraction: {e}")
            
            # Method 2: Fallback to cleaning full text
            if len(content) < 10:
                content = full_text
                
                # Remove username from the beginning
                if username != "Unknown":
                    # Try multiple removal strategies
                    patterns_to_remove = [
                        rf'^{re.escape(username)}\s*',
                        rf'^.*?{re.escape(username)}\s*',
                    ]
                    
                    for pattern in patterns_to_remove:
                        content = re.sub(pattern, '', content, count=1)
                        if len(content) > 10:
                            break
                
                # Remove UI elements
                ui_patterns = [
                    r'\b(Like|Reply|Share|Comment|Translate|See translation|Hide|Report|Block)\b',
                    r'\b\d+\s*(minutes?|hours?|days?|seconds?)\s*ago\b',
                    r'\b(Top fan|Most relevant|Newest|All comments|View more|Show more)\b',
                ]
                
                for pattern in ui_patterns:
                    content = re.sub(pattern, '', content, flags=re.IGNORECASE)
                
                # Final cleanup
                content = re.sub(r'\s+', ' ', content).strip()
                content = re.sub(r'^[^\w\u00C0-\u024F\u1E00-\u1EFF]*', '', content)  # Remove leading non-letter chars
            
            # Strategy 3: Final validation and cleanup
            content = clean_text(content)
            
            # Remove username if it still appears in content
            if username != "Unknown" and username in content:
                content = content.replace(username, "", 1).strip()
            
            print(f"  ✓ Final extraction - Name: '{username}' | Content: '{content[:80]}...'")
            
            return username, content, profile_href
            
        except Exception as e:
            print(f"  Error in name/content extraction: {e}")
            return "Unknown", full_text if 'full_text' in locals() else "", None

    def scrape_all_comments(self, limit=0, resolve_uid=True, progress_callback=None):
        print("=== STARTING IMPROVED COMMENT SCRAPING ===")
        
        # First expand all comments and replies
        self.expand_all_comments_and_replies()
        
        comments = []
        seen = set()
        
        # Save page source for debugging
        try:
            with open("debug_expanded_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("Saved expanded page source to debug_expanded_page.html")
        except:
            pass

        # Improved selectors targeting specific comment structures
        comment_selectors = [
            # Main comment containers with data-ft
            "//div[@data-ft and contains(@data-ft, 'comment')]",
            
            # Comments with profile links in H3
            "//div[.//h3//a[contains(@href, 'profile.php') or contains(@href, 'user.php')]]",
            
            # Article elements (often used for comments)
            "//article",
            "//div[@role='article']",
            
            # Div with comment-like structure (has name link + content)
            "//div[.//a[contains(@href, 'profile.php')] and string-length(normalize-space(text())) > 30]",
            
            # More specific Facebook comment selectors
            "//div[contains(@class, '_5pcr') or contains(@class, '_2a_i') or contains(@class, '_2a_j')]",
            
            # Backup: any div with substantial text that contains profile links
            "//div[.//a[contains(@href, 'facebook.com/')] and string-length(normalize-space(text())) > 50]",
        ]

        all_potential_elements = []
        
        # Collect potential comment elements with priority
        for i, selector in enumerate(comment_selectors):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                print(f"Selector {i+1} (priority): Found {len(elements)} elements")
                
                for elem in elements:
                    if elem not in all_potential_elements:
                        all_potential_elements.append(elem)
                        
            except Exception as e:
                print(f"Selector {i+1} failed: {e}")
                continue

        print(f"Total unique potential comment elements: {len(all_potential_elements)}")

        # Process each potential comment element
        for i, element in enumerate(all_potential_elements):
            try:
                if limit and len(comments) >= limit:
                    break

                print(f"\n--- Processing element {i+1}/{len(all_potential_elements)} ---")
                
                # Detect comment hierarchy first
                comment_type, nesting_level = self.detect_comment_hierarchy(element)
                
                # Extract name and content
                username, content, profile_href = self.extract_name_and_content(element)
                
                # Enhanced validation
                if not content or len(content.strip()) < 5:
                    print("  Skipping: no meaningful content")
                    continue
                
                # Skip obvious UI-only elements
                ui_only_patterns = [
                    r'^(Like|Reply|Share|Comment)(\s+(Like|Reply|Share|Comment))*\s*$',
                    r'^(View more|Show more|See more)\s',
                    r'^(Top fan|Most relevant|Newest)\s*$',
                    r'^\d+\s*(minutes?|hours?|days?)\s*ago\s*$',
                    r'^(Translate|See translation|Hide|Report|Block)\s*$',
                ]
                
                if any(re.match(pattern, content, re.IGNORECASE) for pattern in ui_only_patterns):
                    print("  Skipping: UI element")
                    continue
                
                # Skip very short content
                if len(content) < 10:
                    print(f"  Skipping: too short ({len(content)} chars)")
                    continue
                
                # Resolve UID
                uid = "Unknown"
                if resolve_uid and profile_href:
                    try:
                        uid = try_resolve_numeric_uid(profile_href, self.cookies_dict)
                        if not uid:
                            uid = "Unknown"
                    except:
                        uid = "Unknown"
                
                # Enhanced deduplication
                dedupe_key = f"{username[:20]}_{content[:30]}_{comment_type}"
                if dedupe_key in seen:
                    print("  Skipping: duplicate")
                    continue
                seen.add(dedupe_key)
                
                # Create comment object with hierarchy info
                comment_data = {
                    "Type": comment_type,
                    "NestingLevel": nesting_level,
                    "UID": uid,
                    "Name": username,
                    "Content": content,
                    "ProfileLink": profile_href or "",
                    "ContentLength": len(content)
                }
                
                comments.append(comment_data)
                print(f"  ✓ ADDED {comment_type.upper()} #{len(comments)} (Level: {nesting_level})")
                print(f"    Name: {username}")
                print(f"    Content: {content[:100]}...")
                
                if progress_callback:
                    progress_callback(len(comments))
                    
            except Exception as e:
                print(f"  Error processing element {i}: {e}")
                continue

        print(f"\n=== SCRAPING COMPLETE ===")
        print(f"Total comments and replies extracted: {len(comments)}")
        
        # Count comments vs replies
        comments_count = len([c for c in comments if c['Type'] == 'Comment'])
        replies_count = len([c for c in comments if c['Type'] == 'Reply'])
        print(f"Main Comments: {comments_count}, Replies: {replies_count}")
        
        # Sort by type and nesting level for better organization
        comments.sort(key=lambda x: (x['Type'] == 'Reply', x.get('NestingLevel', 0), x['Name']))
        
        return comments

    def detect_comment_hierarchy(self, element):
        """Improved hierarchy detection to distinguish main comments from replies"""
        try:
            # Method 1: Check HTML attributes and classes
            element_html = element.get_attribute("outerHTML")
            data_ft = element.get_attribute("data-ft") or ""
            class_attr = element.get_attribute("class") or ""
            
            # Direct indicators for replies
            reply_indicators = [
                'reply_comment', 'nested_comment', 'child_comment',
                '"reply"', 'data-ft.*reply', '_2a_i', '_2a_j'
            ]
            
            if any(re.search(indicator, element_html, re.IGNORECASE) for indicator in reply_indicators):
                return "Reply", 2
            
            # Method 2: Check positioning and indentation
            try:
                # Get element position relative to viewport
                location = element.location
                size = element.size
                
                # Check if element has significant left offset (indication of reply)
                if location.get('x', 0) > 50:  # More than 50px from left
                    return "Reply", 1
                    
            except:
                pass
            
            # Method 3: Analyze parent structure
            nesting_score = 0
            current = element
            
            for level in range(8):  # Check up to 8 parent levels
                try:
                    current = current.find_element(By.XPATH, "..")
                    if current.tag_name == 'body':
                        break
                    
                    parent_class = current.get_attribute("class") or ""
                    parent_data_ft = current.get_attribute("data-ft") or ""
                    
                    # Scoring system for nesting
                    if any(keyword in parent_class.lower() for keyword in ['comment', 'reply', 'nested']):
                        nesting_score += 1
                    
                    if 'comment' in parent_data_ft:
                        nesting_score += 1
                        
                    # Check for indentation styles
                    try:
                        margin_left = self.driver.execute_script(
                            "return window.getComputedStyle(arguments[0]).marginLeft;", current
                        )
                        if margin_left and margin_left != '0px':
                            margin_value = int(re.findall(r'\d+', margin_left)[0]) if re.findall(r'\d+', margin_left) else 0
                            if margin_value > 15:
                                nesting_score += 1
                    except:
                        pass
                        
                except:
                    break
            
            # Method 4: Text analysis for reply patterns
            text_lower = full_text.lower()
            reply_text_patterns = [
                r'@\w+',  # Mentions
                r'replied to',
                r'in reply to',
                r'responding to'
            ]
            
            if any(re.search(pattern, text_lower) for pattern in reply_text_patterns):
                nesting_score += 2
            
            # Decision logic
            if nesting_score >= 2:
                return "Reply", nesting_score
            else:
                return "Comment", nesting_score
                
        except Exception as e:
            print(f"  Error in hierarchy detection: {e}")
            return "Comment", 0

    def close(self):
        try: 
            self.driver.quit()
        except: 
            pass

# ----------------------------
# Enhanced GUI
# ----------------------------
class FBCommentAppGUI:
    def __init__(self, root):
        self.root = root
        root.title("FB Advanced Comment & Reply Scraper - FIXED")
        root.geometry("800x650")

        frame = tk.Frame(root)
        frame.pack(padx=12, pady=8, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Link bài viết:").grid(row=0, column=0, sticky="w")
        self.entry_url = tk.Entry(frame, width=90)
        self.entry_url.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0,5))

        tk.Label(frame, text="Cookie:").grid(row=2, column=0, sticky="w")
        self.txt_cookie = tk.Text(frame, height=4, width=90)
        self.txt_cookie.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0,8))

        # Options frame
        options_frame = tk.Frame(frame)
        options_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0,8))
        
        tk.Label(options_frame, text="Số lượng comment (0 = all):").grid(row=0, column=0, sticky="w")
        self.entry_limit = tk.Entry(options_frame, width=12)
        self.entry_limit.insert(0, "0")
        self.entry_limit.grid(row=0, column=1, sticky="w", padx=(5,20))

        self.headless_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Chạy headless", variable=self.headless_var).grid(row=0, column=2, sticky="w")

        self.resolve_uid_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Resolve UID", variable=self.resolve_uid_var).grid(row=0, column=3, sticky="w")

        tk.Label(frame, text="File lưu (Excel):").grid(row=5, column=0, sticky="w")
        file_frame = tk.Frame(frame)
        file_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0,8))
        
        self.entry_file = tk.Entry(file_frame, width=70)
        self.entry_file.grid(row=0, column=0, sticky="ew")
        tk.Button(file_frame, text="Chọn...", command=self.choose_file).grid(row=0, column=1, sticky="w", padx=(5,0))
        
        file_frame.columnconfigure(0, weight=1)

        # Info label
        info_label = tk.Label(frame, text="✓ FIXED: Phân biệt chính xác Comment chính vs Reply\n✓ FIXED: Trích xuất nội dung không bị lộn xộn", 
                             fg="green", justify=tk.LEFT)
        info_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(0,8))

        self.lbl_status = tk.Label(frame, text="Status: Ready", fg="blue")
        self.lbl_status.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(8,4))

        # Buttons and progress
        button_frame = tk.Frame(frame)
        button_frame.grid(row=9, column=0, columnspan=3, sticky="ew", pady=8)
        
        self.btn_start = tk.Button(button_frame, text="Start Scrape", bg="#28a745", fg="white", 
                                  command=self.start_scrape_thread)
        self.btn_start.grid(row=0, column=0, sticky="w")

        self.btn_stop = tk.Button(button_frame, text="Stop", bg="#dc3545", fg="white", 
                                 command=self.stop_scrape, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=1, padx=(10,0), sticky="w")

        self.progress_var = tk.IntVar(value=0)
        self.progress_label = tk.Label(button_frame, textvariable=self.progress_var, fg="green")
        self.progress_label.grid(row=0, column=2, padx=(20,0), sticky="e")
        
        button_frame.columnconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

        self._scrape_thread = None
        self._stop_flag = False
        self.scraper = None

    def choose_file(self):
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                       filetypes=[("Excel files", "*.xlsx")])
        if f:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, f)

    def start_scrape_thread(self):
        url = self.entry_url.get().strip()
        cookie_str = self.txt_cookie.get("1.0", tk.END).strip()
        file_out = self.entry_file.get().strip() or "fb_comments_fixed.xlsx"
        
        if not url:
            messagebox.showerror("Missing input", "Vui lòng nhập link bài viết.")
            return
        
        try: 
            limit = int(self.entry_limit.get().strip())
        except: 
            limit = 0

        self._stop_flag = False
        self.progress_var.set(0)
        self.lbl_status.config(text="Starting improved scraper...", fg="orange")
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        self._scrape_thread = threading.Thread(target=self._scrape_worker, 
                                             args=(url, cookie_str, file_out, limit, 
                                                   self.headless_var.get(), self.resolve_uid_var.get()))
        self._scrape_thread.daemon = True
        self._scrape_thread.start()

    def stop_scrape(self):
        self._stop_flag = True
        self.lbl_status.config(text="Stopping...", fg="red")
        self.btn_stop.config(state=tk.DISABLED)

    def _progress_cb(self, count):
        self.progress_var.set(count)
        self.lbl_status.config(text=f"Đã lấy {count} comment/reply...", fg="green")
        self.root.update_idletasks()

    def _scrape_worker(self, url, cookie_str, file_out, limit, headless, resolve_uid):
        try:
            self.lbl_status.config(text="Khởi tạo trình duyệt...", fg="orange")
            self.scraper = FacebookAdvancedScraper(cookie_str, headless=headless)
            
            if self._stop_flag: return
            
            self.lbl_status.config(text="Tải bài viết...", fg="orange")
            success = self.scraper.load_post(url)
            
            if not success:
                self.lbl_status.config(text="Lỗi: Không thể tải bài viết", fg="red")
                return
                
            if self._stop_flag: return
            
            self.lbl_status.config(text="Mở rộng tất cả comment và reply...", fg="orange")
            comments = self.scraper.scrape_all_comments(limit=limit, resolve_uid=resolve_uid, 
                                                       progress_callback=self._progress_cb)
            
            if self._stop_flag: return
            
            self.lbl_status.config(text="Lưu dữ liệu...", fg="orange")
            
            if comments:
                df = pd.DataFrame(comments)
                if not file_out.lower().endswith(".xlsx"):
                    file_out += ".xlsx"
                    
                # Enhanced sorting: Comments first, then replies, organized by nesting level
                df = df.sort_values(['Type', 'NestingLevel', 'Name'])
                df.to_excel(file_out, index=False, engine="openpyxl")
                
                comments_count = len([c for c in comments if c['Type'] == 'Comment'])
                replies_count = len([c for c in comments if c['Type'] == 'Reply'])
                
                self.lbl_status.config(text=f"THÀNH CÔNG! {comments_count} comments + {replies_count} replies → {file_out}", fg="green")
                
                # Show detailed breakdown by nesting level
                level_breakdown = {}
                for comment in comments:
                    level = comment.get('NestingLevel', 0)
                    comment_type = comment['Type']
                    key = f"{comment_type}_Level{level}"
                    level_breakdown[key] = level_breakdown.get(key, 0) + 1
                
                print("\n=== DETAILED BREAKDOWN ===")
                for key, count in sorted(level_breakdown.items()):
                    print(f"{key}: {count}")
                    
            else:
                self.lbl_status.config(text="Không tìm thấy comment. Xem debug_expanded_page.html", fg="red")
                
        except Exception as e:
            self.lbl_status.config(text=f"Lỗi: {e}", fg="red")
            print(f"Detailed error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.scraper: 
                self.scraper.close()
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FBCommentAppGUI(root)
    root.mainloop()