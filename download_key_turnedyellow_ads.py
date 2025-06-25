#!/usr/bin/env python3
"""
Download key TurnedYellow ad creatives
"""

import requests
import os

def download_image(url, filename):
    """Download image from URL"""
    try:
        print(f"🔄 Downloading: {filename}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded: {filename}")
            return True
        else:
            print(f"❌ Failed to download {url}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error downloading {url}: {str(e)}")
        return False

def main():
    print("🎯 Downloading Key TurnedYellow Ad Creatives")
    
    # Create output directory
    output_dir = "actual_turnedyellow_ads"
    os.makedirs(output_dir, exist_ok=True)
    
    # Key TurnedYellow ad thumbnails from the API response
    ads_to_download = [
        {
            "name": "01_David_Influencer_WINNER_REAL_AD.jpg",
            "url": "https://scontent-lax3-2.xx.fbcdn.net/v/t15.5256-10/506900517_1712278179654694_3869804707552648242_n.jpg?_nc_cat=106&ccb=1-7&_nc_ohc=qP8Wb1E2naIQ7kNvwEg0LkI&_nc_oc=Adl18nW8sHhJ49tRrnkqs-4o9VTcZRQYt7NVjTz-kw_G_CjOo6NkhM-8CDZ3vMVwwaw&_nc_zt=23&_nc_ht=scontent-lax3-2.xx&edm=AAT1rw8EAAAA&_nc_gid=MQd3JwpV3jU_TutuDUKK6g&stp=c0.5000x0.5000f_dst-emg0_p64x64_q75_tt6&ur=7965db&_nc_sid=58080a&oh=00_AfNAJcrx4eMUlxi2EA80Zidl3cc_-yYLAkP-6AQYJG2LVw&oe=68616776"
        },
        {
            "name": "02_TY_Video_1_HIGH_HOOK_REAL_AD.jpg", 
            "url": "https://scontent-lax3-2.xx.fbcdn.net/v/t15.5256-10/506840974_3929466347265050_1838885650304078136_n.jpg?_nc_cat=100&ccb=1-7&_nc_ohc=100jEJDff-YQ7kNvwH8co4l&_nc_oc=AdnuyRJNfULkmV5PEadQfShNQ9wR4-fIgZyqmyVtrceq5PX9RQFMQHs4RJVMahk79Ck&_nc_zt=23&_nc_ht=scontent-lax3-2.xx&edm=AAT1rw8EAAAA&_nc_gid=lf1l9-ZGdgFX2LPSQPkszw&stp=c0.5000x0.5000f_dst-emg0_p64x64_q75_tt6&ur=7965db&_nc_sid=58080a&oh=00_AfMkEZpvEOrrJG2D6mtzfweyV9HY2C2LKLBqz-76K-JOKQ&oe=68615290"
        },
        {
            "name": "03_Royal_Inspo_Hook_STRONG_REAL_AD.jpg",
            "url": "https://scontent-lax3-1.xx.fbcdn.net/v/t15.5256-10/507084537_2590438734496446_8503382340615493958_n.jpg?_nc_cat=105&ccb=1-7&_nc_ohc=FCt9PXKl3A8Q7kNvwF9tarA&_nc_oc=AdmYJjB0LiHKRtzRr3cHFBmEqOvohjEChROl8LqBRlBYpyQDqIibJu7zgQ203O34P0k&_nc_zt=23&_nc_ht=scontent-lax3-1.xx&edm=AAT1rw8EAAAA&_nc_gid=8DjPy8gY9V0ux53AdKFsCA&stp=c0.5000x0.5000f_dst-emg0_p64x64_q75_tt6&ur=7965db&_nc_sid=58080a&oh=00_AfNuJRyxvxWSGn3rtK4_L7L3X6HJBfhoqsgP3vwzS-8h6g&oe=68615210"
        },
        {
            "name": "04_Bigfoot_Jungle_Vlog_REAL_AD.jpg",
            "url": "https://scontent-lax3-1.xx.fbcdn.net/v/t15.5256-10/506696243_9832566163478379_8998767729073793872_n.jpg?_nc_cat=102&ccb=1-7&_nc_ohc=L6IDs3YwI5YQ7kNvwH_I9P-&_nc_oc=AdkNbao_h7RGJXLOyn_0OaX523I4we9Vbol2NLygbaPww6qP5FnfWjcyobEQLa4O-ss&_nc_zt=23&_nc_ht=scontent-lax3-1.xx&edm=AAT1rw8EAAAA&_nc_gid=_wivu0CjUTllbNh22inE9g&stp=c0.5000x0.5000f_dst-emg0_p64x64_q75_tt6&ur=7965db&_nc_sid=58080a&oh=00_AfPti7Cm1Gx8zf1v9IREAN37EDO5X2i2GKV202Wca6KQdw&oe=6861553B"
        }
    ]
    
    # Download each ad
    downloaded_count = 0
    for ad in ads_to_download:
        filename = f"{output_dir}/{ad['name']}"
        if download_image(ad['url'], filename):
            downloaded_count += 1
    
    print(f"\n🎉 Downloaded {downloaded_count}/{len(ads_to_download)} TurnedYellow ad creatives!")
    
    # Also copy to GitHub repository
    if downloaded_count > 0:
        print("\n📁 Copying to GitHub repository...")
        os.system(f"cp {output_dir}/*.jpg creative-ads-repository/TurnedYellow/")
        print("✅ Copied to creative-ads-repository/TurnedYellow/")

if __name__ == "__main__":
    main() 