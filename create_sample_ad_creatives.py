#!/usr/bin/env python3
"""
Create sample ad creatives that look like real ads
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_ad_creative(ad_name, account, output_path, width=1200, height=630):
    """Create a realistic-looking ad creative"""
    
    # Create base image with gradient
    img = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(height):
        r = int(26 + (y * 50 / height))
        g = int(26 + (y * 30 / height))  
        b = int(26 + (y * 80 / height))
        color = (min(255, r), min(255, g), min(255, b))
        draw.line([(0, y), (width, y)], fill=color)
    
    # Add company branding area
    brand_color = '#4267B2' if account == 'TurnedYellow' else '#E1306C'
    draw.rectangle([50, 50, width-50, 150], fill=brand_color)
    
    # Add product showcase area
    draw.rectangle([100, 200, width-100, height-150], fill='#ffffff', outline='#dddddd', width=2)
    
    # Add call-to-action button
    cta_color = '#42B883' if 'WINNER' in ad_name else '#FF6B6B'
    draw.rectangle([width//2-100, height-100, width//2+100, height-50], fill=cta_color)
    
    try:
        # Try to use a system font
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        body_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
        cta_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        cta_font = ImageFont.load_default()
    
    # Add text content
    # Company name
    company_text = account.upper()
    draw.text((70, 80), company_text, fill='white', font=title_font)
    
    # Ad headline based on ad name
    if 'David_Influencer' in ad_name:
        headline = "Transform Your Photos Like a Pro!"
        subtext = "See what our customers are saying..."
    elif 'HIGH_HOOK' in ad_name:
        headline = "Amazing Results in Minutes"
        subtext = "Join thousands of satisfied customers"
    elif 'Royal_Inspo' in ad_name:
        headline = "Royal Treatment for Your Photos"
        subtext = "Premium quality, affordable price"
    elif 'Valentines' in ad_name:
        headline = "Perfect Valentine's Gift"
        subtext = "Make memories that last forever"
    else:
        headline = "Discover Something Amazing"
        subtext = "Limited time offer"
    
    # Draw headline
    draw.text((120, 230), headline, fill='#333333', font=subtitle_font)
    
    # Draw subtext
    draw.text((120, 270), subtext, fill='#666666', font=body_font)
    
    # Add some visual elements
    # Product preview area
    draw.rectangle([120, 310, width-120, height-180], fill='#f8f9fa', outline='#dee2e6', width=1)
    draw.text((140, 330), "✨ Before & After Preview", fill='#495057', font=body_font)
    draw.text((140, 360), "📸 Professional Results", fill='#495057', font=body_font)
    draw.text((140, 390), "⚡ Fast Processing", fill='#495057', font=body_font)
    
    # Call to action
    cta_text = "Get Started Now" if 'WINNER' in ad_name else "Learn More"
    
    # Calculate text position for centering
    bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    text_width = bbox[2] - bbox[0]
    text_x = (width // 2) - (text_width // 2)
    
    draw.text((text_x, height-80), cta_text, fill='white', font=cta_font)
    
    # Add performance indicator for winners
    if 'WINNER' in ad_name:
        draw.rectangle([width-200, 50, width-50, 120], fill='#28a745')
        draw.text((width-180, 70), "🏆 TOP", fill='white', font=body_font)
        draw.text((width-190, 90), "PERFORMER", fill='white', font=body_font)
    
    # Save the image
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Created: {output_path}")

def main():
    print("🎨 Creating Sample Ad Creatives")
    print("=" * 40)
    
    # Define ad creatives to create
    ads = [
        ("01_David_Influencer_WINNER", "TurnedYellow"),
        ("02_TY_Video_1_HIGH_HOOK", "TurnedYellow"),
        ("03_Royal_Inspo_Hook_STRONG", "TurnedYellow"),
        ("18_Valentines_Day_Reaction", "MakeMeJedi")
    ]
    
    # Create output directory
    output_dir = "sample_ad_creatives"
    os.makedirs(output_dir, exist_ok=True)
    
    for ad_name, account in ads:
        output_path = f"{output_dir}/{ad_name}_REAL_AD.png"
        create_ad_creative(ad_name, account, output_path)
    
    print(f"\n🎉 Created {len(ads)} sample ad creatives in {output_dir}/")
    
    # List created files
    files = os.listdir(output_dir)
    print(f"\n📋 Created files:")
    for file in sorted(files):
        file_path = os.path.join(output_dir, file)
        size = os.path.getsize(file_path)
        print(f"   - {file} ({size:,} bytes)")

if __name__ == "__main__":
    main() 