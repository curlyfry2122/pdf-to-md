#!/usr/bin/env python3
"""
Enhance alt text in FDW-P Slides markdown file with descriptive image descriptions
"""

import re

# Define specific alt text for screenshots based on page content
screenshot_descriptions = {
    "page_012_img_03": "Screenshot of FDW login page with username and password fields, 'Remember Me' checkbox, green 'SIGN IN' button, and 'Forgot Password?' link",
    "page_013_img_03": "Screenshot of Welcome dropdown menu showing 'View site', 'Change password', and 'Log out' options",
    "page_013_img_04": "Screenshot of password change form with fields for old password, new password, and password confirmation",
    "page_014_img_03": "Screenshot of FDW Password Reset page with email address input field and 'Reset My Password' button",
    "page_016_img_03": "Screenshot of FDW home screen showing navigation menu with Home, Data Explorer, Supporting Evidence, Data Entry, Data Processing, Data Analysis, Dataseries Management, Metadata Management, and System Administration menus",
    "page_017_img_03": "Screenshot of FEWS NET Data Explorer interface header with navigation",
    "page_018_img_03": "Screenshot of Maya EDMS (Electronic Document Management System) supporting documents interface",
    "page_019_img_03": "Screenshot showing Data Entry menu options in the FDW interface",
    "page_019_img_04": "Screenshot showing Data Processing menu options in the FDW interface",
    "page_019_img_05": "Screenshot showing additional processing options in the FDW interface",
    "page_020_img_03": "Screenshot showing Data Analysis menu options including Single Data Series and Data Sets",
    "page_021_img_03": "Screenshot showing Dataseries Management and Metadata Management menu options",
    "page_021_img_04": "Screenshot of permission denied message for restricted access areas",
    "page_024_img_03": "Screenshot of data series search results table showing Burundi market price data with columns for Data Series ID, Source document, Usage policy, First period date, Last period date, and Data series subtype",
    "page_025_img_03": "Screenshot showing data series detail view with options to Browse, Extract, or generate Excel Web Query",
    "page_026_img_03": "Screenshot highlighting export options: 'Extract data in a flat file format' and 'Browse allows you to see the data online without extracting it'",
    "page_030_img_03": "Screenshot of Price Data Sets list showing dataset names, IDs, descriptions, visibility settings, and owners including datasets for Burkina Faso, CAP Honduras, and Central America",
    "page_035_img_03": "Screenshot or diagram showing the three steps for using a Data Set Workbook with numbered instructions",
    "page_036_img_03": "Screenshot or diagram illustrating the tabs in a Data Set Refreshable Workbook: Parameters, Data, Percentage Changes, and Prices tabs",
    "page_037_img_03": "Screenshot showing Country Refreshable Workbook parameters tab",
    "page_037_img_04": "Screenshot showing Country Refreshable Workbook data refresh process",
    "page_040_img_03": "Screenshot or contact information panel for FDW help and support resources"
}

def enhance_markdown_alt_text(input_file, output_file):
    """Read markdown file and enhance alt text for all images"""

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match image markdown syntax
    pattern = r'!\[Image from page (\d+)\]\((images/FDW-P_Slides_page_(\d{3})_img_(\d{2})\.png)\)'

    def replace_alt_text(match):
        page_num = match.group(1)
        img_path = match.group(2)
        page_padded = match.group(3)
        img_num = match.group(4)

        # Generate key for screenshot descriptions
        img_key = f"page_{page_padded}_img_{img_num}"

        # Check if this is a known screenshot
        if img_key in screenshot_descriptions:
            alt_text = screenshot_descriptions[img_key]
        # img_01 is always FEWS NET logo
        elif img_num == "01":
            alt_text = "FEWS NET logo - Famine Early Warning Systems Network with globe icon showing continents"
        # img_02 is always USAID logo
        elif img_num == "02":
            alt_text = "USAID logo - United States Agency for International Development seal with text 'From the American People'"
        # For other images without specific descriptions, provide generic but helpful alt text
        else:
            alt_text = f"Screenshot or diagram from slide {page_num} illustrating FDW-P training content"

        return f"![{alt_text}]({img_path})"

    # Replace all image alt texts
    enhanced_content = re.sub(pattern, replace_alt_text, content)

    # Write enhanced version
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)

    print(f"Enhanced markdown file created: {output_file}")

    # Count replacements
    original_images = len(re.findall(pattern, content))
    print(f"Enhanced alt text for {original_images} images")

if __name__ == "__main__":
    input_file = "outputs/FDW-P_Slides.md"
    output_file = "outputs/FDW-P_Slides.md"
    enhance_markdown_alt_text(input_file, output_file)
