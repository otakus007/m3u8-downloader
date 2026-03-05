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
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                page = context.new_page()
                page.goto("https://google.com") # Open a default page
                
                found_m3u8 = False

                def handle_request(request):
                    nonlocal found_m3u8
                    if found_m3u8:
                        return
                        
                    # Broad check for m3u8 streams
                    if ".m3u8" in request.url.lower():
                        found_m3u8 = True
                        
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
                
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(e)
