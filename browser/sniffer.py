import os
import threading
from typing import Callable, Optional
from playwright.sync_api import sync_playwright

class WebSniffer:
    def __init__(self, on_found_callback: Callable[[str, str, str, str], None], on_error_callback: Optional[Callable[[Exception], None]] = None):
        """
        on_found_callback(url: str, cookies: str, referer: str, title: str)
        """
        self.on_found_callback = on_found_callback
        self.on_error_callback = on_error_callback
        self._stop_event = threading.Event()

    def start_sniffing(self):
        """Starts the playwright sniffer in a background thread."""
        thread = threading.Thread(target=self._run_playwright, daemon=True)
        thread.start()

    def _run_playwright(self):
        try:
            with sync_playwright() as p:
                user_data_dir = os.path.join(os.getcwd(), "playwright_data")
                
                # Launch persistent context to keep logins/cookies across sessions
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                    no_viewport=True
                )
                
                # Use the default page if it exists, otherwise create a new one
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://google.com") # Open a default page
                
                captured_urls = set()

                def handle_request(request):
                    # Broad check for m3u8 streams
                    if ".m3u8" in request.url.lower():
                        base_url = request.url.split('?')[0]
                        if base_url in captured_urls:
                            return
                        captured_urls.add(base_url)
                        
                        m3u8_url = request.url
                        referer = request.headers.get("referer", "")
                        
                        # Get cookies for this specific domain
                        raw_cookies = context.cookies(urls=[request.url])
                        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in raw_cookies])
                        
                        try:
                            title = page.title()
                        except Exception:
                            title = "Captured_Video"

                        # Emit silently to the GUI without stopping the browser
                        if self.on_found_callback:
                            self.on_found_callback(m3u8_url, cookie_str, referer, title)

                page.on("request", handle_request)
                
                # Keep browser open until user closes it
                while not self._stop_event.is_set():
                    try:
                        # This throws an error if user manually closes the browser window
                        page.wait_for_timeout(500)
                        
                        # Extra check: if page is closed, break
                        if page.is_closed():
                            break
                    except Exception:
                        break # Browser was closed by user
                
                context.close()
                
            # Loop broke cleanly (e.g. user closed tab) -> Re-enable GUI button
            if self.on_error_callback:
                self.on_error_callback(Exception("Browser closed by user"))
                
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(e)
