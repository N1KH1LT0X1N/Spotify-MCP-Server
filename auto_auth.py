"""
Automated Spotify authentication using headless browser.
Only needed for initial setup or when tokens are cleared.

WARNING: This stores your Spotify password in environment variables.
Only use this for development/testing purposes.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverSait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()


def automated_auth():
    """
    Automate the OAuth flow using headless browser.
    Requires: SPOTIFY_USERNAME and SPOTIFY_PASSWORD in .env
    """
    username = os.getenv("SPOTIFY_USERNAME")
    password = os.getenv("SPOTIFY_PASSWORD")
    
    if not username or not password:
        raise ValueError(
            "Missing SPOTIFY_USERNAME or SPOTIFY_PASSWORD in .env\n"
            "This is required for automated authentication."
        )
    
    # Get auth URL from your auth manager
    from src.spotify_mcp.auth import SpotifyAuthManager
    auth_manager = SpotifyAuthManager()
    auth_url = auth_manager.sp_oauth.get_authorize_url()
    
    # Setup headless Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("Opening Spotify authorization page...")
        driver.get(auth_url)
        
        # Wait for login page and fill credentials
        print("Entering credentials...")
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "login-username"))
        )
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.ID, "login-password")
        password_field.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.ID, "login-button")
        login_button.click()
        
        # Wait for authorization page
        print("Authorizing application...")
        time.sleep(2)
        
        # Click authorize button (if not already authorized)
        try:
            authorize_button = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='auth-accept']"))
            )
            authorize_button.click()
        except:
            # Already authorized, will redirect immediately
            pass
        
        # Wait for redirect and capture URL
        print("Waiting for redirect...")
        wait.until(lambda d: "127.0.0.1:8888/callback" in d.current_url)
        redirect_url = driver.current_url
        
        # Extract code and get token
        print("Exchanging code for token...")
        code = auth_manager.sp_oauth.parse_response_code(redirect_url)
        token_info = auth_manager.sp_oauth.get_access_token(code, check_cache=False)
        
        # Save tokens
        auth_manager._save_token_info(token_info)
        
        print("\n✓ Automated authentication successful!")
        print(f"Access token expires at: {token_info['expires_at']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Automated authentication failed: {e}")
        print("Falling back to manual authentication...")
        return False
        
    finally:
        driver.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("Automated Spotify Authentication")
    print("=" * 60)
    print("\nWARNING: This requires storing your Spotify password.")
    print("Only use for development/testing purposes.\n")
    
    try:
        success = automated_auth()
        if not success:
            # Fallback to manual auth
            from src.spotify_mcp.auth import get_spotify_client
            get_spotify_client()
            
    except Exception as e:
        print(f"\nError: {e}")
        print("\nFalling back to manual authentication...")
        from src.spotify_mcp.auth import get_spotify_client
        get_spotify_client()
