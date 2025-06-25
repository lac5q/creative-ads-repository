#!/usr/bin/env python3
"""
Create proper placeholder images for ad creatives
"""

import os
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_placeholder_image(ad_name, account_name, ad_type, output_path, width=1200, height=630):
    """Create a placeholder image with ad information"""
    
    # Create a new image with a gradient background
    img = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(height):
        color_value = int(248 - (y * 20 / height))  # Subtle gradient
        color = (color_value, color_value + 5, color_value + 10)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Try to load a font, fallback to default if not available
    try:
        title_font = ImageFont.truetype("Arial.ttf", 48)
        subtitle_font = ImageFont.truetype("Arial.ttf", 32)
        info_font = ImageFont.truetype("Arial.ttf", 24)
    except:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
            info_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
    
    # Colors
    title_color = '#2c3e50'
    subtitle_color = '#34495e'
    accent_color = '#3498db'
    
    # Draw border
    border_width = 8
    draw.rectangle([border_width//2, border_width//2, width-border_width//2, height-border_width//2], 
                   outline=accent_color, width=border_width)
    
    # Title
    title_text = "AD CREATIVE PLACEHOLDER"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 80), title_text, fill=title_color, font=title_font)
    
    # Account name
    account_text = f"Account: {account_name}"
    account_bbox = draw.textbbox((0, 0), account_text, font=subtitle_font)
    account_width = account_bbox[2] - account_bbox[0]
    account_x = (width - account_width) // 2
    draw.text((account_x, 160), account_text, fill=accent_color, font=subtitle_font)
    
    # Ad type
    type_text = f"Type: {ad_type.upper()}"
    type_bbox = draw.textbbox((0, 0), type_text, font=info_font)
    type_width = type_bbox[2] - type_bbox[0]
    type_x = (width - type_width) // 2
    draw.text((type_x, 220), type_text, fill=subtitle_color, font=info_font)
    
    # Ad name (wrapped)
    wrapped_name = textwrap.fill(ad_name, width=40)
    name_lines = wrapped_name.split('\n')
    
    y_offset = 280
    for line in name_lines:
        line_bbox = draw.textbbox((0, 0), line, font=info_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) // 2
        draw.text((line_x, y_offset), line, fill=title_color, font=info_font)
        y_offset += 35
    
    # Footer message
    footer_text = "Actual creative not available - API permissions required"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=info_font)
    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_x = (width - footer_width) // 2
    draw.text((footer_x, height - 80), footer_text, fill=subtitle_color, font=info_font)
    
    # Save the image
    img.save(output_path, 'PNG', quality=95)
    print(f"Created placeholder: {output_path}")

def main():
    """Create placeholder images for all ad creatives"""
    
    # Ad data from Airtable
    ads_data = [
        {
            "name": "video: influencer David / Most incredible",
            "account": "TurnedYellow",
            "type": "video",
            "filename": "01_David_Influencer_WINNER"
        },
        {
            "name": "video: Gifting hook 1 (Sara) / Life is too short", 
            "account": "TurnedYellow",
            "type": "video",
            "filename": "02_Gifting_Hook_Sara_Life_Short"
        },
        {
            "name": "video: ty video 1 / Make anyone laugh",
            "account": "TurnedYellow", 
            "type": "video",
            "filename": "02_TY_Video_1_HIGH_HOOK"
        },
        {
            "name": "video: Early BF gifs&boomerangs / Get up to 70% off",
            "account": "TurnedYellow",
            "type": "video", 
            "filename": "04_Early_BF_Gifs_Boomerangs"
        },
        {
            "name": "image: Father's day 2025 - 1 / Gift Dad",
            "account": "TurnedYellow",
            "type": "image",
            "filename": "05_Fathers_Day_Video_2025"
        },
        {
            "name": "image: Early BF images 1 / Get up to 70% off", 
            "account": "TurnedYellow",
            "type": "image",
            "filename": "04_Early_BF_Images"
        },
        {
            "name": "video: agency hook Birthday / transform",
            "account": "MakeMeJedi",
            "type": "video",
            "filename": "11_Birthday_Hook_Agency_WINNER"
        },
        {
            "name": "video: FD 1 remake / A long time ago",
            "account": "MakeMeJedi", 
            "type": "video",
            "filename": "12_FD_1_Remake_Long_Time_Ago"
        },
        {
            "name": "video: V day (reaction) 4 / This Valentine's Day",
            "account": "MakeMeJedi",
            "type": "video", 
            "filename": "18_Valentines_Day_Reaction"
        },
        {
            "name": "video: Early BF / Enjoy up to 75% OFF",
            "account": "MakeMeJedi",
            "type": "video",
            "filename": "15_Early_BF_75_Percent_Off"
        },
        {
            "name": "video: FD 2 remake / A long time ago [pdp]",
            "account": "MakeMeJedi",
            "type": "video", 
            "filename": "12_FD_2_Remake_Long_Time_Ago"
        },
        {
            "name": "image: Celebrate Father's Day - up to 70 off!.png (FD2024)",
            "account": "MakeMeJedi",
            "type": "image",
            "filename": "20_Fathers_Day_Mashup_2024"
        },
        {
            "name": "image: couple / Become a Jedi (70%)",
            "account": "MakeMeJedi", 
            "type": "image",
            "filename": "21_Couple_Become_Jedi"
        }
    ]
    
    # Create output directory
    output_dir = "creative-ads-repository"
    os.makedirs(f"{output_dir}/TurnedYellow", exist_ok=True)
    os.makedirs(f"{output_dir}/MakeMeJedi", exist_ok=True)
    
    print("Creating proper placeholder images...")
    
    for ad in ads_data:
        # Determine output path
        if ad["account"] == "TurnedYellow":
            output_path = f"{output_dir}/TurnedYellow/{ad['filename']}_PLACEHOLDER.png"
        else:
            output_path = f"{output_dir}/MakeMeJedi/{ad['filename']}_PLACEHOLDER.png"
        
        # Create placeholder image
        create_placeholder_image(
            ad_name=ad["name"],
            account_name=ad["account"], 
            ad_type=ad["type"],
            output_path=output_path
        )
    
    print(f"\nCreated {len(ads_data)} placeholder images")
    print("These placeholders clearly indicate they are not actual ad creatives")
    print("Actual creatives would need proper Meta API permissions to download")

if __name__ == "__main__":
    main() 