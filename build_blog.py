#!/usr/bin/env python3
"""
Blog Build Script
Converts markdown files to HTML blog posts and updates index.html and insights.html
"""

import os
import re
from datetime import datetime
from pathlib import Path
import markdown
from bs4 import BeautifulSoup


def parse_markdown_file(filepath):
    """Parse a markdown file and extract metadata, content, conclusion, and first image."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract header metadata
    header_match = re.search(r'<header>(.*?)</header>', content, re.DOTALL)
    date = None
    author = None
    
    if header_match:
        header_content = header_match.group(1)
        date_match = re.search(r'<date>(.*?)</date>', header_content)
        author_match = re.search(r'<author>(.*?)</author>', header_content)
        
        if date_match:
            date = date_match.group(1).strip()
        if author_match:
            author = author_match.group(1).strip()
    
    # Remove header from content
    content = re.sub(r'<header>.*?</header>', '', content, flags=re.DOTALL).strip()
    
    # Extract title (first # heading)
    title_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
    title = None
    if title_match:
        title = title_match.group(1).strip()
        # Remove title from content
        content = re.sub(r'^#\s+.*$', '', content, count=1, flags=re.MULTILINE).strip()
    
    # Extract conclusion section
    conclusion = None
    conclusion_text_raw = None
    conclusion_match = re.search(r'##\s+Conclusion\s*\n(.*?)$', content, re.DOTALL)
    if conclusion_match:
        conclusion_text_raw = conclusion_match.group(1).strip()
        # Remove conclusion from main content first
        content = re.sub(r'##\s+Conclusion\s*\n.*$', '', content, flags=re.DOTALL).strip()
    
    # Convert absolute file:// paths to relative paths
    # Handle file:// paths in markdown image syntax
    def convert_file_path(match):
        alt_text = match.group(1)
        full_path = match.group(2)
        if full_path.startswith('file://'):
            # Extract the path after file://
            path_part = full_path[7:]  # Remove 'file://'
            # Get the script directory to find relative path
            script_dir = Path(__file__).parent
            try:
                # Convert to Path object and get relative path
                abs_path = Path(path_part)
                if abs_path.exists():
                    # Get relative path from script directory
                    rel_path = abs_path.relative_to(script_dir)
                    # Convert to forward slashes and ensure it starts with ../
                    rel_str = str(rel_path).replace('\\', '/')
                    # If it's in imgs/ directory, make it ../imgs/filename
                    if 'imgs/' in rel_str:
                        # Extract just the filename
                        filename = rel_path.name
                        return f'![{alt_text}](../imgs/{filename})'
                    return f'![{alt_text}](../{rel_str})'
            except (ValueError, OSError):
                # If path conversion fails, try to extract filename
                filename = Path(path_part).name
                return f'![{alt_text}](../imgs/{filename})'
        return f'![{alt_text}]({full_path})'
    
    # Replace file:// paths in markdown image syntax
    content = re.sub(r'!\[([^\]]*)\]\((file://[^)]+)\)', convert_file_path, content)
    
    # Extract first image URL (after path conversion)
    first_image = None
    image_match = re.search(r'!\[.*?\]\((.*?)\)', content)
    if image_match:
        first_image = image_match.group(1)
    
    # Convert main content to HTML
    main_content_html = markdown.markdown(content)
    
    # Also fix any remaining file:// paths in the HTML output
    def fix_html_image_paths(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        script_dir = Path(__file__).parent
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src.startswith('file://'):
                path_part = src[7:]  # Remove 'file://'
                try:
                    abs_path = Path(path_part)
                    if abs_path.exists():
                        rel_path = abs_path.relative_to(script_dir)
                        filename = rel_path.name
                        if 'imgs' in str(rel_path):
                            img['src'] = f'../imgs/{filename}'
                        else:
                            img['src'] = '../' + str(rel_path).replace('\\', '/')
                    else:
                        # Path doesn't exist, just extract filename
                        filename = Path(path_part).name
                        img['src'] = f'../imgs/{filename}'
                except (ValueError, OSError):
                    # If path conversion fails, extract filename
                    filename = Path(path_part).name
                    img['src'] = f'../imgs/{filename}'
        return str(soup)
    
    main_content_html = fix_html_image_paths(main_content_html)
    
    # Process conclusion if it exists
    if conclusion_text_raw:
        # Convert file:// paths in conclusion markdown
        conclusion_text = re.sub(r'!\[([^\]]*)\]\((file://[^)]+)\)', convert_file_path, conclusion_text_raw)
        # Convert conclusion to HTML
        conclusion_html = markdown.markdown(conclusion_text)
        # Fix any remaining file:// paths in conclusion HTML
        conclusion = fix_html_image_paths(conclusion_html)
    
    # Parse date for sorting (try to parse, but keep original format)
    sort_date = None
    if date:
        # Try various date formats for sorting
        date_formats = ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']
        for fmt in date_formats:
            try:
                sort_date = datetime.strptime(date, fmt)
                break
            except ValueError:
                continue
        # If no format matched, use a default date (oldest)
        if sort_date is None:
            sort_date = datetime(1900, 1, 1)
    
    return {
        'filename': Path(filepath).stem,
        'title': title or 'Untitled',
        'date': date or '',
        'author': author or '',
        'content': main_content_html,
        'conclusion': conclusion or '',
        'first_image': first_image,
        'sort_date': sort_date or datetime(1900, 1, 1)
    }


def generate_blog_post_html(template_path, post_data):
    """Generate HTML blog post from template and post data."""
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    soup = BeautifulSoup(template, 'html.parser')
    
    # Fix stylesheet path (posts are in blog/ subdirectory)
    stylesheet_link = soup.find('link', rel='stylesheet')
    if stylesheet_link and stylesheet_link.get('href') == 'styles.css':
        stylesheet_link['href'] = '../styles.css'
    
    # Update title tag
    title_tag = soup.find('title')
    if title_tag:
        title_tag.string = f"{post_data['title']} - Resolved Law Group"
    
    # Update blog post title
    blog_title = soup.find('h1', class_='blog-post-title')
    if blog_title:
        blog_title.string = post_data['title']
    
    # Update blog post meta
    blog_meta = soup.find('div', class_='blog-post-meta')
    if blog_meta:
        meta_text = f"Posted on {post_data['date']} | Author: {post_data['author']}"
        blog_meta.string = meta_text
    
    # Update blog post content
    blog_content = soup.find('div', class_='blog-post-content')
    if blog_content:
        # Clear all existing content (we'll rebuild it)
        blog_content.clear()
        
        # Parse and insert main content
        content_soup = BeautifulSoup(post_data['content'], 'html.parser')
        for element in content_soup.children:
            if element.name:
                blog_content.append(element)
        
        # Add conclusion div at the end if conclusion exists
        if post_data['conclusion']:
            conclusion_div = soup.new_tag('div', attrs={'class': 'blog-post-conclusion'})
            # Add h2 heading
            h2 = soup.new_tag('h2')
            h2.string = 'Conclusion'
            conclusion_div.append(h2)
            # Parse and add conclusion content
            conclusion_soup = BeautifulSoup(post_data['conclusion'], 'html.parser')
            for element in conclusion_soup.children:
                if element.name:
                    conclusion_div.append(element)
            blog_content.append(conclusion_div)
    
    # Fix image paths in navigation and footer (posts are in blog/ subdirectory)
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src.startswith('imgs/'):
            img['src'] = '../' + src
    
    # Fix navigation links (posts are in blog/ subdirectory)
    for link in soup.find_all('a'):
        href = link.get('href', '')
        if href == 'index.html' or href.startswith('index.html#'):
            link['href'] = '../' + href
        elif href == 'insights.html':
            link['href'] = '../insights.html'
    
    return str(soup)


def update_index_html(index_path, posts):
    """Update index.html with blog posts."""
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Sort posts by date (most recent first)
    sorted_posts = sorted(posts, key=lambda x: x['sort_date'], reverse=True)
    
    # Update featured insight card (most recent post)
    if sorted_posts:
        featured_card = soup.find('div', class_='featured-insight-card')
        if featured_card:
            post = sorted_posts[0]
            
            # Update image
            image_placeholder = featured_card.find('div', class_='featured-image-placeholder')
            if image_placeholder:
                if post['first_image']:
                    # Replace SVG with actual image
                    image_placeholder.clear()
                    img_tag = soup.new_tag('img', src=post['first_image'], alt=post['title'], 
                                          attrs={'class': 'featured-image'})
                    image_placeholder.append(img_tag)
                # If no image, keep the SVG placeholder as-is
            
            # Update title
            title_elem = featured_card.find('h3', class_='featured-card-title')
            if title_elem:
                title_elem.string = post['title']
            
            # Update date
            date_elem = featured_card.find('span', class_='featured-card-date')
            if date_elem:
                date_elem.string = post['date']
            
            # Update link
            link_elem = featured_card.find('a', class_='featured-read-more')
            if link_elem:
                link_elem['href'] = f"blog/{post['filename']}.html"
    
    # Update regular insights (next 3 posts)
    regular_container = soup.find('div', class_='regular-insights-container')
    if regular_container:
        # Clear existing insight cards
        regular_container.clear()
        
        # Add up to 3 more posts
        for post in sorted_posts[1:4]:
            # Create insight card
            card = soup.new_tag('div', attrs={'class': 'insight-card'})
            
            # Image div
            image_div = soup.new_tag('div', attrs={'class': 'insight-card-image'})
            if post['first_image']:
                img_tag = soup.new_tag('img', src=post['first_image'], alt=post['title'])
                image_div.append(img_tag)
            else:
                # Use placeholder SVG
                svg = soup.new_tag('svg', width='32', height='32', viewBox='0 0 24 24', 
                                  fill='none', xmlns='http://www.w3.org/2000/svg')
                path1 = soup.new_tag('path', d='M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z', 
                                    stroke='white', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')
                path2 = soup.new_tag('path', d='M9 22V12H15V22', 
                                    stroke='white', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')
                svg.append(path1)
                svg.append(path2)
                image_div.append(svg)
            card.append(image_div)
            
            # Content div
            content_div = soup.new_tag('div', attrs={'class': 'insight-card-content'})
            
            # Title
            title_h4 = soup.new_tag('h4', attrs={'class': 'insight-card-title'})
            title_h4.string = post['title']
            content_div.append(title_h4)
            
            # Meta div
            meta_div = soup.new_tag('div', attrs={'class': 'insight-card-meta'})
            
            # Date
            date_span = soup.new_tag('span', attrs={'class': 'insight-card-date'})
            date_span.string = post['date']
            meta_div.append(date_span)
            
            # Read more link
            read_more = soup.new_tag('a', href=f"blog/{post['filename']}.html", 
                                     attrs={'class': 'insight-read-more'})
            read_more.string = 'Read More'
            meta_div.append(read_more)
            
            content_div.append(meta_div)
            card.append(content_div)
            
            regular_container.append(card)
    
    # Update footer blog posts (3 most recent)
    footer_posts = soup.find('div', class_='footer-blog-posts')
    if footer_posts:
        footer_posts.clear()
        
        for post in sorted_posts[:3]:
            footer_post = soup.new_tag('div', attrs={'class': 'footer-blog-post'})
            
            # Title
            title_h4 = soup.new_tag('h4', attrs={'class': 'footer-blog-title'})
            title_h4.string = post['title']
            footer_post.append(title_h4)
            
            # Meta
            meta_div = soup.new_tag('div', attrs={'class': 'footer-blog-meta'})
            
            date_span = soup.new_tag('span', attrs={'class': 'footer-blog-date'})
            date_span.string = post['date']
            meta_div.append(date_span)
            
            read_more = soup.new_tag('a', href=f"blog/{post['filename']}.html", 
                                     attrs={'class': 'footer-blog-link'})
            read_more.string = 'Read More'
            meta_div.append(read_more)
            
            footer_post.append(meta_div)
            footer_posts.append(footer_post)
    
    # Write updated HTML
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))


def update_insights_html(insights_path, posts):
    """Update insights.html with all blog posts."""
    with open(insights_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Sort posts by date (most recent first)
    sorted_posts = sorted(posts, key=lambda x: x['sort_date'], reverse=True)
    
    # Update insights list grid
    grid = soup.find('div', class_='insights-list-grid')
    if grid:
        grid.clear()
        
        for post in sorted_posts:
            # Create card
            card = soup.new_tag('div', attrs={'class': 'insights-list-card'})
            
            # Image div
            image_div = soup.new_tag('div', attrs={'class': 'insights-list-card-image'})
            if post['first_image']:
                img_tag = soup.new_tag('img', src=post['first_image'], alt=post['title'])
                image_div.append(img_tag)
            else:
                # Use placeholder SVG
                svg = soup.new_tag('svg', width='48', height='48', viewBox='0 0 24 24', 
                                  fill='none', xmlns='http://www.w3.org/2000/svg')
                path1 = soup.new_tag('path', d='M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z', 
                                    stroke='white', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')
                path2 = soup.new_tag('path', d='M9 22V12H15V22', 
                                    stroke='white', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')
                svg.append(path1)
                svg.append(path2)
                image_div.append(svg)
            card.append(image_div)
            
            # Content div
            content_div = soup.new_tag('div', attrs={'class': 'insights-list-card-content'})
            
            # Title
            title_h3 = soup.new_tag('h3', attrs={'class': 'insights-list-card-title'})
            title_h3.string = post['title']
            content_div.append(title_h3)
            
            # Meta div
            meta_div = soup.new_tag('div', attrs={'class': 'insights-list-card-meta'})
            
            # Date
            date_span = soup.new_tag('span', attrs={'class': 'insights-list-card-date'})
            date_span.string = post['date']
            meta_div.append(date_span)
            
            # Read more link
            read_more = soup.new_tag('a', href=f"blog/{post['filename']}.html", 
                                     attrs={'class': 'insights-list-read-more'})
            read_more.string = 'Read More'
            meta_div.append(read_more)
            
            content_div.append(meta_div)
            card.append(content_div)
            
            grid.append(card)
    
    # Update footer blog posts (3 most recent)
    footer_posts = soup.find('div', class_='footer-blog-posts')
    if footer_posts:
        footer_posts.clear()
        
        for post in sorted_posts[:3]:
            footer_post = soup.new_tag('div', attrs={'class': 'footer-blog-post'})
            
            # Title
            title_h4 = soup.new_tag('h4', attrs={'class': 'footer-blog-title'})
            title_h4.string = post['title']
            footer_post.append(title_h4)
            
            # Meta
            meta_div = soup.new_tag('div', attrs={'class': 'footer-blog-meta'})
            
            date_span = soup.new_tag('span', attrs={'class': 'footer-blog-date'})
            date_span.string = post['date']
            meta_div.append(date_span)
            
            read_more = soup.new_tag('a', href=f"blog/{post['filename']}.html", 
                                     attrs={'class': 'footer-blog-link'})
            read_more.string = 'Read More'
            meta_div.append(read_more)
            
            footer_post.append(meta_div)
            footer_posts.append(footer_post)
    
    # Write updated HTML
    with open(insights_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))


def main():
    """Main function to build blog."""
    # Get script directory
    script_dir = Path(__file__).parent
    blog_md_dir = script_dir / 'blog_md'
    blog_dir = script_dir / 'blog'
    template_path = script_dir / 'blog_post.html'
    index_path = script_dir / 'index.html'
    insights_path = script_dir / 'insights.html'
    
    # Create blog directory if it doesn't exist
    blog_dir.mkdir(exist_ok=True)
    
    # Find all markdown files
    md_files = list(blog_md_dir.glob('*.md'))
    
    if not md_files:
        print("No markdown files found in blog_md/ directory")
        return
    
    # Parse all markdown files
    posts = []
    for md_file in md_files:
        print(f"Processing {md_file.name}...")
        post_data = parse_markdown_file(md_file)
        posts.append(post_data)
        
        # Generate HTML blog post
        html_content = generate_blog_post_html(template_path, post_data)
        
        # Save to blog directory
        output_path = blog_dir / f"{post_data['filename']}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  Generated {output_path}")
    
    # Update index.html
    print("Updating index.html...")
    update_index_html(index_path, posts)
    
    # Update insights.html
    print("Updating insights.html...")
    update_insights_html(insights_path, posts)
    
    print(f"\nDone! Processed {len(posts)} blog posts.")


if __name__ == '__main__':
    main()

