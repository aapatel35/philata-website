"""
Philata Social Media Poster
============================
Posts to Instagram, Facebook, X/Twitter (Direct APIs) and LinkedIn (Make.com + Buffer)

Usage:
    from philata_social_poster import PhilataPoster, create_captions

    poster = PhilataPoster()
    poster.post_image(title, captions, image_url)
    poster.post_carousel(title, captions, image_urls)
    poster.post_reel(title, captions, video_url)
"""

import os
import time
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Cloudinary support
try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    print("Warning: cloudinary not installed. Run: pip install cloudinary")

# Twitter support
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("Warning: tweepy not installed. X/Twitter posting disabled. Run: pip install tweepy")


class PhilataPoster:
    """
    Social Media Poster for Philata
    - Instagram: Direct API (images, carousels, reels)
    - Facebook: Direct API (images, carousels)
    - X/Twitter: Direct API (images)
    - LinkedIn: Direct API (images)
    """

    def __init__(self):
        """Initialize with credentials from environment or defaults."""

        # === FACEBOOK & INSTAGRAM ===
        self.fb_page_id = os.getenv("FB_PAGE_ID", "955963574260191")
        self.ig_business_id = os.getenv("IG_BUSINESS_ID", "17841479624542859")
        self.fb_access_token = os.getenv("FB_ACCESS_TOKEN", "")

        # === X/TWITTER (support both X_ and TWITTER_ prefixes) ===
        self.x_api_key = os.getenv("X_API_KEY") or os.getenv("TWITTER_API_KEY", "")
        self.x_api_secret = os.getenv("X_API_SECRET") or os.getenv("TWITTER_API_SECRET", "")
        self.x_access_token = os.getenv("X_ACCESS_TOKEN") or os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.x_access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET") or os.getenv("TWITTER_ACCESS_SECRET", "")

        # === LINKEDIN (via Make.com + Buffer) ===
        self.linkedin_webhook = os.getenv("LINKEDIN_WEBHOOK_URL", "")

        # === DISCORD NOTIFICATIONS (optional) ===
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL", "")

        # === CLOUDINARY ===
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "dg7yw1j18")
        api_key = os.getenv("CLOUDINARY_API_KEY", "")
        api_secret = os.getenv("CLOUDINARY_API_SECRET", "")

        # Debug: Show what we're reading
        print(f"      [DEBUG] CLOUDINARY_CLOUD_NAME: {cloud_name}")
        print(f"      [DEBUG] CLOUDINARY_API_KEY: {'set' if api_key else 'MISSING'}")
        print(f"      [DEBUG] CLOUDINARY_API_SECRET: {'set' if api_secret else 'MISSING'}")
        print(f"      [DEBUG] LINKEDIN_WEBHOOK_URL: {'set' if self.linkedin_webhook else 'MISSING'}")
        print(f"      [DEBUG] X/Twitter API Key: {'set' if self.x_api_key else 'MISSING'}")
        print(f"      [DEBUG] X/Twitter Access Token: {'set' if self.x_access_token else 'MISSING'}")

        if CLOUDINARY_AVAILABLE:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )

        # === API BASE URL ===
        self.graph_api = "https://graph.facebook.com/v21.0"

        # Get Page Access Token for Facebook posting
        self.fb_page_token = None
        if self.fb_access_token and self.fb_page_id:
            self._get_page_access_token()

        # Initialize Twitter
        self.twitter_client = None
        self.twitter_api_v1 = None
        if TWEEPY_AVAILABLE and self.x_api_key:
            self._init_twitter()

        # Print status
        print("   Philata Poster initialized:")
        print(f"      Instagram: {'Enabled' if self.fb_access_token else 'Disabled'}")
        print(f"      Facebook:  {'Enabled' if self.fb_access_token else 'Disabled'}")
        print(f"      X/Twitter: {'Enabled' if self.twitter_client else 'Disabled'}")
        print(f"      LinkedIn:  {'Enabled (Make.com+Buffer)' if self.linkedin_webhook else 'Disabled'}")

    def _get_page_access_token(self):
        """Get Facebook Page Access Token from User Access Token."""
        try:
            response = requests.get(
                f"{self.graph_api}/{self.fb_page_id}",
                params={
                    "fields": "access_token",
                    "access_token": self.fb_access_token
                }
            )
            result = response.json()
            if "access_token" in result:
                self.fb_page_token = result["access_token"]
                print("      Facebook Page token retrieved")
            else:
                print(f"      Could not get Page token: {result.get('error', result)}")
        except Exception as e:
            print(f"      Page token error: {e}")

    def _init_twitter(self):
        """Initialize Twitter/X client."""
        print(f"      [DEBUG] Initializing Twitter with:")
        print(f"         API Key: {'set (' + self.x_api_key[:8] + '...)' if self.x_api_key else 'MISSING'}")
        print(f"         API Secret: {'set' if self.x_api_secret else 'MISSING'}")
        print(f"         Access Token: {'set' if self.x_access_token else 'MISSING'}")
        print(f"         Access Secret: {'set' if self.x_access_token_secret else 'MISSING'}")

        if not all([self.x_api_key, self.x_api_secret, self.x_access_token, self.x_access_token_secret]):
            print("      ❌ Twitter init failed: Missing credentials")
            return

        try:
            self.twitter_client = tweepy.Client(
                consumer_key=self.x_api_key,
                consumer_secret=self.x_api_secret,
                access_token=self.x_access_token,
                access_token_secret=self.x_access_token_secret
            )
            auth = tweepy.OAuth1UserHandler(
                self.x_api_key,
                self.x_api_secret,
                self.x_access_token,
                self.x_access_token_secret
            )
            self.twitter_api_v1 = tweepy.API(auth)
            print("      ✅ Twitter/X client initialized successfully")
        except Exception as e:
            print(f"      ❌ Twitter init failed: {e}")
            import traceback
            traceback.print_exc()

    def _notify_discord(self, message: str, success: bool = True):
        """Send Discord notification."""
        if not self.discord_webhook:
            return
        try:
            emoji = "+" if success else "x"
            requests.post(self.discord_webhook, json={
                "content": f"**Philata Bot**\n{message}"
            }, timeout=10)
        except:
            pass

    def _handle_instagram_rate_limit(self, step: str, error_msg: str):
        """
        V6.4: Handle Instagram rate limit by SKIPPING Instagram (not pausing bot).

        When Meta API rate limit is hit, skip Instagram for 2 hours
        but continue posting to other platforms.

        Args:
            step: Which step failed (container creation, publish)
            error_msg: The error message from the API
        """
        cooldown_hours = 2
        cooldown_until = datetime.now() + timedelta(hours=cooldown_hours)

        # Set cooldown flag
        self._instagram_cooldown_until = cooldown_until

        print(f"\n{'='*60}")
        print(f"⚠️  INSTAGRAM RATE LIMIT HIT ({step})")
        print(f"{'='*60}")
        print(f"   Error: {error_msg[:100]}...")
        print(f"   ⏭️ SKIPPING Instagram for {cooldown_hours} hours (other platforms continue)")
        print(f"   ⏰ Instagram will resume at: {cooldown_until.strftime('%H:%M:%S')}")
        print(f"{'='*60}\n")

        # Notify Discord
        self._notify_discord(
            f"⚠️ Instagram rate limit hit!\n"
            f"Step: {step}\n"
            f"Skipping IG for {cooldown_hours}h - other platforms continue",
            success=False
        )

    def _is_instagram_on_cooldown(self) -> bool:
        """V6.4: Check if Instagram is on rate limit cooldown."""
        if not hasattr(self, '_instagram_cooldown_until'):
            return False
        if datetime.now() < self._instagram_cooldown_until:
            remaining = (self._instagram_cooldown_until - datetime.now()).seconds // 60
            print(f"   ⏭️ Instagram on cooldown ({remaining} min remaining) - skipping")
            return True
        return False

    # =========================================================================
    # CLOUDINARY UPLOAD
    # =========================================================================

    def upload_to_cloudinary(self, file_path: str, resource_type: str = "image") -> Optional[str]:
        """Upload a file to Cloudinary and return the secure URL."""
        if not CLOUDINARY_AVAILABLE:
            print("      Cloudinary not available")
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path).replace('.png', '').replace('.jpg', '').replace('.mp4', '')

            result = cloudinary.uploader.upload(
                file_path,
                resource_type=resource_type,
                folder="philata",
                overwrite=True
            )

            print(f"      Uploaded: {os.path.basename(file_path)}")
            return result['secure_url']

        except Exception as e:
            print(f"      Cloudinary upload failed: {e}")
            return None

    def upload_multiple_to_cloudinary(self, file_paths: List[str]) -> List[str]:
        """Upload multiple files to Cloudinary."""
        urls = []
        for path in file_paths:
            if os.path.exists(path):
                url = self.upload_to_cloudinary(path)
                if url:
                    urls.append(url)
        return urls

    # =========================================================================
    # INSTAGRAM - DIRECT API
    # =========================================================================

    def post_instagram_image(self, image_url: str, caption: str, retry_count: int = 0) -> Optional[str]:
        """
        Post single image to Instagram.

        Args:
            image_url: Public URL (use Cloudinary)
            caption: Caption with hashtags
            retry_count: Number of retries (for rate limiting)

        Returns:
            Post ID or None
        """
        print("   Posting to Instagram...")

        if not self.fb_access_token:
            print("      Instagram not configured (missing FB_ACCESS_TOKEN)")
            return None

        try:
            # Step 1: Create container
            response = requests.post(
                f"{self.graph_api}/{self.ig_business_id}/media",
                data={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.fb_access_token
                }
            )
            result = response.json()

            # V5.22: Handle rate limiting
            if "error" in result:
                error = result.get("error", {})
                error_code = error.get("code", 0)
                error_msg = error.get("message", str(result))

                # Rate limit error codes: 4, 17, 32, 613
                if error_code in [4, 17, 32, 613] or "rate" in error_msg.lower() or "limit" in error_msg.lower():
                    # V5.30: Sleep for 30 minutes on rate limit
                    self._handle_instagram_rate_limit("container creation", error_msg)
                    return None

                print(f"      Instagram container failed: {error_msg}")
                return None

            if "id" not in result:
                print(f"      Instagram container failed: {result}")
                return None

            container_id = result["id"]

            # Step 2: Publish
            response = requests.post(
                f"{self.graph_api}/{self.ig_business_id}/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": self.fb_access_token
                }
            )
            result = response.json()

            if "id" in result:
                print(f"      Instagram posted: {result['id']}")
                self._notify_discord(f"Instagram image posted: {result['id']}")
                return result["id"]
            else:
                error = result.get("error", {})
                error_msg = error.get("message", str(result))
                # V5.30: Check for rate limit on publish step too
                if "rate" in error_msg.lower() or "limit" in error_msg.lower() or "request limit" in error_msg.lower():
                    self._handle_instagram_rate_limit("publish", error_msg)
                    return None
                print(f"      Instagram publish failed: {error_msg}")
                return None

        except Exception as e:
            print(f"      Instagram error: {e}")
            return None

    def post_instagram_carousel(self, image_urls: List[str], caption: str) -> Optional[str]:
        """
        Post carousel (2-10 images) to Instagram.

        Args:
            image_urls: List of 2-10 public image URLs
            caption: Caption with hashtags

        Returns:
            Post ID or None
        """
        print(f"   Posting Instagram carousel ({len(image_urls)} images)...")

        if not self.fb_access_token:
            print("      Instagram not configured")
            return None

        if len(image_urls) < 2:
            print("      Need at least 2 images for carousel")
            return None

        if len(image_urls) > 10:
            print("      Max 10 images, truncating...")
            image_urls = image_urls[:10]

        try:
            # Step 1: Create child containers
            children_ids = []
            for i, url in enumerate(image_urls):
                response = requests.post(
                    f"{self.graph_api}/{self.ig_business_id}/media",
                    data={
                        "image_url": url,
                        "is_carousel_item": "true",
                        "access_token": self.fb_access_token
                    }
                )
                result = response.json()

                if "id" in result:
                    children_ids.append(result["id"])
                    print(f"      Image {i+1}/{len(image_urls)} uploaded")
                else:
                    print(f"      Image {i+1} failed: {result.get('error', result)}")
                    return None

            # Step 2: Create carousel container
            response = requests.post(
                f"{self.graph_api}/{self.ig_business_id}/media",
                data={
                    "media_type": "CAROUSEL",
                    "children": ",".join(children_ids),
                    "caption": caption,
                    "access_token": self.fb_access_token
                }
            )
            result = response.json()

            if "id" not in result:
                print(f"      Carousel container failed: {result.get('error', result)}")
                return None

            carousel_id = result["id"]

            # Step 3: Publish
            response = requests.post(
                f"{self.graph_api}/{self.ig_business_id}/media_publish",
                data={
                    "creation_id": carousel_id,
                    "access_token": self.fb_access_token
                }
            )
            result = response.json()

            if "id" in result:
                print(f"      Instagram carousel posted: {result['id']}")
                self._notify_discord(f"Instagram carousel posted: {result['id']}")
                return result["id"]
            else:
                print(f"      Carousel publish failed: {result.get('error', result)}")
                return None

        except Exception as e:
            print(f"      Instagram carousel error: {e}")
            return None

    def post_instagram_reel(self, video_url: str, caption: str, cover_url: str = None) -> Optional[str]:
        """
        Post reel to Instagram.

        Args:
            video_url: Public video URL (3-90 seconds, 9:16 ratio)
            caption: Caption with hashtags
            cover_url: Optional cover image URL

        Returns:
            Post ID or None
        """
        print("   Posting Instagram reel...")

        if not self.fb_access_token:
            print("      Instagram not configured")
            return None

        try:
            # Step 1: Create container
            data = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": self.fb_access_token
            }
            if cover_url:
                data["cover_url"] = cover_url

            response = requests.post(
                f"{self.graph_api}/{self.ig_business_id}/media",
                data=data
            )
            result = response.json()

            if "id" not in result:
                print(f"      Reel container failed: {result.get('error', result)}")
                return None

            container_id = result["id"]
            print("      Video processing...")

            # Step 2: Wait for processing
            for attempt in range(30):
                response = requests.get(
                    f"{self.graph_api}/{container_id}",
                    params={
                        "fields": "status_code",
                        "access_token": self.fb_access_token
                    }
                )
                status = response.json().get("status_code")

                if status == "FINISHED":
                    print("      Video processed")
                    break
                elif status == "ERROR":
                    print("      Video processing failed")
                    return None
                else:
                    print(f"      Status: {status} (attempt {attempt+1}/30)")
                    time.sleep(5)
            else:
                print("      Video processing timeout")
                return None

            # Step 3: Publish
            response = requests.post(
                f"{self.graph_api}/{self.ig_business_id}/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": self.fb_access_token
                }
            )
            result = response.json()

            if "id" in result:
                print(f"      Instagram reel posted: {result['id']}")
                self._notify_discord(f"Instagram reel posted: {result['id']}")
                return result["id"]
            else:
                print(f"      Reel publish failed: {result.get('error', result)}")
                return None

        except Exception as e:
            print(f"      Instagram reel error: {e}")
            return None

    # =========================================================================
    # FACEBOOK - DIRECT API
    # =========================================================================

    def post_facebook_image(self, image_url: str, message: str) -> Optional[str]:
        """
        Post single image to Facebook Page.

        Args:
            image_url: Public image URL
            message: Post message

        Returns:
            Post ID or None
        """
        print("   Posting to Facebook...")

        if not self.fb_page_token:
            print("      Facebook not configured (no page token)")
            return None

        try:
            response = requests.post(
                f"{self.graph_api}/{self.fb_page_id}/photos",
                data={
                    "url": image_url,
                    "message": message,
                    "access_token": self.fb_page_token
                }
            )
            result = response.json()

            if "id" in result:
                print(f"      Facebook posted: {result['id']}")
                self._notify_discord(f"Facebook image posted: {result['id']}")
                return result["id"]
            else:
                print(f"      Facebook failed: {result.get('error', result)}")
                return None

        except Exception as e:
            print(f"      Facebook error: {e}")
            return None

    def post_facebook_carousel(self, image_urls: List[str], message: str) -> Optional[str]:
        """
        Post multiple photos to Facebook Page.

        Args:
            image_urls: List of public image URLs
            message: Post message

        Returns:
            Post ID or None
        """
        print(f"   Posting Facebook carousel ({len(image_urls)} images)...")

        if not self.fb_page_token:
            print("      Facebook not configured (no page token)")
            return None

        try:
            # Step 1: Upload each photo as unpublished
            photo_ids = []
            for i, url in enumerate(image_urls):
                response = requests.post(
                    f"{self.graph_api}/{self.fb_page_id}/photos",
                    data={
                        "url": url,
                        "published": "false",
                        "access_token": self.fb_page_token
                    }
                )
                result = response.json()

                if "id" in result:
                    photo_ids.append({"media_fbid": result["id"]})
                    print(f"      Photo {i+1}/{len(image_urls)} uploaded")
                else:
                    print(f"      Photo {i+1} failed: {result.get('error', result)}")
                    return None

            # Step 2: Create post with all photos
            post_data = {
                "message": message,
                "access_token": self.fb_page_token
            }
            for i, photo in enumerate(photo_ids):
                post_data[f"attached_media[{i}]"] = json.dumps(photo)

            response = requests.post(
                f"{self.graph_api}/{self.fb_page_id}/feed",
                data=post_data
            )
            result = response.json()

            if "id" in result:
                print(f"      Facebook carousel posted: {result['id']}")
                self._notify_discord(f"Facebook carousel posted: {result['id']}")
                return result["id"]
            else:
                print(f"      Facebook carousel failed: {result.get('error', result)}")
                return None

        except Exception as e:
            print(f"      Facebook carousel error: {e}")
            return None

    def post_facebook_reel(self, video_url: str, description: str) -> Optional[str]:
        """
        Post reel to Facebook Page.

        Args:
            video_url: Public video URL
            description: Reel description

        Returns:
            Post ID or None
        """
        print("   Posting Facebook reel...")

        if not self.fb_page_token:
            print("      Facebook not configured (no page token)")
            return None

        try:
            # Step 1: Initialize upload
            init_response = requests.post(
                f"{self.graph_api}/{self.fb_page_id}/video_reels",
                data={
                    "upload_phase": "start",
                    "access_token": self.fb_page_token
                }
            )
            init_result = init_response.json()

            if "video_id" not in init_result:
                print(f"      Facebook reel init failed: {init_result.get('error', init_result)}")
                return None

            video_id = init_result["video_id"]

            # Step 2: Transfer video
            transfer_response = requests.post(
                f"{self.graph_api}/{video_id}",
                data={
                    "upload_phase": "transfer",
                    "file_url": video_url,
                    "access_token": self.fb_page_token
                }
            )
            transfer_result = transfer_response.json()

            if not transfer_result.get("success"):
                print(f"      Facebook reel transfer failed: {transfer_result}")
                return None

            # Step 3: Publish
            publish_response = requests.post(
                f"{self.graph_api}/{self.fb_page_id}/video_reels",
                data={
                    "upload_phase": "finish",
                    "video_id": video_id,
                    "video_state": "PUBLISHED",
                    "description": description,
                    "access_token": self.fb_page_token
                }
            )
            publish_result = publish_response.json()

            if publish_result.get("success"):
                print(f"      Facebook reel posted: {video_id}")
                self._notify_discord(f"Facebook reel posted: {video_id}")
                return video_id
            else:
                print(f"      Facebook reel publish failed: {publish_result}")
                return None

        except Exception as e:
            print(f"      Facebook reel error: {e}")
            return None

    # =========================================================================
    # X/TWITTER - DIRECT API
    # =========================================================================

    def post_x_image(self, image_url: str, text: str, retry_count: int = 0) -> Optional[str]:
        """
        Post image to X/Twitter.

        Args:
            image_url: Public image URL
            text: Tweet text (max 280 chars)
            retry_count: Number of retries (for rate limiting)

        Returns:
            Tweet ID or None
        """
        print("   Posting to X/Twitter...")

        if not self.twitter_client:
            print("      Twitter client not initialized")
            return None

        try:
            # Download image
            image_data = requests.get(image_url, timeout=30).content
            temp_path = "/tmp/philata_twitter_img.jpg"
            with open(temp_path, "wb") as f:
                f.write(image_data)

            # Upload media
            media = self.twitter_api_v1.media_upload(temp_path)

            # Post tweet
            response = self.twitter_client.create_tweet(
                text=text,
                media_ids=[media.media_id]
            )

            if response.data:
                tweet_id = response.data["id"]
                print(f"      X/Twitter posted: {tweet_id}")
                self._notify_discord(f"X/Twitter posted: {tweet_id}")
                return tweet_id
            else:
                print("      X/Twitter failed")
                return None

        except Exception as e:
            error_str = str(e).lower()
            # V5.22: Handle rate limiting (429)
            if "429" in str(e) or "rate" in error_str or "limit" in error_str or "too many" in error_str:
                if retry_count < 2:
                    wait_time = 300 * (retry_count + 1)  # 5 min, 10 min (X has strict limits)
                    print(f"      X/Twitter rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    return self.post_x_image(image_url, text, retry_count + 1)
                else:
                    print(f"      X/Twitter rate limit exceeded after {retry_count} retries. Try again later.")
                    return None
            print(f"      X/Twitter error: {e}")
            return None

    def post_x_text(self, text: str) -> Optional[str]:
        """Post text-only tweet."""
        print("   Posting to X/Twitter (text only)...")

        if not self.twitter_client:
            print("      Twitter client not initialized")
            return None

        try:
            response = self.twitter_client.create_tweet(text=text)
            if response.data:
                tweet_id = response.data["id"]
                print(f"      X/Twitter posted: {tweet_id}")
                return tweet_id
            return None
        except Exception as e:
            print(f"      X/Twitter error: {e}")
            return None

    def post_x_thread(self, image_url: str, thread_text: str, retry_count: int = 0) -> Optional[str]:
        """
        V5.29: Post to X/Twitter - supports both threads and single long posts.

        Thread format: tweets separated by ---TWEET---
        Single post: No separator, uses full text (X Premium allows 4000 chars)

        Args:
            image_url: Public image URL for first tweet
            thread_text: Full thread with ---TWEET--- separators OR single long post
            retry_count: Number of retries for rate limiting

        Returns:
            First tweet ID or None
        """
        if not self.twitter_client:
            print("      ❌ Twitter client not initialized - check X_API_KEY env vars")
            return None

        # Parse thread into individual tweets
        if '---TWEET---' in thread_text:
            # Legacy thread format
            tweets = [t.strip() for t in thread_text.split('---TWEET---') if t.strip()]
            print(f"   Posting X/Twitter THREAD ({len(tweets)} tweets)...")
        else:
            # V6.0: Text-only posts on X (no images - captions were getting cut off)
            print("   Posting X/Twitter TEXT-ONLY (no image)...")
            # X Premium allows up to 4000 chars, but we limit to 2500 for readability
            post_text = thread_text[:2500] if len(thread_text) > 2500 else thread_text
            print(f"      Post length: {len(post_text)} chars")
            # V6.0: Use text-only posting - images were causing caption cutoff
            return self.post_x_text(post_text)

        if not tweets:
            print("      ❌ No tweets to post after parsing")
            return None

        print(f"      Thread has {len(tweets)} tweets")
        print(f"      First tweet preview: {tweets[0][:50]}...")

        try:
            # Download and upload image for first tweet
            print("      Downloading image...")
            image_data = requests.get(image_url, timeout=30).content
            temp_path = "/tmp/philata_twitter_img.jpg"
            with open(temp_path, "wb") as f:
                f.write(image_data)

            print("      Uploading media to Twitter...")
            media = self.twitter_api_v1.media_upload(temp_path)
            print(f"      Media uploaded: {media.media_id}")

            # Post first tweet with image
            first_tweet = tweets[0][:280]
            print(f"      Posting first tweet ({len(first_tweet)} chars)...")
            response = self.twitter_client.create_tweet(
                text=first_tweet,
                media_ids=[media.media_id]
            )

            if not response.data:
                print("      ❌ First tweet failed - no response data")
                return None

            first_tweet_id = response.data["id"]
            print(f"      ✅ Tweet 1/{len(tweets)} posted: {first_tweet_id}")

            # Post remaining tweets as replies
            previous_id = first_tweet_id
            for i, tweet_text in enumerate(tweets[1:], start=2):
                tweet_text = tweet_text[:280]  # Enforce limit
                try:
                    response = self.twitter_client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_id
                    )
                    if response.data:
                        previous_id = response.data["id"]
                        print(f"      ✅ Tweet {i}/{len(tweets)} posted")
                    else:
                        print(f"      ⚠️ Tweet {i} failed - no response")
                except Exception as e:
                    print(f"      ⚠️ Tweet {i} error: {e}")
                    # Continue with remaining tweets
                time.sleep(1)  # Small delay between tweets to avoid rate limit

            self._notify_discord(f"X/Twitter thread posted: {len(tweets)} tweets")
            return first_tweet_id

        except Exception as e:
            error_str = str(e).lower()
            # V5.22: Handle rate limiting
            if "429" in str(e) or "rate" in error_str or "limit" in error_str or "too many" in error_str:
                if retry_count < 2:
                    wait_time = 300 * (retry_count + 1)  # 5 min, 10 min
                    print(f"      ⏳ X/Twitter rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    return self.post_x_thread(image_url, thread_text, retry_count + 1)
                else:
                    print(f"      ❌ X/Twitter rate limit exceeded. Try again later.")
                    return None
            print(f"      ❌ X/Twitter thread error: {e}")
            import traceback
            traceback.print_exc()
            return None

    # =========================================================================
    # LINKEDIN - VIA MAKE.COM + BUFFER
    # =========================================================================

    def post_linkedin(self, image_url: str, text: str, title: str = "") -> bool:
        """
        Post image to LinkedIn via Make.com webhook (Buffer).

        Args:
            image_url: Public image URL
            text: Post text
            title: Optional title

        Returns:
            True if webhook accepted
        """
        print("   Posting to LinkedIn (Make.com + Buffer)...")

        if not self.linkedin_webhook:
            print("      LinkedIn not configured (no webhook)")
            return False

        # Validate text is not empty - Buffer requires text
        if not text or not text.strip():
            print(f"      LinkedIn skipped: text is empty (title: {title})")
            # Use title as fallback if text is empty
            if title and title.strip():
                text = f"{title}\n\nRead more at philata.ca\n\n#CanadaImmigration #IRCC"
                print(f"      Using title as fallback text")
            else:
                print(f"      Cannot post to LinkedIn without text")
                return False

        try:
            # Simple format for Make.com → Buffer
            payload = {
                "text": text,
                "media": image_url
            }
            print(f"      LinkedIn payload: text={len(text)} chars, media={image_url[:50]}...")

            response = requests.post(
                self.linkedin_webhook,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200 or "Accepted" in response.text:
                print("      LinkedIn webhook sent successfully")
                self._notify_discord("LinkedIn posted via Make.com + Buffer")
                return True
            else:
                print(f"      LinkedIn webhook failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"      LinkedIn error: {e}")
            return False

    # =========================================================================
    # UNIFIED POSTING METHODS
    # =========================================================================

    def post_image(self, title: str, captions: Dict[str, str], image_url: str) -> Dict[str, any]:
        """
        Post single image to ALL platforms.

        Args:
            title: Post title
            captions: Dict with caption_instagram, caption_facebook, caption_linkedin, caption_x
            image_url: Public image URL (Cloudinary)

        Returns:
            Dict with results per platform
        """
        print("\n" + "="*60)
        print(f"POSTING IMAGE: {title}")
        print("="*60)

        results = {}

        # Instagram
        results["instagram"] = self.post_instagram_image(
            image_url, captions.get("caption_instagram", "")
        )

        # Facebook
        results["facebook"] = self.post_facebook_image(
            image_url, captions.get("caption_facebook", "")
        )

        # X/Twitter - V6.0: Text-only (no image)
        x_caption = captions.get("caption_x", "")
        if x_caption:
            results["x"] = self.post_x_text(x_caption[:2500])
        else:
            results["x"] = None

        # LinkedIn
        results["linkedin"] = self.post_linkedin(
            image_url, captions.get("caption_linkedin", ""), title
        )

        self._print_summary(results)
        return results

    def post_carousel(self, title: str, captions: Dict[str, str], image_urls: List[str]) -> Dict[str, any]:
        """
        Post carousel to Instagram/Facebook, single image to X/LinkedIn.

        Args:
            title: Post title
            captions: Dict with platform captions
            image_urls: List of 2-10 public image URLs

        Returns:
            Dict with results per platform
        """
        print("\n" + "="*60)
        print(f"POSTING CAROUSEL: {title} ({len(image_urls)} images)")
        print("="*60)

        results = {}

        # Instagram Carousel
        results["instagram"] = self.post_instagram_carousel(
            image_urls, captions.get("caption_instagram", "")
        )

        # Facebook Carousel
        results["facebook"] = self.post_facebook_carousel(
            image_urls, captions.get("caption_facebook", "")
        )

        # X/Twitter - V6.0: Text-only (no image)
        x_caption = captions.get("caption_x", "")
        if x_caption:
            results["x"] = self.post_x_text(x_caption[:2500])
        else:
            results["x"] = None

        # LinkedIn (first image only)
        results["linkedin"] = self.post_linkedin(
            image_urls[0], captions.get("caption_linkedin", ""), title
        )

        self._print_summary(results)
        return results

    def post_reel(self, title: str, captions: Dict[str, str], video_url: str,
                  thumbnail_url: str = None) -> Dict[str, any]:
        """
        Post reel to Instagram only, image to all other platforms.

        Content strategy:
        - Instagram: Reel (video)
        - Facebook: Image (thumbnail)
        - X/Twitter: Image (thumbnail)
        - LinkedIn: Image (thumbnail)

        Args:
            title: Post title
            captions: Dict with platform captions
            video_url: Public video URL
            thumbnail_url: Thumbnail image for Facebook/X/LinkedIn

        Returns:
            Dict with results per platform
        """
        print("\n" + "="*60)
        print(f"POSTING REEL: {title}")
        print("="*60)

        results = {}

        # Instagram - Reel (video)
        results["instagram"] = self.post_instagram_reel(
            video_url, captions.get("caption_instagram", "")
        )

        # Facebook, LinkedIn - Image (thumbnail)
        if thumbnail_url:
            results["facebook"] = self.post_facebook_image(
                thumbnail_url, captions.get("caption_facebook", "")
            )
            results["linkedin"] = self.post_linkedin(
                thumbnail_url, captions.get("caption_linkedin", ""), title
            )
        else:
            print("      No thumbnail - skipping Facebook/LinkedIn")
            results["facebook"] = None
            results["linkedin"] = None

        # X/Twitter - V6.0: Always text-only (no image)
        x_caption = captions.get("caption_x", "")
        if x_caption:
            results["x"] = self.post_x_text(x_caption[:2500])
        else:
            results["x"] = None

        self._print_summary(results)
        return results

    def post_from_folder(self, output_folder: str, article: Dict = None) -> Dict[str, any]:
        """
        Post content from a generated output folder.
        Automatically detects content type and posts to all platforms.

        Args:
            output_folder: Path to folder containing generated content
            article: Optional article dict with title

        Returns:
            Dict with results per platform
        """
        if not os.path.exists(output_folder):
            print(f"   Folder not found: {output_folder}")
            return {"instagram": None, "facebook": None, "x": None, "linkedin": None}

        # Get title
        title = "Immigration Update"
        if article:
            title = article.get('title', title)

        # Load captions
        captions = self._load_captions_from_folder(output_folder)

        if not captions.get('caption_instagram'):
            print("   No Instagram caption found")
            return {"instagram": None, "facebook": None, "x": None, "linkedin": None}

        # Find content files
        image_files = []
        video_file = None
        reel_thumbnail = None

        for filename in sorted(os.listdir(output_folder)):
            filepath = os.path.join(output_folder, filename)

            if filename.endswith(('.png', '.jpg', '.jpeg')):
                # Check for reel thumbnail specifically
                if filename == 'reel_thumbnail.png':
                    reel_thumbnail = filepath
                elif not any(x in filename.lower() for x in ['thumb', 'screenshot', 'evidence']):
                    image_files.append(filepath)
            elif filename.endswith('.mp4') and 'reel' in filename.lower():
                video_file = filepath

        print(f"   Found: {len(image_files)} images, {'1 reel' if video_file else 'no reel'}, {'thumbnail' if reel_thumbnail else 'no thumbnail'}")

        # Upload and post based on content type
        if video_file:
            # Reel
            print("   Uploading reel...")
            video_url = self.upload_to_cloudinary(video_file, "video")

            # Use reel_thumbnail if available, otherwise fall back to first image
            if reel_thumbnail:
                print("   Uploading reel thumbnail...")
                thumbnail_url = self.upload_to_cloudinary(reel_thumbnail)
            elif image_files:
                print("   Using first carousel image as thumbnail...")
                thumbnail_url = self.upload_to_cloudinary(image_files[0])
            else:
                thumbnail_url = None

            if video_url:
                return self.post_reel(title, captions, video_url, thumbnail_url)

        elif len(image_files) >= 2:
            # Carousel
            print("   Uploading carousel images...")
            image_urls = self.upload_multiple_to_cloudinary(image_files)

            if len(image_urls) >= 2:
                return self.post_carousel(title, captions, image_urls)

        elif len(image_files) == 1:
            # Single image
            print("   Uploading image...")
            image_url = self.upload_to_cloudinary(image_files[0])

            if image_url:
                return self.post_image(title, captions, image_url)

        print("   No content to post")
        return {"instagram": None, "facebook": None, "x": None, "linkedin": None}

    def post_from_folder_per_platform(self, output_folder: str, platform_formats: Dict[str, str],
                                       article: Dict = None) -> Dict[str, any]:
        """
        V5.10: Post different content formats to different platforms.

        Args:
            output_folder: Path to folder containing generated content
            platform_formats: Dict mapping platform to format
                e.g. {'instagram': 'reel', 'facebook': 'single_post', 'linkedin': 'single_post', 'twitter': 'single_post'}
            article: Optional article dict with title

        Returns:
            Dict with results per platform
        """
        import sys
        import traceback

        print(f"   📤 Starting post_from_folder_per_platform...")
        sys.stdout.flush()

        try:
            if not os.path.exists(output_folder):
                print(f"   Folder not found: {output_folder}")
                return {"instagram": None, "facebook": None, "x": None, "linkedin": None}

            # Get title
            title = "Immigration Update"
            if article:
                title = article.get('title', title)
            print(f"   Title: {title[:50]}...")
            sys.stdout.flush()

            # Load captions
            captions = self._load_captions_from_folder(output_folder)
        except Exception as e:
            print(f"   ❌ CRASH in post_from_folder_per_platform: {type(e).__name__}: {e}")
            print(traceback.format_exc())
            sys.stdout.flush()
            return {"instagram": None, "facebook": None, "x": None, "linkedin": None}

        if not captions.get('caption_instagram'):
            print("   No Instagram caption found")
            return {"instagram": None, "facebook": None, "x": None, "linkedin": None}

        # Find and categorize content files
        single_post_image = None
        carousel_images = []
        video_file = None
        reel_thumbnail = None

        for filename in sorted(os.listdir(output_folder)):
            filepath = os.path.join(output_folder, filename)

            if filename == 'single_post.png':
                single_post_image = filepath
            elif filename == 'reel_thumbnail.png':
                reel_thumbnail = filepath
            elif filename.endswith(('.png', '.jpg', '.jpeg')):
                if 'slide_' in filename.lower():
                    carousel_images.append(filepath)
                elif not single_post_image and not any(x in filename.lower() for x in ['thumb', 'screenshot', 'evidence']):
                    single_post_image = filepath
            elif filename.endswith('.mp4') and 'reel' in filename.lower():
                video_file = filepath

        # Sort carousel images
        carousel_images.sort()

        print(f"   Content found: single_post={bool(single_post_image)}, carousel={len(carousel_images)}, reel={bool(video_file)}")
        print(f"   Platform formats: {platform_formats}")

        # Upload content as needed
        single_url = None
        carousel_urls = []
        video_url = None
        thumbnail_url = None

        results = {"instagram": None, "facebook": None, "x": None, "linkedin": None}

        # Determine what content needs to be uploaded
        needs_single = any(platform_formats.get(p) == 'single_post' for p in ['instagram', 'facebook', 'linkedin', 'twitter'])
        needs_carousel = any(platform_formats.get(p) == 'carousel' for p in ['instagram', 'facebook'])
        needs_reel = any(platform_formats.get(p) == 'reel' for p in ['instagram', 'facebook'])

        print(f"   Upload needs: single={needs_single}, carousel={needs_carousel}, reel={needs_reel}")

        # Upload single post image if needed
        if needs_single and single_post_image:
            print(f"   Uploading single post image: {os.path.basename(single_post_image)}...")
            single_url = self.upload_to_cloudinary(single_post_image)
            print(f"   Single URL: {'✅ Got URL' if single_url else '❌ Failed'}")
        elif needs_single:
            print(f"   ⚠️ Single post needed but no image found")

        # Upload carousel images if needed
        if needs_carousel and len(carousel_images) >= 2:
            print(f"   Uploading {len(carousel_images)} carousel images...")
            carousel_urls = self.upload_multiple_to_cloudinary(carousel_images)
            print(f"   Carousel URLs: {len(carousel_urls)} uploaded")
        elif needs_carousel:
            print(f"   ⚠️ Carousel needed but only {len(carousel_images)} images")

        # Upload reel if needed
        if needs_reel and video_file:
            print("   Uploading reel video...")
            video_url = self.upload_to_cloudinary(video_file, "video")
            if reel_thumbnail:
                thumbnail_url = self.upload_to_cloudinary(reel_thumbnail)
            elif single_post_image:
                thumbnail_url = self.upload_to_cloudinary(single_post_image)

        print(f"   --- POSTING TO PLATFORMS ---")

        # V6.4: Check Instagram cooldown before posting
        if self._is_instagram_on_cooldown():
            print("   📸 Instagram: ⏭️ SKIPPED (rate limit cooldown)")
            results['instagram'] = None
        else:
            # Post to Instagram based on format
            ig_format = platform_formats.get('instagram', 'single_post')
            print(f"   📸 Instagram: format={ig_format}, carousel_urls={len(carousel_urls)}, single_url={bool(single_url)}")
            if ig_format == 'reel' and video_url:
                print("   📸 Instagram: Posting REEL")
                results['instagram'] = self.post_instagram_reel(video_url, captions.get('caption_instagram', ''))
            elif ig_format == 'carousel' and len(carousel_urls) >= 2:
                print("   📸 Instagram: Posting CAROUSEL")
                results['instagram'] = self.post_instagram_carousel(carousel_urls, captions.get('caption_instagram', ''))
            elif single_url:
                print("   📸 Instagram: Posting SINGLE IMAGE (fallback)")
                results['instagram'] = self.post_instagram_image(single_url, captions.get('caption_instagram', ''))
            else:
                print("   📸 Instagram: ❌ No content available to post")

        # Post to Facebook based on format
        fb_format = platform_formats.get('facebook', 'single_post')
        print(f"   📘 Facebook: format={fb_format}, carousel_urls={len(carousel_urls)}, single_url={bool(single_url)}")
        if fb_format == 'reel' and video_url:
            print("   📘 Facebook: Posting REEL")
            results['facebook'] = self.post_facebook_reel(video_url, captions.get('caption_facebook', ''))
        elif fb_format == 'carousel' and len(carousel_urls) >= 2:
            print("   📘 Facebook: Posting CAROUSEL")
            results['facebook'] = self.post_facebook_carousel(carousel_urls, captions.get('caption_facebook', ''))
        elif single_url:
            print("   📘 Facebook: Posting SINGLE IMAGE (fallback)")
            results['facebook'] = self.post_facebook_image(single_url, captions.get('caption_facebook', ''))
        else:
            print("   📘 Facebook: ❌ No content available to post")

        # LinkedIn always gets single image
        print(f"   💼 LinkedIn: single_url={bool(single_url)}")
        if single_url:
            print("   💼 LinkedIn: Posting SINGLE IMAGE")
            results['linkedin'] = self.post_linkedin(single_url, captions.get('caption_linkedin', ''), title)
        else:
            print("   💼 LinkedIn: ❌ No single_url available")

        # Twitter/X - V5.20: Check if thread format
        twitter_caption = captions.get('caption_x', '')
        print(f"   🐦 Twitter/X: single_url={bool(single_url)}, caption_x={bool(twitter_caption)}")
        if twitter_caption:
            # V6.0: Text-only posts on X (no images - captions were getting cut off)
            if '---TWEET---' in twitter_caption:
                print("   🐦 Twitter/X: Posting THREAD (text-only)")
                results['x'] = self.post_x_thread(single_url, twitter_caption)
            else:
                print("   🐦 Twitter/X: Posting TEXT-ONLY (no image)")
                # V6.0: Use full caption length (X Premium allows 4000 chars)
                post_text = twitter_caption[:2500] if len(twitter_caption) > 2500 else twitter_caption
                results['x'] = self.post_x_text(post_text)
        else:
            print("   🐦 Twitter/X: ❌ No caption available")

        print(f"   --- POSTING COMPLETE: {results} ---")

        return results

    def _load_captions_from_folder(self, output_folder: str) -> Dict[str, str]:
        """Load platform-specific captions from folder."""
        captions = {
            "caption_instagram": "",
            "caption_facebook": "",
            "caption_linkedin": "",
            "caption_x": ""
        }

        platform_map = {
            'instagram': 'caption_instagram',
            'facebook': 'caption_facebook',
            'linkedin': 'caption_linkedin',
            'twitter': 'caption_x',
            'x': 'caption_x'
        }

        print(f"   Loading captions from: {output_folder}")
        import sys
        sys.stdout.flush()
        files_found = []

        try:
            all_files = os.listdir(output_folder)
            print(f"      Directory contains {len(all_files)} files")
            sys.stdout.flush()
        except Exception as e:
            print(f"      ❌ Error listing directory: {e}")
            sys.stdout.flush()
            return captions

        for filename in all_files:
            if filename.startswith('caption_') and filename.endswith('.txt'):
                platform = filename.replace('caption_', '').replace('.txt', '').lower()
                caption_key = platform_map.get(platform)

                if caption_key:
                    filepath = os.path.join(output_folder, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            captions[caption_key] = content
                            files_found.append(f"{filename} ({len(content)} chars)")
                    except Exception as e:
                        print(f"      Error reading {filename}: {e}")
                        sys.stdout.flush()

        print(f"      Found: {', '.join(files_found) if files_found else 'no caption files'}")
        sys.stdout.flush()

        # Fallback - use Instagram caption for missing platforms
        if captions['caption_instagram']:
            for key in captions:
                if not captions[key]:
                    if key == 'caption_x':
                        captions[key] = captions['caption_instagram'][:270] + "..."
                    else:
                        captions[key] = captions['caption_instagram']
                    print(f"      Using Instagram fallback for {key}")

        return captions

    def _print_summary(self, results: Dict):
        """Print results summary."""
        print("\n" + "-"*60)
        print("RESULTS SUMMARY")
        print("-"*60)
        for platform, result in results.items():
            status = "SUCCESS" if result else "FAILED"
            print(f"   {platform.upper()}: {status}")
        print("-"*60 + "\n")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_captions(
    instagram: str,
    facebook: str = None,
    linkedin: str = None,
    x: str = None
) -> Dict[str, str]:
    """
    Create captions dictionary for all platforms.

    Args:
        instagram: Instagram caption (required, used as default)
        facebook: Facebook caption (optional, defaults to instagram)
        linkedin: LinkedIn caption (optional, defaults to facebook)
        x: X/Twitter caption (optional, defaults to truncated instagram)

    Returns:
        Dict with all captions
    """
    ig_caption = instagram
    fb_caption = facebook or instagram
    li_caption = linkedin or facebook or instagram
    x_caption = x or (instagram[:270] + "..." if len(instagram) > 270 else instagram)

    return {
        "caption_instagram": ig_caption,
        "caption_facebook": fb_caption,
        "caption_linkedin": li_caption,
        "caption_x": x_caption
    }


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

# Alias for old code
PhilataSocialPoster = PhilataPoster


# =============================================================================
# TEST
# =============================================================================

def test_all_platforms():
    """Test posting to all platforms."""
    from dotenv import load_dotenv
    load_dotenv()

    poster = PhilataPoster()

    captions = create_captions(
        instagram="Test from Philata Bot!\n\n#CanadaImmigration #Test #Philata",
        facebook="Test from Philata Bot!",
        linkedin="Test from Philata automation system.",
        x="Test from Philata! #Test"
    )

    # Use a sample image
    results = poster.post_image(
        title="Test Post",
        captions=captions,
        image_url="https://res.cloudinary.com/dg7yw1j18/image/upload/v1734412800/philata/test.jpg"
    )

    return results


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()

    print("="*60)
    print("PHILATA SOCIAL MEDIA POSTER")
    print("="*60)

    if len(sys.argv) > 1:
        command = sys.argv[1]
        poster = PhilataPoster()

        if command == "test-all":
            test_all_platforms()
        elif command == "test-instagram":
            poster.post_instagram_image(
                "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                "Test from Philata!\n\n#Test"
            )
        elif command == "test-facebook":
            poster.post_facebook_image(
                "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                "Test from Philata!"
            )
        elif command == "test-x":
            poster.post_x_image(
                "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                "Test from Philata! #Test"
            )
        elif command == "test-linkedin":
            poster.post_linkedin(
                "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                "Test from Philata",
                "Test"
            )
        else:
            print(f"Unknown command: {command}")
    else:
        print("\nUsage:")
        print("  python philata_social_poster.py test-all")
        print("  python philata_social_poster.py test-instagram")
        print("  python philata_social_poster.py test-facebook")
        print("  python philata_social_poster.py test-x")
        print("  python philata_social_poster.py test-linkedin")
