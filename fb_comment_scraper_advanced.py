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

    def expand_all_comments_and_replies(self, max_attempts=200):
        print("=== EXPANDING COMMENTS & REPLIES ===")
        attempts = 0
        no_expansion_count = 0
        total_expanded = 0
        
        while attempts < max_attempts and no_expansion_count < 8:
            expanded = False
            attempts += 1
            print(f"[Attempt {attempts}] scrolling and checking for expand links...")

            # Progressive scrolling strategy
            if attempts % 3 == 0:
                # Every 3rd attempt, scroll to top first then to bottom
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))

            # Comprehensive list of expand link selectors
            expand_selectors = [
                # English
                "//a[contains(text(),'View more comments')]",
                "//a[contains(text(),'View previous comments')]", 
                "//a[contains(text(),'View more replies')]",
                "//a[contains(text(),'Show more')]",
                "//a[contains(text(),'See more')]",
                "//a[contains(text(),'Load more')]",
                
                # Vietnamese
                "//a[contains(text(),'Xem thêm bình luận')]",
                "//a[contains(text(),'Xem bình luận trước')]",
                "//a[contains(text(),'Xem thêm phản hồi')]",
                "//a[contains(text(),'Hiển thị thêm')]",
                "//a[contains(text(),'Xem thêm')]",
                
                # Generic patterns
                "//a[contains(@href,'comment')]",
                "//a[contains(@href,'reply')]",
                "//div[contains(text(),'View more')]/parent::*",
                "//div[contains(text(),'See more')]/parent::*",
                "//div[contains(text(),'Show more')]/parent::*",
                "//div[contains(text(),'Xem thêm')]/parent::*",
                
                # Data attributes and classes
                "//a[@data-testid='UFI2CommentsPagerRenderer/pager_depth_0']",
                "//a[@data-testid='UFI2CommentsPagerRenderer/pager_depth_1']",
                "//a[contains(@data-testid,'pager')]",
                "//*[contains(@class,'_4ssp')]",
                "//*[contains(@class,'_42ft')]",
                "//*[contains(@class,'_5v47')]",
                
                # Additional mbasic-specific selectors
                "//a[contains(@href,'comment_id')]",
                "//a[contains(@href,'reply_comment_id')]",
            ]

            all_expand_links = []
            for selector in expand_selectors:
                try:
                    links = self.driver.find_elements(By.XPATH, selector)
                    all_expand_links.extend(links)
                except:
                    continue

            # Remove duplicates and filter valid links
            unique_links = []
            seen_elements = set()
            for link in all_expand_links:
                try:
                    # Use location and text as unique identifier
                    location = link.location
                    text = link.text.strip()
                    unique_key = f"{location['x']},{location['y']}_{text}"
                    
                    if unique_key not in seen_elements and link.is_displayed():
                        seen_elements.add(unique_key)
                        unique_links.append(link)
                except:
                    continue

            print(f"Found {len(unique_links)} unique expand links")

            # Click expand links with better error handling
            for i, link in enumerate(unique_links):
                try:
                    if not link.is_displayed() or not link.is_enabled():
                        continue
                        
                    # Scroll to element
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    time.sleep(1)
                    
                    # Get link info before clicking
                    link_text = link.text.strip()[:50]
                    link_href = link.get_attribute('href')
                    
                    # Try different click methods
                    clicked = False
                    try:
                        link.click()
                        clicked = True
                    except:
                        try:
                            self.driver.execute_script("arguments[0].click();", link)
                            clicked = True
                        except:
                            # Try navigating to href if it's a valid link
                            if link_href and ('comment' in link_href or 'reply' in link_href):
                                try:
                                    self.driver.get(link_href)
                                    clicked = True
                                except:
                                    continue
                    
                    if clicked:
                        print(f"✓ Clicked expand link {i+1}: '{link_text}'")
                        expanded = True
                        total_expanded += 1
                        time.sleep(random.uniform(3, 6))
                        
                        # Don't break immediately - try to click more links in this round
                        
                except Exception as e:
                    print(f"Failed to click link {i+1}: {e}")
                    continue

            if not expanded:
                no_expansion_count += 1
                print(f"No expansion in this attempt ({no_expansion_count}/8)")
            else:
                no_expansion_count = 0

        print(f"=== EXPANSION DONE === (Total expanded: {total_expanded})")
    
        # Final comprehensive scroll with pauses
        print("Final loading scroll...")
        for i in range(10):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            # Also scroll up a bit to trigger lazy loading
            if i % 2 == 0:
                self.driver.execute_script("window.scrollBy(0, -800);")
                time.sleep(1)
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(1)

    def detect_comment_structure(self, element):
        """Advanced detection of comment vs reply based on HTML structure"""
        try:
            # Method 1: Check nesting depth
            ancestor_divs = element.find_elements(By.XPATH, "./ancestor::div")
            nesting_depth = len(ancestor_divs)
            
            # Method 2: Check for reply indicators in the element or ancestors
            element_html = element.get_attribute('outerHTML')
            
            # Look for reply-specific patterns
            reply_indicators = [
                'reply_comment_id',
                'comment_reply',
                'data-depth',
                'margin-left',
                'padding-left',
                'ml-',  # margin-left classes
                'pl-',  # padding-left classes
            ]
            
            has_reply_indicator = any(indicator in element_html.lower() for indicator in reply_indicators)
            
            # Method 3: Check CSS positioning
            try:
                margin_left = element.value_of_css_property('margin-left')
                padding_left = element.value_of_css_property('padding-left')
                
                # Parse pixel values
                margin_px = int(re.search(r'(\d+)', margin_left or '0').group(1)) if margin_left else 0
                padding_px = int(re.search(r'(\d+)', padding_left or '0').group(1)) if padding_left else 0
                
                # If significantly indented, likely a reply
                is_indented = margin_px > 20 or padding_px > 20
                
            except:
                is_indented = False
            
            # Method 4: Check parent structure
            is_nested_comment = False
            try:
                # Look for parent comment containers
                parent_comment = element.find_element(By.XPATH, 
                    "./ancestor::div[contains(@data-ft,'comment') or contains(@class,'comment')]")
                if parent_comment:
                    is_nested_comment = True
            except:
                pass
            
            # Method 5: Check for specific reply structure patterns
            is_reply_structure = False
            try:
                # Look for common reply structure patterns
                reply_patterns = [
                    ".//ancestor::div[contains(@class,'_2b04')]",  # FB reply container
                    ".//ancestor::div[contains(@class,'_7a9a')]",  # Another reply class
                    ".//ancestor::div[@data-depth]",               # Depth attribute
                ]
                
                for pattern in reply_patterns:
                    if element.find_elements(By.XPATH, pattern):
                        is_reply_structure = True
                        break
                        
            except:
                pass
            
            # Decision logic
            reply_score = 0
            
            if nesting_depth > 12: reply_score += 2
            if has_reply_indicator: reply_score += 3
            if is_indented: reply_score += 2
            if is_nested_comment: reply_score += 2
            if is_reply_structure: reply_score += 3
            
            # If score >= 4, consider it a reply
            is_reply = reply_score >= 4
            
            print(f"    Structure analysis: depth={nesting_depth}, indicators={has_reply_indicator}, "
                  f"indented={is_indented}, nested={is_nested_comment}, reply_struct={is_reply_structure}")
            print(f"    Reply score: {reply_score} -> {'REPLY' if is_reply else 'COMMENT'}")
            
            return "Reply" if is_reply else "Comment"
            
        except Exception as e:
            print(f"    Error in structure detection: {e}")
            return "Comment"  # Default to comment if detection fails

    def extract_name_and_content(self, element):
        """Advanced name and content separation with improved accuracy"""
        try:
            full_text = element.text.strip()
            if not full_text:
                return "Unknown", "", None
            
            print(f"  Processing element with text: '{full_text[:100]}...'")
            
            # Strategy 1: Look for profile links (most reliable for names)
            profile_links = []
            
            # Multiple ways to find profile links
            link_selectors = [
                ".//a[contains(@href,'profile.php')]",
                ".//a[contains(@href,'user.php')]", 
                ".//a[contains(@href,'/profile/')]",
                ".//h3//a",  # Names often in h3 tags
                ".//strong//a",  # Sometimes in strong tags
                ".//b//a",  # Or bold tags
            ]
            
            for selector in link_selectors:
                try:
                    links = element.find_elements(By.XPATH, selector)
                    for link in links:
                        link_text = link.text.strip()
                        link_href = link.get_attribute("href")
                        
                        # Validate that this looks like a name
                        if (link_text and len(link_text) < 100 and 
                            not link_text.lower().startswith('http') and
                            not any(ui in link_text.lower() for ui in ['like', 'reply', 'share', 'comment'])):
                            profile_links.append((link_text, link_href))
                            break  # Take first valid name per selector
                except:
                    continue
            
            # Choose the best name
            username = "Unknown"
            profile_href = None
            
            if profile_links:
                # Prefer the first profile link found
                username, profile_href = profile_links[0]
                print(f"    Found name: '{username}' from profile link")
            
            # Strategy 2: If no profile link, look for h3/strong/b tags
            if username == "Unknown":
                name_selectors = [".//h3", ".//strong", ".//b"]
                for selector in name_selectors:
                    try:
                        name_elements = element.find_elements(By.XPATH, selector)
                        for name_elem in name_elements:
                            name_text = name_elem.text.strip()
                            if (name_text and len(name_text) < 100 and 
                                not any(ui in name_text.lower() for ui in ['like', 'reply', 'share'])):
                                username = name_text
                                print(f"    Found name: '{username}' from {selector}")
                                break
                        if username != "Unknown":
                            break
                    except:
                        continue
            
            # Strategy 3: Advanced content extraction
            content = full_text
            
            # Remove username from content if found
            if username != "Unknown":
                # Try multiple removal strategies
                patterns_to_try = [
                    rf'^{re.escape(username)}\s*',  # Username at start
                    rf'^.*?{re.escape(username)}\s*',  # Username after some text
                    rf'{re.escape(username)}\s*',  # Username anywhere (last resort)
                ]
                
                for pattern in patterns_to_try:
                    new_content = re.sub(pattern, '', content, count=1).strip()
                    if len(new_content) < len(content) and len(new_content) > 5:
                        content = new_content
                        break
            
            # Strategy 4: Look for content in specific containers
            if len(content) < 15:  # If content is too short, look deeper
                content_selectors = [
                    ".//div[not(.//a)]",  # Divs without links (likely pure content)
                    ".//span[string-length(text()) > 10]",  # Long span text
                    ".//p",  # Paragraph tags
                ]
                
                longest_content = content
                for selector in content_selectors:
                    try:
                        content_elements = element.find_elements(By.XPATH, selector)
                        for content_elem in content_elements:
                            elem_text = content_elem.text.strip()
                            if (len(elem_text) > len(longest_content) and 
                                elem_text != username and
                                not any(ui in elem_text.lower() for ui in ['like', 'reply', 'share', 'comment'])):
                                longest_content = elem_text
                    except:
                        continue
                
                if len(longest_content) > len(content):
                    content = longest_content
            
            # Final content cleaning
            content = clean_text(content)
            
            # Remove common UI elements that might remain
            ui_patterns = [
                r'^(Like|Reply|Share|Comment|Translate)\s*',
                r'\s*(Like|Reply|Share|Comment|Translate)$',
                r'^\d+\s*(min|hour|day|sec).*?ago\s*',
                r'^(Top fan|Most relevant)\s*',
            ]
            
            for pattern in ui_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE).strip()
            
            # Final validation
            if len(content) < 3:
                print(f"    Content too short after cleaning: '{content}'")
                return username, "", profile_href
            
            print(f"    ✓ Final result - Name: '{username}' | Content: '{content[:80]}...'")
            
            return username, content, profile_href
            
        except Exception as e:
            print(f"  Error in name/content extraction: {e}")
            return "Unknown", full_text if 'full_text' in locals() else "", None

    def scrape_all_comments(self, limit=0, resolve_uid=True, progress_callback=None):
        print("=== STARTING ADVANCED COMMENT SCRAPING ===")
        
        # First expand all comments and replies
        self.expand_all_comments_and_replies()
        
        comments = []
        seen = set()
        
        # Save page source for debugging
        try:
            with open("/workspace/debug_expanded_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("Saved expanded page source to debug_expanded_page.html")
        except:
            pass

        # Enhanced selectors targeting Facebook's comment structure more precisely
        primary_selectors = [
            # Main comment containers
            "//div[@data-ft and contains(@data-ft,'comment_id')]",
            "//div[contains(@aria-label,'Comment by')]",
            "//div[@role='article']",
            "//article",
            
            # mbasic specific structures
            "//div[h3/a[contains(@href,'profile.php') or contains(@href,'user.php')]]",
            "//div[.//*[contains(@href,'profile.php') or contains(@href,'user.php')]]",
            
            # Content-based detection
            "//div[string-length(normalize-space(text())) > 30 and .//a[contains(@href,'profile.php')]]",
            "//div[string-length(normalize-space(text())) > 30 and .//a[contains(@href,'user.php')]]",
            
            # Generic but filtered
            "//div[h3 and string-length(normalize-space(text())) > 25]",
            "//div[.//strong and string-length(normalize-space(text())) > 25]",
        ]

        all_potential_elements = []
        
        # Collect elements from primary selectors
        for i, selector in enumerate(primary_selectors):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                print(f"Primary selector {i+1}: Found {len(elements)} elements")
                
                for elem in elements:
                    # Check if element is unique by location
                    try:
                        location = elem.location
                        size = elem.size
                        unique_key = f"{location['x']},{location['y']},{size['width']},{size['height']}"
                        
                        # Add to list if unique
                        if not any(getattr(existing, '_unique_key', None) == unique_key 
                                  for existing in all_potential_elements):
                            elem._unique_key = unique_key
                            all_potential_elements.append(elem)
                    except:
                        # If location check fails, add anyway
                        all_potential_elements.append(elem)
                        
            except Exception as e:
                print(f"Primary selector {i+1} failed: {e}")
                continue

        print(f"Total unique potential comment elements: {len(all_potential_elements)}")

        # Process each potential comment element
        processed_count = 0
        for i, element in enumerate(all_potential_elements):
            try:
                if limit and len(comments) >= limit:
                    break

                print(f"\n--- Processing element {i+1}/{len(all_potential_elements)} ---")
                
                # Check if element is still valid and visible
                try:
                    if not element.is_displayed():
                        print("  Skipping: element not displayed")
                        continue
                except:
                    print("  Skipping: stale element")
                    continue
                
                # Extract name and content using advanced method
                username, content, profile_href = self.extract_name_and_content(element)
                
                # Enhanced validation
                if not content or len(content.strip()) < 5:
                    print("  Skipping: no meaningful content")
                    continue
                
                # Skip obvious UI-only elements with more patterns
                ui_only_patterns = [
                    r'^(Like|Reply|Share|Comment|Translate)(\s+(Like|Reply|Share|Comment|Translate))*\s*$',
                    r'^(View more|Show more|See more|Load more)\s',
                    r'^(Top fan|Most relevant|Newest|All comments)\s*$',
                    r'^\d+\s*(minutes?|hours?|days?|seconds?|mins?|hrs?)\s*ago\s*$',
                    r'^(Xem thêm|Hiển thị thêm|Tải thêm)\s',
                    r'^(Thích|Phản hồi|Chia sẻ|Bình luận)\s*$',
                ]
                
                if any(re.match(pattern, content, re.IGNORECASE) for pattern in ui_only_patterns):
                    print("  Skipping: UI element")
                    continue
                
                # Enhanced deduplication
                content_normalized = re.sub(r'\s+', ' ', content.lower().strip())
                username_normalized = username.lower().strip()
                dedupe_key = f"{username_normalized}_{content_normalized[:100]}"
                
                if dedupe_key in seen:
                    print("  Skipping: duplicate content")
                    continue
                seen.add(dedupe_key)
                
                # Detect comment type using improved method
                comment_type = self.detect_comment_structure(element)
                
                # Resolve UID with retry
                uid = "Unknown"
                if resolve_uid and profile_href:
                    try:
                        uid = try_resolve_numeric_uid(profile_href, self.cookies_dict)
                        if not uid:
                            uid = "Unknown"
                    except:
                        uid = "Unknown"
                
                # Create comment object
                comment_data = {
                    "Type": comment_type,
                    "UID": uid,
                    "Name": username,
                    "Content": content,
                    "ProfileLink": profile_href or "",
                    "ContentLength": len(content),
                    "ProcessedIndex": processed_count
                }
                
                comments.append(comment_data)
                processed_count += 1
                
                print(f"  ✓ ADDED {comment_type.upper()} #{len(comments)}")
                print(f"    Name: {username}")
                print(f"    Content: {content[:100]}{'...' if len(content) > 100 else ''}")
                
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
        
        # Sort comments: main comments first, then their replies
        comments.sort(key=lambda x: (x['Type'] == 'Reply', x['ProcessedIndex']))
        
        return comments

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
        root.title("FB Advanced Comment & Reply Scraper - FIXED VERSION")
        root.geometry("900x700")

        frame = tk.Frame(root)
        frame.pack(padx=12, pady=8, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Link bài viết:").grid(row=0, column=0, sticky="w")
        self.entry_url = tk.Entry(frame, width=100)
        self.entry_url.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0,5))

        tk.Label(frame, text="Cookie:").grid(row=2, column=0, sticky="w")
        self.txt_cookie = tk.Text(frame, height=5, width=100)
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
        
        self.entry_file = tk.Entry(file_frame, width=80)
        self.entry_file.grid(row=0, column=0, sticky="ew")
        tk.Button(file_frame, text="Chọn...", command=self.choose_file).grid(row=0, column=1, sticky="w", padx=(5,0))
        
        file_frame.columnconfigure(0, weight=1)

        # Status and progress
        self.lbl_status = tk.Label(frame, text="Status: Ready - IMPROVED VERSION", fg="blue", font=("Arial", 10, "bold"))
        self.lbl_status.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(8,4))

        # Progress info
        self.lbl_progress = tk.Label(frame, text="Comments: 0 | Replies: 0", fg="green")
        self.lbl_progress.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(0,4))

        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.grid(row=9, column=0, columnspan=3, sticky="ew", pady=8)
        
        self.btn_start = tk.Button(button_frame, text="Start Advanced Scrape", bg="#28a745", fg="white", 
                                  command=self.start_scrape_thread, font=("Arial", 10, "bold"))
        self.btn_start.grid(row=0, column=0, sticky="w")

        self.btn_stop = tk.Button(button_frame, text="Stop", bg="#dc3545", fg="white", 
                                 command=self.stop_scrape, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=1, padx=(10,0), sticky="w")

        self.progress_var = tk.IntVar(value=0)
        self.progress_label = tk.Label(button_frame, textvariable=self.progress_var, fg="green", font=("Arial", 10))
        self.progress_label.grid(row=0, column=2, padx=(20,0), sticky="e")
        
        button_frame.columnconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

        self._scrape_thread = None
        self._stop_flag = False
        self.scraper = None
        self.current_comments = []

    def choose_file(self):
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                       filetypes=[("Excel files", "*.xlsx")])
        if f:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, f)

    def start_scrape_thread(self):
        url = self.entry_url.get().strip()
        cookie_str = self.txt_cookie.get("1.0", tk.END).strip()
        file_out = self.entry_file.get().strip() or "fb_comments_advanced_fixed.xlsx"
        
        if not url:
            messagebox.showerror("Missing input", "Vui lòng nhập link bài viết.")
            return
        
        try: 
            limit = int(self.entry_limit.get().strip())
        except: 
            limit = 0

        self._stop_flag = False
        self.progress_var.set(0)
        self.current_comments = []
        self.lbl_status.config(text="Starting improved advanced scraper...", fg="orange")
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
        self.lbl_status.config(text="Stopping...", fg="red")
        self.btn_stop.config(state=tk.DISABLED)

    def _progress_cb(self, count):
        self.progress_var.set(count)
        
        # Update comment/reply counts
        if hasattr(self, 'current_comments'):
            comments_count = len([c for c in self.current_comments if c.get('Type') == 'Comment'])
            replies_count = len([c for c in self.current_comments if c.get('Type') == 'Reply'])
            self.lbl_progress.config(text=f"Comments: {comments_count} | Replies: {replies_count}")
        
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
            
            def progress_wrapper(count):
                self.current_comments = self.scraper.current_comments if hasattr(self.scraper, 'current_comments') else []
                self._progress_cb(count)
            
            comments = self.scraper.scrape_all_comments(limit=limit, resolve_uid=resolve_uid, 
                                                       progress_callback=progress_wrapper)
            
            if self._stop_flag: return
            
            self.lbl_status.config(text="Lưu dữ liệu...", fg="orange")
            
            if comments:
                df = pd.DataFrame(comments)
                if not file_out.lower().endswith(".xlsx"):
                    file_out += ".xlsx"
                    
                # Sort: Comments first, then replies, maintaining order within each type
                df = df.sort_values(['Type', 'ProcessedIndex'])
                
                # Remove ProcessedIndex column before saving
                df = df.drop('ProcessedIndex', axis=1)
                
                df.to_excel(file_out, index=False, engine="openpyxl")
                
                comments_count = len([c for c in comments if c['Type'] == 'Comment'])
                replies_count = len([c for c in comments if c['Type'] == 'Reply'])
                
                self.lbl_status.config(text=f"THÀNH CÔNG! {comments_count} comments + {replies_count} replies → {file_out}", fg="green")
                self.lbl_progress.config(text=f"Final: Comments: {comments_count} | Replies: {replies_count}")
                
                # Show summary
                messagebox.showinfo("Hoàn thành", 
                                  f"Đã lấy thành công:\n"
                                  f"• {comments_count} comment chính\n"
                                  f"• {replies_count} reply\n"
                                  f"• Tổng: {len(comments)} items\n"
                                  f"• Lưu tại: {file_out}")
            else:
                self.lbl_status.config(text="Không tìm thấy comment. Kiểm tra debug file.", fg="red")
                messagebox.showwarning("Không có dữ liệu", 
                                     "Không tìm thấy comment nào. Kiểm tra:\n"
                                     "• Cookie có đúng không?\n"
                                     "• Link bài viết có public không?\n"
                                     "• File debug_expanded_page.html")
                
        except Exception as e:
            error_msg = f"Lỗi: {str(e)[:100]}"
            self.lbl_status.config(text=error_msg, fg="red")
            print(f"Detailed error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n{str(e)}")
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