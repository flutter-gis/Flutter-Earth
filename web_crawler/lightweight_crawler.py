#!/usr/bin/env python3
"""
Local HTML Data Extractor - Extracts ALL information from local HTML files
Saves each page as individual JSON files with thumbnails for later classification
"""

import os
import sys
import json
import time
import threading
import warnings
import re
import gc
import psutil
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCore import Qt
import requests
import html
import faulthandler
import logging
from logging.handlers import RotatingFileHandler
import pathlib

# Enable fault handler to capture hard crashes
try:
    crash_log_path = os.path.join(os.path.dirname(__file__), 'lightweight_crash.log')
    _fh = open(crash_log_path, 'w', buffering=1, encoding='utf-8')
    faulthandler.enable(file=_fh)
except Exception:
    pass

# Global exception hook to log uncaught exceptions
def _log_excepthook(exctype, value, tb):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'lightweight_errors.log'), 'a', encoding='utf-8') as ef:
            ef.write(f"[{datetime.now().isoformat()}] Uncaught: {exctype.__name__}: {value}\n")
    except Exception:
        pass
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = _log_excepthook

# Configure comprehensive logging
_logs_dir = pathlib.Path(os.path.join(os.path.dirname(__file__), 'logs'))
_logs_dir.mkdir(parents=True, exist_ok=True)

_logger = logging.getLogger('lightweight')
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(message)s')
    file_handler = RotatingFileHandler(_logs_dir / 'app.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(fmt)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

def _log_json(event_type: str, **kwargs):
    try:
        record = {
            'ts': datetime.now().isoformat(),
            'event': event_type,
            **kwargs
        }
        with open(_logs_dir / 'structured.log', 'a', encoding='utf-8') as jf:
            jf.write(json.dumps(record, ensure_ascii=False) + '\n')
    except Exception:
        pass

# Suppress warnings
warnings.filterwarnings('ignore')

class LocalHTMLDataExtractor:
    """Extracts ALL data from local HTML files without external requests"""
    
    def __init__(self):
        # Create output directory for JSON files
        self.output_dir = "collected_data"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Create thumbnails directory
        self.thumbnails_dir = os.path.join(self.output_dir, "thumbnails")
        if not os.path.exists(self.thumbnails_dir):
            os.makedirs(self.thumbnails_dir)
        
        # Network session and defaults for link-following
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        # Log all HTTP responses
        def _resp_hook(resp, *args, **kwargs):
            try:
                _logger.info(f"HTTP {resp.status_code} {resp.request.method} {resp.url} ({resp.elapsed.total_seconds():.3f}s)")
                _log_json('http_response', status=resp.status_code, method=resp.request.method, url=resp.url, elapsed_ms=int(resp.elapsed.total_seconds()*1000))
            except Exception:
                pass
            return resp
        self.session.hooks['response'] = [ _resp_hook ]
        self.config = {
            'performance': {'timeout': 15, 'request_delay': 0.5},
            'processing': {'batch_size': 10}
        }
    
    def extract_all_data(self, soup, file_path, progress_callback=None, log_callback=None):
        """Extract satellite catalog data from HTML file"""
        print(f"🔍 Starting satellite catalog extraction from: {os.path.basename(file_path)}")
        _logger.info(f"extract_all_data:start file={file_path}")
        
        try:
            data = {
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'title': '',
                'satellite_catalog': {},
                'catalog_links': [],
                'thumbnails': [],
                'extraction_metadata': {}
            }
            
            print("📋 Extracting satellite catalog data...")
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                data['title'] = title_tag.get_text().strip()
                print(f"   📝 Title: {data['title'][:50]}...")
                _logger.info(f"title: {data['title']}")
            
            # Extract catalog links (thumbnails with satellite data)
            print("🛰️ Extracting satellite catalog links with smart classification...")
            catalog_links = []
            
            try:
                # Look for catalog grid containers first
                catalog_containers = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'catalog|grid|item|dataset|collection'))
                
                if catalog_containers:
                    print(f"     🎯 Found {len(catalog_containers)} catalog containers")
                    for container in catalog_containers:
                        self.extract_links_from_container(container, catalog_links)
                else:
                    # Fallback to general link extraction
                    print("     🔍 No catalog containers found, using general link extraction")
                    self.extract_links_generally(soup, catalog_links)
            except re.error as e:
                print(f"     ⚠️ Regex error in catalog container search: {e}")
                # Fallback to general link extraction
                print("     🔍 Using fallback link extraction due to regex error")
                self.extract_links_generally(soup, catalog_links)
            
            data['catalog_links'] = catalog_links
            print(f"   📊 Found {len(catalog_links)} catalog links")
            _log_json('catalog_links', file=file_path, count=len(catalog_links))
            
            # Classify catalog links by type
            try:
                self.classify_catalog_links(catalog_links)
            except Exception as e:
                print(f"     ⚠️ Error in link classification: {e}")
                _logger.exception("link_classification_error")
            
            # Extract satellite catalog data using smart extraction
            print("🌍 Starting smart satellite catalog data extraction...")
            try:
                data['satellite_catalog'] = self.extract_satellite_data(soup, data)
                print("✅ Smart satellite catalog data extraction completed")
                _log_json('satellite_data_extracted', completeness=len(data['satellite_catalog']))
            except Exception as e:
                print(f"     ⚠️ Error in satellite data extraction: {e}")
                data['satellite_catalog'] = {}
                _logger.exception("satellite_data_extraction_error")
            
            # Now follow individual dataset links to extract detailed information
            if catalog_links:
                try:
                    # Keep only dataset detail links
                    detail_links = [l for l in catalog_links if l.get('link_type') == 'dataset_detail']
                    print(f"🔗 Following {len(detail_links)} dataset detail links to extract detailed information...")
                    _log_json('detail_links', file=file_path, count=len(detail_links))
                    detailed_extractions = 0
                    
                    # Process ALL detail links - no artificial limits
                    for i, link in enumerate(detail_links):
                        if progress_callback:
                            # Update progress: 50% for initial extraction, 50% for dataset processing
                            progress = 50 + (i / len(detail_links)) * 50
                            progress_callback(progress)
                        if log_callback:
                            log_callback(f"Processing dataset {i+1}/{len(detail_links)}: {link['text'][:80]}")
                        
                        print(f"     🔍 Processing dataset {i+1}/{len(detail_links)}: {link['text'][:50]}...")
                        
                        try:
                            # Extract detailed data from this dataset link
                            detailed_data = self.extract_from_dataset_link(link, soup)
                            if detailed_data:
                                # Add to satellite catalog
                                if 'satellite_catalog' not in data:
                                    data['satellite_catalog'] = {}
                                
                                # Merge detailed data
                                for key, value in detailed_data.items():
                                    if value and value != 'Unknown':
                                        data['satellite_catalog'][key] = value
                                
                                detailed_extractions += 1
                                print(f"       ✅ Extracted detailed data for: {link['text'][:30]}...")
                                _log_json('detail_extracted', href=link.get('href', ''), text=link.get('text', '')[:120])
                            else:
                                print(f"       ⚠️ No detailed data found for: {link['text'][:30]}...")
                        except Exception as e:
                            print(f"       ⚠️ Error processing dataset link: {e}")
                            continue
                    
                    print(f"🎯 Completed detailed extraction of {detailed_extractions} datasets")
                    if progress_callback:
                        progress_callback(100)
                except Exception as e:
                    print(f"     ⚠️ Error in dataset link processing: {e}")
                    _logger.exception("dataset_link_processing_error")
            
            # Generate extraction summary
            if catalog_links:
                try:
                    summary = self.generate_extraction_summary(catalog_links, data['satellite_catalog'])
                    data['extraction_summary'] = summary
                    print(f"   📋 Smart Extraction Summary:")
                    print(f"      • Total links discovered: {summary['total_links_discovered']}")
                    print(f"      • Junk links filtered: {summary['junk_links_filtered']}")
                    print(f"      • Clean catalog links: {summary['total_links']}")
                    print(f"      • Links by type: {', '.join([f'{k}: {v}' for k, v in summary['links_by_type'].items()])}")
                    print(f"      • Confidence: {summary['extraction_confidence']}")
                    print(f"      • Completeness: {summary['data_completeness']:.1f}%")
                    print(f"      • Quality: {summary['extraction_quality']}")
                    if summary['junk_examples']:
                        print(f"      • Junk examples: {', '.join(summary['junk_examples'][:3])}")
                    if summary['recommendations']:
                        print(f"      • Recommendations: {', '.join(summary['recommendations'][:2])}")
                    _log_json('extraction_summary', **summary)
                except Exception as e:
                    print(f"     ⚠️ Error generating extraction summary: {e}")
                    data['extraction_summary'] = {}
                    _logger.exception("summary_error")
            
            return data
            
        except Exception as e:
            print(f"❌ Critical error in extract_all_data: {e}")
            _logger.exception("extract_all_data_critical_error")
            # Return minimal data structure
            return {
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'title': 'Extraction Failed',
                'satellite_catalog': {},
                'catalog_links': [],
                'thumbnails': [],
                'extraction_metadata': {'error': str(e)}
            }
    
    def extract_links_from_container(self, container, catalog_links):
        """Extract links from a catalog container with smart classification"""
        # Look for links within the container
        links = container.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Skip navigation and utility links
            if self.is_navigation_link(href, text):
                continue
            
            # Check if this is a dataset link
            if self.is_dataset_link(href, text):
                # Find associated thumbnail
                thumbnail = self.find_thumbnail_for_link(link, container)
                
                catalog_link = {
                    'text': text,
                    'href': href,
                    'title': link.get('title', ''),
                    'thumbnail': thumbnail,
                    'is_catalog_item': True,
                    'link_type': self.classify_link_type(href, text),
                    'extraction_priority': self.calculate_link_priority(href, text)
                }
                catalog_links.append(catalog_link)
    
    def extract_links_generally(self, soup, catalog_links):
        """Extract links using general patterns when no containers found"""
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Look for satellite/dataset links
            if any(keyword in href.lower() for keyword in ['dataset', 'catalog', 'satellite', 'collection', 'product']):
                # Find associated thumbnail
                thumbnail = self.find_thumbnail_for_link(link, soup)
                
                catalog_link = {
                    'text': text,
                    'href': href,
                    'title': link.get('title', ''),
                    'thumbnail': thumbnail,
                    'is_catalog_item': True,
                    'link_type': self.classify_link_type(href, text),
                    'extraction_priority': self.calculate_link_priority(href, text)
                }
                catalog_links.append(catalog_link)
    
    def is_navigation_link(self, href, text):
        """Check if a link is navigation/utility rather than dataset content"""
        navigation_keywords = [
            'home', 'about', 'contact', 'help', 'support', 'login', 'signup',
            'documentation', 'api', 'tutorial', 'forum', 'blog', 'news',
            'privacy', 'terms', 'cookies', 'feedback', 'report'
        ]
        
        # Check href for navigation patterns
        if any(keyword in href.lower() for keyword in navigation_keywords):
            return True
        
        # Check text for navigation patterns
        if any(keyword in text.lower() for keyword in navigation_keywords):
            return True
        
        # Check for common navigation patterns
        if href.startswith('#') or href == '/' or href == '':
            return True
        
        # Check for social media and external junk links
        if self.is_social_media_link(href, text):
            return True
        
        # Check for utility and non-content links
        if self.is_utility_link(href, text):
            return True
        
        return False
    
    def is_social_media_link(self, href, text):
        """Check if a link is social media or external junk"""
        social_media_patterns = [
            'facebook.com', 'twitter.com', 'x.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'reddit.com', 'github.com', 'stackoverflow.com',
            'medium.com', 'dev.to', 'hashnode.dev', 'substack.com',
            'discord.com', 'slack.com', 'telegram.org', 'whatsapp.com',
            'tiktok.com', 'snapchat.com', 'pinterest.com', 'tumblr.com'
        ]
        
        # Check href for social media domains
        if any(domain in href.lower() for domain in social_media_patterns):
            return True
        
        # Check for social media icons/text
        social_indicators = [
            'follow us', 'like us', 'share', 'tweet', 'post', 'comment',
            'social', 'community', 'connect', 'join us', 'subscribe'
        ]
        
        if any(indicator in text.lower() for indicator in social_indicators):
            return True
        
        return False
    
    def is_utility_link(self, href, text):
        """Check if a link is utility/non-content"""
        utility_patterns = [
            'javascript:', 'mailto:', 'tel:', 'sms:', 'ftp://',
            'chrome://', 'about:', 'data:', 'file://', 'view-source:'
        ]
        
        # Check for utility protocols
        if any(pattern in href.lower() for pattern in utility_patterns):
            return True
        
        # Check for utility text
        utility_indicators = [
            'print', 'download', 'export', 'save', 'bookmark', 'favorite',
            'share', 'email', 'copy link', 'permalink', 'qr code',
            'accessibility', 'language', 'translate', 'search', 'filter',
            'sort', 'refresh', 'reload', 'back', 'forward', 'close'
        ]
        
        if any(indicator in text.lower() for indicator in utility_indicators):
            return True
        
        return False
    
    def is_dataset_link(self, href, text):
        """Check if a link points to a dataset/satellite page"""
        dataset_keywords = [
            'dataset', 'catalog', 'satellite', 'collection', 'product', 'layer',
            'imagery', 'data', 'coverage', 'temporal', 'spatial'
        ]
        
        # Check href for dataset patterns
        if any(keyword in href.lower() for keyword in dataset_keywords):
            return True
        
        # Check text for dataset patterns
        if any(keyword in text.lower() for keyword in dataset_keywords):
            return True
        
        # Check for Earth Engine specific patterns
        if '/datasets/' in href or '/collections/' in href:
            return True
        
        return False
    
    def find_thumbnail_for_link(self, link, container):
        """Find thumbnail image associated with a link"""
        thumbnail = None
        
        # Look for thumbnail in the link itself
        thumbnail = link.find('img')
        if thumbnail:
            return {
                'src': thumbnail.get('src', ''),
                'alt': thumbnail.get('alt', ''),
                'title': thumbnail.get('title', ''),
                'width': thumbnail.get('width', ''),
                'height': thumbnail.get('height', '')
            }
        
        # Look for thumbnail in parent container
        parent = link.parent
        if parent:
            thumbnail = parent.find('img')
            if thumbnail:
                return {
                    'src': thumbnail.get('src', ''),
                    'alt': thumbnail.get('alt', ''),
                    'title': thumbnail.get('title', ''),
                    'width': thumbnail.get('width', ''),
                    'height': thumbnail.get('height', '')
                }
        
        # Look for thumbnail in sibling elements
        siblings = link.find_next_siblings()
        for sibling in siblings:
            if sibling.name == 'img':
                return {
                    'src': sibling.get('src', ''),
                    'alt': sibling.get('alt', ''),
                    'title': sibling.get('title', ''),
                    'width': sibling.get('width', ''),
                    'height': sibling.get('height', '')
                }
        
        return None
    
    def classify_link_type(self, href, text):
        """Classify the type of catalog link"""
        href_lower = href.lower()
        text_lower = text.lower()
        
        # Satellite/Platform links
        if any(word in href_lower for word in ['satellite', 'platform', 'sensor', 'instrument']):
            return 'satellite_info'
        
        # Dataset/Collection links (prefer catalog pages, exclude tag/tag-like pages)
        if ('/datasets/catalog/' in href_lower) or any(word in href_lower for word in ['dataset', 'collection', 'product']):
            if '/datasets/tags/' in href_lower or '/tags/' in href_lower:
                return 'tag_page'
            return 'dataset_detail'
        
        # Imagery/Data links
        if any(word in href_lower for word in ['imagery', 'data', 'coverage']):
            return 'data_coverage'
        
        # Documentation links
        if any(word in href_lower for word in ['docs', 'documentation', 'guide', 'tutorial']):
            return 'documentation'
        
        # API/Technical links
        if any(word in href_lower for word in ['api', 'code', 'example', 'snippet']):
            return 'technical'
        
        return 'general'
    
    def calculate_link_priority(self, href, text):
        """Calculate extraction priority for a link"""
        priority = 0
        
        # High priority for dataset/collection links
        if any(word in href.lower() for word in ['dataset', 'collection', 'product']):
            priority += 10
        
        # High priority for satellite/sensor links
        if any(word in href.lower() for word in ['satellite', 'sensor', 'instrument']):
            priority += 8
        
        # Medium priority for imagery/data links
        if any(word in href.lower() for word in ['imagery', 'data', 'coverage']):
            priority += 6
        
        # Lower priority for documentation
        if any(word in href.lower() for word in ['docs', 'documentation', 'guide']):
            priority += 3
        
        # Bonus for Earth Engine specific URLs
        if '/datasets/' in href or '/collections/' in href:
            priority += 5
        
        return priority
    
    def classify_catalog_links(self, catalog_links):
        """Classify and organize catalog links by type and priority - Enhanced junk filtering"""
        if not catalog_links:
            return
        
        # Filter out junk links before classification
        print("     🧹 Filtering out junk links...")
        junk_links = []
        clean_links = []
        
        for link in catalog_links:
            href = link.get('href', '')
            text = link.get('text', '')
            
            if self.is_junk_link(href, text):
                junk_links.append(link)
            else:
                clean_links.append(link)
        
        # Report junk filtering results
        print(f"     🗑️ Filtered out {len(junk_links)} junk links")
        print(f"     ✨ Kept {len(clean_links)} clean catalog links")
        
        if junk_links:
            print("     📋 Junk link examples:")
            for junk in junk_links[:5]:  # Show first 5 junk examples
                print(f"        • {junk['text'][:50]}... ({junk['href'][:50]}...)")
        
        # Sort clean links by priority
        clean_links.sort(key=lambda x: x.get('extraction_priority', 0), reverse=True)
        
        # Group by type
        link_types = {}
        for link in clean_links:
            link_type = link.get('link_type', 'general')
            if link_type not in link_types:
                link_types[link_type] = []
            link_types[link_type].append(link)
        
        # Print classification summary
        print("     🏷️ Clean catalog link classification:")
        for link_type, links in link_types.items():
            print(f"       • {link_type.title()}: {len(links)} links")
        
        # Print high-priority links
        high_priority = [link for link in clean_links if link.get('extraction_priority', 0) >= 8]
        if high_priority:
            print(f"     ⭐ High-priority clean links ({len(high_priority)}):")
            for link in high_priority[:5]:  # Show first 5
                print(f"       • {link['text'][:50]}... (Priority: {link['extraction_priority']})")
        
        # Update the catalog_links list to only contain clean links
        catalog_links.clear()
        catalog_links.extend(clean_links)
    
    def is_junk_link(self, href, text):
        """Comprehensive junk link detection - Less aggressive to capture all datasets"""
        # Only filter out obviously non-dataset links
        # Check for all types of junk
        if self.is_navigation_link(href, text):
            return True
        
        if self.is_social_media_link(href, text):
            return True
        
        if self.is_utility_link(href, text):
            return True
        
        # Only filter external junk if it's clearly not a dataset
        if self.is_external_junk_domain(href) and not self.looks_like_dataset_link(href, text):
            return True
        
        # Don't filter out links that might be datasets
        if self.is_clearly_not_dataset(href, text):
            return False  # Changed from True to False - be less aggressive
        
        # Don't filter out advertisement/tracking if they might be dataset links
        if self.is_advertisement_link(href, text) and not self.looks_like_dataset_link(href, text):
            return True
        
        if self.is_tracking_link(href, text) and not self.looks_like_dataset_link(href, text):
            return True
        
        if self.is_broken_link(href, text):
            return True
        
        return False
    
    def is_advertisement_link(self, href, text):
        """Check if a link is an advertisement"""
        ad_patterns = [
            'ad', 'advertisement', 'sponsor', 'sponsored', 'promotion',
            'banner', 'click', 'offer', 'deal', 'discount', 'sale',
            'affiliate', 'referral', 'tracking', 'analytics'
        ]
        
        # Check href for ad patterns
        if any(pattern in href.lower() for pattern in ad_patterns):
            return True
        
        # Check text for ad patterns
        if any(pattern in text.lower() for pattern in ad_patterns):
            return True
        
        return False
    
    def is_tracking_link(self, href, text):
        """Check if a link is a tracking/analytics link"""
        tracking_patterns = [
            'utm_', 'gclid', 'fbclid', 'msclkid', 'ref_',
            'source=', 'medium=', 'campaign=', 'term=', 'content=',
            'tracking', 'analytics', 'pixel', 'beacon', 'tag'
        ]
        
        # Check href for tracking parameters
        if any(pattern in href.lower() for pattern in tracking_patterns):
            return True
        
        return False
    
    def is_broken_link(self, href, text):
        """Check if a link appears to be broken"""
        broken_patterns = [
            'javascript:void(0)', 'javascript:;', '#', 'javascript:',
            'mailto:', 'tel:', 'sms:', 'ftp://', 'chrome://',
            'about:', 'data:', 'file://', 'view-source:'
        ]
        
        # Check for broken link patterns
        if any(pattern in href.lower() for pattern in broken_patterns):
            return True
        
        # Check for empty or placeholder links
        if not href or href.strip() == '' or href.strip() == '#':
            return True
        
        return False
    
    def save_local_image_reference(self, img_src, base_file_path):
        """Save reference to local image (don't download external ones)"""
        try:
            # Only process local image references
            if img_src.startswith('http'):
                return None
            
            # Generate filename for reference
            filename = f"local_img_{int(time.time() * 1000)}_{hash(img_src) % 10000}.txt"
            filepath = os.path.join(self.thumbnails_dir, filename)
            
            # Save image reference info
            img_info = {
                'original_src': img_src,
                'base_file': base_file_path,
                'timestamp': datetime.now().isoformat(),
                'note': 'Local image reference - not downloaded'
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(img_info, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            print(f"Failed to save local image reference {img_src}: {e}")
            return None
    
    def save_data_to_json(self, data, file_path):
        """Save extracted data to individual JSON file"""
        try:
            # Create safe filename from file path
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', os.path.basename(file_path))
            safe_filename = safe_filename[:200]  # Limit length
            
            # Add timestamp to ensure uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{safe_filename}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            _logger.info(f"save_json:start path={filepath}")
            _log_json('save_json_start', file=file_path, out=filepath)
            
            # Save to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            _logger.info(f"save_json:done path={filepath}")
            _log_json('save_json_done', out=filepath, size_bytes=os.path.getsize(filepath))
            return filepath
            
        except Exception as e:
            print(f"Failed to save data for {file_path}: {e}")
            try:
                _logger.exception("save_json_error")
                _log_json('save_json_error', file=file_path, error=str(e))
            except Exception:
                pass
            return None

    def save_satellite_catalog_data(self, satellite_data, satellite_name):
        """Save satellite catalog data organized by satellite"""
        try:
            # Create satellite catalog file
            catalog_file = os.path.join(self.output_dir, "satellite_catalog.json")
            
            # Load existing catalog if it exists
            existing_catalog = {}
            if os.path.exists(catalog_file):
                try:
                    with open(catalog_file, 'r', encoding='utf-8') as f:
                        existing_catalog = json.load(f)
                except:
                    existing_catalog = {}
            
            # Add or update satellite data
            if satellite_name not in existing_catalog:
                existing_catalog[satellite_name] = []
            
            # Add timestamp to the data
            satellite_data['extraction_timestamp'] = datetime.now().isoformat()
            existing_catalog[satellite_name].append(satellite_data)
            
            # Save updated catalog
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(existing_catalog, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved satellite data for {satellite_name} to catalog")
            return catalog_file
            
        except Exception as e:
            print(f"Failed to save satellite catalog data for {satellite_name}: {e}")
            return None

    def categorize_content(self, soup, data):
        """Categorize content into meaningful groups"""
        print("   🏷️ Categorizing content into groups...")
        
        categories = {
            'navigation': [],
            'main_content': [],
            'sidebar': [],
            'footer': [],
            'header': [],
            'metadata': [],
            'interactive_elements': [],
            'media_content': [],
            'data_tables': [],
            'forms_and_inputs': []
        }
        
        # Categorize links by purpose
        print("     🔗 Categorizing links...")
        for link in data['links']:
            link_text = link.get('text', '').lower()
            href = link.get('href', '').lower()
            
            if any(word in link_text for word in ['home', 'main', 'index', 'start']):
                categories['navigation'].append(link)
            elif any(word in href for word in ['nav', 'menu', 'navigation']):
                categories['navigation'].append(link)
            elif any(word in link_text for word in ['contact', 'about', 'help', 'support']):
                categories['footer'].append(link)
            elif any(word in link_text for word in ['login', 'sign', 'register', 'submit']):
                categories['interactive_elements'].append(link)
            else:
                categories['main_content'].append(link)
        
        print(f"       📊 Navigation: {len(categories['navigation'])} links")
        print(f"       📊 Main content: {len(categories['main_content'])} links")
        print(f"       📊 Footer: {len(categories['footer'])} links")
        print(f"       📊 Interactive: {len(categories['interactive_elements'])} links")
        
        # Categorize images by type
        print("     🖼️ Categorizing images...")
        for img in data['images']:
            img_src = img.get('src', '').lower()
            alt_text = img.get('alt', '').lower()
            
            if any(word in alt_text for word in ['logo', 'brand', 'header']):
                categories['header'].append(img)
            elif any(word in alt_text for word in ['icon', 'button', 'arrow']):
                categories['navigation'].append(img)
            elif any(word in img_src for word in ['chart', 'graph', 'diagram']):
                categories['data_tables'].append(img)
            else:
                categories['media_content'].append(img)
        
        print(f"       📊 Header images: {len(categories['header'])}")
        print(f"       📊 Navigation images: {len(categories['navigation'])}")
        print(f"       📊 Data images: {len(categories['data_tables'])}")
        print(f"       📊 Media images: {len(categories['media_content'])}")
        
        # Categorize forms
        categories['forms_and_inputs'] = data['forms']
        print(f"     📝 Forms: {len(categories['forms_and_inputs'])}")
        
        # Categorize tables
        categories['data_tables'] = data['tables']
        print(f"     📊 Tables: {len(categories['data_tables'])}")
        
        # Categorize headings by hierarchy
        print("     🎯 Categorizing headings...")
        for heading in data['headings']:
            if heading.get('level') in ['h1', 'h2']:
                categories['header'].append(heading)
            elif heading.get('level') in ['h3', 'h4']:
                categories['main_content'].append(heading)
            else:
                categories['sidebar'].append(heading)
        
        print(f"       📊 Header headings: {len([h for h in categories['header'] if isinstance(h, dict) and h.get('level') in ['h1', 'h2']])}")
        print(f"       📊 Main headings: {len([h for h in categories['main_content'] if isinstance(h, dict) and h.get('level') in ['h3', 'h4']])}")
        print(f"       📊 Sidebar headings: {len([h for h in categories['sidebar'] if isinstance(h, dict) and h.get('level') not in ['h1', 'h2', 'h3', 'h4']])}")
        
        print("   ✅ Content categorization completed")
        return categories
    
    def analyze_semantics(self, soup, data):
        """Analyze semantic meaning of content"""
        semantics = {
            'topics': [],
            'keywords': [],
            'entities': [],
            'sentiment': 'neutral',
            'language': 'en',
            'content_type': 'unknown',
            'subject_matter': 'general'
        }
        
        # Extract keywords from text
        text = data['raw_text'].lower()
        words = re.findall(r'\b\w+\b', text)
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        semantics['keywords'] = [word for word, freq in sorted_words[:20]]
        
        # Detect content type
        if any(word in text for word in ['dataset', 'catalog', 'earth engine', 'satellite']):
            semantics['content_type'] = 'earth_engine_data'
            semantics['subject_matter'] = 'geospatial_data'
        elif any(word in text for word in ['tutorial', 'guide', 'help', 'documentation']):
            semantics['content_type'] = 'documentation'
            semantics['subject_matter'] = 'educational'
        elif any(word in text for word in ['api', 'reference', 'endpoint', 'parameter']):
            semantics['content_type'] = 'api_reference'
            semantics['subject_matter'] = 'technical'
        
        # Detect language (simple detection)
        if any(word in text for word in ['the', 'and', 'for', 'with']):
            semantics['language'] = 'en'
        
        return semantics
    
    # Old analyze_structure method removed - no longer needed for satellite catalog extraction
    
    def generate_content_summary(self, data):
        """Generate comprehensive content summary"""
        summary = {
            'total_elements': 0,
            'content_distribution': {},
            'richness_score': 0,
            'interactivity_level': 'low',
            'media_richness': 'low',
            'data_density': 'low',
            'overall_complexity': 'simple'
        }
        
        # Calculate total elements
        summary['total_elements'] = (
            len(data['links']) + 
            len(data['images']) + 
            len(data['forms']) + 
            len(data['tables']) + 
            len(data['lists']) + 
            len(data['headings']) + 
            len(data['paragraphs'])
        )
        
        # Content distribution
        summary['content_distribution'] = {
            'text_content': len(data['paragraphs']) + len(data['headings']),
            'interactive_elements': len(data['forms']) + len(data['links']),
            'media_elements': len(data['images']),
            'data_structures': len(data['tables']) + len(data['lists'])
        }
        
        # Calculate richness scores
        if summary['total_elements'] > 100:
            summary['overall_complexity'] = 'very_complex'
        elif summary['total_elements'] > 50:
            summary['overall_complexity'] = 'complex'
        elif summary['total_elements'] > 20:
            summary['overall_complexity'] = 'moderate'
        else:
            summary['overall_complexity'] = 'simple'
        
        # Media richness
        if len(data['images']) > 20:
            summary['media_richness'] = 'very_high'
        elif len(data['images']) > 10:
            summary['media_richness'] = 'high'
        elif len(data['images']) > 5:
            summary['media_richness'] = 'moderate'
        else:
            summary['media_richness'] = 'low'
        
        # Interactivity level
        if len(data['forms']) > 5 or len(data['links']) > 50:
            summary['interactivity_level'] = 'very_high'
        elif len(data['forms']) > 2 or len(data['links']) > 25:
            summary['interactivity_level'] = 'high'
        elif len(data['forms']) > 0 or len(data['links']) > 10:
            summary['interactivity_level'] = 'moderate'
        else:
            summary['interactivity_level'] = 'low'
        
        # Data density
        if len(data['tables']) > 5 or len(data['lists']) > 20:
            summary['data_density'] = 'very_high'
        elif len(data['tables']) > 2 or len(data['lists']) > 10:
            summary['data_density'] = 'high'
        elif len(data['tables']) > 0 or len(data['lists']) > 5:
            summary['data_density'] = 'moderate'
        else:
            summary['data_density'] = 'low'
        
        return summary

    def extract_satellite_data(self, soup, data):
        """Extract satellite catalog data with smart classification based on Earth Engine catalog structure"""
        print("   🛰️ Starting smart satellite catalog data extraction...")
        
        satellite_data = {
            'layer_name': '',
            'date_range': {'start': '', 'end': ''},
            'satellites_used': [],
            'location': '',
            'gee_code_snippet': '',
            'thumbnails': [],
            'band_information': [],
            'category_tags': [],
            'dataset_provider': '',
            'pixel_size': '',
            'citations': [],
            'description': '',
            'terms_of_use': '',
            'doi': '',
            'extraction_confidence': 'low',
            'detected_page_type': 'unknown'
        }
        
        # Smart page type detection
        page_type = self.detect_page_type(soup)
        satellite_data['detected_page_type'] = page_type
        print(f"     🎯 Detected page type: {page_type}")
        
        # Extract based on page type
        if page_type == 'catalog_main':
            self.extract_from_catalog_main(soup, satellite_data)
        elif page_type == 'dataset_detail':
            self.extract_from_dataset_detail(soup, satellite_data)
        elif page_type == 'satellite_info':
            self.extract_from_satellite_info(soup, satellite_data)
        else:
            self.extract_generic_data(soup, satellite_data)
        
        # Calculate extraction confidence
        satellite_data['extraction_confidence'] = self.calculate_extraction_confidence(satellite_data)
        
        return satellite_data
    
    def detect_page_type(self, soup):
        """Detect the type of Earth Engine page based on content and structure"""
        text_content = soup.get_text().lower()

        # Prefer canonical URL hints first
        canonical = soup.find('link', rel='canonical')
        if canonical:
            href = canonical.get('href', '')
            if '/earth-engine/datasets/catalog/' in href:
                return 'dataset_detail'
            if '/earth-engine/datasets' in href and href.rstrip('/').endswith('datasets'):
                return 'catalog_main'

        # Dataset detail: look for strong EE detail markers
        dataset_detail_markers = [
            'earth engine snippet',
            'dataset availability',
            'dataset provider',
            'citations',
            'doi',
            'tags',
            'bands',
            'pixel size',
            'resolution',
            'explore with earth engine',
            'open in code editor'
        ]
        if any(marker in text_content for marker in dataset_detail_markers):
            return 'dataset_detail'

        # Dataset detail: presence of ee.* code blocks
        code_blocks = soup.find_all(['pre', 'code'])
        for cb in code_blocks:
            if 'ee.' in cb.get_text():
                return 'dataset_detail'

        # Main catalog indicators (checked after dataset detail to avoid false positives)
        if any(phrase in text_content for phrase in [
            'earth engine data catalog',
            'dataset catalog',
            'satellite catalog',
            'collection catalog'
        ]):
            return 'catalog_main'

        # Satellite information page
        if any(phrase in text_content for phrase in [
            'satellite information',
            'sensor details',
            'instrument details',
            'platform information'
        ]):
            return 'satellite_info'

        return 'unknown'
    
    def extract_from_catalog_main(self, soup, satellite_data):
        """Extract data from main catalog page with thumbnail grid"""
        print("     📋 Extracting from main catalog page...")
        
        # Look for catalog grid items
        catalog_items = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'catalog|item|dataset|collection'))
        
        for item in catalog_items:
            # Extract thumbnail and link
            thumbnail = item.find('img')
            if thumbnail:
                thumbnail_data = {
                    'src': thumbnail.get('src', ''),
                    'alt': thumbnail.get('alt', ''),
                    'title': thumbnail.get('title', ''),
                    'width': thumbnail.get('width', ''),
                    'height': thumbnail.get('height', '')
                }
                satellite_data['thumbnails'].append(thumbnail_data)
            
            # Extract dataset name from heading or link
            heading = item.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if heading:
                satellite_data['layer_name'] = heading.get_text().strip()
                break
            
            # Extract from link text
            link = item.find('a')
            if link and not satellite_data['layer_name']:
                satellite_data['layer_name'] = link.get_text().strip()
        
        # Extract provider from page metadata
        provider_meta = soup.find('meta', attrs={'name': re.compile(r'provider|organization|institution', re.I)})
        if provider_meta:
            satellite_data['dataset_provider'] = provider_meta.get('content', '')
        
        # Extract description from meta description
        desc_meta = soup.find('meta', attrs={'name': 'description'})
        if desc_meta:
            satellite_data['description'] = desc_meta.get('content', '')
    
    def extract_from_dataset_detail(self, soup, satellite_data):
        """Extract data from detailed dataset page - Enhanced for Earth Engine structure"""
        print("     📊 Extracting from dataset detail page...")
        
        # Extract dataset name from main heading
        main_heading = soup.find(['h1', 'h2'], class_=re.compile(r'main|title|dataset'))
        if main_heading:
            satellite_data['layer_name'] = main_heading.get_text().strip()
        
        # Look for Earth Engine specific data structure
        self.extract_earth_engine_metadata(soup, satellite_data)
        
        # Look for structured data sections
        sections = soup.find_all(['section', 'div'], class_=re.compile(r'section|info|details'))
        
        for section in sections:
            section_text = section.get_text().lower()
            section_title = section.find(['h2', 'h3', 'h4'])
            title_text = section_title.get_text().lower() if section_title else ''
            
            # Temporal coverage section
            if any(word in title_text for word in ['temporal', 'time', 'date', 'coverage', 'availability']):
                self.extract_temporal_data(section, satellite_data)
            
            # Spatial coverage section
            elif any(word in title_text for word in ['spatial', 'coverage', 'extent', 'boundary']):
                self.extract_spatial_data(section, satellite_data)
            
            # Technical specifications section
            elif any(word in title_text for word in ['technical', 'specifications', 'bands', 'resolution']):
                self.extract_technical_data(section, satellite_data)
            
            # Provider information section
            elif any(word in title_text for word in ['provider', 'source', 'organization']):
                self.extract_provider_data(section, satellite_data)
        
        # Extract GEE code examples
        code_blocks = soup.find_all(['code', 'pre'], class_=re.compile(r'example|code|snippet'))
        for code in code_blocks:
            code_text = code.get_text()
            if any(word in code_text.lower() for word in ['ee.', 'earth engine', 'dataset', 'collection']):
                satellite_data['gee_code_snippet'] = code_text.strip()
                break
        
        # Extract DOI and citations
        self.extract_citation_data(soup, satellite_data)
    
    def extract_earth_engine_metadata(self, soup, satellite_data):
        """Extract Earth Engine specific metadata structure - Enhanced based on actual HTML structure"""
        print("     🌍 Extracting Earth Engine metadata...")
        
        try:
            # Method 1: Look for specific text patterns in the entire page
            page_text = soup.get_text()
            
            # Extract dataset availability (date range) - Look for ISO date format
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}Z\s*-\s*(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}Z',
                r'(\d{4}-\d{2}-\d{2})\s*to\s*(\d{4}-\d{2}-\d{2})',
                r'(\d{4}-\d{2}-\d{2})\s*-\s*(\d{4}-\d{2}-\d{2})'
            ]
            
            for pattern in date_patterns:
                try:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        satellite_data['date_range']['start'] = matches[0][0]
                        satellite_data['date_range']['end'] = matches[0][1]
                        print(f"       📅 Found date range: {matches[0][0]} to {matches[0][1]}")
                        break
                except re.error as e:
                    print(f"       ⚠️ Regex error in date pattern: {e}")
                    continue
            
            # Extract dataset provider - Look for common providers
            provider_patterns = [
                r'provider[:\s]+([^.\n]+)',
                r'managed by[:\s]+([^.\n]+)',
                r'hosted by[:\s]+([^.\n]+)',
                r'produced by[:\s]+([^.\n]+)',
                r'developed by[:\s]+([^.\n]+)'
            ]
            
            for pattern in provider_patterns:
                try:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        provider = matches[0].strip()
                        if len(provider) > 2 and provider.lower() not in ['unknown', 'n/a', 'none']:
                            satellite_data['dataset_provider'] = provider
                            print(f"       🏢 Found provider: {provider}")
                            break
                except re.error as e:
                    print(f"       ⚠️ Regex error in provider pattern: {e}")
                    continue
            
            # Method 2: Look for specific HTML structures
            # Look for dataset availability label
            availability_elements = soup.find_all(string=re.compile(r'Dataset Availability', re.I))
            for element in availability_elements:
                parent = element.parent
                if parent:
                    # Look for the next sibling or parent that contains the date
                    date_container = parent.find_next_sibling() or parent.parent
                    if date_container:
                        date_text = date_container.get_text()
                        for pattern in date_patterns:
                            try:
                                matches = re.findall(pattern, date_text)
                                if matches and not satellite_data['date_range']['start']:
                                    satellite_data['date_range']['start'] = matches[0][0]
                                    satellite_data['date_range']['end'] = matches[0][1]
                                    print(f"       📅 Found date range from structure: {matches[0][0]} to {matches[0][1]}")
                                    break
                            except re.error as e:
                                print(f"       ⚠️ Regex error in date structure pattern: {e}")
                                continue
            
            # Look for dataset provider label
            provider_elements = soup.find_all(string=re.compile(r'Dataset Provider', re.I))
            for element in provider_elements:
                parent = element.parent
                if parent:
                    # Look for provider name in nearby elements
                    provider_container = parent.find_next_sibling() or parent.parent
                    if provider_container:
                        provider_text = provider_container.get_text()
                        try:
                            provider_match = re.search(r'([A-Z][a-zA-Z\s&]+)', provider_text)
                            if provider_match:
                                provider = provider_match.group(1).strip()
                                if len(provider) > 2 and provider.lower() not in ['unknown', 'n/a', 'none']:
                                    satellite_data['dataset_provider'] = provider
                                    print(f"       🏢 Found provider from structure: {provider}")
                                    break
                        except re.error as e:
                            print(f"       ⚠️ Regex error in provider structure pattern: {e}")
                            continue
            
            # Look for Earth Engine snippet
            snippet_elements = soup.find_all(string=re.compile(r'Earth Engine Snippet', re.I))
            for element in snippet_elements:
                parent = element.parent
                if parent:
                    # Look for code in the same container
                    code_element = parent.find(['code', 'pre'])
                    if code_element:
                        snippet = code_element.get_text().strip()
                        if 'ee.' in snippet or 'ImageCollection' in snippet:
                            satellite_data['gee_code_snippet'] = snippet
                            print(f"       💻 Found GEE snippet: {snippet[:50]}...")
                            break
            
            # Method 3: Look for common Earth Engine patterns
            # Look for any code blocks that contain Earth Engine code
            code_blocks = soup.find_all(['code', 'pre'])
            for code in code_blocks:
                code_text = code.get_text()
                if ('ee.' in code_text or 'ImageCollection' in code_text) and not satellite_data.get('gee_code_snippet'):
                    satellite_data['gee_code_snippet'] = code_text.strip()
                    print(f"       💻 Found GEE code block: {code_text[:50]}...")
                    break
            
            # Look for tags/categories
            tag_elements = soup.find_all(string=re.compile(r'Tags?', re.I))
            for element in tag_elements:
                parent = element.parent
                if parent:
                    # Look for tag elements in the same container
                    tag_links = parent.find_all('a')
                    if tag_links:
                        tags = [tag.get_text().strip() for tag in tag_links if tag.get_text().strip()]
                        if tags:
                            satellite_data['category_tags'].extend(tags)
                            print(f"       🏷️ Found tags: {', '.join(tags)}")
                            break
            
            # Look for pixel size/resolution
            resolution_patterns = [
                r'pixel size[:\s]+([^.\n]+)',
                r'resolution[:\s]+([^.\n]+)',
                r'spatial resolution[:\s]+([^.\n]+)'
            ]
            
            for pattern in resolution_patterns:
                try:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        satellite_data['pixel_size'] = matches[0].strip()
                        print(f"       📏 Found pixel size: {matches[0].strip()}")
                        break
                except re.error as e:
                    print(f"       ⚠️ Regex error in resolution pattern: {e}")
                    continue
                    
        except Exception as e:
            print(f"       ⚠️ Error in Earth Engine metadata extraction: {e}")
            # Continue with basic extraction
    
    def extract_from_satellite_info(self, soup, satellite_data):
        """Extract data from satellite information page"""
        print("     🛰️ Extracting from satellite info page...")
        
        # Extract satellite name
        satellite_heading = soup.find(['h1', 'h2'], class_=re.compile(r'satellite|platform|instrument'))
        if satellite_heading:
            satellite_data['layer_name'] = satellite_heading.get_text().strip()
        
        # Extract sensor/instrument information
        sensor_sections = soup.find_all(['div', 'section'], class_=re.compile(r'sensor|instrument|platform'))
        for section in sensor_sections:
            section_text = section.get_text()
            if 'band' in section_text.lower():
                self.extract_band_data(section, satellite_data)
            if 'resolution' in section_text.lower():
                self.extract_resolution_data(section, satellite_data)
    
    def extract_generic_data(self, soup, satellite_data):
        """Extract data using generic patterns when page type is unknown"""
        print("     🔍 Using generic extraction patterns...")
        
        text_content = soup.get_text()
        
        # Try to extract dataset name from various sources
        if not satellite_data['layer_name']:
            # Look for dataset names in headings
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings:
                heading_text = heading.get_text().lower()
                if any(word in heading_text for word in ['dataset', 'collection', 'product', 'layer']):
                    satellite_data['layer_name'] = heading.get_text().strip()
                    break
        
        # Extract using regex patterns
        self.extract_with_regex_patterns(text_content, satellite_data)
    
    def extract_temporal_data(self, section, satellite_data):
        """Extract temporal coverage information"""
        section_text = section.get_text()
        
        # Look for date patterns
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})\s*to\s*(\d{4}-\d{2}-\d{2})',
            r'(\d{4}/\d{2}/\d{2})\s*-\s*(\d{4}/\d{2}/\d{2})',
            r'start[:\s]+(\d{4}[-/]\d{2}[-/]\d{2}).*?end[:\s]+(\d{4}[-/]\d{2}[-/]\d{2})',
            r'(\d{4})\s*to\s*(\d{4})',
            r'coverage[:\s]+(\d{4})\s*-\s*(\d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 2:
                    satellite_data['date_range']['start'] = matches[0][0]
                    satellite_data['date_range']['end'] = matches[0][1]
                    break
    
    def extract_spatial_data(self, section, satellite_data):
        """Extract spatial coverage information"""
        section_text = section.get_text()
        
        # Look for location/coverage patterns
        location_patterns = [
            r'coverage[:\s]+([^.\n]+)',
            r'extent[:\s]+([^.\n]+)',
            r'boundary[:\s]+([^.\n]+)',
            r'region[:\s]+([^.\n]+)',
            r'area[:\s]+([^.\n]+)',
            r'global|worldwide|continental|regional|local'
        ]
        
        for pattern in location_patterns:
            if pattern in ['global', 'worldwide', 'continental', 'regional', 'local']:
                if pattern in section_text.lower():
                    satellite_data['location'] = pattern.title()
                    break
            else:
                matches = re.findall(pattern, section_text, re.IGNORECASE)
                if matches:
                    satellite_data['location'] = matches[0].strip()
                    break
    
    def extract_technical_data(self, section, satellite_data):
        """Extract technical specifications"""
        section_text = section.get_text()
        
        # Extract bands
        band_patterns = [
            r'band[s]?[:\s]+([^.\n]+)',
            r'wavelength[s]?[:\s]+([^.\n]+)',
            r'channel[s]?[:\s]+([^.\n]+)'
        ]
        
        for pattern in band_patterns:
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            if matches:
                bands = [b.strip() for b in matches[0].split(',')]
                satellite_data['band_information'].extend(bands)
        
        # Extract resolution/pixel size
        resolution_patterns = [
            r'resolution[:\s]+([^.\n]+)',
            r'pixel[:\s]+([^.\n]+)',
            r'spatial[:\s]+([^.\n]+)'
        ]
        
        for pattern in resolution_patterns:
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            if matches:
                satellite_data['pixel_size'] = matches[0].strip()
                break
    
    def extract_provider_data(self, section, satellite_data):
        """Extract provider/organization information"""
        section_text = section.get_text()
        
        provider_patterns = [
            r'provider[:\s]+([^\.\n]+)',
            r'source[:\s]+([^\.\n]+)',
            r'organization[:\s]+([^\.\n]+)',
            r'institution[:\s]+([^\.\n]+)',
            r'developed by[:\s]+([^\.\n]+)',
            r'created by[:\s]+([^\.\n]+)',
            r'managed by[:\s]+([^\.\n]+)',
            r'hosted by[:\s]+([^\.\n]+)',
            r'maintained by[:\s]+([^\.\n]+)',
            r'agency[:\s]+([^\.\n]+)',
            r'authority[:\s]+([^\.\n]+)'
        ]
        
        for pattern in provider_patterns:
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            if matches:
                satellite_data['dataset_provider'] = matches[0].strip()
                break
        
        # Fallback via meta tags if still empty
        if not satellite_data.get('dataset_provider'):
            meta = section.find('meta', attrs={'name': re.compile(r'provider|organization|institution|author|og:site_name', re.I)})
            if meta:
                satellite_data['dataset_provider'] = meta.get('content', '').strip()
    
    def extract_band_data(self, section, satellite_data):
        """Extract band information from sensor section - Enhanced for Earth Engine bands table"""
        section_text = section.get_text()
        
        # Look for band tables
        band_tables = section.find_all('table')
        for table in band_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    band_name = cells[0].get_text().strip()
                    if 'band' in band_name.lower() or 'channel' in band_name.lower() or 'wavelength' in band_name.lower():
                        satellite_data['band_information'].append(band_name)
        
        # Look for Earth Engine specific band structure
        bands_divs = section.find_all(['div', 'span'], string=re.compile(r'Bands?', re.I))
        for div in bands_divs:
            parent = div.parent
            if parent:
                # Look for band information in the same container
                bands_text = parent.get_text()
                
                # Extract band names from text
                band_patterns = [
                    r'band[s]?[:\s]+([^.\n]+)',
                    r'wavelength[s]?[:\s]+([^.\n]+)',
                    r'channel[s]?[:\s]+([^.\n]+)'
                ]
                
                for pattern in band_patterns:
                    matches = re.findall(pattern, bands_text, re.IGNORECASE)
                    if matches:
                        bands = [b.strip() for b in matches[0].split(',')]
                        satellite_data['band_information'].extend(bands)
                        print(f"       📊 Found bands from text: {', '.join(bands)}")
                        break
                
                # Also look for band table in this section
                band_table = parent.find('table')
                if band_table:
                    rows = band_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 1:
                            band_name = cells[0].get_text().strip()
                            if band_name and band_name.lower() not in ['name', 'band', 'bands']:
                                satellite_data['band_information'].append(band_name)
                    
                    if satellite_data['band_information']:
                        print(f"       📊 Found {len(satellite_data['band_information'])} bands from table")
                break
    
    def extract_resolution_data(self, section, satellite_data):
        """Extract resolution information from sensor section"""
        section_text = section.get_text()
        
        resolution_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:meter|m|km|pixel|arcsecond)',
            r'resolution[:\s]+([^.\n]+)',
            r'pixel[:\s]+([^.\n]+)'
        ]
        
        for pattern in resolution_patterns:
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            if matches:
                satellite_data['pixel_size'] = matches[0].strip()
                break
    
    def extract_citation_data(self, soup, satellite_data):
        """Extract DOI and citation information - Enhanced for Earth Engine structure"""
        print("     📚 Extracting citation data...")
        
        page_text = soup.get_text()
        
        # Look for DOI in text - Enhanced patterns
        doi_patterns = [
            r'doi[:\s]+([^.\n]+)',
            r'10\.\d{4,}/[^\s\n]+',
            r'digital object identifier[:\s]+([^.\n]+)',
            r'doi\.org/([^\s\n]+)'
        ]
        
        for pattern in doi_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                doi = matches[0].strip()
                if doi.startswith('10.'):
                    satellite_data['doi'] = doi
                else:
                    satellite_data['doi'] = f"10.{doi}"
                print(f"       🔗 Found DOI: {satellite_data['doi']}")
                break
        
        # Look for citations in structured elements
        citation_elements = soup.find_all(['div', 'section'], class_=re.compile(r'citation|reference|cite'))
        for element in citation_elements:
            citation_text = element.get_text().strip()
            if citation_text:
                satellite_data['citations'].append(citation_text)
                print(f"       📖 Found citation: {citation_text[:100]}...")
        
        # Look for Earth Engine specific citation structure
        citations_divs = soup.find_all(['div', 'span'], string=re.compile(r'Citations?', re.I))
        for div in citations_divs:
            parent = div.parent
            if parent:
                # Look for citation text in the same container
                citation_text = parent.get_text()
                # Extract the citation content (everything after "Citations:")
                try:
                    citation_match = re.search(r'Citations?[:\s]*(.+)', citation_text, re.I | re.DOTALL)
                    if citation_match:
                        citation_content = citation_match.group(1).strip()
                        if citation_content and len(citation_content) > 10:  # Avoid very short matches
                            satellite_data['citations'].append(citation_content)
                            print(f"       📖 Found structured citation: {citation_content[:100]}...")
                except re.error as e:
                    print(f"       ⚠️ Regex error in citation pattern: {e}")
                
                # Also look for DOI in the citation section
                try:
                    doi_match = re.search(r'doi[:\s]*([^.\s]+)', citation_text, re.I)
                    if doi_match and not satellite_data.get('doi'):
                        doi = doi_match.group(1).strip()
                        if doi.startswith('10.'):
                            satellite_data['doi'] = doi
                        else:
                            satellite_data['doi'] = f"10.{doi}"
                        print(f"       🔗 Found DOI in citations: {satellite_data['doi']}")
                except re.error as e:
                    print(f"       ⚠️ Regex error in DOI pattern: {e}")
                break
        
        # Look for terms of use
        terms_divs = soup.find_all(['div', 'span'], string=re.compile(r'Terms of Use', re.I))
        for div in terms_divs:
            parent = div.parent
            if parent:
                # Look for terms content in the same container
                terms_text = parent.get_text()
                try:
                    terms_match = re.search(r'Terms of Use[:\s]*(.+)', terms_text, re.I | re.DOTALL)
                    if terms_match:
                        terms_content = terms_match.group(1).strip()
                        if terms_content and len(terms_content) > 10:
                            satellite_data['terms_of_use'] = terms_content
                            print(f"       📋 Found terms of use: {terms_content[:100]}...")
                except re.error as e:
                    print(f"       ⚠️ Regex error in terms pattern: {e}")
                break
        
        # Look for description
        description_divs = soup.find_all(['div', 'span'], string=re.compile(r'Description', re.I))
        for div in description_divs:
            parent = div.parent
            if parent:
                # Look for description content in the same container
                desc_text = parent.get_text()
                try:
                    desc_match = re.search(r'Description[:\s]*(.+)', desc_text, re.I | re.DOTALL)
                    if desc_match:
                        desc_content = desc_match.group(1).strip()
                        if desc_content and len(desc_content) > 10:
                            satellite_data['description'] = desc_content
                            print(f"       📝 Found description: {desc_content[:100]}...")
                except re.error as e:
                    print(f"       ⚠️ Regex error in description pattern: {e}")
                break
        
        # Method 4: Look for any text that looks like a citation
        citation_patterns = [
            r'([A-Z][a-zA-Z\s&]+)\s*\(\d{4}\)[:\s]+([^.\n]+)',
            r'([A-Z][a-zA-Z\s&]+)\s*Climate\s+Change\s+Service[^.\n]*',
            r'([A-Z][a-zA-Z\s&]+)\s*Climate\s+Data\s+Store[^.\n]*'
        ]
        
        for pattern in citation_patterns:
            try:
                matches = re.findall(pattern, page_text)
                if matches and not satellite_data.get('citations'):
                    for match in matches:
                        if isinstance(match, tuple):
                            citation = ' '.join(match).strip()
                        else:
                            citation = match.strip()
                        if citation and len(citation) > 20:
                            satellite_data['citations'].append(citation)
                            print(f"       📖 Found citation pattern: {citation[:100]}...")
            except re.error as e:
                print(f"       ⚠️ Regex error in citation pattern: {e}")
                continue
    
    def extract_with_regex_patterns(self, text_content, satellite_data):
        """Extract data using comprehensive regex patterns"""
        # Extract satellites used
        satellite_patterns = [
            r'satellite[:\s]+([^.\n]+)',
            r'sensor[:\s]+([^.\n]+)',
            r'instrument[:\s]+([^.\n]+)',
            r'platform[:\s]+([^.\n]+)'
        ]
        
        for pattern in satellite_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                satellites = [s.strip() for s in matches[0].split(',')]
                satellite_data['satellites_used'].extend(satellites)
        
        # Extract category tags
        tag_patterns = [
            r'category[:\s]+([^.\n]+)',
            r'tag[s]?[:\s]+([^.\n]+)',
            r'type[:\s]+([^.\n]+)',
            r'classification[:\s]+([^.\n]+)'
        ]
        
        for pattern in tag_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                tags = [t.strip() for t in matches[0].split(',')]
                satellite_data['category_tags'].extend(tags)
        
        # Extract terms of use
        terms_patterns = [
            r'terms[:\s]+([^.\n]+)',
            r'license[:\s]+([^.\n]+)',
            r'usage[:\s]+([^.\n]+)',
            r'conditions[:\s]+([^.\n]+)'
        ]
        
        for pattern in terms_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                satellite_data['terms_of_use'] = matches[0].strip()
                break
    
    def calculate_extraction_confidence(self, satellite_data):
        """Calculate confidence level of extracted data"""
        confidence_score = 0
        max_score = 100
        
        # Layer name (20 points)
        if satellite_data['layer_name']:
            confidence_score += 20
        
        # Date range (15 points)
        if satellite_data['date_range']['start'] and satellite_data['date_range']['end']:
            confidence_score += 15
        elif satellite_data['date_range']['start'] or satellite_data['date_range']['end']:
            confidence_score += 7
        
        # Satellites used (15 points)
        if satellite_data['satellites_used']:
            confidence_score += 15
        
        # Location (10 points)
        if satellite_data['location']:
            confidence_score += 10
        
        # GEE code (10 points)
        if satellite_data['gee_code_snippet']:
            confidence_score += 10
        
        # Provider (10 points)
        if satellite_data['dataset_provider']:
            confidence_score += 10
        
        # Technical specs (10 points)
        if satellite_data['pixel_size'] or satellite_data['band_information']:
            confidence_score += 10
        
        # Determine confidence level
        if confidence_score >= 80:
            return 'high'
        elif confidence_score >= 50:
            return 'medium'
        else:
            return 'low'

    def process_catalog_extraction(self, soup, file_path):
        """Process catalog extraction with detailed progress tracking"""
        print(f"🔍 Processing catalog extraction for: {os.path.basename(file_path)}")
        
        # Step 1: Analyze page structure
        print("   📋 Step 1: Analyzing page structure...")
        page_type = self.detect_page_type(soup)
        print(f"      ✅ Detected page type: {page_type}")
        
        # Step 2: Extract catalog links
        print("   🔗 Step 2: Extracting catalog links...")
        catalog_links = self.extract_catalog_links_smart(soup)
        print(f"      ✅ Found {len(catalog_links)} catalog links")
        
        # Step 3: Classify and prioritize links
        print("   🏷️ Step 3: Classifying and prioritizing links...")
        classified_links = self.classify_and_prioritize_links(catalog_links)
        print(f"      ✅ Classified into {len(classified_links)} categories")
        
        # Step 4: Extract satellite data
        print("   🛰️ Step 4: Extracting satellite catalog data...")
        satellite_data = self.extract_satellite_data_enhanced(soup, catalog_links)
        print(f"      ✅ Extracted satellite data with {satellite_data.get('extraction_confidence', 'unknown')} confidence")
        
        # Step 5: Validate and enhance data
        print("   ✅ Step 5: Validating and enhancing data...")
        enhanced_data = self.enhance_satellite_data(satellite_data, soup)
        print(f"      ✅ Data enhancement completed")
        
        return {
            'page_type': page_type,
            'catalog_links': catalog_links,
            'classified_links': classified_links,
            'satellite_catalog': enhanced_data,
            'extraction_summary': self.generate_extraction_summary(catalog_links, enhanced_data)
        }
    
    def extract_catalog_links_smart(self, soup):
        """Smart extraction of catalog links with better pattern recognition"""
        catalog_links = []
        
        # Method 1: Look for structured catalog containers
        containers = self.find_catalog_containers(soup)
        if containers:
            print(f"      🎯 Found {len(containers)} catalog containers")
            for container in containers:
                links = self.extract_from_container(container)
                catalog_links.extend(links)
        
        # Method 2: Look for specific link patterns
        if not catalog_links:
            print("      🔍 No containers found, using link pattern analysis")
            pattern_links = self.extract_by_link_patterns(soup)
            catalog_links.extend(pattern_links)
        
        # Method 3: Look for thumbnail-based links
        if not catalog_links:
            print("      🖼️ No pattern links found, using thumbnail analysis")
            thumbnail_links = self.extract_by_thumbnails(soup)
            catalog_links.extend(thumbnail_links)
        
        # Remove duplicates and validate
        unique_links = self.deduplicate_links(catalog_links)
        valid_links = self.validate_catalog_links(unique_links)
        
        return valid_links
    
    def find_catalog_containers(self, soup):
        """Find catalog containers using multiple strategies"""
        containers = []
        
        # Strategy 1: Look for common catalog class names
        catalog_classes = [
            'catalog', 'grid', 'item', 'dataset', 'collection', 'product',
            'catalog-item', 'catalog-grid', 'dataset-grid', 'collection-grid'
        ]
        
        for class_name in catalog_classes:
            found = soup.find_all(['div', 'section', 'article'], class_=re.compile(class_name, re.I))
            containers.extend(found)
        
        # Strategy 2: Look for catalog-like structures
        catalog_structures = soup.find_all(['div', 'section'], class_=re.compile(r'container|wrapper|content'))
        for structure in catalog_structures:
            # Check if it contains multiple links and images (likely a catalog)
            links = structure.find_all('a')
            images = structure.find_all('img')
            if len(links) > 3 and len(images) > 2:
                containers.append(structure)
        
        # Strategy 3: Look for grid-like layouts
        grid_elements = soup.find_all(['div', 'section'], style=re.compile(r'grid|flex|display'))
        containers.extend(grid_elements)
        
        return list(set(containers))  # Remove duplicates
    
    def extract_from_container(self, container):
        """Extract catalog links from a container"""
        links = []
        
        # Find all links in the container
        container_links = container.find_all('a', href=True)
        
        for link in container_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Skip navigation links
            if self.is_navigation_link(href, text):
                continue
            
            # Check if this looks like a dataset link
            if self.looks_like_dataset_link(href, text):
                # Find associated thumbnail
                thumbnail = self.find_thumbnail_for_link(link, container)
                
                catalog_link = {
                    'text': text,
                    'href': href,
                    'title': link.get('title', ''),
                    'thumbnail': thumbnail,
                    'is_catalog_item': True,
                    'link_type': self.classify_link_type(href, text),
                    'extraction_priority': self.calculate_link_priority(href, text),
                    'container_type': 'structured'
                }
                links.append(catalog_link)
        
        return links
    
    def extract_by_link_patterns(self, soup):
        """Extract links by analyzing URL patterns"""
        links = []
        
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Look for Earth Engine specific patterns
            if self.is_earth_engine_link(href):
                thumbnail = self.find_thumbnail_for_link(link, soup)
                
                catalog_link = {
                    'text': text,
                    'href': href,
                    'title': link.get('title', ''),
                    'thumbnail': thumbnail,
                    'is_catalog_item': True,
                    'link_type': 'earth_engine',
                    'extraction_priority': 9,
                    'container_type': 'pattern_based'
                }
                links.append(catalog_link)
        
        return links
    
    def extract_by_thumbnails(self, soup):
        """Extract links by finding thumbnail images and their associated links"""
        links = []
        
        # Find all images that look like thumbnails
        thumbnails = soup.find_all('img', src=True)
        
        for thumbnail in thumbnails:
            # Check if this looks like a dataset thumbnail
            if self.looks_like_dataset_thumbnail(thumbnail):
                # Find associated link
                link = self.find_link_for_thumbnail(thumbnail)
                if link:
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    catalog_link = {
                        'text': text,
                        'href': href,
                        'title': link.get('title', ''),
                        'thumbnail': {
                            'src': thumbnail.get('src', ''),
                            'alt': thumbnail.get('alt', ''),
                            'title': thumbnail.get('title', ''),
                            'width': thumbnail.get('width', ''),
                            'height': thumbnail.get('height', '')
                        },
                        'is_catalog_item': True,
                        'link_type': 'thumbnail_based',
                        'extraction_priority': 7,
                        'container_type': 'thumbnail_based'
                    }
                    links.append(catalog_link)
        
        return links
    
    def is_earth_engine_link(self, href):
        """Check if a link is Earth Engine specific"""
        earth_engine_patterns = [
            '/datasets/',
            '/collections/',
            'earth-engine',
            'earthengine',
            'google.com/earthengine',
            'developers.google.com/earth-engine'
        ]
        
        return any(pattern in href.lower() for pattern in earth_engine_patterns)
    
    def looks_like_dataset_link(self, href, text):
        """Check if a link looks like it points to a dataset - Enhanced filtering"""
        # First, check if it's clearly NOT a dataset link
        if self.is_clearly_not_dataset(href, text):
            return False
        
        dataset_indicators = [
            'dataset', 'collection', 'product', 'layer', 'imagery',
            'satellite', 'sensor', 'coverage', 'temporal', 'spatial',
            'earth engine', 'earthengine', 'gee', 'landsat', 'sentinel',
            'modis', 'copernicus', 'nasa', 'esa', 'usgs', 'noaa'
        ]
        
        # Check href for dataset patterns
        if any(indicator in href.lower() for indicator in dataset_indicators):
            return True
        
        # Check text for dataset patterns
        if any(indicator in text.lower() for indicator in dataset_indicators):
            return True
        
        # Check for data-like patterns
        if re.search(r'\d{4}', text):  # Contains year
            return True
        
        if re.search(r'[A-Z]{2,}', text):  # Contains acronyms
            return True
        
        # Check for Earth Engine specific patterns
        if self.is_earth_engine_specific(href, text):
            return True
        
        return False
    
    def is_clearly_not_dataset(self, href, text):
        """Check if a link is clearly NOT a dataset link"""
        # Check for obvious non-dataset patterns
        non_dataset_patterns = [
            'login', 'signup', 'register', 'account', 'profile',
            'settings', 'preferences', 'admin', 'dashboard',
            'cart', 'checkout', 'payment', 'billing',
            'support', 'help', 'faq', 'contact', 'about',
            'privacy', 'terms', 'legal', 'cookies',
            'news', 'blog', 'article', 'press', 'media',
            'careers', 'jobs', 'team', 'company', 'organization',
            'events', 'conferences', 'webinars', 'workshops'
        ]
        
        # Check href
        if any(pattern in href.lower() for pattern in non_dataset_patterns):
            return True
        
        # Check text
        if any(pattern in text.lower() for pattern in non_dataset_patterns):
            return True
        
        # Check for social media and external domains
        if self.is_external_junk_domain(href):
            return True
        
        return False
    
    def is_external_junk_domain(self, href):
        """Check if href points to external junk domains"""
        if not href.startswith('http'):
            return False
        
        junk_domains = [
            'facebook.com', 'twitter.com', 'x.com', 'instagram.com',
            'linkedin.com', 'youtube.com', 'reddit.com', 'github.com',
            'stackoverflow.com', 'medium.com', 'dev.to', 'hashnode.dev',
            'discord.com', 'slack.com', 'telegram.org', 'whatsapp.com',
            'tiktok.com', 'snapchat.com', 'pinterest.com', 'tumblr.com',
            'amazon.com', 'ebay.com', 'etsy.com', 'shopify.com',
            'booking.com', 'airbnb.com', 'tripadvisor.com', 'yelp.com',
            'wikipedia.org', 'wikimedia.org', 'quora.com', 'yahoo.com',
            'bing.com', 'duckduckgo.com', 'baidu.com', 'yandex.com'
        ]
        
        return any(domain in href.lower() for domain in junk_domains)
    
    def is_earth_engine_specific(self, href, text):
        """Check if a link is specifically Earth Engine related"""
        earth_engine_patterns = [
            '/datasets/', '/collections/', '/products/', '/layers/',
            'earth-engine', 'earthengine', 'google.com/earthengine',
            'developers.google.com/earth-engine', 'code.earthengine.google.com',
            'explorer.earthengine.google.com', 'signup.earthengine.google.com'
        ]
        
        # Check href for Earth Engine patterns
        if any(pattern in href.lower() for pattern in earth_engine_patterns):
            return True
        
        # Check text for Earth Engine patterns
        earth_engine_indicators = [
            'earth engine', 'earthengine', 'gee', 'google earth engine',
            'dataset', 'collection', 'satellite', 'imagery', 'remote sensing'
        ]
        
        if any(indicator in text.lower() for indicator in earth_engine_indicators):
            return True
        
        return False
    
    def looks_like_dataset_thumbnail(self, img):
        """Check if an image looks like a dataset thumbnail"""
        src = img.get('src', '').lower()
        alt = img.get('alt', '').lower()
        title = img.get('title', '').lower()
        
        # Check for thumbnail indicators
        thumbnail_indicators = [
            'thumb', 'preview', 'sample', 'example', 'dataset', 'collection'
        ]
        
        if any(indicator in src for indicator in thumbnail_indicators):
            return True
        
        if any(indicator in alt for indicator in thumbnail_indicators):
            return True
        
        if any(indicator in title for indicator in thumbnail_indicators):
            return True
        
        # Check size (thumbnails are usually small)
        width = img.get('width')
        height = img.get('height')
        if width and height:
            try:
                if int(width) < 300 and int(height) < 300:
                    return True
            except ValueError:
                pass
        
        return False
    
    def find_link_for_thumbnail(self, thumbnail):
        """Find the link associated with a thumbnail image"""
        # Look for parent link
        parent = thumbnail.parent
        while parent and parent.name != 'a':
            parent = parent.parent
        
        if parent and parent.name == 'a':
            return parent
        
        # Look for sibling link
        siblings = thumbnail.find_next_siblings()
        for sibling in siblings:
            if sibling.name == 'a':
                return sibling
        
        # Look for nearby link
        nearby = thumbnail.find_next('a')
        if nearby:
            return nearby
        
        return None
    
    def deduplicate_links(self, links):
        """Remove duplicate links based on href"""
        seen = set()
        unique_links = []
        
        for link in links:
            href = link.get('href', '')
            if href not in seen:
                seen.add(href)
                unique_links.append(link)
        
        return unique_links
    
    def validate_catalog_links(self, links):
        """Validate that links are actually catalog-related - Enhanced filtering"""
        valid_links = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get('text', '')
            
            # Skip empty or invalid links
            if not href or href == '#' or href == '':
                continue
            
            # Skip navigation links
            if self.is_navigation_link(href, text):
                continue
            
            # Skip external junk domains
            if self.is_external_junk_domain(href):
                continue
            
            # Skip utility and non-content links
            if self.is_utility_link(href, text):
                continue
            
            # Skip social media links
            if self.is_social_media_link(href, text):
                continue
            
            # Skip clearly non-dataset links
            if self.is_clearly_not_dataset(href, text):
                continue
            
            # Skip external non-Earth Engine links (unless they have strong dataset indicators)
            if href.startswith('http') and not self.is_earth_engine_link(href):
                # Only include if it has very strong dataset indicators
                if not self.has_strong_dataset_indicators(href, text):
                    continue
            
            valid_links.append(link)
        
        return valid_links
    
    def has_strong_dataset_indicators(self, href, text):
        """Check if a link has very strong dataset indicators"""
        strong_indicators = [
            'satellite', 'sensor', 'imagery', 'remote sensing', 'earth observation',
            'landsat', 'sentinel', 'modis', 'copernicus', 'nasa', 'esa', 'usgs', 'noaa',
            'dataset', 'collection', 'product', 'layer', 'coverage', 'temporal', 'spatial'
        ]
        
        # Count strong indicators
        indicator_count = 0
        for indicator in strong_indicators:
            if indicator in href.lower():
                indicator_count += 2  # href matches are worth more
            if indicator in text.lower():
                indicator_count += 1
        
        # Require multiple strong indicators for external links
        return indicator_count >= 3
    
    def classify_and_prioritize_links(self, links):
        """Classify links by type and assign priorities"""
        if not links:
            return {}
        
        # Sort by priority
        links.sort(key=lambda x: x.get('extraction_priority', 0), reverse=True)
        
        # Group by type
        classified = {}
        for link in links:
            link_type = link.get('link_type', 'general')
            if link_type not in classified:
                classified[link_type] = []
            classified[link_type].append(link)
        
        return classified
    
    def extract_satellite_data_enhanced(self, soup, catalog_links):
        """Enhanced satellite data extraction using catalog links context"""
        # Use the existing enhanced extraction method
        return self.extract_satellite_data(soup, {'catalog_links': catalog_links})
    
    def enhance_satellite_data(self, satellite_data, soup):
        """Enhance satellite data with additional context"""
        enhanced = satellite_data.copy()
        
        # Add extraction metadata
        enhanced['extraction_timestamp'] = datetime.now().isoformat()
        enhanced['extraction_method'] = 'enhanced_smart_extraction'
        
        # Add confidence indicators
        enhanced['data_completeness'] = self.calculate_data_completeness(enhanced)
        enhanced['extraction_quality'] = self.assess_extraction_quality(enhanced)
        
        # Add context information
        enhanced['page_context'] = self.extract_page_context(soup)
        
        return enhanced
    
    def calculate_data_completeness(self, data):
        """Calculate how complete the extracted data is"""
        fields = [
            'layer_name', 'date_range', 'satellites_used', 'location',
            'gee_code_snippet', 'dataset_provider', 'pixel_size', 'doi'
        ]
        
        completed_fields = 0
        for field in fields:
            if field == 'date_range':
                if data.get('date_range', {}).get('start') and data.get('date_range', {}).get('end'):
                    completed_fields += 1
            elif data.get(field):
                completed_fields += 1
        
        return (completed_fields / len(fields)) * 100
    
    def assess_extraction_quality(self, data):
        """Assess the overall quality of extracted data"""
        quality_score = 0
        
        # Layer name quality
        if data.get('layer_name'):
            if len(data['layer_name']) > 10:
                quality_score += 20
            else:
                quality_score += 10
        
        # Date range quality
        if data.get('date_range', {}).get('start') and data.get('date_range', {}).get('end'):
            quality_score += 20
        
        # Technical data quality
        if data.get('pixel_size') or data.get('band_information'):
            quality_score += 15
        
        # Provider information quality
        if data.get('dataset_provider'):
            quality_score += 15
        
        # GEE code quality
        if data.get('gee_code_snippet'):
            quality_score += 10
        
        # Metadata quality
        if data.get('doi') or data.get('citations'):
            quality_score += 10
        
        # Determine quality level
        if quality_score >= 80:
            return 'excellent'
        elif quality_score >= 60:
            return 'good'
        elif quality_score >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def extract_page_context(self, soup):
        """Extract contextual information about the page"""
        context = {
            'page_title': '',
            'breadcrumbs': [],
            'related_links': [],
            'page_metadata': {}
        }
        
        # Extract page title
        title_tag = soup.find('title')
        if title_tag:
            context['page_title'] = title_tag.get_text().strip()
        
        # Extract breadcrumbs
        breadcrumb_elements = soup.find_all(['nav', 'div'], class_=re.compile(r'breadcrumb|navigation'))
        for element in breadcrumb_elements:
            links = element.find_all('a')
            for link in links:
                context['breadcrumbs'].append({
                    'text': link.get_text().strip(),
                    'href': link.get('href', '')
                })
        
        # Extract related links
        related_sections = soup.find_all(['div', 'section'], class_=re.compile(r'related|similar|additional'))
        for section in related_sections:
            links = section.find_all('a')
            for link in links:
                context['related_links'].append({
                    'text': link.get_text().strip(),
                    'href': link.get('href', '')
                })
        
        # Extract page metadata
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                context['page_metadata'][name] = content
        
        return context
    
    def generate_extraction_summary(self, catalog_links, satellite_data):
        """Generate a comprehensive summary of the extraction process with junk filtering details"""
        summary = {
            'total_links_discovered': 0,  # Total before filtering
            'junk_links_filtered': 0,     # How many were filtered out
            'total_links': len(catalog_links),
            'links_by_type': {},
            'extraction_confidence': satellite_data.get('extraction_confidence', 'unknown'),
            'data_completeness': satellite_data.get('data_completeness', 0),
            'extraction_quality': satellite_data.get('extraction_quality', 'unknown'),
            'junk_examples': [],
            'recommendations': [],
            'filtering_stats': {
                'social_media_removed': 0,
                'navigation_removed': 0,
                'utility_removed': 0,
                'external_junk_removed': 0,
                'broken_links_removed': 0,
                'advertisement_removed': 0
            }
        }
        
        # Count links by type
        for link in catalog_links:
            link_type = link.get('link_type', 'unknown')
            if link_type not in summary['links_by_type']:
                summary['links_by_type'][link_type] = 0
            summary['links_by_type'][link_type] += 1
        
        # Generate recommendations
        if satellite_data.get('extraction_confidence') == 'low':
            summary['recommendations'].append('Consider manual review of extracted data')
        
        if satellite_data.get('data_completeness', 0) < 50:
            summary['recommendations'].append('Data extraction incomplete - may need additional sources')
        
        if not satellite_data.get('gee_code_snippet'):
            summary['recommendations'].append('No GEE code found - check for code examples or documentation')
        
        # Add junk filtering recommendations
        if summary['junk_links_filtered'] > 0:
            summary['recommendations'].append(f'Successfully filtered out {summary["junk_links_filtered"]} junk links for cleaner data')
        
        if summary['total_links'] < 100:
            summary['recommendations'].append('Low link count - may need to adjust filtering criteria')
        
        return summary

    def extract_from_dataset_link(self, link, base_soup):
        """Extract detailed data from an individual dataset link"""
        try:
            href = link.get('href', '')
            text = link.get('text', '')
            
            print(f"         🌐 Processing link: {href[:80]}...")
            
            # Try to fetch the linked dataset page for real details
            details_soup = None
            if href.startswith('http'):
                try:
                    resp = self.session.get(href, timeout=self.config['performance']['timeout'], verify=False, allow_redirects=True)
                    resp.raise_for_status()
                    details_soup = BeautifulSoup(resp.content, 'html.parser')
                except Exception as e:
                    print(f"         ⚠️ Failed to fetch detail page: {e}")
            
            # Create a dataset entry and prefer real details when available
            dataset_data = {
                'layer_name': text.strip(),
                'date_range': {'start': '', 'end': ''},
                'satellites_used': [],
                'location': '',
                'gee_code_snippet': '',
                'thumbnails': [],
                'band_information': [],
                'category_tags': [],
                'dataset_provider': '',
                'pixel_size': '',
                'citations': [],
                'description': '',
                'terms_of_use': '',
                'doi': ''
            }
            
            # If we have a detail soup, extract structured metadata first
            if details_soup is not None:
                try:
                    # First try JSON-LD structured data (fastest and most reliable)
                    json_ld_data = self.extract_json_ld_metadata(details_soup)
                    for k, v in json_ld_data.items():
                        if k in dataset_data and v:
                            dataset_data[k] = v
                        
                    # Then try the general satellite data extractor
                    structured = self.extract_satellite_data(details_soup, {'catalog_links': []})
                    for k, v in structured.items():
                        if k in dataset_data and v and not dataset_data[k]:  # Don't overwrite JSON-LD data
                            dataset_data[k] = v
                            
                except Exception as e:
                    print(f"         ⚠️ Detail parse error: {e}")
            
            # If we still have many unknowns and this is a developers.google.com page, try headless browser
            if (details_soup is None or 
                sum(1 for v in dataset_data.values() if v and v != 'Unknown') < 5) and 'developers.google.com' in href:
                print(f"         🔄 Trying headless browser fallback for better extraction...")
                headless_soup = self.extract_with_headless_browser(href)
                if headless_soup:
                    try:
                        # Extract from fully rendered page
                        headless_data = self.extract_json_ld_metadata(headless_soup)
                        headless_structured = self.extract_satellite_data(headless_soup, {'catalog_links': []})
                        
                        # Merge headless data, preferring it over previous attempts
                        for k, v in headless_data.items():
                            if k in dataset_data and v:
                                dataset_data[k] = v
                        for k, v in headless_structured.items():
                            if k in dataset_data and v:
                                dataset_data[k] = v
                                
                        print(f"         ✅ Headless browser extracted additional data")
                    except Exception as e:
                        print(f"         ⚠️ Headless extraction error: {e}")
            
            # Extract provider from link text or URL
            if 'copernicus' in text.lower() or 'copernicus' in href.lower():
                dataset_data['dataset_provider'] = 'Copernicus'
            elif 'nasa' in text.lower() or 'nasa' in href.lower():
                dataset_data['dataset_provider'] = 'NASA'
            elif 'esa' in text.lower() or 'esa' in href.lower():
                dataset_data['dataset_data'] = 'ESA'
            elif 'usgs' in text.lower() or 'usgs' in href.lower():
                dataset_data['dataset_provider'] = 'USGS'
            elif 'noaa' in text.lower() or 'noaa' in href.lower():
                dataset_data['dataset_provider'] = 'NOAA'
            
            # Extract satellites from text
            satellite_keywords = ['landsat', 'sentinel', 'modis', 'aster', 'viirs', 'olci', 'meris', 'seawifs']
            for keyword in satellite_keywords:
                if keyword in text.lower():
                    dataset_data['satellites_used'].append(keyword.title())
            
            # Extract location from text
            location_keywords = ['global', 'worldwide', 'continental', 'regional', 'local', 'greenland', 'arctic', 'antarctic']
            for keyword in location_keywords:
                if keyword in text.lower():
                    dataset_data['location'] = keyword.title()
                    break
            
            # Extract date patterns from text
            date_patterns = [
                r'(\d{4})',
                r'(\d{4}-\d{2})',
                r'(\d{4}/\d{2})'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    if not dataset_data['date_range']['start']:
                        dataset_data['date_range']['start'] = matches[0]
                    elif not dataset_data['date_range']['end']:
                        dataset_data['date_range']['end'] = matches[0]
                    break
            
            # Extract categories from text
            category_keywords = ['ocean', 'marine', 'land', 'atmosphere', 'climate', 'vegetation', 'water', 'ice', 'snow', 'urban', 'agriculture']
            for keyword in category_keywords:
                if keyword in text.lower():
                    dataset_data['category_tags'].append(keyword.title())
            
            # Look for GEE code patterns in the link
            if 'ee.' in text or 'ImageCollection' in text:
                dataset_data['gee_code_snippet'] = text
            
            # Extract resolution from text
            resolution_patterns = [
                r'(\d+(?:\.\d+)?)\s*(?:meter|m|km)',
                r'(\d+(?:\.\d+)?)\s*(?:pixel|resolution)'
            ]
            
            for pattern in resolution_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    dataset_data['pixel_size'] = f"{matches[0]} meters"
                    break
            
            # Look for description in link title or text
            if link.get('title'):
                dataset_data['description'] = link['title']
            elif len(text) > 50:
                dataset_data['description'] = text[:100] + "..."
            
            return dataset_data
            
        except Exception as e:
            print(f"         ❌ Error extracting from dataset link: {e}")
            return None

    def extract_links_by_thumbnails(self, soup, catalog_links):
        """Extract links by finding ALL thumbnail images and their associated links"""
        print("     🖼️ Extracting ALL thumbnail-based links...")
        
        # Find ALL images that could be thumbnails
        all_images = soup.find_all('img', src=True)
        print(f"       📊 Found {len(all_images)} total images")
        
        thumbnail_count = 0
        for img in all_images:
            # Check if this looks like a dataset thumbnail
            if self.looks_like_dataset_thumbnail(img):
                # Find associated link
                link = self.find_link_for_thumbnail(img)
                if link:
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    # Only add if we don't already have this link
                    if not any(existing['href'] == href for existing in catalog_links):
                        catalog_link = {
                            'text': text,
                            'href': href,
                            'title': link.get('title', ''),
                            'thumbnail': {
                                'src': img.get('src', ''),
                                'alt': img.get('alt', ''),
                                'title': img.get('title', ''),
                                'width': img.get('width', ''),
                                'height': img.get('height', '')
                            },
                            'is_catalog_item': True,
                            'link_type': 'thumbnail_based',
                            'extraction_priority': 10,  # High priority for thumbnails
                            'container_type': 'thumbnail_based'
                        }
                        catalog_links.append(catalog_link)
                        thumbnail_count += 1
                        
                        if thumbnail_count <= 10:  # Show first 10 for debugging
                            print(f"         🖼️ Found thumbnail {thumbnail_count}: {text[:40]}...")
        
        print(f"       ✅ Extracted {thumbnail_count} thumbnail-based links")
        return thumbnail_count

    def extract_json_ld_metadata(self, soup):
        """Extract structured metadata from JSON-LD scripts"""
        metadata = {}
        try:
            # Look for JSON-LD structured data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Extract common fields
                        if 'name' in data and not metadata.get('layer_name'):
                            metadata['layer_name'] = data['name']
                        if 'description' in data and not metadata.get('description'):
                            metadata['description'] = data['description']
                        if 'provider' in data and not metadata.get('dataset_provider'):
                            metadata['dataset_provider'] = data['provider']['name'] if isinstance(data['provider'], dict) else data['provider']
                        if 'datePublished' in data and not metadata.get('date_range'):
                            metadata['date_range'] = {'start': data['datePublished'], 'end': ''}
                        if 'identifier' in data and not metadata.get('doi'):
                            # Check if it's a DOI
                            identifier = data['identifier']
                            if isinstance(identifier, dict) and identifier.get('@type') == 'PropertyValue':
                                identifier = identifier.get('value', '')
                            if 'doi.org' in str(identifier) or str(identifier).startswith('10.'):
                                metadata['doi'] = str(identifier)
                        if 'keywords' in data and not metadata.get('category_tags'):
                            metadata['category_tags'] = data['keywords'] if isinstance(data['keywords'], list) else [data['keywords']]
                        if 'spatialCoverage' in data and not metadata.get('location'):
                            spatial = data['spatialCoverage']
                            if isinstance(spatial, dict):
                                if 'name' in spatial:
                                    metadata['location'] = spatial['name']
                                elif 'geo' in spatial:
                                    geo = spatial['geo']
                                    if isinstance(geo, dict) and 'latitude' in geo and 'longitude' in geo:
                                        metadata['location'] = f"Lat: {geo['latitude']}, Lon: {geo['longitude']}"
                except (json.JSONDecodeError, AttributeError) as e:
                    continue
            
            # Also check for microdata attributes
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                property_name = meta.get('property', meta.get('name', ''))
                content = meta.get('content', '')
                
                if 'og:title' in property_name and not metadata.get('layer_name'):
                    metadata['layer_name'] = content
                elif 'og:description' in property_name and not metadata.get('description'):
                    metadata['description'] = content
                elif 'citation_doi' in property_name and not metadata.get('doi'):
                    metadata['doi'] = content
                elif 'citation_author' in property_name and not metadata.get('dataset_provider'):
                    metadata['dataset_provider'] = content
                elif 'citation_keywords' in property_name and not metadata.get('category_tags'):
                    metadata['category_tags'] = [kw.strip() for kw in content.split(',') if kw.strip()]
            
        except Exception as e:
            print(f"         ⚠️ JSON-LD extraction error: {e}")
        
        return metadata

    def extract_with_headless_browser(self, url):
        """Fallback: Use headless browser to get fully rendered content"""
        try:
            # Try to import playwright (install with: pip install playwright)
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                print("         ⚠️ Playwright not installed. Install with: pip install playwright")
                return None
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    viewport={"width": 1280, "height": 720}
                )
                page = context.new_page()
                
                # Navigate and wait for content to load
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait a bit more for dynamic content
                page.wait_for_timeout(2000)
                
                # Get the fully rendered HTML
                html_content = page.content()
                context.close()
                browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup
                
        except Exception as e:
            print(f"         ⚠️ Headless browser fallback failed: {e}")
            return None

class LocalHTMLDataExtractorUI(QWidget):
    """UI for local HTML data extraction"""
    
    # Define signals for thread-safe UI updates
    progress_updated = Signal(int, int)
    status_updated = Signal(str)
    data_updated = Signal()
    log_updated = Signal(str)
    error_updated = Signal(str)
    extraction_percent_updated = Signal(int)
    realtime_viewer_updated = Signal(str, object)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satellite Catalog Extractor - Earth Engine Pages")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.extractor = LocalHTMLDataExtractor()
        
        # Create session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Data storage
        self.extracted_data = []
        self.is_extracting = False
        self.stop_requested = False
        self.processed_files = set()
        self.processed_urls = set()  # Track processed URLs for link following
        
        # Statistics
        self.total_processed = 0
        self.successful_extractions = 0
        self.failed_extractions = 0
        self.start_time = None
        
        self.setup_ui()
        
        # Connect signals
        self.progress_updated.connect(self.update_progress)
        self.status_updated.connect(self.update_status)
        self.data_updated.connect(self.update_data_viewer_after_extraction)
        self.log_updated.connect(self.log_message)
        self.error_updated.connect(self.log_error)
        self.extraction_percent_updated.connect(self.update_extraction_percent)
        self.realtime_viewer_updated.connect(self._on_realtime_viewer_updated)
        
        # Load configuration after UI is ready
        self.load_config()
        
        # Heartbeat to confirm UI event loop is alive
        try:
            self._hb_counter = 0
            self._heartbeat = QTimer(self)
            self._heartbeat.setInterval(2000)
            self._heartbeat.timeout.connect(self._emit_heartbeat)
            self._heartbeat.start()
        except Exception:
            pass
    
    def load_config(self):
        """Load configuration"""
        self.config = {
            'processing': {
                'max_files_per_run': 999999,  # Process all files
                'batch_size': 10
            },
            'performance': {
                'request_delay': 1, # Seconds between requests
                'timeout': 10 # Seconds for requests
            },
            'safe_mode': True,
            'limits': {
                'max_detail_links': 5,
                'max_follow_links': 5
            },
            'logging': {
                'max_console_lines': 2000
            },
            'minimal_mode': False,
            'noop_mode': False,
            'names_only_mode': True
        }
        self.log_message("✅ Configuration loaded - Local processing only")
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # File selection group
        file_group = QGroupBox("HTML Files to Process")
        file_layout = QVBoxLayout()
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        
        # File controls
        file_controls = QHBoxLayout()
        add_files_btn = QPushButton("Add HTML Files")
        add_files_btn.clicked.connect(self.add_html_files)
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_html_folder)
        add_gee_cat_btn = QPushButton("Add GEE Cat Folder")
        add_gee_cat_btn.clicked.connect(self.add_gee_cat_folder)
        clear_files_btn = QPushButton("Clear List")
        clear_files_btn.clicked.connect(self.clear_file_list)
        
        file_controls.addWidget(add_files_btn)
        file_controls.addWidget(add_folder_btn)
        file_controls.addWidget(add_gee_cat_btn)
        file_controls.addWidget(clear_files_btn)
        file_controls.addStretch()
        
        file_layout.addLayout(file_controls)
        file_layout.addWidget(self.file_list)
        file_group.setLayout(file_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Extraction")
        self.start_btn.clicked.connect(self.start_extraction)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_extraction)
        self.stop_btn.setEnabled(False)
        
        # Overwrite checkbox
        self.overwrite_checkbox = QCheckBox("Overwrite existing data")
        self.overwrite_checkbox.setChecked(True)
        
        # Safe mode and link following controls
        self.safe_mode_checkbox = QCheckBox("Safe Mode (limit workload)")
        self.safe_mode_checkbox.setChecked(True)
        self.follow_links_checkbox = QCheckBox("Follow external links")
        self.follow_links_checkbox.setChecked(False)
        self.minimal_mode_checkbox = QCheckBox("Minimal mode (title only)")
        self.minimal_mode_checkbox.setChecked(True)
        self.noop_mode_checkbox = QCheckBox("No-op mode (extract nothing)")
        self.noop_mode_checkbox.setChecked(True)
        
        # Clear data button
        self.clear_data_btn = QPushButton("Clear Extracted Data")
        self.clear_data_btn.clicked.connect(self.clear_extracted_data)
        
        # Open output folder button
        self.open_folder_btn = QPushButton("Open Output Folder")
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.overwrite_checkbox)
        control_layout.addWidget(self.safe_mode_checkbox)
        control_layout.addWidget(self.follow_links_checkbox)
        control_layout.addWidget(self.minimal_mode_checkbox)
        control_layout.addWidget(self.noop_mode_checkbox)
        control_layout.addWidget(self.clear_data_btn)
        control_layout.addWidget(self.open_folder_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Status label
        self.status_label = QLabel("Ready - Add HTML files to begin")
        self.status_label.setStyleSheet("font-weight: bold; color: #007acc;")
        
        # Real-time Data Viewer
        data_viewer_group = QGroupBox("Real-Time Data Viewer")
        data_viewer_layout = QVBoxLayout()
        
        # Viewer controls
        viewer_controls = QHBoxLayout()
        self.refresh_viewer_btn = QPushButton("🔄 Refresh")
        self.refresh_viewer_btn.clicked.connect(self.refresh_data_viewer)
        self.export_viewer_btn = QPushButton("📊 Export Data")
        self.export_viewer_btn.clicked.connect(self.export_viewer_data)
        self.filter_btn = QPushButton("🔍 Filter")
        self.filter_btn.clicked.connect(self.show_filter_dialog)
        
        viewer_controls.addWidget(self.refresh_viewer_btn)
        viewer_controls.addWidget(self.export_viewer_btn)
        viewer_controls.addWidget(self.filter_btn)
        viewer_controls.addStretch()
        
        # Data viewer tabs
        self.data_viewer_tabs = QTabWidget()
        
        # Tab 1: Summary Dashboard
        self.summary_tab = QWidget()
        self.setup_summary_tab()
        self.data_viewer_tabs.addTab(self.summary_tab, "📊 Summary Dashboard")
        
        # Tab 2: Satellite Catalog Table
        self.catalog_tab = QWidget()
        self.setup_catalog_tab()
        self.data_viewer_tabs.addTab(self.catalog_tab, "🛰️ Satellite Catalog")
        
        # Tab 3: Real-time Extraction Log
        self.extraction_tab = QWidget()
        self.setup_extraction_tab()
        self.data_viewer_tabs.addTab(self.extraction_tab, "🔍 Live Extraction")
        
        # Tab 4: Data Analysis
        self.analysis_tab = QWidget()
        self.setup_analysis_tab()
        self.data_viewer_tabs.addTab(self.analysis_tab, "📈 Data Analysis")
        
        data_viewer_layout.addLayout(viewer_controls)
        data_viewer_layout.addWidget(self.data_viewer_tabs)
        data_viewer_group.setLayout(data_viewer_layout)
        
        # Console for logging
        console_group = QGroupBox("Logs")
        console_layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setMaximumHeight(120)
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        
        # Add all components to main layout
        layout.addWidget(file_group)
        layout.addLayout(control_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(data_viewer_group)
        layout.addWidget(console_group)
        
        self.setLayout(layout)
        
        # Hide non-essential controls to simplify UI
        try:
            # Keep Add Folder and Clear Data visible; hide advanced controls
            add_gee_cat_btn.setVisible(False)
            # add_folder_btn stays visible
            self.safe_mode_checkbox.setVisible(False)
            self.follow_links_checkbox.setVisible(False)
            self.minimal_mode_checkbox.setVisible(False)
            self.noop_mode_checkbox.setVisible(False)
            # clear_data_btn stays visible
            self.refresh_viewer_btn.setVisible(False)
            self.export_viewer_btn.setVisible(False)
            self.filter_btn.setVisible(False)
            # Keep all tabs visible as requested
        except Exception:
            pass
    
    def setup_summary_tab(self):
        """Setup the summary dashboard tab"""
        layout = QVBoxLayout()
        
        # Statistics grid
        stats_grid = QGridLayout()
        
        # Create stat widgets
        self.total_satellites_label = QLabel("0")
        self.total_satellites_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #007acc;")
        self.total_satellites_desc = QLabel("Total Satellites")
        self.total_satellites_desc.setStyleSheet("color: #666;")
        
        self.total_datasets_label = QLabel("0")
        self.total_datasets_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #28a745;")
        self.total_datasets_desc = QLabel("Total Datasets")
        self.total_datasets_desc.setStyleSheet("color: #666;")
        
        self.total_providers_label = QLabel("0")
        self.total_providers_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffc107;")
        self.total_providers_desc = QLabel("Data Providers")
        self.total_providers_desc.setStyleSheet("color: #666;")
        
        self.extraction_status_label = QLabel("Idle")
        self.extraction_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #6c757d;")
        self.extraction_status_desc = QLabel("Extraction Status")
        self.extraction_status_desc.setStyleSheet("color: #666;")
        
        # Add to grid
        stats_grid.addWidget(self.total_satellites_label, 0, 0)
        stats_grid.addWidget(self.total_satellites_desc, 1, 0)
        stats_grid.addWidget(self.total_datasets_label, 0, 1)
        stats_grid.addWidget(self.total_datasets_desc, 1, 1)
        stats_grid.addWidget(self.total_providers_label, 0, 2)
        stats_grid.addWidget(self.total_providers_desc, 1, 2)
        stats_grid.addWidget(self.extraction_status_label, 0, 3)
        stats_grid.addWidget(self.extraction_status_desc, 1, 3)
        
        # Recent activity
        recent_group = QGroupBox("Recent Activity")
        recent_layout = QVBoxLayout()
        self.recent_activity_list = QListWidget()
        self.recent_activity_list.setMaximumHeight(200)
        recent_layout.addWidget(self.recent_activity_list)
        recent_group.setLayout(recent_layout)
        
        layout.addLayout(stats_grid)
        layout.addWidget(recent_group)
        self.summary_tab.setLayout(layout)
    
    def setup_catalog_tab(self):
        """Setup the satellite catalog table tab"""
        layout = QVBoxLayout()
        
        # Enhanced table with better columns
        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(15)
        self.catalog_table.setHorizontalHeaderLabels([
            "Layer Name", "Satellites", "Date Range", "Location", "Provider", 
            "Pixel Size", "Bands", "Categories", "Thumbnails", "GEE Code", "DOI",
            "Description", "Citations", "Terms", "Status"
        ])
        
        # Set column widths
        self.catalog_table.setColumnWidth(0, 200)  # Layer Name
        self.catalog_table.setColumnWidth(1, 150)  # Satellites
        self.catalog_table.setColumnWidth(2, 120)  # Date Range
        self.catalog_table.setColumnWidth(3, 150)  # Location
        self.catalog_table.setColumnWidth(4, 120)  # Provider
        self.catalog_table.setColumnWidth(5, 80)   # Pixel Size
        self.catalog_table.setColumnWidth(6, 100)  # Bands
        self.catalog_table.setColumnWidth(7, 120)  # Categories
        self.catalog_table.setColumnWidth(8, 80)   # Thumbnails
        self.catalog_table.setColumnWidth(9, 100)  # GEE Code
        self.catalog_table.setColumnWidth(10, 100) # DOI
        self.catalog_table.setColumnWidth(11, 150) # Description
        self.catalog_table.setColumnWidth(12, 100) # Citations
        self.catalog_table.setColumnWidth(13, 100) # Terms
        self.catalog_table.setColumnWidth(14, 80)  # Status
        
        # Enable sorting and selection
        self.catalog_table.setSortingEnabled(True)
        self.catalog_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.catalog_table.setAlternatingRowColors(True)
        
        # Context menu
        self.catalog_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.catalog_table.customContextMenuRequested.connect(self.show_catalog_context_menu)
        
        # Double-click to view details
        self.catalog_table.itemDoubleClicked.connect(self.show_satellite_details)
        
        layout.addWidget(self.catalog_table)
        self.catalog_tab.setLayout(layout)
    
    def setup_extraction_tab(self):
        """Setup the real-time extraction log tab"""
        layout = QVBoxLayout()
        
        # Live extraction status
        status_group = QGroupBox("Extraction Progress")
        status_layout = QVBoxLayout()
        
        # Progress indicators
        progress_layout = QHBoxLayout()
        self.files_progress = QProgressBar()
        self.files_progress.setFormat("Files: %v/%m")
        self.links_progress = QProgressBar()
        self.links_progress.setFormat("Links: %v/%m")
        self.data_progress = QProgressBar()
        self.data_progress.setFormat("Data: %v/%m")
        
        progress_layout.addWidget(self.files_progress)
        progress_layout.addWidget(self.links_progress)
        progress_layout.addWidget(self.data_progress)
        
        status_layout.addLayout(progress_layout)
        status_group.setLayout(status_layout)
        
        # Live extraction log
        log_group = QGroupBox("Live Extraction Log")
        log_layout = QVBoxLayout()
        self.extraction_log = QTextEdit()
        self.extraction_log.setMaximumHeight(300)
        self.extraction_log.setReadOnly(True)
        log_layout.addWidget(self.extraction_log)
        log_group.setLayout(log_layout)
        
        # Current file being processed
        current_group = QGroupBox("Currently Processing")
        current_layout = QVBoxLayout()
        self.current_file_label = QLabel("No file being processed")
        self.current_file_label.setStyleSheet("font-weight: bold; color: #007acc;")
        self.current_status_label = QLabel("Idle")
        self.current_status_label.setStyleSheet("color: #666;")
        current_layout.addWidget(self.current_file_label)
        current_layout.addWidget(self.current_status_label)
        current_group.setLayout(current_layout)
        
        layout.addWidget(status_group)
        layout.addWidget(current_group)
        layout.addWidget(log_group)
        self.extraction_tab.setLayout(layout)
    
    def setup_analysis_tab(self):
        """Setup the data analysis tab"""
        layout = QVBoxLayout()
        
        # Analysis controls
        controls_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("🔍 Analyze Data")
        self.analyze_btn.clicked.connect(self.analyze_extracted_data)
        self.generate_report_btn = QPushButton("📋 Generate Report")
        self.generate_report_btn.clicked.connect(self.generate_analysis_report)
        
        controls_layout.addWidget(self.analyze_btn)
        controls_layout.addWidget(self.generate_report_btn)
        controls_layout.addStretch()
        
        # Analysis results
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setPlaceholderText("Click 'Analyze Data' to see analysis results...")
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.analysis_text)
        self.analysis_tab.setLayout(layout)
    
    def add_html_files(self):
        """Add individual HTML files"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select HTML files", "", "HTML files (*.html *.htm)"
        )
        for file_path in file_paths:
            if file_path not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                self.file_list.addItem(file_path)
        self.log_message(f"📁 Added {len(file_paths)} HTML files")
        try:
            _log_json('ui_add_files', count=len(file_paths))
        except Exception:
            pass
    
    def add_html_folder(self):
        """Add all HTML files from a folder"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select folder with HTML files")
        if folder_path:
            html_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.html', '.htm')):
                        html_files.append(os.path.join(root, file))
            
            # Add files that aren't already in the list
            existing_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            new_files = [f for f in html_files if f not in existing_files]
            
            for file_path in new_files:
                self.file_list.addItem(file_path)
            
            self.log_message(f"📁 Added {len(new_files)} HTML files from folder")
            try:
                _log_json('ui_add_folder', folder=folder_path, added=len(new_files))
            except Exception:
                pass
    
    def add_gee_cat_folder(self):
        """Add HTML files from the gee cat folder"""
        gee_cat_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gee cat")
        
        if os.path.exists(gee_cat_path):
            html_files = []
            for root, dirs, files in os.walk(gee_cat_path):
                for file in files:
                    if file.lower().endswith(('.html', '.htm')):
                        html_files.append(os.path.join(root, file))
            
            if html_files:
                # Add files that aren't already in the list
                existing_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
                new_files = [f for f in html_files if f not in existing_files]
                
                for file_path in new_files:
                    self.file_list.addItem(file_path)
                
                self.log_message(f"🌍 Added {len(new_files)} HTML files from GEE Cat folder")
                self.log_message(f"📁 GEE Cat path: {gee_cat_path}")
                try:
                    _log_json('ui_add_gee_cat', path=gee_cat_path, added=len(new_files))
                except Exception:
                    pass
            else:
                self.log_message("⚠️ No HTML files found in GEE Cat folder")
                try:
                    _log_json('ui_add_gee_cat_empty', path=gee_cat_path)
                except Exception:
                    pass
        else:
            self.log_message("❌ GEE Cat folder not found")
            QMessageBox.warning(self, "Warning", "GEE Cat folder not found in the expected location.")
            try:
                _log_json('ui_add_gee_cat_missing', path=gee_cat_path)
            except Exception:
                pass
    
    def clear_file_list(self):
        """Clear the file list"""
        self.file_list.clear()
        self.log_message("🗑️ File list cleared")
        try:
            _log_json('ui_clear_files')
        except Exception:
            pass
    
    def start_extraction(self):
        """Start data extraction process (names-only mode enabled)"""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Warning", "Please add HTML files to process first!")
            return
        
        # Apply UI options to config
        self.config['safe_mode'] = True
        self.config['follow_links'] = True
        self.config['minimal_mode'] = False
        self.config['noop_mode'] = False
        self.config['names_only_mode'] = True
        # Ensure reasonable caps
        if 'limits' not in self.config:
            self.config['limits'] = {}
        self.config['limits'].setdefault('max_follow_links', 5)
        self.config['limits'].setdefault('max_detail_links', 5)
        # Mirror limits into extractor config for use inside extraction
        self.extractor.config.update({
            'safe_mode': self.config['safe_mode'],
            'limits': self.config.get('limits', {})
        })
        self.extraction_log.clear()
        self.add_extraction_log_entry("🛑 Extraction is disabled in this build.", "warning")
        self.status_label.setText("Extraction disabled")
        self.extraction_status_label.setText("Disabled")
        self.extraction_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #6c757d;")
        _log_json('extraction_disabled', files=self.file_list.count())
        self.extraction_finished()
    
    def stop_extraction(self):
        """Stop extraction process"""
        self.stop_requested = True
        self.is_extracting = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        try:
            _log_json('ui_stop_clicked')
        except Exception:
            pass
        
        # Update extraction status
        self.extraction_status_label.setText("Stopped")
        self.extraction_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #dc3545;")
        
        # Update current status
        self.current_file_label.setText("No file being processed")
        self.current_status_label.setText("Stopped by user")
        
        # Add stop entry to extraction log
        self.add_extraction_log_entry("🛑 Extraction stopped by user", "warning")
        
        self.log_message("🛑 Extraction stopped by user")
    
    def extract_from_files(self):
        """Extract data from all HTML files in the list"""
        try:
            _log_json('worker_start')
            file_paths = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            total_files = len(file_paths)
            _log_json('worker_files_collected', total=total_files)
            
            # Reset progress bar for extraction process
            self.progress_bar.setMaximum(100)  # Use percentage-based progress
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.status_updated.emit("Starting extraction...")
            
            self.log_message(f"🚀 Starting local HTML data extraction...")
            self.log_message(f"📁 Processing {total_files} HTML files")
            _log_json('worker_begin_processing', total=total_files)
            
            # Process files in batches
            batch_size = self.config['processing']['batch_size']
            
            for i, file_path in enumerate(file_paths):
                if self.stop_requested:
                    break
                _log_json('worker_process_file', index=i+1, total=total_files, file=file_path)
                
                self.log_message(f"🔍 Processing {i+1}/{total_files}: {os.path.basename(file_path)}")
                success = self.process_html_file(file_path, i+1, total_files)
                
                if success:
                    # Now follow links found in this file to extract data from each linked page
                    self.log_message(f"🔗 Following links from {os.path.basename(file_path)} to extract data from each page...")
                    self.follow_links_from_file(file_path, i+1, total_files)
                    _log_json('worker_file_done', file=file_path)
                    
                    time.sleep(0.1)  # Small delay to prevent UI freezing
                else:
                    time.sleep(1)  # Longer delay on failure
                
                # Memory cleanup every batch
                if (i + 1) % batch_size == 0:
                    self.cleanup_memory()
        
            self.log_message("✅ Local extraction completed!")
            self.show_summary()
            _log_json('worker_complete')
            
        except Exception as e:
            self.log_error(f"❌ Extraction failed: {e}")
            _log_json('worker_error', error=str(e))
        finally:
            self.extraction_finished()
    
    def follow_links_from_file(self, file_path, current, total):
        """Follow links found in an HTML file to extract data from each linked page"""
        try:
            # Read the HTML file to find only image-wrapped links
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            try:
                import lxml  # noqa: F401
                soup = BeautifulSoup(content, 'lxml')
            except Exception:
                soup = BeautifulSoup(content, 'html.parser')
            
            # Collect anchors that contain an <img>
            img_links = []
            for a in soup.find_all('a', href=True):
                if a.find('img') is not None:
                    href = a.get('href', '').strip()
                    text = a.get_text(" ", strip=True)
                    if href and href.startswith('http'):
                        img_links.append({'href': href, 'text': text})
            
            self.total_links = len(img_links)
            self.log_message(f"🖼️ Image links discovered: {self.total_links}")
            _log_json('image_links_discovered', file=file_path, count=self.total_links)
            if self.total_links == 0:
                return
            
            # Process each image link: fetch, extract names, save minimal JSON
            for i, link in enumerate(img_links, start=1):
                if self.stop_requested:
                    break
                url = link['href']
                self.log_message(f"🌐 [{i}/{self.total_links}] Fetching: {url}")
                _log_json('fetch_link', index=i, total=self.total_links, url=url)
                try:
                    resp = self.session.get(url, timeout=self.extractor.config.get('performance', {}).get('timeout', 15))
                    status = resp.status_code
                    if status != 200:
                        self.log_message(f"   ⚠️ HTTP {status} for {url}")
                        _log_json('fetch_non_200', url=url, status=status)
                        continue
                    page_html = resp.text
                    try:
                        import lxml  # noqa: F401
                        page_soup = BeautifulSoup(page_html, 'lxml')
                    except Exception:
                        page_soup = BeautifulSoup(page_html, 'html.parser')
                    names = self.extract_names_from_soup(page_soup)
                    title = (page_soup.title.get_text().strip() if page_soup.title else '')
                    self.log_message(f"   ✅ Names: {len(names)} | Title: {title[:60]}")
                    _log_json('link_names_extracted', url=url, count=len(names), sample=names[:5])
                    data = {
                        'source_file': file_path,
                        'link_url': url,
                        'timestamp': datetime.now().isoformat(),
                        'title': title,
                        'names': names,
                        'extraction_summary': {'mode': 'names_only_link'}
                    }
                    json_file = self.extractor.save_data_to_json(data, file_path)
                    if json_file:
                        self.log_message(f"   💾 Saved: {os.path.basename(json_file)}")
                        _log_json('link_saved', url=url, json=json_file)
                except Exception as e:
                    self.log_message(f"   ❌ Link processing failed: {e}")
                    _log_json('link_error', url=url, error=str(e))
                finally:
                    # Small delay to keep UI responsive
                    time.sleep(0.1)
            
            self.log_message(f"✅ Completed processing {self.total_links} image links")
        except Exception as e:
            self.log_error(f"❌ Failed to process image links from {os.path.basename(file_path)}: {e}")
    
    def cleanup_memory(self):
        """Clean up memory to prevent infinite growth"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Log memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.log_message(f"💾 Memory usage: {memory_mb:.1f} MB")
            
        except Exception as e:
            self.log_message(f"⚠️ Memory cleanup failed: {e}")
    
    def process_html_file(self, file_path, current, total):
        """Hard-disabled file processing"""
        try:
            self.log_message(f"🟦 Skipping processing for: {os.path.basename(file_path)} (hard disabled)")
            _log_json('file_skipped_hard', file=file_path)
            self.successful_extractions += 1
            self.processed_files.add(file_path)
            self.data_updated.emit()
            return True
            
        except Exception as e:
            self.failed_extractions += 1
            self.error_updated.emit(f"❌ Failed in hard-disable path for {file_path}: {e}")
            _logger.exception("file_processing_error_hard")
            _log_json('file_processing_error_hard', file=file_path, error=str(e))
            return False
    
    def process_links_from_soup(self, soup, base_url):
        """Process links from parsed HTML soup and extract data from each linked page"""
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            url = link.get('href')
            if url and url.startswith('http'):
                if '/datasets/catalog/' in url and not url.endswith('/catalog'):
                    links.append(url)
        
        self.log_message(f"🔗 Found {len(links)} catalog links to process")
        
        # Process ALL links found
        self.log_message(f"📊 Processing ALL {len(links)} links to extract data from each page")
        
        if not links:
            self.log_message("⚠️ No valid links found")
            return
        
        # Process links
        for i, url in enumerate(links):
            if self.stop_requested:
                break
            
            self.log_message(f"🔍 Processing {i+1}/{len(links)}: {url}")
            success = self.process_link(url, i+1, len(links))
            
            if success:
                time.sleep(self.config['performance']['request_delay'])
            else:
                time.sleep(5)  # Longer delay on failure
            
            # Memory cleanup every 10 processed items
            if (i + 1) % 10 == 0:
                self.cleanup_memory()
        
        self.log_message("✅ Collection completed!")
        self.show_summary()
    
    def process_link(self, url, current, total):
        """Process individual link and extract data from the linked page"""
        try:
            # Check if URL already processed (unless overwrite is enabled)
            if url in self.processed_urls and not self.overwrite_checkbox.isChecked():
                self.log_message(f"⏭️ Skipping already processed: {url}")
                return True
            
            self.total_processed += 1
            self.progress_updated.emit(current, total)
            self.status_updated.emit(f"Processing: {current}/{total}")
            
            # Enhanced request with retry mechanism
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    # Enhanced headers for better compatibility
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    }
                    
                    response = self.session.get(
                        url, 
                        timeout=self.config['performance']['timeout'],
                        verify=False,
                        headers=headers,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    
                    # Check if response is HTML
                    content_type = response.headers.get('content-type', '').lower()
                    if not content_type.startswith('text/html'):
                        self.log_error(f"❌ URL does not return HTML: {content_type} - {url}")
                        return False
                    
                    break  # Success, exit retry loop
                    
                except requests.exceptions.Timeout:
                    self.log_error(f"⏰ Timeout (attempt {attempt + 1}/{max_retries}): {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        return False
                        
                except requests.exceptions.ConnectionError:
                    self.log_error(f"🌐 Connection error (attempt {attempt + 1}/{max_retries}): {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        return False
                        
                except requests.exceptions.HTTPError as e:
                    self.log_error(f"📡 HTTP error {e.response.status_code} (attempt {attempt + 1}/{max_retries}): {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        return False
                        
                except Exception as e:
                    self.log_error(f"❌ Request failed (attempt {attempt + 1}/{max_retries}): {e} - {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        return False
            
            # Parse response
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                self.log_error(f"❌ Failed to parse response: {e}")
                return False
            
            # Collect ALL data from the linked page using the extractor
            def link_progress(pct):
                try:
                    self.links_progress.setMaximum(100)
                    self.links_progress.setValue(int(pct))
                    self.current_status_label.setText(f"Processing link: {int(pct)}%")
                    QApplication.processEvents()
                except Exception:
                    pass
            def link_log(msg):
                try:
                    self.add_extraction_log_entry(msg, "info")
                except Exception:
                    pass
            data = self.extractor.extract_all_data(soup, url, link_progress, link_log)
            
            # Save to JSON file
            json_file = self.extractor.save_data_to_json(data, url)
            
            if json_file:
                # Add to collected data list
                collection_info = {
                    'title': data.get('title', 'Unknown'),
                    'url': url,
                    'file_path': url,  # Use URL as file path for links
                    'satellite_catalog': data.get('satellite_catalog', {}),
                    'json_file': json_file
                }
                
                # Save satellite data to catalog if available
                if data.get('satellite_catalog'):
                    satellite_name = data['satellite_catalog'].get('layer_name', 'Unknown_Satellite')
                    if satellite_name == 'Unknown_Satellite':
                        satellite_name = f"Satellite_{len(self.extracted_data) + 1}"
                    
                    # Save to satellite catalog
                    catalog_file = self.extractor.save_satellite_catalog_data(
                        data['satellite_catalog'], 
                        satellite_name
                    )
                    if catalog_file:
                        collection_info['catalog_file'] = catalog_file
                
                self.extracted_data.append(collection_info)
                self.successful_extractions += 1
                self.processed_urls.add(url)
                self.data_updated.emit()
                
                self.log_updated.emit(
                    f"✅ {data.get('title', 'Unknown')[:50]}... "
                    f"(Saved to: {os.path.basename(json_file)})"
                )
                
                self.log_message(f"🎯 Data extracted from linked page: {url}")
                if data.get('satellite_catalog'):
                    catalog = data['satellite_catalog']
                    self.log_message(f"   🛰️ Layer: {catalog.get('layer_name', 'Unknown')}")
                    self.log_message(f"   🏢 Provider: {catalog.get('dataset_provider', 'Unknown')}")
                    self.log_message(f"   🌍 Location: {catalog.get('location', 'Unknown')}")
                    self.log_message(f"   📅 Date Range: {catalog.get('date_range', {}).get('start', '')} to {catalog.get('date_range', {}).get('end', '')}")
                    self.log_message(f"   📊 Bands: {len(catalog.get('band_information', []))}")
                    self.log_message(f"   🖼️ Thumbnails: {len(catalog.get('thumbnails', []))}")
                else:
                    self.log_message(f"   📊 General data extracted (no satellite catalog data found)")
                    self.log_message(f"   📁 File processed: {os.path.basename(file_path)}")
            
            else:
                self.failed_extractions += 1
                self.log_updated.emit(f"⚠️ Failed to save data for: {url}")
            
            return True
            
        except Exception as e:
            self.failed_extractions += 1
            self.error_updated.emit(f"❌ Failed to process {url}: {e}")
            return False
    
    def update_progress(self, current, total):
        """Update file-level progress (does not affect main percent bar)"""
        try:
            self.files_progress.setMaximum(total)
            self.files_progress.setValue(current)
            self.files_progress.setFormat(f"Files: {current}/{total}")
            self.files_progress.setVisible(True)
            self.current_status_label.setText(f"Processing file {current}/{total}")
            QApplication.processEvents()
        except Exception:
            pass
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
    
    def update_data_viewer_after_extraction(self):
        """Update data viewer after successful extraction"""
        try:
            # Update summary dashboard
            self.update_summary_dashboard()
            
            # Update catalog table
            self.update_catalog_table()
            
            # Add success entry to extraction log
            self.add_extraction_log_entry("Data extraction completed successfully", "success")
            
        except Exception as e:
            self.log_error(f"Failed to update data viewer after extraction: {e}")
    
    def add_extraction_log_entry(self, message, level="info"):
        """Add entry to the live extraction log"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Color code based on level
            if level == "error":
                color = "#dc3545"
                icon = "❌"
            elif level == "warning":
                color = "#ffc107"
                icon = "⚠️"
            elif level == "success":
                color = "#28a745"
                icon = "✅"
            else:
                color = "#007acc"
                icon = "ℹ️"
            
            formatted_message = f'<span style="color: {color};">[{timestamp}] {icon} {message}</span>'
            self.extraction_log.append(formatted_message)
            
            # Auto-scroll to bottom
            self.extraction_log.ensureCursorVisible()
            
        except Exception as e:
            self.log_error(f"Failed to add extraction log entry: {e}")
    
    def show_satellite_details(self, item):
        """Show detailed view of a satellite dataset"""
        try:
            row = item.row()
            if row < self.catalog_table.rowCount():
                # Get the data for this row
                catalog_data = []
                for data in self.extracted_data:
                    if data.get('satellite_catalog'):
                        catalog_data.append(data)
                
                if row < len(catalog_data):
                    data = catalog_data[row]
                    catalog = data.get('satellite_catalog', {})
                    
                    # Create detailed view dialog
                    self.show_satellite_detail_dialog(catalog, data)
                    
        except Exception as e:
            self.log_error(f"Failed to show satellite details: {e}")
    
    def show_satellite_detail_dialog(self, catalog, full_data):
        """Show detailed satellite information in a dialog"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Satellite Details - {catalog.get('layer_name', 'Unknown')}")
            dialog.setGeometry(200, 200, 800, 600)
            
            layout = QVBoxLayout()
            
            # Create scrollable content
            scroll = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout()
            
            # Layer information
            info_group = QGroupBox("Layer Information")
            info_layout = QFormLayout()
            
            info_layout.addRow("Layer Name:", QLabel(str(catalog.get('layer_name', 'Unknown'))))
            info_layout.addRow("Provider:", QLabel(str(catalog.get('dataset_provider', 'Unknown'))))
            info_layout.addRow("Location:", QLabel(str(catalog.get('location', 'Unknown'))))
            info_layout.addRow("Pixel Size:", QLabel(str(catalog.get('pixel_size', 'Unknown'))))
            info_layout.addRow("DOI:", QLabel(str(catalog.get('doi', 'Unknown'))))
            
            info_group.setLayout(info_layout)
            scroll_layout.addWidget(info_group)
            
            # Date range
            date_group = QGroupBox("Temporal Coverage")
            date_layout = QFormLayout()
            date_range = catalog.get('date_range', {})
            date_layout.addRow("Start Date:", QLabel(str(date_range.get('start', 'Unknown'))))
            date_layout.addRow("End Date:", QLabel(str(date_range.get('end', 'Unknown'))))
            date_group.setLayout(date_layout)
            scroll_layout.addWidget(date_group)
            
            # Satellites and bands
            tech_group = QGroupBox("Technical Specifications")
            tech_layout = QFormLayout()
            
            satellites = catalog.get('satellites_used', [])
            tech_layout.addRow("Satellites:", QLabel(', '.join(satellites) if satellites else 'Unknown'))
            
            bands = catalog.get('band_information', [])
            tech_layout.addRow("Bands:", QLabel(', '.join(bands) if bands else 'Unknown'))
            
            categories = catalog.get('category_tags', [])
            tech_layout.addRow("Categories:", QLabel(', '.join(categories) if categories else 'Unknown'))
            
            tech_group.setLayout(tech_layout)
            scroll_layout.addWidget(tech_group)
            
            # Description
            if catalog.get('description'):
                desc_group = QGroupBox("Description")
                desc_layout = QVBoxLayout()
                desc_label = QLabel(str(catalog.get('description')))
                desc_label.setWordWrap(True)
                desc_layout.addWidget(desc_label)
                desc_group.setLayout(desc_layout)
                scroll_layout.addWidget(desc_group)
            
            # GEE Code
            if catalog.get('gee_code_snippet'):
                code_group = QGroupBox("GEE Code Snippet")
                code_layout = QVBoxLayout()
                code_text = QTextEdit()
                code_text.setPlainText(str(catalog.get('gee_code_snippet')))
                code_text.setMaximumHeight(150)
                code_text.setReadOnly(True)
                code_layout.addWidget(code_text)
                code_group.setLayout(code_layout)
                scroll_layout.addWidget(code_group)
            
            # Citations
            if catalog.get('citations'):
                cite_group = QGroupBox("Citations")
                cite_layout = QVBoxLayout()
                citations = catalog.get('citations', [])
                for citation in citations:
                    cite_label = QLabel(f"• {citation}")
                    cite_label.setWordWrap(True)
                    cite_layout.addWidget(cite_label)
                cite_group.setLayout(cite_layout)
                scroll_layout.addWidget(cite_group)
            
            # Terms of use
            if catalog.get('terms_of_use'):
                terms_group = QGroupBox("Terms of Use")
                terms_layout = QVBoxLayout()
                terms_label = QLabel(str(catalog.get('terms_of_use')))
                terms_label.setWordWrap(True)
                terms_layout.addWidget(terms_label)
                terms_group.setLayout(terms_layout)
                scroll_layout.addWidget(terms_group)
            
            scroll_widget.setLayout(scroll_layout)
            scroll.setWidget(scroll_widget)
            scroll.setWidgetResizable(True)
            
            layout.addWidget(scroll)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            self.log_error(f"Failed to show satellite detail dialog: {e}")
    
    def export_viewer_data(self):
        """Export the current viewer data to various formats"""
        try:
            # Create export dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Export Data")
            dialog.setGeometry(300, 300, 400, 200)
            
            layout = QVBoxLayout()
            
            # Export options
            options_group = QGroupBox("Export Options")
            options_layout = QVBoxLayout()
            
            csv_checkbox = QCheckBox("CSV Format")
            csv_checkbox.setChecked(True)
            json_checkbox = QCheckBox("JSON Format")
            json_checkbox.setChecked(True)
            summary_checkbox = QCheckBox("Summary Report (HTML)")
            summary_checkbox.setChecked(True)
            
            options_layout.addWidget(csv_checkbox)
            options_layout.addWidget(json_checkbox)
            options_layout.addWidget(summary_checkbox)
            options_group.setLayout(options_layout)
            
            # Export button
            export_btn = QPushButton("Export")
            export_btn.clicked.connect(lambda: self.perform_export(
                csv_checkbox.isChecked(),
                json_checkbox.isChecked(),
                summary_checkbox.isChecked(),
                dialog
            ))
            
            layout.addWidget(options_group)
            layout.addWidget(export_btn)
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            self.log_error(f"Failed to show export dialog: {e}")
    
    def perform_export(self, export_csv, export_json, export_summary, dialog):
        """Perform the actual data export"""
        try:
            export_dir = os.path.join(self.extractor.output_dir, "exports")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_csv:
                csv_file = os.path.join(export_dir, f"satellite_catalog_{timestamp}.csv")
                self.export_to_csv(csv_file)
                self.log_message(f"📊 Exported CSV: {os.path.basename(csv_file)}")
            
            if export_json:
                json_file = os.path.join(export_dir, f"satellite_catalog_{timestamp}.json")
                self.export_to_json(json_file)
                self.log_message(f"📄 Exported JSON: {os.path.basename(json_file)}")
            
            if export_summary:
                html_file = os.path.join(export_dir, f"satellite_summary_{timestamp}.html")
                self.export_to_html(html_file)
                self.log_message(f"🌐 Exported HTML: {os.path.basename(html_file)}")
            
            dialog.accept()
            QMessageBox.information(self, "Export Complete", "Data exported successfully!")
            
        except Exception as e:
            self.log_error(f"Failed to perform export: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")
    
    def export_to_csv(self, filename):
        """Export satellite catalog data to CSV"""
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Layer Name', 'Satellites', 'Date Range Start', 'Date Range End',
                    'Location', 'Provider', 'Pixel Size', 'Bands', 'Categories',
                    'Thumbnails Count', 'GEE Code Available', 'DOI', 'Description',
                    'Citations Count', 'Terms of Use'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for data in self.extracted_data:
                    if data.get('satellite_catalog'):
                        catalog = data['satellite_catalog']
                        date_range = catalog.get('date_range', {})
                        
                        writer.writerow({
                            'Layer Name': catalog.get('layer_name', ''),
                            'Satellites': ', '.join(catalog.get('satellites_used', [])),
                            'Date Range Start': date_range.get('start', ''),
                            'Date Range End': date_range.get('end', ''),
                            'Location': catalog.get('location', ''),
                            'Provider': catalog.get('dataset_provider', ''),
                            'Pixel Size': catalog.get('pixel_size', ''),
                            'Bands': ', '.join(catalog.get('band_information', [])),
                            'Categories': ', '.join(catalog.get('category_tags', [])),
                            'Thumbnails Count': len(catalog.get('thumbnails', [])),
                            'GEE Code Available': 'Yes' if catalog.get('gee_code_snippet') else 'No',
                            'DOI': catalog.get('doi', ''),
                            'Description': catalog.get('description', ''),
                            'Citations Count': len(catalog.get('citations', [])),
                            'Terms of Use': catalog.get('terms_of_use', '')
                        })
                        
        except Exception as e:
            raise Exception(f"CSV export failed: {e}")
    
    def export_to_json(self, filename):
        """Export satellite catalog data to JSON"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_datasets': len(self.extracted_data),
                'satellite_catalog': []
            }
            
            for data in self.extracted_data:
                if data.get('satellite_catalog'):
                    export_data['satellite_catalog'].append({
                        'metadata': {
                            'title': data.get('title', ''),
                            'file_path': data.get('file_path', ''),
                            'extraction_timestamp': data.get('timestamp', '')
                        },
                        'satellite_data': data['satellite_catalog']
                    })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"JSON export failed: {e}")
    
    def export_to_html(self, filename):
        """Export satellite catalog data to HTML report"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Satellite Catalog Summary Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #007acc; color: white; padding: 20px; border-radius: 5px; }}
                    .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
                    .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; }}
                    .stat-number {{ font-size: 2em; font-weight: bold; color: #007acc; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .success {{ color: #28a745; }}
                    .warning {{ color: #ffc107; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🛰️ Satellite Catalog Summary Report</h1>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{len(self.extracted_data)}</div>
                        <div>Total Datasets</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(set(data.get('satellite_catalog', {}).get('dataset_provider', '') for data in self.extracted_data if data.get('satellite_catalog'))) - 1}</div>
                        <div>Data Providers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len([data for data in self.extracted_data if data.get('satellite_catalog', {}).get('gee_code_snippet')])}</div>
                        <div>With GEE Code</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len([data for data in self.extracted_data if data.get('satellite_catalog', {}).get('doi')])}</div>
                        <div>With DOI</div>
                    </div>
                </div>
                
                <h2>📊 Satellite Catalog Data</h2>
                <table>
                    <tr>
                        <th>Layer Name</th>
                        <th>Provider</th>
                        <th>Location</th>
                        <th>Date Range</th>
                        <th>Status</th>
                    </tr>
            """
            
            for data in self.extracted_data:
                if data.get('satellite_catalog'):
                    catalog = data['satellite_catalog']
                    date_range = catalog.get('date_range', {})
                    status_class = "success" if catalog.get('layer_name') else "warning"
                    status_text = "Complete" if catalog.get('layer_name') else "Incomplete"
                    
                    html_content += f"""
                    <tr>
                        <td>{catalog.get('layer_name', 'Unknown')}</td>
                        <td>{catalog.get('dataset_provider', 'Unknown')}</td>
                        <td>{catalog.get('location', 'Unknown')}</td>
                        <td>{date_range.get('start', '')} to {date_range.get('end', '')}</td>
                        <td class="{status_class}">{status_text}</td>
                    </tr>
                    """
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            raise Exception(f"HTML export failed: {e}")
    
    def show_filter_dialog(self):
        """Show dialog for filtering catalog data"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Filter Satellite Catalog")
            dialog.setGeometry(300, 300, 400, 300)
            
            layout = QVBoxLayout()
            
            # Filter options
            filter_group = QGroupBox("Filter Options")
            filter_layout = QFormLayout()
            
            provider_filter = QLineEdit()
            provider_filter.setPlaceholderText("Filter by provider...")
            
            location_filter = QLineEdit()
            location_filter.setPlaceholderText("Filter by location...")
            
            has_gee_code = QCheckBox("Has GEE Code")
            has_doi = QCheckBox("Has DOI")
            
            filter_layout.addRow("Provider:", provider_filter)
            filter_layout.addRow("Location:", location_filter)
            filter_layout.addRow("", has_gee_code)
            filter_layout.addRow("", has_doi)
            
            filter_group.setLayout(filter_layout)
            
            # Apply button
            apply_btn = QPushButton("Apply Filter")
            apply_btn.clicked.connect(lambda: self.apply_catalog_filter(
                provider_filter.text(),
                location_filter.text(),
                has_gee_code.isChecked(),
                has_doi.isChecked(),
                dialog
            ))
            
            layout.addWidget(filter_group)
            layout.addWidget(apply_btn)
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            self.log_error(f"Failed to show filter dialog: {e}")
    
    def apply_catalog_filter(self, provider, location, has_gee, has_doi, dialog):
        """Apply filters to the catalog table"""
        try:
            # Store filter criteria
            self.current_filters = {
                'provider': provider.lower(),
                'location': location.lower(),
                'has_gee_code': has_gee,
                'has_doi': has_doi
            }
            
            # Apply filters to table
            self.update_catalog_table_with_filters()
            
            dialog.accept()
            self.log_message(f"🔍 Applied filters: Provider='{provider}', Location='{location}', GEE={has_gee}, DOI={has_doi}")
            
        except Exception as e:
            self.log_error(f"Failed to apply filters: {e}")
    
    def update_catalog_table_with_filters(self):
        """Update catalog table with applied filters"""
        try:
            # Filter the data
            filtered_data = []
            for data in self.extracted_data:
                if data.get('satellite_catalog'):
                    catalog = data['satellite_catalog']
                    
                    # Apply filters
                    if self.current_filters.get('provider') and catalog.get('dataset_provider', '').lower() != self.current_filters['provider']:
                        continue
                    
                    if self.current_filters.get('location') and catalog.get('location', '').lower() != self.current_filters['location']:
                        continue
                    
                    if self.current_filters.get('has_gee_code') and not catalog.get('gee_code_snippet'):
                        continue
                    
                    if self.current_filters.get('has_doi') and not catalog.get('doi'):
                        continue
                    
                    filtered_data.append(data)
            
            # Update table with filtered data
            self.catalog_table.setRowCount(len(filtered_data))
            
            for row, data in enumerate(filtered_data):
                # ... (same table population logic as update_catalog_table)
                # This would be the same as the existing update_catalog_table method
                pass
                
        except Exception as e:
            self.log_error(f"Failed to update catalog table with filters: {e}")
    
    def analyze_extracted_data(self):
        """Analyze the extracted satellite catalog data"""
        try:
            analysis_text = "🔍 Satellite Catalog Data Analysis\n"
            analysis_text += "=" * 50 + "\n\n"
            
            if not self.extracted_data:
                analysis_text += "No data available for analysis.\n"
                self.analysis_text.setPlainText(analysis_text)
                return
            
            # Basic statistics
            total_datasets = len(self.extracted_data)
            complete_datasets = len([d for d in self.extracted_data if d.get('satellite_catalog', {}).get('layer_name')])
            incomplete_datasets = total_datasets - complete_datasets
            
            analysis_text += f"📊 Basic Statistics:\n"
            analysis_text += f"   • Total datasets processed: {total_datasets}\n"
            analysis_text += f"   • Complete datasets: {complete_datasets}\n"
            analysis_text += f"   • Incomplete datasets: {incomplete_datasets}\n"
            analysis_text += f"   • Completion rate: {(complete_datasets/total_datasets*100):.1f}%\n\n"
            
            # Provider analysis
            providers = {}
            for data in self.extracted_data:
                if data.get('satellite_catalog', {}).get('dataset_provider'):
                    provider = data['satellite_catalog']['dataset_provider']
                    providers[provider] = providers.get(provider, 0) + 1
            
            if providers:
                analysis_text += f"🏢 Data Provider Analysis:\n"
                for provider, count in sorted(providers.items(), key=lambda x: x[1], reverse=True):
                    analysis_text += f"   • {provider}: {count} datasets\n"
                analysis_text += "\n"
            
            # Technical analysis
            gee_code_count = len([d for d in self.extracted_data if d.get('satellite_catalog', {}).get('gee_code_snippet')])
            doi_count = len([d for d in self.extracted_data if d.get('satellite_catalog', {}).get('doi')])
            thumbnail_count = sum(len(d.get('satellite_catalog', {}).get('thumbnails', [])) for d in self.extracted_data)
            
            analysis_text += f"⚙️ Technical Analysis:\n"
            analysis_text += f"   • Datasets with GEE code: {gee_code_count} ({(gee_code_count/total_datasets*100):.1f}%)\n"
            analysis_text += f"   • Datasets with DOI: {doi_count} ({(doi_count/total_datasets*100):.1f}%)\n"
            analysis_text += f"   • Total thumbnails: {thumbnail_count}\n\n"
            
            # Date range analysis
            date_ranges = []
            for data in self.extracted_data:
                if data.get('satellite_catalog', {}).get('date_range', {}).get('start'):
                    date_ranges.append(data['satellite_catalog']['date_range']['start'])
            
            if date_ranges:
                analysis_text += f"📅 Temporal Analysis:\n"
                analysis_text += f"   • Earliest date: {min(date_ranges)}\n"
                analysis_text += f"   • Latest date: {max(date_ranges)}\n"
                analysis_text += f"   • Date ranges found: {len(date_ranges)}\n\n"
            
            # Recommendations
            analysis_text += f"💡 Recommendations:\n"
            if incomplete_datasets > 0:
                analysis_text += f"   • Review {incomplete_datasets} incomplete datasets for missing information\n"
            if gee_code_count < total_datasets * 0.8:
                analysis_text += f"   • Consider improving GEE code extraction for better coverage\n"
            if doi_count < total_datasets * 0.5:
                analysis_text += f"   • DOI extraction could be enhanced for better citation tracking\n"
            
            self.analysis_text.setPlainText(analysis_text)
            
        except Exception as e:
            self.log_error(f"Failed to analyze data: {e}")
            self.analysis_text.setPlainText(f"Analysis failed: {e}")
    
    def generate_analysis_report(self):
        """Generate a comprehensive analysis report"""
        try:
            report_dir = os.path.join(self.extractor.output_dir, "reports")
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(report_dir, f"analysis_report_{timestamp}.html")
            
            # Generate comprehensive HTML report
            self.generate_comprehensive_report(report_file)
            
            self.log_message(f"📋 Generated analysis report: {os.path.basename(report_file)}")
            QMessageBox.information(self, "Report Generated", f"Analysis report saved to:\n{report_file}")
            
        except Exception as e:
            self.log_error(f"Failed to generate analysis report: {e}")
            QMessageBox.critical(self, "Report Error", f"Failed to generate report: {e}")
    
    def generate_comprehensive_report(self, filename):
        """Generate a comprehensive HTML analysis report"""
        try:
            # This would create a detailed HTML report with charts and analysis
            # For now, we'll create a basic enhanced version
            self.export_to_html(filename)
            
        except Exception as e:
            raise Exception(f"Comprehensive report generation failed: {e}")
    
    def show_catalog_context_menu(self, position):
        """Show context menu for catalog table items"""
        try:
            menu = QMenu()
            
            # Get the item under the cursor
            item = self.catalog_table.itemAt(position)
            if item:
                row = item.row()
                
                # Add context menu actions
                view_details = menu.addAction("👁️ View Details")
                export_row = menu.addAction("📤 Export Row")
                open_source = menu.addAction("🌐 Open Source")
                
                # Connect actions
                view_details.triggered.connect(lambda: self.show_satellite_details(item))
                export_row.triggered.connect(lambda: self.export_table_row(row))
                open_source.triggered.connect(lambda: self.open_source_file(row))
                
                menu.exec(self.catalog_table.mapToGlobal(position))
                
        except Exception as e:
            self.log_error(f"Failed to show catalog context menu: {e}")
    
    def export_table_row(self, row):
        """Export a single table row to JSON"""
        try:
            if row < self.catalog_table.rowCount():
                # Get the data for this row
                catalog_data = []
                for data in self.extracted_data:
                    if data.get('satellite_catalog'):
                        catalog_data.append(data)
                
                if row < len(catalog_data):
                    data = catalog_data[row]
                    
                    # Export to file
                    export_dir = os.path.join(self.extractor.output_dir, "exports")
                    if not os.path.exists(export_dir):
                        os.makedirs(export_dir)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(export_dir, f"row_{row}_{timestamp}.json")
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    self.log_message(f"📤 Exported row {row} to: {os.path.basename(filename)}")
                    
        except Exception as e:
            self.log_error(f"Failed to export table row: {e}")
    
    def open_source_file(self, row):
        """Open the source file for a table row"""
        try:
            if row < self.catalog_table.rowCount():
                # Get the data for this row
                catalog_data = []
                for data in self.extracted_data:
                    if data.get('satellite_catalog'):
                        catalog_data.append(data)
                
                if row < len(catalog_data):
                    data = catalog_data[row]
                    source_file = data.get('file_path', '')
                    
                    if source_file and os.path.exists(source_file):
                        os.startfile(source_file)
                        self.log_message(f"🌐 Opened source file: {os.path.basename(source_file)}")
                    else:
                        QMessageBox.warning(self, "File Not Found", "Source file not found or accessible.")
                        
        except Exception as e:
            self.log_error(f"Failed to open source file: {e}")
    
    def update_real_time_viewer(self, file_path, data):
        """Update real-time data viewer with current extraction progress"""
        try:
            # Update current file being processed
            self.current_file_label.setText(f"📁 {os.path.basename(file_path)}")
            
            # Update extraction status
            if data.get('satellite_catalog'):
                catalog = data['satellite_catalog']
                layer_name = catalog.get('layer_name', 'Unknown')
                self.current_status_label.setText(f"🛰️ Extracting: {layer_name}")
                
                # Add to live extraction log
                self.add_extraction_log_entry(f"Processing satellite: {layer_name}", "info")
            else:
                self.current_status_label.setText("📊 Extracting general data...")
                self.add_extraction_log_entry(f"Processing file: {os.path.basename(file_path)}", "info")
            
            # Update progress bars
            self.update_extraction_progress()
            
        except Exception as e:
            self.log_error(f"Failed to update real-time viewer: {e}")
    
    def update_summary_dashboard(self):
        """Update the summary dashboard with current statistics"""
        try:
            # Count unique satellites
            unique_satellites = set()
            unique_providers = set()
            total_datasets = 0
            
            for data in self.extracted_data:
                if data.get('satellite_catalog'):
                    catalog = data['satellite_catalog']
                    if catalog.get('layer_name'):
                        unique_satellites.add(catalog['layer_name'])
                    if catalog.get('dataset_provider'):
                        unique_providers.add(catalog['dataset_provider'])
                    total_datasets += 1
            
            # Update labels
            self.total_satellites_label.setText(str(len(unique_satellites)))
            self.total_datasets_label.setText(str(total_datasets))
            self.total_providers_label.setText(str(len(unique_providers)))
            
            # Update extraction status
            if self.is_extracting:
                self.extraction_status_label.setText("Running")
                self.extraction_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #28a745;")
            else:
                self.extraction_status_label.setText("Idle")
                self.extraction_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #6c757d;")
            
            # Update recent activity
            self.recent_activity_list.clear()
            recent_items = []
            for data in self.extracted_data[-10:]:  # Last 10 items
                if data.get('satellite_catalog', {}).get('layer_name'):
                    layer_name = data['satellite_catalog']['layer_name']
                    timestamp = data.get('timestamp', 'Unknown')
                    recent_items.append(f"📡 {layer_name} - {timestamp}")
            
            for item in recent_items:
                self.recent_activity_list.addItem(item)
                
        except Exception as e:
            self.log_error(f"Failed to update summary dashboard: {e}")
    
    def update_catalog_table(self):
        """Update the satellite catalog table with extracted data"""
        try:
            # Filter data to only show satellite catalog entries
            catalog_data = []
            for data in self.extracted_data:
                if data.get('satellite_catalog'):
                    catalog_data.append(data)
            
            self.catalog_table.setRowCount(len(catalog_data))
            
            for row, data in enumerate(catalog_data):
                catalog = data.get('satellite_catalog', {})
                
                # Layer Name
                layer_name = html.unescape(str(catalog.get('layer_name', 'Unknown')))
                self.catalog_table.setItem(row, 0, QTableWidgetItem(layer_name))
                
                # Satellites
                satellites = catalog.get('satellites_used', [])
                satellites_str = ', '.join(satellites) if satellites else 'Unknown'
                self.catalog_table.setItem(row, 1, QTableWidgetItem(html.unescape(satellites_str)))
                
                # Date Range
                date_range = catalog.get('date_range', {})
                date_str = f"{date_range.get('start', '')} to {date_range.get('end', '')}"
                self.catalog_table.setItem(row, 2, QTableWidgetItem(date_str))
                
                # Location
                location = html.unescape(str(catalog.get('location', 'Unknown')))
                self.catalog_table.setItem(row, 3, QTableWidgetItem(location))
                
                # Provider
                provider = html.unescape(str(catalog.get('dataset_provider', 'Unknown')))
                self.catalog_table.setItem(row, 4, QTableWidgetItem(provider))
                
                # Pixel Size
                pixel_size = html.unescape(str(catalog.get('pixel_size', 'Unknown')))
                self.catalog_table.setItem(row, 5, QTableWidgetItem(pixel_size))
                
                # Bands
                bands = catalog.get('band_information', [])
                bands_str = ', '.join(bands) if bands else 'Unknown'
                self.catalog_table.setItem(row, 6, QTableWidgetItem(html.unescape(bands_str)))
                
                # Categories
                categories = catalog.get('category_tags', [])
                categories_str = ', '.join(categories) if categories else 'Unknown'
                self.catalog_table.setItem(row, 7, QTableWidgetItem(html.unescape(categories_str)))
                
                # Thumbnails
                thumbnails = catalog.get('thumbnails', [])
                thumbnails_count = len(thumbnails) if thumbnails else 0
                self.catalog_table.setItem(row, 8, QTableWidgetItem(str(thumbnails_count)))
                
                # GEE Code
                gee_code = catalog.get('gee_code_snippet', '')
                gee_code_str = 'Found' if gee_code else 'Not found'
                self.catalog_table.setItem(row, 9, QTableWidgetItem(gee_code_str))
                
                # DOI
                doi = html.unescape(str(catalog.get('doi', 'Unknown')))
                self.catalog_table.setItem(row, 10, QTableWidgetItem(doi))
                
                # Description
                description = html.unescape(str(catalog.get('description', 'Unknown')))
                desc_str = description[:50] + "..." if len(description) > 50 else description
                self.catalog_table.setItem(row, 11, QTableWidgetItem(desc_str))
                
                # Citations
                citations = catalog.get('citations', [])
                citations_count = len(citations) if citations else 0
                self.catalog_table.setItem(row, 12, QTableWidgetItem(str(citations_count)))
                
                # Terms
                terms = html.unescape(str(catalog.get('terms_of_use', 'Unknown')))
                terms_str = terms[:30] + "..." if len(terms) > 30 else terms
                self.catalog_table.setItem(row, 13, QTableWidgetItem(terms_str))
                
                # Status (computed)
                completeness = 0
                if catalog.get('layer_name'): completeness += 1
                if catalog.get('date_range', {}).get('start') or catalog.get('date_range', {}).get('end'): completeness += 1
                if catalog.get('dataset_provider'): completeness += 1
                if catalog.get('gee_code_snippet'): completeness += 1
                if catalog.get('doi'): completeness += 1
                status = '✅ Complete' if completeness >= 4 else ('➕ Partial' if completeness >= 2 else '⚠️ Incomplete')
                self.catalog_table.setItem(row, 14, QTableWidgetItem(status))
                
        except Exception as e:
            self.log_error(f"Failed to update catalog table: {e}")
    
    def update_extraction_progress(self):
        """Update the extraction progress indicators"""
        try:
            # Update file progress
            if hasattr(self, 'total_files'):
                self.files_progress.setMaximum(self.total_files)
                self.files_progress.setValue(self.total_processed)
            
            # Update link progress (if following links)
            if hasattr(self, 'total_links'):
                self.links_progress.setMaximum(self.total_links)
                self.links_progress.setValue(self.processed_urls.__len__())
            
            # Update data progress
            self.data_progress.setMaximum(len(self.extracted_data) + 10)  # Estimate
            self.data_progress.setValue(len(self.extracted_data))
            
        except Exception as e:
            self.log_error(f"Failed to update extraction progress: {e}")
    
    def extraction_finished(self):
        """Cleanup after extraction"""
        self.is_extracting = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Ready - Add HTML files to begin")
        
        # Update extraction status
        self.extraction_status_label.setText("Completed")
        self.extraction_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #28a745;")
        
        # Update current status
        self.current_file_label.setText("No file being processed")
        self.current_status_label.setText("Extraction completed")
        
        # Add completion entry to extraction log
        self.add_extraction_log_entry("✅ Extraction completed successfully", "success")
        
        # End comprehensive logging
        self.end_extraction_logging()
    
    def start_extraction_logging(self):
        """Start comprehensive logging for extraction session"""
        self.start_time = datetime.now()
        session_id = self.start_time.strftime('%Y%m%d_%H%M%S')
        
        self.log_message(f"🚀 Starting local extraction session: {session_id}")
        self.log_message(f"📊 Initial statistics: Processed={self.total_processed}, Success={self.successful_extractions}, Failed={self.failed_extractions}")
        self.log_message(f"⚙️ Configuration: Batch size={self.config['processing']['batch_size']}")
        self.log_message(f"🔄 Overwrite mode: {'Enabled' if self.overwrite_checkbox.isChecked() else 'Disabled'}")
    
    def end_extraction_logging(self):
        """End extraction session with comprehensive statistics"""
        if self.start_time:
            duration = datetime.now() - self.start_time
            self.log_message(f"⏱️ Extraction session duration: {duration}")
        
        self.log_message(f"📊 Final statistics:")
        self.log_message(f"   Total processed: {self.total_processed}")
        self.log_message(f"   Successful extractions: {self.successful_extractions}")
        self.log_message(f"   Failed extractions: {self.failed_extractions}")
        
        if self.total_processed > 0:
            success_rate = (self.successful_extractions / self.total_processed) * 100
            self.log_message(f"   Success rate: {success_rate:.1f}%")
        
        self.log_message(f"💾 Data files created: {len(self.extracted_data)}")
        self.log_message(f"📁 Output directory: {self.extractor.output_dir}")
    
    def log_message(self, message):
        """Log message to console (thread-safe)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = f"[{timestamp}] {message}"
        try:
            if QThread.currentThread() != self.thread():
                QTimer.singleShot(0, lambda: self._append_console(text))
            else:
                self._append_console(text)
        except Exception:
            # Fallback without UI safety if scheduling fails
            self._append_console(text)
    
    def _append_console(self, text):
        self.console.append(text)
        self.console.ensureCursorVisible()
        # Truncate console to prevent memory bloat
        try:
            max_lines = self.config.get('logging', {}).get('max_console_lines', 2000)
            if self.console.document().blockCount() > max_lines:
                self.console.clear()
                self.console.append("[log truncated]\n" + text)
        except Exception:
            pass
    
    def log_error(self, message):
        """Log error to console (thread-safe)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = f"[{timestamp}] ERROR: {message}"
        try:
            if QThread.currentThread() != self.thread():
                QTimer.singleShot(0, lambda: self._append_console(text))
            else:
                self._append_console(text)
        except Exception:
            self._append_console(text)
    
    def show_context_menu(self, position):
        """Show context menu for table items - DEPRECATED"""
        pass  # This method is no longer used with the new UI
    
    def open_json_file(self, row):
        """Open JSON file in default application - DEPRECATED"""
        pass  # This method is no longer used with the new UI
    
    def open_html_file(self, row):
        """Open HTML file in default application - DEPRECATED"""
        pass  # This method is no longer used with the new UI
    
    def refresh_data_viewer(self):
        """Refresh all data viewer components"""
        self.update_summary_dashboard()
        self.update_catalog_table()
        self.update_extraction_progress()
        self.log_message("🔄 Data viewer refreshed")
    
    def clear_extracted_data(self):
        """Clear extracted data from memory"""
        self.extracted_data = []
        self.processed_files.clear()
        self.total_processed = 0
        self.successful_extractions = 0
        self.failed_extractions = 0
        
        # Update all data viewer components
        self.update_summary_dashboard()
        self.update_catalog_table()
        self.update_extraction_progress()
        
        self.log_message("🗑️ Extracted data cleared from memory")
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        try:
            os.startfile(self.extractor.output_dir)
            self.log_message(f"📁 Opened output folder: {self.extractor.output_dir}")
            try:
                _log_json('ui_open_output', path=self.extractor.output_dir)
            except Exception:
                pass
        except Exception as e:
            self.log_error(f"❌ Failed to open output folder: {e}")
    
    def show_statistics(self):
        """Show statistics about the extracted data"""
        if not self.extracted_data:
            QMessageBox.information(self, "Statistics", "No data available for statistics.")
            return
        
        total_items = len(self.extracted_data)
        total_size = sum(data.get('file_size', 0) for data in self.extracted_data)
        total_text = sum(data.get('text_length', 0) for data in self.extracted_data)
        total_links = sum(data.get('link_count', 0) for data in self.extracted_data)
        total_images = sum(data.get('image_count', 0) for data in self.extracted_data)
        total_forms = sum(data.get('form_count', 0) for data in self.extracted_data)
        
        stats_text = f"""
        📊 LOCAL EXTRACTION STATISTICS
        
        Total Items: {total_items}
        Total File Size: {total_size:,} characters
        Total Text Length: {total_text:,} characters
        Total Links: {total_links:,}
        Total Images: {total_images:,}
        Total Forms: {total_forms:,}
        
        Average File Size: {total_size // total_items:,} characters
        Average Text Length: {total_text // total_items:,} characters
        Average Links per Page: {total_links // total_items:,}
        Average Images per Page: {total_images // total_items:,}
        Average Forms per Page: {total_forms // total_items:,}
        
        Output Directory: {self.extractor.output_dir}
        Thumbnails Directory: {self.extractor.thumbnails_dir}
        """
        
        QMessageBox.information(self, "Extraction Statistics", stats_text)
    
    def apply_dark_theme(self):
        """Apply dark theme styling"""
        # Dark theme colors
        dark_bg = "#2b2b2b"
        dark_text = "#ffffff"
        dark_alt_bg = "#3c3c3c"
        dark_border = "#555555"
        dark_highlight = "#007acc"
        
        # Main application styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {dark_bg};
                color: {dark_text};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }}
            
            QGroupBox {{
                border: 2px solid {dark_border};
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
                color: {dark_text};
                background-color: {dark_alt_bg};
                padding: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {dark_highlight};
            }}
            
            QLineEdit, QTextEdit, QListWidget {{
                background-color: {dark_alt_bg};
                border: 2px solid {dark_border};
                border-radius: 5px;
                padding: 8px;
                color: {dark_text};
                selection-background-color: {dark_highlight};
            }}
            
            QPushButton {{
                background-color: {dark_highlight};
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: #005a9e;
            }}
            
            QPushButton:disabled {{
                background-color: {dark_border};
                color: #888888;
            }}
            
            QProgressBar {{
                border: 2px solid {dark_border};
                border-radius: 5px;
                text-align: center;
                background-color: {dark_alt_bg};
                color: {dark_text};
            }}
            
            QProgressBar::chunk {{
                background-color: {dark_highlight};
                border-radius: 3px;
            }}
            
            QTableWidget {{
                background-color: {dark_alt_bg};
                alternate-background-color: {dark_bg};
                gridline-color: {dark_border};
                border: 2px solid {dark_border};
                border-radius: 5px;
                color: {dark_text};
                selection-background-color: {dark_highlight};
                selection-color: white;
            }}
            
            QHeaderView::section {{
                background-color: {dark_border};
                color: {dark_text};
                padding: 8px;
                border: 1px solid {dark_alt_bg};
                font-weight: bold;
            }}
        """)
    
    def show_summary(self):
        """Show extraction summary"""
        summary = f"""
📊 Local Extraction Summary:
   Total processed: {self.total_processed}
   Successful extractions: {self.successful_extractions}
   Failed exractions: {self.failed_extractions}
   Data files: {len(self.extracted_data)}
   Output directory: {self.extractor.output_dir}
        """
        self.log_message(summary)

    def update_extraction_percent(self, percent):
        """Thread-safe update for percent-based extraction progress"""
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(int(percent))
        self.progress_bar.setVisible(True)
        self.current_status_label.setText(f"Extracting data: {int(percent)}%")

    def _on_realtime_viewer_updated(self, file_path, data):
        """Thread-safe wrapper to update the real-time viewer from signals"""
        self.update_real_time_viewer(file_path, data)

    def _emit_heartbeat(self):
        try:
            self._hb_counter += 1
            if self._hb_counter % 5 == 0:
                self.log_message("[heartbeat] UI alive")
                _log_json('ui_heartbeat', count=self._hb_counter)
        except Exception:
            pass

def main():
    """Main function"""
    _logger.info("ui_start")
    _log_json('ui_start')
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("Satellite Catalog Extractor - Earth Engine Pages")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Flutter Earth")
    
    window = LocalHTMLDataExtractorUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()