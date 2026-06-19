from playwright.sync_api import sync_playwright
import time

def verify_upload():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to login...")
        page.goto('http://localhost:3000/login')

        # Mock login flow
        page.fill('input[type="email"]', 'test@example.com')
        page.fill('input[type="password"]', 'password123')
        page.click('button[type="submit"]')

        page.wait_for_url('http://localhost:3000/dashboard')
        print("Logged in, on dashboard.")

        # Simulate upload (attach to the hidden file input)
        with open('test_upload.pdf', 'w') as f:
            f.write('dummy content')

        page.set_input_files('input[type="file"]', 'test_upload.pdf')
        print("File attached.")

        # Wait for analyzing state
        page.wait_for_selector('text=Analyzing Lab Report...', timeout=5000)
        print("Analyzing state displayed.")

        # Wait for redirect
        page.wait_for_url('**/dashboard/analysis/1', timeout=5000)
        print("Successfully routed to analysis page!")

        page.screenshot(path='/home/jules/verification/screenshots/upload_result.png')

        browser.close()

if __name__ == "__main__":
    verify_upload()
