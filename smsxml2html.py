#!/usr/bin/env python3

# SMS XML to HTML App Style (Python 3 Compatible - Embedded Images Edition)
# Original by Christopher Mitchell, Ph.D.
# Modified for Python 3 compatibility, embedded images, and group conversation support
# Original: https://github.com/KermMartian/smsxml2html
# Fork: https://github.com/hondaguy900/smsxml2html-appstyle

import os
import hashlib
import sys
from lxml import etree
import argparse
import base64
import re
import time
import datetime
import locale
from pathlib import Path

STYLESHEET_TEMPLATE = """
body {
	font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
	margin: 0;
	padding: 0;
	background-color: #e0e0e0;
}
.phone-view {
	max-width: 1000px;
	margin: 0 auto;
	background-color: white;
	min-height: 100vh;
	box-shadow: 0 0 20px rgba(0,0,0,0.1);
}
.header {
	background-color: #2196F3;
	color: white;
	padding: 15px 20px;
    min-height: 60px;
	display: flex;
	align-items: center;
	gap: 15px;
	box-shadow: 0 2px 4px rgba(0,0,0,0.2);
	position: sticky;
	top: 0;
	z-index: 101;
}
.back-button {
	background: none;
	border: none;
	color: white;
	font-size: 24px;
	cursor: pointer;
	padding: 0;
	margin: 0;
	display: none;
}
.back-button:hover {
	opacity: 0.8;
}
.header h1 {
	margin: 0;
	font-size: 20px;
	font-weight: 500;
	flex: 1;
    line-height: 1.3;
}
.header-search {
	width: 300px;
}
.header-search input {
	width: 100%;
	padding: 8px 12px;
	border: none;
	border-radius: 20px;
	font-size: 14px;
	outline: none;
	box-sizing: border-box;
	background-color: rgba(255, 255, 255, 0.9);
}
.header-search input:focus {
	background-color: white;
}
.header-search.hidden {
	display: none;
}
.conversation-list {
	padding: 0;
}
.conversation-item {
	padding: 15px 20px;
	border-bottom: 1px solid #e0e0e0;
	cursor: pointer;
	transition: background-color 0.2s;
	display: flex;
	align-items: center;
}
.conversation-item:hover {
	background-color: #f5f5f5;
}
.conversation-item:active {
	background-color: #e8e8e8;
}
.conversation-avatar {
	width: 50px;
	height: 50px;
	border-radius: 50%;
	background-color: #2196F3;
	color: white;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 20px;
	font-weight: bold;
	margin-right: 15px;
	flex-shrink: 0;
}
.conversation-avatar-group {
	width: 50px;
	height: 50px;
	margin-right: 15px;
	flex-shrink: 0;
	display: grid;
	gap: 2px;
	position: relative;
}
.conversation-avatar-group.group-2 {
	grid-template-columns: 24px 24px;
	grid-template-rows: 50px;
	align-items: center;
}
.conversation-avatar-group.group-3 {
	grid-template-columns: 24px 24px;
	grid-template-rows: 24px 24px;
	align-content: center;
}
.conversation-avatar-group.group-4 {
	grid-template-columns: 24px 24px;
	grid-template-rows: 24px 24px;
}
.conversation-avatar-group .mini-avatar {
	background-color: #2196F3;
	color: white;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 11px;
	font-weight: bold;
	width: 24px;
	height: 24px;
}
.conversation-avatar-group.group-3 .mini-avatar:first-child {
	grid-column: 1 / -1;
	justify-self: center;
}
.conversation-info {
	flex: 1;
	min-width: 0;
}
.conversation-name {
	font-weight: 600;
	font-size: 16px;
	margin-bottom: 4px;
	color: #333;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
.conversation-preview {
	font-size: 14px;
	color: #666;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.conversation-meta {
	text-align: right;
	flex-shrink: 0;
	margin-left: 10px;
}
.conversation-date {
	font-size: 12px;
	color: #999;
	white-space: nowrap;
	margin-bottom: 4px;
}
.conversation-count {
	background-color: #2196F3;
	color: white;
	border-radius: 10px;
	padding: 2px 8px;
	font-size: 12px;
	font-weight: bold;
    text-align: center;
}
.conversation-view {
	display: none;
	padding-top: 90px;
}
.conversation-view.no-pagination {
	padding-top: 0;
}
.conversation-details {
	padding: 15px 20px;
	background-color: #f9f9f9;
	border-bottom: 2px solid #e0e0e0;
}
.conversation-details p {
	margin: 5px 0;
	font-size: 14px;
	color: #666;
}
.conversation-details strong {
	color: #333;
}
.month-jump {
	background-color: white;
	padding: 12px 20px;
	border-bottom: 1px solid #e0e0e0;
	font-size: 13px;
	overflow-x: auto;
	white-space: nowrap;
}
.month-jump a {
	color: #2196F3;
	text-decoration: none;
	padding: 0 8px;
}
.month-jump a:hover {
	text-decoration: underline;
}

.pagination-controls {
	background-color: #f9f9f9;
	border: 1px solid #e0e0e0;
	padding: 15px 20px;
	display: flex;
	justify-content: space-between;
	align-items: center;
	position: fixed;
	top: 90px;
	left: 50%;
	transform: translateX(-50%);
	width: 100%;
	max-width: 1000px;
	z-index: 100;
	box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	box-sizing: border-box;
}
.pagination-controls button {
	background-color: #2196F3;
	color: white;
	border: none;
	padding: 10px 20px;
	border-radius: 4px;
	cursor: pointer;
	font-size: 14px;
	font-weight: 500;
	transition: background-color 0.2s;
}
.pagination-controls button:hover:not(:disabled) {
	background-color: #1976D2;
}
.pagination-controls button:disabled {
	background-color: #ccc;
	cursor: not-allowed;
	opacity: 0.6;
}
.pagination-info {
	font-size: 14px;
	color: #666;
	font-weight: 500;
}
h2 {
	color: #555;
	margin: 20px 20px 10px;
	padding: 10px 0;
	font-size: 14px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
	color: #999;
}
.messages_table {
	width: 100%;
	border-collapse: collapse;
}
.messages_table th {
	background-color: #f0f0f0;
	padding: 10px;
	text-align: left;
	font-weight: 600;
	font-size: 12px;
	border-bottom: 1px solid #e0e0e0;
	color: #666;
	text-transform: uppercase;
}
.messages_table td {
	padding: 12px 10px;
	border-bottom: 1px solid #f0f0f0;
	vertical-align: top;
	font-size: 14px;
	word-wrap: break-word;
	word-break: break-word;
	overflow-wrap: break-word;
	max-width: 0;
}
.msg_type {
	font-weight: 600;
	font-size: 11px;
	text-transform: uppercase;
}
.msg_received {
	background-color: #f0f8ff;
}
.msg_sent {
	background-color: #f0fff0;
}
.msg_date {
	white-space: nowrap;
	color: #999;
	font-size: 12px;
}
.msg_contact {
	color: #333;
	font-weight: 600;
	font-size: 13px;
	word-wrap: break-word;
	overflow-wrap: break-word;
}
.mms_img {
	max-width: 100%;
	max-height: 400px;
	margin-top: 10px;
	border-radius: 8px;
	display: block;
	cursor: pointer;
	transition: opacity 0.2s;
}
.mms_img:hover {
	opacity: 0.9;
}
.image-modal {
	display: none;
	position: fixed;
	z-index: 1000;
	left: 0;
	top: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0,0,0,0.9);
	cursor: pointer;
}
.image-modal img {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	max-width: 95%;
	max-height: 95%;
	border-radius: 8px;
}
.image-modal-close {
	position: absolute;
	top: 20px;
	right: 35px;
	color: #f1f1f1;
	font-size: 40px;
	font-weight: bold;
	cursor: pointer;
}
.image-modal-close:hover {
	color: #bbb;
}
.single-conversation {
	padding: 20px;
}
.single-conversation h1 {
	color: #333;
	border-bottom: 2px solid #2196F3;
	padding-bottom: 10px;
	margin-bottom: 20px;
}

/* Dark Mode Styles */
body.dark-mode {
	background-color: #1a1a1a;
}
body.dark-mode .phone-view {
	background-color: #2d2d2d;
	color: #e0e0e0;
}
body.dark-mode .header {
	background-color: #1976D2;
}
body.dark-mode .header-search input {
	background-color: rgba(255, 255, 255, 0.15);
	color: white;
}
body.dark-mode .header-search input::placeholder {
	color: rgba(255, 255, 255, 0.6);
}
body.dark-mode .header-search input:focus {
	background-color: rgba(255, 255, 255, 0.25);
}
body.dark-mode .conversation-item {
	border-bottom: 1px solid #404040;
}
body.dark-mode .conversation-item:hover {
	background-color: #3a3a3a;
}
body.dark-mode .conversation-item:active {
	background-color: #454545;
}
body.dark-mode .conversation-name {
	color: #e0e0e0;
}
body.dark-mode .conversation-preview {
	color: #a0a0a0;
}
body.dark-mode .conversation-date {
	color: #808080;
}
body.dark-mode .conversation-details {
	background-color: #252525;
	border-bottom: 2px solid #404040;
	color: #d0d0d0;
}
body.dark-mode .conversation-details strong {
	color: #e0e0e0;
}
body.dark-mode .month-jump {
	background-color: #2d2d2d;
	border-bottom: 1px solid #404040;
}
body.dark-mode .month-jump a {
	color: #64B5F6;
}
body.dark-mode .pagination-controls {
	background-color: #252525;
	border: 1px solid #404040;
}
body.dark-mode h2 {
	color: #808080;
}
body.dark-mode .messages_table th {
	background-color: #252525;
	border-bottom: 1px solid #404040;
	color: #a0a0a0;
}
body.dark-mode .messages_table td {
	border-bottom: 1px solid #353535;
	color: #d0d0d0;
}
body.dark-mode .msg_received {
	background-color: #1e2a3a;
}
body.dark-mode .msg_sent {
	background-color: #1a2e1a;
}
body.dark-mode .msg_date {
	color: #808080;
}
body.dark-mode .msg_contact {
	color: #e0e0e0;
}
body.dark-mode .conversation-details p {
	color: #b0b0b0;
}
body.dark-mode .pagination-info {
	color: #b0b0b0;
}
body.dark-mode .messages_table {
	color: #d0d0d0;
}
.dark-mode-toggle {
	background: none;
	border: none;
	color: white;
	font-size: 20px;
	cursor: pointer;
	padding: 5px;
	margin: 0;
	width: 36px;
	height: 36px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 4px;
	transition: background-color 0.2s;
	flex-shrink: 0;
	filter: grayscale(100%) brightness(200%);
}
.dark-mode-toggle:hover {
	background-color: rgba(255, 255, 255, 0.1);
}

"""

class SMSMsg:
	def __init__(self, timestamp, text, type_, extra):
		self.timestamp = timestamp
		if isinstance(text, bytes):
			self.text = text.decode('utf8')
		else:
			self.text = text if text else ""
		self.type_ = type_
		self.extra = extra
		self.sender_address = None  # Who sent this message
		self.sender_name = None
		
class MMSMsg(SMSMsg):
	def __init__(self, timestamp=0, text="", type_=1, extra=None):
		if extra is None:
			extra = {}
		SMSMsg.__init__(self, timestamp, text, type_, extra)
		self.images = []
		
	def addImageData(self, mime, data):
		"""Add image as embedded base64 data URI"""
		# Normalize MIME type and handle variants
		mime_lower = mime.lower()
		
		# Map of MIME types to their standard format
		mime_map = {
		    'image/png': 'image/png',
		    'image/jpeg': 'image/jpeg',
		    'image/jpg': 'image/jpeg',  # Non-standard but common
		    'image/gif': 'image/gif',
		    'image/webp': 'image/webp',
		    'image/avif': 'image/avif',
		    'image/bmp': 'image/bmp',
		    'image/svg+xml': 'image/svg+xml',
		    'image/tiff': 'image/tiff',
		    'image/x-icon': 'image/x-icon',
		    'image/vnd.microsoft.icon': 'image/x-icon',
		}
		
		# Check if we support this MIME type
		if mime_lower in mime_map:
		    mime_type = mime_map[mime_lower]
		else:
			print("Unknown MIME type '%s' for MMS content; omitting content" % (mime))
			return
		
		try:
			# Store as data URI for embedding
			data_uri = f"data:{mime_type};base64,{data}"
			self.images.append(data_uri)
		except Exception as e:
			print(f"Failed to process image: {e}")

def parseCarrierNumber(number):
	number = re.sub('[^0-9]', '', number)
	if len(number) == 10:
		number = '1' + number
	return number

def formatPhoneNumber(number):
	"""Format phone number for display"""
	if len(number) == 11 and number.startswith('1'):
		return f"({number[1:4]}) {number[4:7]}-{number[7:]}"
	elif len(number) == 10:
		return f"({number[0:3]}) {number[3:6]}-{number[6:]}"
	return number

def formatPhoneNumberSimple(number):
	"""Format phone number without parentheses"""
	if len(number) == 11 and number.startswith('1'):
		return f"{number[1:4]}-{number[4:7]}-{number[7:]}"
	elif len(number) == 10:
		return f"{number[0:3]}-{number[3:6]}-{number[6:]}"
	return number

def makeConversationKey(addresses):
	"""Create a unique key for a conversation based on all participants"""
	# Sort addresses to ensure same key regardless of order
	return '~'.join(sorted(addresses))
	
def parseConversations(root, conversations, carrier_number, debug_mode=False):
	messages = 0
	type_counts = {}
	contact_map = {}  # Map phone numbers to contact names
	
	for child in root:
		child_messages, child_types = parseConversations(child, conversations, carrier_number, debug_mode)
		messages += child_messages
		for type_, count in child_types.items():
			type_counts[type_] = type_counts.get(type_, 0) + count
			
		if child.tag == 'sms':
			address = parseCarrierNumber(child.attrib['address'])
			date    = int(child.attrib['date'])
			type_   = child.attrib['type']
			name    = child.attrib.get('contact_name', '(Unknown)')
			body    = child.attrib.get('body', '')
			
			if debug_mode and messages < 5:
				print(f"DEBUG SMS: type={type_}, address={address}, name={name}")
			
			# Store contact name mapping
			if name != '(Unknown)':
				contact_map[address] = name
			
			save_msg = SMSMsg(date, body, type_, {})
			save_msg.sender_name = name if type_ == '1' else 'You'
			save_msg.sender_address = address if type_ == '1' else carrier_number
			
			# Create conversation key (just the other person for SMS)
			conv_key = address
			conv_name = name if name != '(Unknown)' else formatPhoneNumber(address)
			
			if debug_mode and messages < 10:
				print(f"  SMS Conv Key: {conv_key}, Name: {conv_name}")
			
			type_counts[type_] = type_counts.get(type_, 0) + 1
			
			if conv_key not in conversations:
				conversations[conv_key] = {
					'name': conv_name,
					'participants': [address],
					'messages': {},
					'contact_map': contact_map
				}
			conversations[conv_key]['messages'][date] = save_msg
			messages += 1
		
		elif child.tag == 'mms':
			save_msg = MMSMsg()
			date = int(child.attrib['date'])
			msg_box = child.attrib.get('msg_box', '1')
			contact_name = child.attrib.get('contact_name', 'Unknown')
			
			if msg_box == '2':
				actual_msg_type = '151'  # Sent MMS
			else:
				actual_msg_type = '137'  # Received MMS
			
			sender_address = None
			all_addresses = []
			address_names = {}  # Map addresses to names from this MMS
			
			if debug_mode and messages < 5:
				print(f"\nDEBUG MMS: date={date}, msg_box={msg_box}, contact_name={contact_name}")
			
			for mms_child in child:
				if mms_child.tag == 'parts':
					for part_child in mms_child:
						if part_child.tag == 'part':
							part_data = part_child.attrib.get('data', '')
							part_text = part_child.attrib.get('text', '')
							part_mime = part_child.attrib['ct']
							if "image" in part_mime and part_data:
								save_msg.addImageData(part_mime, part_data)
							elif "text" in part_mime:
								save_msg.text += part_text
								
				elif mms_child.tag == 'addrs':
					for addr_child in mms_child:
						if addr_child.tag == 'addr':
							parsed_addr = parseCarrierNumber(addr_child.attrib['address'])
							addr_type = addr_child.attrib.get('type', '137')
							addr_charset = addr_child.attrib.get('charset', '')
							
							if debug_mode and messages < 5:
								print(f"  Address: {parsed_addr}, type={addr_type}")
							
							# Skip empty addresses and your own number
							if parsed_addr and carrier_number not in parsed_addr:
								all_addresses.append(parsed_addr)
								
								# In received MMS (msg_box=1), type 137 indicates the sender
								# Type 151 typically indicates recipients/CC
								if addr_type == '137' and msg_box == '1':
									sender_address = parsed_addr
									if debug_mode and messages < 5:
										print(f"    -> Identified as sender (type 137)")
			
			# Parse contact_name to extract individual names
			# Format is usually "Name1, Name2" or "Name1 Name2"
			if contact_name and contact_name != 'Unknown':
				# The contact_name order matches the address field order in the XML
				address_field = child.attrib.get('address', '')
				
				if ',' in contact_name and address_field:
					names = [n.strip() for n in contact_name.split(',')]
					
					if debug_mode and messages < 5:
						print(f"  Parsing names: {names}")
						print(f"  Address field: {address_field}")
					
					# Parse the address field which has addresses in same order as names
					raw_addresses = [parseCarrierNumber(a.strip()) for a in address_field.split('~')]
					# Filter out your own number
					ordered_addresses = [a for a in raw_addresses if a and carrier_number not in a]
					
					if debug_mode and messages < 5:
						print(f"  Ordered addresses: {ordered_addresses}")
					
					# Now match names to addresses in order
					for i, addr in enumerate(ordered_addresses):
						if i < len(names):
							address_names[addr] = names[i]
							contact_map[addr] = names[i]
							if debug_mode and messages < 5:
								print(f"  Mapped: {addr} -> {names[i]}")
				elif address_field and '~' not in address_field:
					# Single person conversation, map the name to the single address
					single_addr = parseCarrierNumber(address_field)
					if single_addr and carrier_number not in single_addr:
						address_names[single_addr] = contact_name
						contact_map[single_addr] = contact_name
						if debug_mode and messages < 5:
							print(f"  Single person mapped: {single_addr} -> {contact_name}")
			
			# Set sender info
			if msg_box == '2':
				sender_address_final = carrier_number
				sender_name_final = 'You'
			elif sender_address:
				sender_address_final = sender_address
				# Try multiple sources for the name
				sender_name_final = (address_names.get(sender_address) or 
				                    contact_map.get(sender_address) or 
				                    formatPhoneNumber(sender_address))
				if debug_mode and messages < 5:
					print(f"  Sender address: {sender_address}")
					print(f"  address_names.get: {address_names.get(sender_address)}")
					print(f"  contact_map.get: {contact_map.get(sender_address)}")
					print(f"  Final sender: {sender_name_final} ({sender_address_final})")
			else:
				sender_address_final = all_addresses[0] if all_addresses else None
				if sender_address_final:
					sender_name_final = (address_names.get(sender_address_final) or 
					                    contact_map.get(sender_address_final) or 
					                    formatPhoneNumber(sender_address_final))
				else:
					sender_name_final = contact_name
				if debug_mode and messages < 5:
					print(f"  No explicit sender, using first address: {sender_address_final}")
					print(f"  Sender name: {sender_name_final}")
			
			# Store sender info in the message
			save_msg.sender_address = sender_address_final
			save_msg.sender_name = sender_name_final
			save_msg.type_ = actual_msg_type
			save_msg.timestamp = date
			
			# Create conversation key from all participants
			# Remove duplicates and normalize
			unique_addresses = list(set(all_addresses))
			
			# Preserve original order from address field for display
			address_field = child.attrib.get('address', '')
			if address_field:
				raw_addresses = [parseCarrierNumber(a.strip()) for a in address_field.split('~')]
				ordered_unique = [a for a in raw_addresses if a in unique_addresses and carrier_number not in a]
			else:
				ordered_unique = unique_addresses
			
			# If only one unique participant (excluding self), treat as 1-on-1
			if len(unique_addresses) == 1:
				conv_key = unique_addresses[0]
			else:
				conv_key = makeConversationKey(unique_addresses)
			
			if debug_mode and messages < 10:
				print(f"  MMS All addresses: {all_addresses}")
				print(f"  MMS Unique addresses: {unique_addresses}")
				print(f"  MMS Ordered unique: {ordered_unique}")
				print(f"  MMS Conv Key: {conv_key}")
			
			type_counts[actual_msg_type] = type_counts.get(actual_msg_type, 0) + 1
			
			if conv_key not in conversations:
				# Use the single person's name for 1-on-1, group name for actual groups
				if len(unique_addresses) == 1:
					conv_name = contact_map.get(unique_addresses[0]) or formatPhoneNumber(unique_addresses[0])
				else:
					conv_name = contact_name
				
				conversations[conv_key] = {
					'name': conv_name,
					'participants': ordered_unique,  # Use ordered list
					'messages': {},
					'contact_map': {}
				}
			
			# Update the contact map for this conversation
			conversations[conv_key]['contact_map'].update(contact_map)
			
			# Store the message (only once per conversation, not per address)
			conversations[conv_key]['messages'][date] = save_msg
			messages += 1
			
	return messages, type_counts

def dumpConversations(base_path, conversations, carrier_number, sorted_conv_keys, xml_file):
	os.makedirs(base_path, exist_ok=True)
	
	# Generate filename based on conversations
	# today = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
	
	# Get all conversation names
	conv_names = []
	for conv in conversations.values():
		# Clean up the name for filename
		name = conv['name'].replace(',', '_').replace(' ', '_')
		conv_names.append(name)
	# Create base filename
	# Always use XML filename for consistency
	xml_basename = Path(xml_file).stem
	base_filename = xml_basename

	# Check if we need to split into multiple files (estimate size)
	# Rough estimate: each message with image could be ~50KB
	max_size_mb = 500
	estimated_size_mb = 0
	
	for conv in conversations.values():
		for msg in conv['messages'].values():
			estimated_size_mb += 0.05  # Base message size
			if isinstance(msg, MMSMsg) and msg.images:
				estimated_size_mb += len(msg.images) * 0.5  # Rough image size estimate
	
	# Always use split logic for consistency and proper image modal support
	# Add incrementing number to base_filename
	counter = 1
	while True:
	    numbered_folder = f'{base_filename}_{counter:04d}'
	    test_path = os.path.join(base_path, numbered_folder)
	    if not os.path.exists(test_path):
	        base_filename = numbered_folder
	        break
	    counter += 1
	
	subfolder = os.path.join(base_path, base_filename)
	os.makedirs(subfolder, exist_ok=True)
	return dumpConversationsSplit(subfolder, conversations, carrier_number, sorted_conv_keys, base_filename, max_size_mb)
def dumpConversationsSplit(subfolder, conversations, carrier_number, sorted_conv_keys, base_filename, max_size_mb):
	"""Split large conversation sets - each conversation in separate files, large ones split into chunks"""
	print(f"\n  Large file detected! Creating separate conversation files in subfolder: {base_filename}/")
	
	# Create the conv_files subfolder
	conv_files_dir = os.path.join(subfolder, "conv_files")
	os.makedirs(conv_files_dir, exist_ok=True)
	
	conv_metadata = []
	max_chunk_size = 50 * 1024 * 1024  # 50MB per chunk (in characters)
	
	# Create individual JS files for each conversation
	for conv_key in sorted_conv_keys:
		conv = conversations[conv_key]
		# Use hash for short, unique ID to avoid Windows path length issues
		conv_hash = hashlib.md5(conv_key.encode()).hexdigest()[:12]
		safe_id = conv_hash
		contact_map = conv.get('contact_map', {})
		
		# Build all message HTML first to check size
		message_htmls = []
		
		# Generate month TOC and messages
		prev_month_year = ""
		months = []
		month_amap = {}
		sorted_dates = sorted(conv['messages'].keys(), reverse=True)
		
		for date in sorted_dates:
			msg = conv['messages'][date]
			dt = datetime.datetime.fromtimestamp(msg.timestamp / 1000, tz=None)
			month_year = dt.strftime('%B %Y')
			if month_year != prev_month_year:
				month_year_short = dt.strftime('%y%m') + '_' + safe_id
				months.append(month_year)
				month_amap[month_year] = month_year_short
			prev_month_year = month_year
		
		# Generate messages grouped by month
		prev_month_year = ""
		current_month_html = []
		
		for date in sorted_dates:
			msg = conv['messages'][date]
			dt = datetime.datetime.fromtimestamp(msg.timestamp / 1000, tz=None)
			month_year = dt.strftime('%B %Y')
			
			if month_year != prev_month_year:
				# Save previous month if exists
				if current_month_html:
					current_month_html.append('</table>')
					message_htmls.append({
						'month': prev_month_year,
						'html': ''.join(current_month_html),
						'anchor': month_amap[prev_month_year]
					})
					current_month_html = []
				
				# Start new month
				current_month_html.append(f'<a id="month-{month_amap[month_year]}"></a>')
				current_month_html.append(f"<h2>{month_year}</h2>")
				current_month_html.append('<table class="messages_table">')
				current_month_html.append('<tr>')
				current_month_html.append('<th style="width: 80px;">Type</th>')
				current_month_html.append('<th style="width: 150px;">Date</th>')
				current_month_html.append('<th style="width: 200px;">Name / Number</th>')
				current_month_html.append('<th>Content</th>')
				current_month_html.append('</tr>')
			
			# Determine message type and styling
			if msg.type_ in ['1', '137', '130']:
				msg_type = 'Received'
				row_class = 'msg_received'
				if msg.sender_name and msg.sender_address:
					sender_info = f"{msg.sender_name}<br>{formatPhoneNumber(msg.sender_address)}"
				elif msg.sender_address:
					sender_info = f"{formatPhoneNumber(msg.sender_address)}"
				else:
					sender_info = msg.sender_name or "Unknown"
			elif msg.type_ in ['2', '151']:
				msg_type = 'Sent'
				row_class = 'msg_sent'
				sender_info = f"You<br>{formatPhoneNumber(carrier_number)}"
			else:
				msg_type = f'Type {msg.type_}'
				row_class = 'msg_received'
				sender_info = f"{msg.sender_name}<br>{formatPhoneNumber(msg.sender_address) if msg.sender_address else ''}"
			
			current_month_html.append(f'<tr class="{row_class}">')
			current_month_html.append(f'<td class="msg_type">{msg_type}</td>')
			current_month_html.append(f'<td class="msg_date">{dt.strftime("%b %d, %Y")}<br>{dt.strftime("%I:%M:%S %p")}</td>')
			current_month_html.append(f'<td class="msg_contact">{sender_info}</td>')
			current_month_html.append('<td>')
			
			msg_text = msg.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
			current_month_html.append(msg_text)
			
			if isinstance(msg, MMSMsg) and msg.images:
				for img_data in msg.images:
					current_month_html.append(f'<br><img class="mms_img" src="{img_data}" alt="MMS Image" onclick="openImageModal(this.src)" />')
			
			current_month_html.append('</td>')
			current_month_html.append('</tr>')
			prev_month_year = month_year
		
		# Save last month
		if current_month_html:
			current_month_html.append('</table>')
			message_htmls.append({
				'month': prev_month_year,
				'html': ''.join(current_month_html),
				'anchor': month_amap[prev_month_year]
			})
		
		# Create header HTML
		header_html = []
		if len(conv['participants']) > 1:
			header_html.append('<div class="conversation-details">')
			header_html.append('<p><strong>Group Conversation</strong></p>')
			header_html.append('<p><strong>Participants:</strong> ')
			participant_info = []
			for addr in conv['participants']:
				name = contact_map.get(addr, formatPhoneNumber(addr))
				phone = formatPhoneNumberSimple(addr)
				participant_info.append(f"{name} ({phone})")
			header_html.append(', '.join(participant_info))
			header_html.append('</p>')
			header_html.append(f'<p><strong>Total Messages:</strong> {len(conv["messages"])}</p>')
			header_html.append('</div>')
		
		if len(months) > 1:
			header_html.append('<div class="month-jump"><strong>Jump to:</strong> ')
			month_links = []
			for month_year in months:
				month_links.append(f'<a href="javascript:void(0)" onclick="jumpToMonth(\'month-{month_amap[month_year]}\')">{month_year}</a>')
			header_html.append(' | '.join(month_links))
			header_html.append('</div>')
		
		# Decide if we need to chunk this conversation
		total_size = len(''.join(header_html)) + sum(len(m['html']) for m in message_htmls)
		
		if total_size > max_chunk_size:
			# Large conversation - split into chunks by month
			print(f"  Large conversation detected: {conv['name']} (~{total_size/1024/1024:.1f}MB), splitting into chunks...")
			
			chunk_num = 0
			current_chunk = []
			current_chunk_size = 0
			chunk_files = []
			chunk_months = {}  # Track which months are in which chunk
			
			for msg_data in message_htmls:
				msg_size = len(msg_data['html'])
				
				if current_chunk_size + msg_size > max_chunk_size and current_chunk:
					# Write current chunk to conv_files subfolder
					chunk_num += 1
					chunk_filename = f"conv_{safe_id}_chunk{chunk_num}.js"
					chunk_path = os.path.join(conv_files_dir, chunk_filename)
					
					chunk_html = ''.join(current_chunk)
					escaped_html = chunk_html.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
					
					with open(chunk_path, 'w', encoding='utf-8') as jsf:
						jsf.write(f'window.convChunk_{safe_id}_{chunk_num} = `{escaped_html}`;')
					
					chunk_files.append(chunk_filename)
					# Track which months are in this chunk
					# Extract months from the HTML we just processed
					import re
					months_in_chunk = list(set(re.findall(r'<h2>(.*?)</h2>', chunk_html)))
					chunk_months[chunk_num] = months_in_chunk
					current_chunk = []
					current_chunk_size = 0
				
				current_chunk.append(msg_data['html'])
				current_chunk_size += msg_size
			
			# Write last chunk to conv_files subfolder
			if current_chunk:
				chunk_num += 1
				chunk_filename = f"conv_{safe_id}_chunk{chunk_num}.js"
				chunk_path = os.path.join(conv_files_dir, chunk_filename)
				
				chunk_html = ''.join(current_chunk)
				escaped_html = chunk_html.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
				
				with open(chunk_path, 'w', encoding='utf-8') as jsf:
					jsf.write(f'window.convChunk_{safe_id}_{chunk_num} = `{escaped_html}`;')
				
				chunk_files.append(chunk_filename)
			
			# Write header file to conv_files subfolder
			header_filename = f"conv_{safe_id}_header.js"
			header_path = os.path.join(conv_files_dir, header_filename)
			header_escaped = ''.join(header_html).replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
			
			with open(header_path, 'w', encoding='utf-8') as jsf:
				jsf.write(f'window.convHeader_{safe_id} = `{header_escaped}`;')
			
			conv_metadata.append({
				'id': safe_id,
				'chunked': True,
				'header_file': header_filename,
				'chunk_files': chunk_files,
				'name': conv['name'],
				'participants': conv['participants'],
				'msg_count': len(conv['messages']),
				'latest_date': max(conv['messages'].keys()) if conv['messages'] else 0,
				'chunk_months': chunk_months
			})
			
		else:
			# Small enough - single file in conv_files subfolder
			js_filename = f"conv_{safe_id}.js"
			js_path = os.path.join(conv_files_dir, js_filename)
			
			full_html = ''.join(header_html) + ''.join(m['html'] for m in message_htmls)
			escaped_html = full_html.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
			
			with open(js_path, 'w', encoding='utf-8') as jsf:
				jsf.write(f'window.convData_{safe_id} = `{escaped_html}`;')
			
			conv_metadata.append({
				'id': safe_id,
				'chunked': False,
				'js_file': js_filename,
				'name': conv['name'],
				'participants': conv['participants'],
				'msg_count': len(conv['messages']),
				'latest_date': max(conv['messages'].keys()) if conv['messages'] else 0
			})
	
	# Create messages.html (renamed from 0_index.html)
	index_path = os.path.join(subfolder, "messages.html")
	with open(index_path, 'w', encoding='utf-8') as f:
		f.write('<!DOCTYPE html>\n<html><head>\n')
		f.write('<meta charset="UTF-8">\n')
		f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
		f.write('<style>\n')
		f.write(STYLESHEET_TEMPLATE)
		f.write('</style>\n')
		f.write(f'<title>{base_filename}</title>\n')
		f.write('</head><body>\n')
		
		# Image modal (at top level, always available)
		f.write('<div id="imageModal" class="image-modal" onclick="closeImageModal()">\n')
		f.write('<span class="image-modal-close">&times;</span>\n')
		f.write('<img id="modalImage" src="" />\n')
		f.write('</div>\n')
		
		f.write('<div class="phone-view">\n')
		f.write('<div class="header">\n')
		f.write('<button class="back-button" onclick="showList()">←</button>\n')
		f.write('<h1 id="header-title">Messages</h1>\n')
		f.write('<div id="headerSearch" class="header-search">\n')
		f.write('<input type="text" id="searchInput" placeholder="Search..." oninput="filterConversations()" />\n')
		f.write('</div>\n')
		f.write('<button class="dark-mode-toggle" onclick="toggleDarkMode()" title="Toggle Dark Mode">&#127769;</button>\n')
		f.write('</div>\n')
		
		# Conversation list
		f.write('<div id="conversation-list" class="conversation-list">\n')
		
		for meta in conv_metadata:
			# Get date string
			if meta['latest_date']:
				dt = datetime.datetime.fromtimestamp(meta['latest_date'] / 1000, tz=None)
				date_str = dt.strftime('%b %d, %Y')
			else:
				date_str = ''
			
			# Get initials for avatar
			if len(meta['participants']) > 1:
				# Group conversation - create mini avatars
				is_group = True
				num_avatars = min(len(meta['participants']), 4)
				group_class = f"group-{num_avatars}"
				
				# Get first letter of each participant
				participant_initials = []
				
				# Try to split the name by comma to get individual names
				if ',' in meta.get('name', ''):
					name_parts = [n.strip() for n in meta['name'].split(',')]
				else:
					name_parts = []
				
				for i, participant in enumerate(meta['participants'][:num_avatars]):
					# Get name for this participant
					if i < len(name_parts) and name_parts[i]:
						part_name = name_parts[i]
					else:
						# Fallback to formatted phone number
						part_name = formatPhoneNumber(participant)
					
					# Get initial
					name_check = ''.join(c for c in part_name if c.isalnum() or c.isspace()).strip()
					if name_check and not name_check[0].isdigit():
						initial = part_name[0].upper()
					else:
						initial = '#'
					participant_initials.append(initial)
				
				avatar_html = f'<div class="conversation-avatar-group {group_class}">'
				for initial in participant_initials:
					avatar_html += f'<div class="mini-avatar">{initial}</div>'
				avatar_html += '</div>'
			else:
				is_group = False
				# Check if it's an unknown contact (formatted phone number)
				# Remove all non-alphanumeric except spaces to check
				name_check = ''.join(c for c in meta['name'] if c.isalnum() or c.isspace()).strip()
				if name_check.isdigit() or meta['name'].startswith('('):
					# Unknown contact - phone number
					initials = '#'
				else:
					name_parts = meta['name'].split()
					if len(name_parts) >= 2:
						initials = name_parts[0][0] + name_parts[1][0]
					else:
						initials = meta['name'][:2]
					initials = initials.upper()
				avatar_html = f'<div class="conversation-avatar">{initials}</div>'
			
			# Format subtitle
			if len(meta['participants']) > 1:
				subtitle = f"Group · {len(meta['participants'])} people"
			elif len(meta['participants']) == 1:
				subtitle = formatPhoneNumberSimple(meta['participants'][0])
			else:
				subtitle = "Unknown"
			
			f.write(f'<div class="conversation-item" data-name="{meta["name"].lower()}" data-participants="{" ".join([formatPhoneNumberSimple(p) for p in meta["participants"]])}" onclick="loadConversation(\'{meta["id"]}\', \'{meta["name"].replace("'", "\\'")}\')">\n')
			f.write(avatar_html + '\n')
			f.write('<div class="conversation-info">\n')
			f.write(f'<div class="conversation-name">{meta["name"]}</div>\n')
			f.write(f'<div class="conversation-preview">{subtitle}</div>\n')
			f.write('</div>\n')
			f.write('<div class="conversation-meta">\n')
			f.write(f'<div class="conversation-date">{date_str}</div>\n')
			f.write(f'<div class="conversation-count">{meta["msg_count"]}</div>\n')
			f.write('</div>\n')
			f.write('</div>\n')
		
		f.write('</div>\n')
		
		# Container for loaded conversation
		f.write('<div id="conversation-content" class="conversation-view"></div>\n')
		
		f.write('</div>\n')  # Close phone-view
		
		# JavaScript - define image modal functions first, before everything else
		f.write('<script>\n')
		f.write('// Image modal functions (must be globally available)\n')
		f.write('function openImageModal(src) {\n')
		f.write('  event.stopPropagation();\n')
		f.write('  const modal = document.getElementById("imageModal");\n')
		f.write('  const modalImg = document.getElementById("modalImage");\n')
		f.write('  modal.style.display = "block";\n')
		f.write('  modalImg.src = src;\n')
		f.write('}\n\n')
		f.write('function loadScriptPromise(src) {\n')
		f.write('  return new Promise((resolve, reject) => {\n')
		f.write('    const script = document.createElement("script");\n')
		f.write('    script.src = src;\n')
		f.write('    script.onload = () => resolve();\n')
		f.write('    script.onerror = () => reject(new Error(`Failed to load ${src}`));\n')
		f.write('    document.head.appendChild(script);\n')
		f.write('  });\n')
		f.write('}\n\n')
		
		f.write('function closeImageModal() {\n')
		f.write('  document.getElementById("imageModal").style.display = "none";\n')
		f.write('}\n\n')
		f.write('\n')
		f.write('// Month jump function (works for both chunked and non-chunked conversations)\n')
		f.write('function jumpToMonth(monthId) {\n')
		f.write('  const anchor = document.getElementById(monthId);\n')
		f.write('  if (anchor) {\n')
		f.write("    anchor.scrollIntoView({ behavior: 'smooth' });\n")
		f.write('  }\n')
		f.write('}\n')
		f.write('\n\n')
		f.write('// Dark mode toggle\n')
		f.write('function toggleDarkMode() {\n')
		f.write('  document.body.classList.toggle(\'dark-mode\');\n')
		f.write('  const isDark = document.body.classList.contains(\'dark-mode\');\n')
		f.write('  localStorage.setItem(\'darkMode\', isDark);\n')
		f.write('  const btn = document.querySelector(\'.dark-mode-toggle\');\n')
		f.write('  btn.innerHTML = isDark ? \'&#9728;\' : \'&#127769;\';\n')
		f.write('}\n')
		f.write('\n')
		f.write('// Load dark mode preference\n')
		f.write('if (localStorage.getItem(\'darkMode\') === \'true\') {\n')
		f.write('  document.body.classList.add(\'dark-mode\');\n')
		f.write('  const btn = document.querySelector(\'.dark-mode-toggle\');\n')
		f.write('  if (btn) btn.innerHTML = \'&#9728;\';\n')
		f.write('}\n')
		
		# Rest of the JavaScript - UPDATE PATHS TO INCLUDE conv_files/
		f.write('const loadedConversations = new Set();\n')
		f.write('const convMetadata = ' + str(conv_metadata).replace("'", '"').replace('True', 'true').replace('False', 'false') + ';\n\n')
		
		f.write('function loadConversation(id, name) {\n')
		f.write('  document.getElementById("conversation-list").style.display = "none";\n')
		f.write('  document.querySelector(".back-button").style.display = "block";\n')
		f.write('  document.getElementById("header-title").textContent = name;\n')
		f.write('  document.getElementById("headerSearch").classList.add("hidden");\n')
		f.write('  const content = document.getElementById("conversation-content");\n')
		f.write('  \n')
		f.write('  const meta = convMetadata.find(m => m.id === id);\n')
		f.write('  if (!meta) {\n')
		f.write('    content.innerHTML = "<div style=\\"padding: 40px; text-align: center; color: red;\\">Conversation not found</div>";\n')
		f.write('    return;\n')
		f.write('  }\n')
		f.write('  \n')
		f.write('  if (loadedConversations.has(id)) {\n')
		f.write('    // Already loaded\n')
		f.write('    if (meta.chunked) {\n')
		f.write('      // Reload with proper pagination\n')
		f.write('      content.classList.remove("no-pagination");\n')
		f.write('      content.style.display = "block";\n')
		f.write('      loadChunkedConversation(id, meta);\n')
		f.write('      return; // Exit early\n')
		f.write('    } else {\n')
		f.write('      content.innerHTML = window["convData_" + id];\n')
		f.write('      content.classList.add("no-pagination");\n')
		f.write('    }\n')
		f.write('    content.style.display = "block";\n')
		f.write('    window.scrollTo(0, 0);\n')
		f.write('  } else {\n')
		f.write('    // Load the conversation\n')
		f.write('    content.innerHTML = "<div style=\\"padding: 40px; text-align: center;\\">Loading conversation...</div>";\n')
		f.write('    content.style.display = "block";\n')
		f.write('    \n')
		f.write('    if (meta.chunked) {\n')
		f.write('      // Load chunked conversation\n')
		f.write('      loadChunkedConversation(id, meta);\n')
		f.write('    } else {\n')
		f.write('      // Load single file - ADD conv_files/ prefix\n')
		f.write('      loadScript("conv_files/" + meta.js_file, () => {\n')
		f.write('        loadedConversations.add(id);\n')
		f.write('        content.innerHTML = window["convData_" + id];\n')
		f.write('        content.classList.add("no-pagination");\n')
		f.write('        window.scrollTo(0, 0);\n')
		f.write('      }, () => {\n')
		f.write('        content.innerHTML = "<div style=\\"padding: 40px; text-align: center; color: red;\\">Error loading conversation</div>";\n')
		f.write('      });\n')
		f.write('    }\n')
		f.write('  }\n')
		f.write('}\n\n')
		
		f.write('function loadChunkedConversation(id, meta) {\n')
		f.write('  const content = document.getElementById("conversation-content");\n')
		f.write('  let currentChunk = 1;\n')
		f.write('  let isLoading = false;\n')
		f.write('  \n')
		f.write('  function showChunk(chunkNum) {\n')
		f.write('    if (isLoading) return;\n')
		f.write('    isLoading = true;\n')
		f.write('    \n')
		f.write('    // Show loading indicator\n')
		f.write('    content.innerHTML = `<div style="padding: 40px; text-align: center;">\n')
		f.write('      <div style="font-size: 18px; margin-bottom: 10px;">Loading page ${chunkNum} of ${meta.chunk_files.length}...</div>\n')
		f.write('      <div style="background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden; max-width: 400px; margin: 0 auto;">\n')
		f.write('        <div style="background: #2196F3; height: 100%; width: 100%; animation: pulse 1.5s ease-in-out infinite;"></div>\n')
		f.write('      </div>\n')
		f.write('    </div>`;\n')
		f.write('    \n')
		f.write('    // Load header if first chunk\n')
		f.write('    const headerPromise = chunkNum === 1 && !window["convHeader_" + id] ? \n')
		f.write('      loadScriptPromise("conv_files/" + meta.header_file) : Promise.resolve();\n')
		f.write('    \n')
		f.write('    // Load the chunk if not already loaded\n')
		f.write('    const chunkFile = meta.chunk_files[chunkNum - 1];\n')
		f.write('    const chunkPromise = !window["convChunk_" + id + "_" + chunkNum] ? \n')
		f.write('      loadScriptPromise("conv_files/" + chunkFile) : Promise.resolve();\n')
		f.write('    \n')
		f.write('    Promise.all([headerPromise, chunkPromise])\n')
		f.write('      .then(() => {\n')
		f.write('        // Render the chunk\n')
		f.write('        const header = window["convHeader_" + id] || "";\n')
		f.write('        const chunk = window["convChunk_" + id + "_" + chunkNum] || "<p>Error: Chunk not found</p>";\n')
		f.write('        \n')
		f.write('        // Build pagination controls\n')
		f.write('        const totalChunks = meta.chunk_files.length;\n')
		f.write('        const paginationTop = `\n')
		f.write('          <div class="pagination-controls">\n')
		f.write('            <button onclick="loadPrevChunk()" ${chunkNum === 1 ? \'disabled\' : \'\'}>&larr; Previous</button>\n')
		f.write('            <div class="pagination-info">Page ${chunkNum} of ${totalChunks}</div>\n')
		f.write('            <button onclick="loadNextChunk()" ${chunkNum === totalChunks ? \'disabled\' : \'\'}>&rarr; Next</button>\n')
		f.write('          </div>\n')
		f.write('        `;\n')
		f.write('        const paginationBottom = paginationTop.replace("pagination-controls", "pagination-controls" + " style=\\"position: static;\\"");\n')
		f.write('        \n')
		f.write('        content.innerHTML = paginationTop + \'<div style="padding-top: 0px;">\' + header + chunk + \'</div>\' + paginationBottom;\n')
		f.write('        \n')
		f.write('        // Filter month links to show only months present in current chunk\n')
		f.write('        setTimeout(() => {\n')
		f.write('          const monthJumpDiv = content.querySelector(".month-jump");\n')
		f.write('          if (monthJumpDiv) {\n')
		f.write('            const allLinks = monthJumpDiv.querySelectorAll("a");\n')
		f.write('            const monthsOnPage = new Set();\n')
		f.write('            \n')
		f.write('            const monthHeaders = content.querySelectorAll("h2");\n')
		f.write('            monthHeaders.forEach(h2 => {\n')
		f.write('              monthsOnPage.add(h2.textContent.trim());\n')
		f.write('            });\n')
		f.write('            \n')
		f.write('            let visibleCount = 0;\n')
		f.write('            allLinks.forEach((link, index) => {\n')
		f.write('              const monthText = link.textContent.trim();\n')
		f.write('              const nextSibling = link.nextSibling;\n')
		f.write('              \n')
		f.write('              if (monthsOnPage.has(monthText)) {\n')
		f.write('                link.style.display = "inline";\n')
		f.write('                visibleCount++;\n')
		f.write('                \n')
		f.write('                if (nextSibling && nextSibling.nodeType === 3 && nextSibling.textContent.includes("|")) {\n')
		f.write('                  const nextLink = link.nextElementSibling;\n')
		f.write('                  if (nextLink && monthsOnPage.has(nextLink.textContent.trim())) {\n')
		f.write('                    nextSibling.textContent = " | ";\n')
		f.write('                  } else {\n')
		f.write('                    nextSibling.textContent = " ";\n')
		f.write('                  }\n')
		f.write('                }\n')
		f.write('              } else {\n')
		f.write('                link.style.display = "none";\n')
		f.write('                if (nextSibling && nextSibling.nodeType === 3) {\n')
		f.write('                  nextSibling.textContent = " ";\n')
		f.write('                }\n')
		f.write('              }\n')
		f.write('            });\n')
		f.write('            \n')
		f.write('            if (monthJumpDiv.textContent.trim().startsWith("|")) {\n')
		f.write('              const firstText = monthJumpDiv.childNodes[0];\n')
		f.write('              if (firstText && firstText.nodeType === 3) {\n')
		f.write('                firstText.textContent = firstText.textContent.replace(/^\\\\s*\\\\|\\\\s*/, "");\n')
		f.write('              }\n')
		f.write('            }\n')
		f.write('            \n')
		f.write('            if (visibleCount === 0) {\n')
		f.write('              monthJumpDiv.style.display = "none";\n')
		f.write('            } else {\n')
		f.write('              monthJumpDiv.style.display = "block";\n')
		f.write('            }\n')
		f.write('          }\n')
		f.write('        }, 100);\n')
		f.write('        currentChunk = chunkNum;\n')
		f.write('        isLoading = false;\n')
		f.write('        window.scrollTo(0, 0);\n')
		f.write('      })\n')
		f.write('      .catch(err => {\n')
		f.write('        content.innerHTML = `<div style="padding: 40px; text-align: center; color: red;">Error loading chunk ${chunkNum}: ${err.message}</div>`;\n')
		f.write('        isLoading = false;\n')
		f.write('      });\n')
		f.write('  }\n')
		f.write('  \n')
		f.write('  // Make prev/next functions global so buttons can call them\n')
		f.write('  window.loadNextChunk = () => {\n')
		f.write('    if (currentChunk < meta.chunk_files.length) {\n')
		f.write('      showChunk(currentChunk + 1);\n')
		f.write('    }\n')
		f.write('  };\n')
		f.write('  \n')
		f.write('  window.loadPrevChunk = () => {\n')
		f.write('    if (currentChunk > 1) {\n')
		f.write('      showChunk(currentChunk - 1);\n')
		f.write('    }\n')
		f.write('  };\n')
		f.write('  \n')
		f.write('  \n')
  
		f.write('  \n')
		f.write('  // Mark as loaded and show first chunk\n')
		f.write('  loadedConversations.add(id);\n')
		f.write('  \n')
		f.write('  \n')
		f.write('  showChunk(1);\n')
		f.write('}\n\n')
		
		f.write('function loadScript(src, onSuccess, onError) {\n')
		f.write('  const script = document.createElement("script");\n')
		f.write('  script.src = src;\n')
		f.write('  script.onload = onSuccess;\n')
		f.write('  script.onerror = onError;\n')
		f.write('  document.head.appendChild(script);\n')
		f.write('}\n\n')
		
		f.write('function showList() {\n')
		f.write('  document.getElementById("conversation-list").style.display = "block";\n')
		f.write('  document.getElementById("conversation-content").style.display = "none";\n')
		f.write('  document.querySelector(".back-button").style.display = "none";\n')
		f.write('  document.getElementById("header-title").textContent = "Messages";\n')
		f.write('  document.getElementById("headerSearch").classList.remove("hidden");\n')
		f.write('  document.getElementById("searchInput").value = "";\n')
		f.write('  filterConversations();\n')
		f.write('  window.scrollTo(0, 0);\n')
		f.write('}\n\n')
		
		f.write('function filterConversations() {\n')
		f.write('  const searchTerm = document.getElementById("searchInput").value.toLowerCase();\n')
		f.write('  const items = document.querySelectorAll(".conversation-item");\n')
		f.write('  \n')
		f.write('  items.forEach(item => {\n')
		f.write('    const name = item.getAttribute("data-name");\n')
		f.write('    const participants = item.getAttribute("data-participants");\n')
		f.write('    const searchText = name + " " + participants;\n')
		f.write('    \n')
		f.write('    if (searchText.includes(searchTerm)) {\n')
		f.write('      item.style.display = "flex";\n')
		f.write('    } else {\n')
		f.write('      item.style.display = "none";\n')
		f.write('    }\n')
		f.write('  });\n')
		f.write('}\n')
		f.write('</script>\n')
		
		f.write('</body></html>\n')
	
	print(f"  Created messages.html and {len(conv_metadata)} conversation JS files in conv_files/\n")
	return f"{base_filename}/messages.html"

	"""Split large conversation sets - each conversation in separate files, large ones split into chunks"""
	print(f"\n⚠️  Large file detected! Creating separate conversation files in subfolder: {base_filename}/")
	
	conv_metadata = []
	max_chunk_size = 50 * 1024 * 1024  # 50MB per chunk (in characters)
	
	# Create individual JS files for each conversation
	for conv_key in sorted_conv_keys:
		conv = conversations[conv_key]
		safe_id = re.sub('[^A-Za-z0-9_-]', '_', conv_key)
		contact_map = conv.get('contact_map', {})
		
		# Build all message HTML first to check size
		message_htmls = []
		
		# Generate month TOC and messages
		prev_month_year = ""
		months = []
		month_amap = {}
		sorted_dates = sorted(conv['messages'].keys(), reverse=True)
		
		for date in sorted_dates:
			msg = conv['messages'][date]
			dt = datetime.datetime.fromtimestamp(msg.timestamp / 1000, tz=None)
			month_year = dt.strftime('%B %Y')
			if month_year != prev_month_year:
				month_year_short = dt.strftime('%y%m') + '_' + safe_id
				months.append(month_year)
				month_amap[month_year] = month_year_short
			prev_month_year = month_year
		
		# Generate messages grouped by month
		prev_month_year = ""
		current_month_html = []
		
		for date in sorted_dates:
			msg = conv['messages'][date]
			dt = datetime.datetime.fromtimestamp(msg.timestamp / 1000, tz=None)
			month_year = dt.strftime('%B %Y')
			
			if month_year != prev_month_year:
				# Save previous month if exists
				if current_month_html:
					current_month_html.append('</table>')
					message_htmls.append({
						'month': prev_month_year,
						'html': ''.join(current_month_html),
						'anchor': month_amap[prev_month_year]
					})
					current_month_html = []
				
				# Start new month
				current_month_html.append(f'<a id="month-{month_amap[month_year]}"></a>')
				current_month_html.append(f"<h2>{month_year}</h2>")
				current_month_html.append('<table class="messages_table">')
				current_month_html.append('<tr>')
				current_month_html.append('<th style="width: 80px;">Type</th>')
				current_month_html.append('<th style="width: 150px;">Date</th>')
				current_month_html.append('<th style="width: 200px;">Name / Number</th>')
				current_month_html.append('<th>Content</th>')
				current_month_html.append('</tr>')
			
			# Determine message type and styling
			if msg.type_ in ['1', '137', '130']:
				msg_type = 'Received'
				row_class = 'msg_received'
				if msg.sender_name and msg.sender_address:
					sender_info = f"{msg.sender_name}<br>{formatPhoneNumber(msg.sender_address)}"
				elif msg.sender_address:
					sender_info = f"{formatPhoneNumber(msg.sender_address)}"
				else:
					sender_info = msg.sender_name or "Unknown"
			elif msg.type_ in ['2', '151']:
				msg_type = 'Sent'
				row_class = 'msg_sent'
				sender_info = f"You<br>{formatPhoneNumber(carrier_number)}"
			else:
				msg_type = f'Type {msg.type_}'
				row_class = 'msg_received'
				sender_info = f"{msg.sender_name}<br>{formatPhoneNumber(msg.sender_address) if msg.sender_address else ''}"
			
			current_month_html.append(f'<tr class="{row_class}">')
			current_month_html.append(f'<td class="msg_type">{msg_type}</td>')
			current_month_html.append(f'<td class="msg_date">{dt.strftime("%b %d, %Y")}<br>{dt.strftime("%I:%M:%S %p")}</td>')
			current_month_html.append(f'<td class="msg_contact">{sender_info}</td>')
			current_month_html.append('<td>')
			
			msg_text = msg.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
			current_month_html.append(msg_text)
			
			if isinstance(msg, MMSMsg) and msg.images:
				for img_data in msg.images:
					current_month_html.append(f'<br><img class="mms_img" src="{img_data}" alt="MMS Image" onclick="openImageModal(this.src)" />')
			
			current_month_html.append('</td>')
			current_month_html.append('</tr>')
			prev_month_year = month_year
		
		# Save last month
		if current_month_html:
			current_month_html.append('</table>')
			message_htmls.append({
				'month': prev_month_year,
				'html': ''.join(current_month_html),
				'anchor': month_amap[prev_month_year]
			})
		
		# Create header HTML
		header_html = []
		if len(conv['participants']) > 1:
			header_html.append('<div class="conversation-details">')
			header_html.append('<p><strong>Group Conversation</strong></p>')
			header_html.append('<p><strong>Participants:</strong> ')
			participant_info = []
			for addr in conv['participants']:
				name = contact_map.get(addr, formatPhoneNumber(addr))
				phone = formatPhoneNumberSimple(addr)
				participant_info.append(f"{name} ({phone})")
			header_html.append(', '.join(participant_info))
			header_html.append('</p>')
			header_html.append(f'<p><strong>Total Messages:</strong> {len(conv["messages"])}</p>')
			header_html.append('</div>')
		
		if len(months) > 1:
			header_html.append('<div class="month-jump"><strong>Jump to:</strong> ')
			month_links = []
			for month_year in months:
				month_links.append(f'<a href="javascript:void(0)" onclick="jumpToMonth(\'month-{month_amap[month_year]}\')">{month_year}</a>')
			header_html.append(' | '.join(month_links))
			header_html.append('</div>')
		
		# Decide if we need to chunk this conversation
		total_size = len(''.join(header_html)) + sum(len(m['html']) for m in message_htmls)
		
		if total_size > max_chunk_size:
			# Large conversation - split into chunks by month
			print(f"  Large conversation detected: {conv['name']} (~{total_size/1024/1024:.1f}MB), splitting into chunks...")
			
			chunk_num = 0
			current_chunk = []
			current_chunk_size = 0
			chunk_files = []
			
			for msg_data in message_htmls:
				msg_size = len(msg_data['html'])
				
				if current_chunk_size + msg_size > max_chunk_size and current_chunk:
					# Write current chunk
					chunk_num += 1
					chunk_filename = f"conv_{safe_id}_chunk{chunk_num}.js"
					chunk_path = os.path.join(subfolder, chunk_filename)
					
					chunk_html = ''.join(current_chunk)
					escaped_html = chunk_html.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
					
					with open(chunk_path, 'w', encoding='utf-8') as jsf:
						jsf.write(f'window.convChunk_{safe_id}_{chunk_num} = `{escaped_html}`;')
					
					chunk_files.append(chunk_filename)
					current_chunk = []
					current_chunk_size = 0
				
				current_chunk.append(msg_data['html'])
				current_chunk_size += msg_size
			
			# Write last chunk
			if current_chunk:
				chunk_num += 1
				chunk_filename = f"conv_{safe_id}_chunk{chunk_num}.js"
				chunk_path = os.path.join(subfolder, chunk_filename)
				
				chunk_html = ''.join(current_chunk)
				escaped_html = chunk_html.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
				
				with open(chunk_path, 'w', encoding='utf-8') as jsf:
					jsf.write(f'window.convChunk_{safe_id}_{chunk_num} = `{escaped_html}`;')
				
				chunk_files.append(chunk_filename)
			
			# Write header file
			header_filename = f"conv_{safe_id}_header.js"
			header_path = os.path.join(subfolder, header_filename)
			header_escaped = ''.join(header_html).replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
			
			with open(header_path, 'w', encoding='utf-8') as jsf:
				jsf.write(f'window.convHeader_{safe_id} = `{header_escaped}`;')
			
			conv_metadata.append({
				'id': safe_id,
				'chunked': True,
				'header_file': header_filename,
				'chunk_files': chunk_files,
				'name': conv['name'],
				'participants': conv['participants'],
				'msg_count': len(conv['messages']),
				'latest_date': max(conv['messages'].keys()) if conv['messages'] else 0
			})
			
		else:
			# Small enough - single file
			js_filename = f"conv_{safe_id}.js"
			js_path = os.path.join(subfolder, js_filename)
			
			full_html = ''.join(header_html) + ''.join(m['html'] for m in message_htmls)
			escaped_html = full_html.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
			
			with open(js_path, 'w', encoding='utf-8') as jsf:
				jsf.write(f'window.convData_{safe_id} = `{escaped_html}`;')
			
			conv_metadata.append({
				'id': safe_id,
				'chunked': False,
				'js_file': js_filename,
				'name': conv['name'],
				'participants': conv['participants'],
				'msg_count': len(conv['messages']),
				'latest_date': max(conv['messages'].keys()) if conv['messages'] else 0
			})
	
	# Create index HTML
	index_path = os.path.join(subfolder, "0_index.html")
	with open(index_path, 'w', encoding='utf-8') as f:
		f.write('<!DOCTYPE html>\n<html><head>\n')
		f.write('<meta charset="UTF-8">\n')
		f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
		f.write('<style>\n')
		f.write(STYLESHEET_TEMPLATE)
		f.write('</style>\n')
		f.write(f'<title>{base_filename}</title>\n')
		f.write('</head><body>\n')
		
		# Image modal (at top level, always available)
		f.write('<div id="imageModal" class="image-modal" onclick="closeImageModal()">\n')
		f.write('<span class="image-modal-close">&times;</span>\n')
		f.write('<img id="modalImage" src="" />\n')
		f.write('</div>\n')
		
		f.write('<div class="phone-view">\n')
		f.write('<div class="header">\n')
		f.write('<button class="back-button" onclick="showList()">←</button>\n')
		f.write('<h1 id="header-title">Messages</h1>\n')
		f.write('<div id="headerSearch" class="header-search">\n')
		f.write('<input type="text" id="searchInput" placeholder="Search..." oninput="filterConversations()" />\n')
		f.write('</div>\n')
		f.write('<button class="dark-mode-toggle" onclick="toggleDarkMode()" title="Toggle Dark Mode">&#127769;</button>\n')
		f.write('</div>\n')
		
		# Conversation list
		f.write('<div id="conversation-list" class="conversation-list">\n')
		
		for meta in conv_metadata:
			# Get date string
			if meta['latest_date']:
				dt = datetime.datetime.fromtimestamp(meta['latest_date'] / 1000, tz=None)
				date_str = dt.strftime('%b %d, %Y')
			else:
				date_str = ''
			
			# Get initials for avatar
			if len(meta['participants']) > 1:
				# Group conversation - create mini avatars
				is_group = True
				num_avatars = min(len(meta['participants']), 4)
				group_class = f"group-{num_avatars}"
				
				# Get first letter of each participant
				participant_initials = []
				
				# Try to split the name by comma to get individual names
				if ',' in meta.get('name', ''):
					name_parts = [n.strip() for n in meta['name'].split(',')]
				else:
					name_parts = []
				
				for i, participant in enumerate(meta['participants'][:num_avatars]):
					# Get name for this participant
					if i < len(name_parts) and name_parts[i]:
						part_name = name_parts[i]
					else:
						# Fallback to formatted phone number
						part_name = formatPhoneNumber(participant)
					
					# Get initial
					name_check = ''.join(c for c in part_name if c.isalnum() or c.isspace()).strip()
					if name_check and not name_check[0].isdigit():
						initial = part_name[0].upper()
					else:
						initial = '#'
					participant_initials.append(initial)
				
				avatar_html = f'<div class="conversation-avatar-group {group_class}">'
				for initial in participant_initials:
					avatar_html += f'<div class="mini-avatar">{initial}</div>'
				avatar_html += '</div>'
			else:
				is_group = False
				# Check if it's an unknown contact (formatted phone number)
				# Remove all non-alphanumeric except spaces to check
				name_check = ''.join(c for c in meta['name'] if c.isalnum() or c.isspace()).strip()
				if name_check.isdigit() or meta['name'].startswith('('):
					# Unknown contact - phone number
					initials = '#'
				else:
					name_parts = meta['name'].split()
					if len(name_parts) >= 2:
						initials = name_parts[0][0] + name_parts[1][0]
					else:
						initials = meta['name'][:2]
					initials = initials.upper()
				avatar_html = f'<div class="conversation-avatar">{initials}</div>'
			
			# Format subtitle
			if len(meta['participants']) > 1:
				subtitle = f"Group · {len(meta['participants'])} people"
			elif len(meta['participants']) == 1:
				subtitle = formatPhoneNumberSimple(meta['participants'][0])
			else:
				subtitle = "Unknown"
			
			f.write(f'<div class="conversation-item" data-name="{meta["name"].lower()}" data-participants="{" ".join([formatPhoneNumberSimple(p) for p in meta["participants"]])}" onclick="loadConversation(\'{meta["id"]}\', \'{meta["name"].replace("'", "\\'")}\')">\n')
			f.write(avatar_html + '\n')
			f.write('<div class="conversation-info">\n')
			f.write(f'<div class="conversation-name">{meta["name"]}</div>\n')
			f.write(f'<div class="conversation-preview">{subtitle}</div>\n')
			f.write('</div>\n')
			f.write('<div class="conversation-meta">\n')
			f.write(f'<div class="conversation-date">{date_str}</div>\n')
			f.write(f'<div class="conversation-count">{meta["msg_count"]}</div>\n')
			f.write('</div>\n')
			f.write('</div>\n')
		
		f.write('</div>\n')
		
		# Container for loaded conversation
		f.write('<div id="conversation-content" class="conversation-view"></div>\n')
		
		f.write('</div>\n')  # Close phone-view
		
		# JavaScript - define image modal functions first, before everything else
		f.write('<script>\n')
		f.write('// Image modal functions (must be globally available)\n')
		f.write('function openImageModal(src) {\n')
		f.write('  event.stopPropagation();\n')
		f.write('  const modal = document.getElementById("imageModal");\n')
		f.write('  const modalImg = document.getElementById("modalImage");\n')
		f.write('  modal.style.display = "block";\n')
		f.write('  modalImg.src = src;\n')
		f.write('}\n\n')
		
		f.write('function closeImageModal() {\n')
		f.write('  document.getElementById("imageModal").style.display = "none";\n')
		f.write('}\n\n')
		f.write('\n\n')
		f.write('// Dark mode toggle\n')
		f.write('function toggleDarkMode() {\n')
		f.write('  document.body.classList.toggle(\'dark-mode\');\n')
		f.write('  const isDark = document.body.classList.contains(\'dark-mode\');\n')
		f.write('  localStorage.setItem(\'darkMode\', isDark);\n')
		f.write('  const btn = document.querySelector(\'.dark-mode-toggle\');\n')
		f.write('  btn.innerHTML = isDark ? \'&#9728;\' : \'&#127769;\';\n')
		f.write('}\n')
		f.write('\n')
		f.write('// Load dark mode preference\n')
		f.write('if (localStorage.getItem(\'darkMode\') === \'true\') {\n')
		f.write('  document.body.classList.add(\'dark-mode\');\n')
		f.write('  const btn = document.querySelector(\'.dark-mode-toggle\');\n')
		f.write('  if (btn) btn.innerHTML = \'&#9728;\';\n')
		f.write('}\n')
		
		# Rest of the JavaScript
		f.write('const loadedConversations = new Set();\n')
		f.write('const convMetadata = ' + str(conv_metadata).replace("'", '"').replace('True', 'true').replace('False', 'false') + ';\n\n')
		
		f.write('function loadConversation(id, name) {\n')
		f.write('  document.getElementById("conversation-list").style.display = "none";\n')
		f.write('  document.querySelector(".back-button").style.display = "block";\n')
		f.write('  document.getElementById("header-title").textContent = name;\n')
		f.write('  document.getElementById("headerSearch").classList.add("hidden");\n')
		f.write('  const content = document.getElementById("conversation-content");\n')
		f.write('  \n')
		f.write('  const meta = convMetadata.find(m => m.id === id);\n')
		f.write('  if (!meta) {\n')
		f.write('    content.innerHTML = "<div style=\\"padding: 40px; text-align: center; color: red;\\">Conversation not found</div>";\n')
		f.write('    return;\n')
		f.write('  }\n')
		f.write('  \n')
		f.write('  if (loadedConversations.has(id)) {\n')
		f.write('    // Already loaded\n')
		f.write('    if (meta.chunked) {\n')
		f.write('      let html = window["convHeader_" + id] || "";\n')
		f.write('      for (let i = 1; i <= meta.chunk_files.length; i++) {\n')
		f.write('        html += window["convChunk_" + id + "_" + i] || "";\n')
		f.write('      }\n')
		f.write('      content.innerHTML = html;\n')
		f.write('    } else {\n')
		f.write('      content.innerHTML = window["convData_" + id];\n')
		f.write('    }\n')
		f.write('    content.style.display = "block";\n')
		f.write('    window.scrollTo(0, 0);\n')
		f.write('  } else {\n')
		f.write('    // Load the conversation\n')
		f.write('    content.innerHTML = "<div style=\\"padding: 40px; text-align: center;\\">Loading conversation...</div>";\n')
		f.write('    content.style.display = "block";\n')
		f.write('    \n')
		f.write('    if (meta.chunked) {\n')
		f.write('      // Load chunked conversation\n')
		f.write('      loadChunkedConversation(id, meta);\n')
		f.write('    } else {\n')
		f.write('      // Load single file\n')
		f.write('      loadScript(meta.js_file, () => {\n')
		f.write('        loadedConversations.add(id);\n')
		f.write('        content.innerHTML = window["convData_" + id];\n')
		f.write('        window.scrollTo(0, 0);\n')
		f.write('      }, () => {\n')
		f.write('        content.innerHTML = "<div style=\\"padding: 40px; text-align: center; color: red;\\">Error loading conversation</div>";\n')
		f.write('      });\n')
		f.write('    }\n')
		f.write('  }\n')
		f.write('}\n\n')
		
		f.write('function loadChunkedConversation(id, meta) {\n')
		f.write('  const content = document.getElementById("conversation-content");\n')
		f.write('  let loaded = 0;\n')
		f.write('  const total = meta.chunk_files.length + 1; // chunks + header\n')
		f.write('  \n')
		f.write('  function updateProgress() {\n')
		f.write('    loaded++;\n')
		f.write('    const pct = Math.round((loaded / total) * 100);\n')
		f.write('    const chunks = meta.chunk_files.length;\n')
		f.write('    const header = 1;\n')
		f.write('    const currentItem = loaded <= header ? \'header\' : `chunk ${loaded - header} of ${chunks}`;\n')
		f.write('    content.innerHTML = `<div style="padding: 40px; text-align: center;">\n')
		f.write('      <div style="font-size: 18px; margin-bottom: 10px;">Loading conversation...</div>\n')
		f.write('      <div style="font-size: 14px; color: #666; margin-bottom: 15px;">Loading ${currentItem}</div>\n')
		f.write('      <div style="background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden; max-width: 400px; margin: 0 auto;">\n')
		f.write('        <div style="background: #2196F3; height: 100%; width: ${pct}%; transition: width 0.3s;"></div>\n')
		f.write('      </div>\n')
		f.write('      <div style="margin-top: 10px; font-size: 16px; font-weight: bold;">${pct}%</div>\n')
		f.write('    </div>`;\n')
		f.write('    \n')
		f.write('    // Render progressively as chunks load\n')
		f.write('    if (loaded === 1) {\n')
		f.write('      // First load (header) - create container and show header\n')
		f.write('      content.innerHTML = window["convHeader_" + id] || "";\n')
		f.write('      window.scrollTo(0, 0);\n')
		f.write('    } else if (loaded > 1) {\n')
		f.write('      // Append each chunk as it loads\n')
		f.write('      const chunkNum = loaded - 1;\n')
		f.write('      const chunkData = window["convChunk_" + id + "_" + chunkNum];\n')
		f.write('      if (chunkData) {\n')
		f.write('        // Create a temporary div to parse the chunk HTML\n')
		f.write('        const tempDiv = document.createElement("div");\n')
		f.write('        tempDiv.innerHTML = chunkData;\n')
		f.write('        // Append all children to the content\n')
		f.write('        while (tempDiv.firstChild) {\n')
		f.write('          content.appendChild(tempDiv.firstChild);\n')
		f.write('        }\n')
		f.write('      }\n')
		f.write('    }\n')
		f.write('    \n')
		f.write('    if (loaded === total) {\n')
		f.write('      // All loaded, mark as complete\n')
		f.write('      loadedConversations.add(id);\n')
		f.write('      // Hide progress indicator\n')
		f.write('      const progressDivs = content.querySelectorAll("div[style*=\'padding: 40px\']");\n')
		f.write('      progressDivs.forEach(div => {\n')
		f.write('        if (div.textContent.includes("Loading")) div.remove();\n')
		f.write('      });\n')
		f.write('    }\n')
		f.write('  }\n')
		f.write('  \n')
		f.write('  function onError() {\n')
		f.write('    content.innerHTML = "<div style=\\"padding: 40px; text-align: center; color: red;\\">Error loading conversation</div>";\n')
		f.write('  }\n')
		f.write('  \n')
		f.write('  // Load header\n')
		f.write('  loadScript(meta.header_file, updateProgress, onError);\n')
		f.write('  \n')
		f.write('  // Load all chunks\n')
		f.write('  meta.chunk_files.forEach(file => {\n')
		f.write('    loadScript(file, updateProgress, onError);\n')
		f.write('  });\n')
		f.write('}\n\n')
		
		f.write('function loadScript(src, onSuccess, onError) {\n')
		f.write('  const script = document.createElement("script");\n')
		f.write('  script.src = src;\n')
		f.write('  script.onload = onSuccess;\n')
		f.write('  script.onerror = onError;\n')
		f.write('  document.head.appendChild(script);\n')
		f.write('}\n\n')
		
		f.write('function showList() {\n')
		f.write('  document.getElementById("conversation-list").style.display = "block";\n')
		f.write('  document.getElementById("conversation-content").style.display = "none";\n')
		f.write('  document.querySelector(".back-button").style.display = "none";\n')
		f.write('  document.getElementById("header-title").textContent = "Messages";\n')
		f.write('  document.getElementById("headerSearch").classList.remove("hidden");\n')
		f.write('  document.getElementById("searchInput").value = "";\n')
		f.write('  filterConversations();\n')
		f.write('  window.scrollTo(0, 0);\n')
		f.write('}\n\n')
		
		f.write('function filterConversations() {\n')
		f.write('  const searchTerm = document.getElementById("searchInput").value.toLowerCase();\n')
		f.write('  const items = document.querySelectorAll(".conversation-item");\n')
		f.write('  \n')
		f.write('  items.forEach(item => {\n')
		f.write('    const name = item.getAttribute("data-name");\n')
		f.write('    const participants = item.getAttribute("data-participants");\n')
		f.write('    const searchText = name + " " + participants;\n')
		f.write('    \n')
		f.write('    if (searchText.includes(searchTerm)) {\n')
		f.write('      item.style.display = "flex";\n')
		f.write('    } else {\n')
		f.write('      item.style.display = "none";\n')
		f.write('    }\n')
		f.write('  });\n')
		f.write('}\n')
		f.write('</script>\n')
		
		f.write('</body></html>\n')
	
	print(f"  Created 0_index.html and {len(conv_metadata)} conversation JS files\n")
	return f"{base_filename}/0_index.html"


def main():
	parser = argparse.ArgumentParser(description='Turns SMS Backup and Restore XML into HTML conversations with embedded images')
	parser.add_argument('input', metavar='input', nargs='+', type=str,
				help='Input XML file(s)')
	parser.add_argument('-o', '--output', type=str, required=True,
				help='Output directory')
	parser.add_argument('-n', '--number', type=str, required=True,
				help='Your carrier phone number')
	args = parser.parse_args()
	carrier_number = parseCarrierNumber(args.number)
	
	messages = 0
	conversations = {}
	all_type_counts = {}
	contact_map = {}  # Global contact name mapping
	debug_mode = False  # Set to True for debugging output
	locale.setlocale(locale.LC_ALL, '')
	
	print("Starting SMS XML to HTML conversion...")
	print(f"Your number: {formatPhoneNumber(carrier_number)}\n")
	
	for input_file in args.input:
		if not os.path.exists(input_file):
			print(f"Warning: File not found: {input_file}")
			continue
			
		print(f"Parsing conversations from {input_file}...")
		
		# Use iterparse for large files to avoid memory issues
		context = etree.iterparse(input_file, events=('end',), tag=('sms', 'mms'), huge_tree=True)
		
		msg_count = 0
		type_counts = {}
		
		for event, elem in context:
			if elem.tag == 'sms':
				address = parseCarrierNumber(elem.attrib['address'])
				date    = int(elem.attrib['date'])
				type_   = elem.attrib['type']
				name    = elem.attrib.get('contact_name', '(Unknown)')
				body    = elem.attrib.get('body', '')
				
				if debug_mode and msg_count < 10:
					print(f"DEBUG SMS: type={type_}, address={address}, name={name}")
					print(f"  SMS Conv Key: {address}, Name: {name}")
				
				# Store contact name mapping
				if name != '(Unknown)':
					contact_map[address] = name
				
				save_msg = SMSMsg(date, body, type_, {})
				save_msg.sender_name = name if type_ == '1' else 'You'
				save_msg.sender_address = address if type_ == '1' else carrier_number
				
				# Create conversation key (just the other person for SMS)
				conv_key = address
				conv_name = name if name != '(Unknown)' else formatPhoneNumber(address)
				
				type_counts[type_] = type_counts.get(type_, 0) + 1
				
				if conv_key not in conversations:
					conversations[conv_key] = {
						'name': conv_name,
						'participants': [address],
						'messages': {},
						'contact_map': contact_map.copy()
					}
				conversations[conv_key]['messages'][date] = save_msg
				msg_count += 1
				
			elif elem.tag == 'mms':
				save_msg = MMSMsg()
				date = int(elem.attrib['date'])
				msg_box = elem.attrib.get('msg_box', '1')
				contact_name = elem.attrib.get('contact_name', 'Unknown')
				
				if msg_box == '2':
					actual_msg_type = '151'  # Sent MMS
				else:
					actual_msg_type = '137'  # Received MMS
				
				sender_address = None
				all_addresses = []
				address_names = {}  # Map addresses to names from this MMS
				
				if debug_mode and msg_count < 10:
					print(f"\nDEBUG MMS: date={date}, msg_box={msg_box}, contact_name={contact_name}")
				
				for mms_child in elem:
					if mms_child.tag == 'parts':
						for part_child in mms_child:
							if part_child.tag == 'part':
								part_data = part_child.attrib.get('data', '')
								part_text = part_child.attrib.get('text', '')
								part_mime = part_child.attrib['ct']
								if "image" in part_mime and part_data:
									save_msg.addImageData(part_mime, part_data)
								elif "text" in part_mime:
									save_msg.text += part_text
									
					elif mms_child.tag == 'addrs':
						for addr_child in mms_child:
							if addr_child.tag == 'addr':
								parsed_addr = parseCarrierNumber(addr_child.attrib['address'])
								addr_type = addr_child.attrib.get('type', '137')
								
								if debug_mode and msg_count < 10:
									print(f"  Address: {parsed_addr}, type={addr_type}")
								
								# Skip empty addresses and your own number
								if parsed_addr and carrier_number not in parsed_addr:
									all_addresses.append(parsed_addr)
									
									# In received MMS (msg_box=1), type 137 indicates the sender
									# Type 151 typically indicates recipients/CC
									if addr_type == '137' and msg_box == '1':
										sender_address = parsed_addr
										if debug_mode and msg_count < 10:
											print(f"    -> Identified as sender (type 137)")
				
				# Parse contact_name to extract individual names
				if contact_name and contact_name != 'Unknown':
					# The contact_name order matches the address field order in the XML
					address_field = elem.attrib.get('address', '')
					
					if ',' in contact_name and address_field:
						names = [n.strip() for n in contact_name.split(',')]
						
						if debug_mode and msg_count < 10:
							print(f"  Parsing names: {names}")
							print(f"  Address field: {address_field}")
						
						# Parse the address field which has addresses in same order as names
						raw_addresses = [parseCarrierNumber(a.strip()) for a in address_field.split('~')]
						# Filter out your own number
						ordered_addresses = [a for a in raw_addresses if a and carrier_number not in a]
						
						if debug_mode and msg_count < 10:
							print(f"  Ordered addresses: {ordered_addresses}")
						
						# Now match names to addresses in order
						for i, addr in enumerate(ordered_addresses):
							if i < len(names):
								address_names[addr] = names[i]
								contact_map[addr] = names[i]
								if debug_mode and msg_count < 10:
									print(f"  Mapped: {addr} -> {names[i]}")
					elif address_field and '~' not in address_field:
						# Single person conversation, map the name to the single address
						single_addr = parseCarrierNumber(address_field)
						if single_addr and carrier_number not in single_addr:
							address_names[single_addr] = contact_name
							contact_map[single_addr] = contact_name
							if debug_mode and msg_count < 10:
								print(f"  Single person mapped: {single_addr} -> {contact_name}")
				
				# Set sender info
				if msg_box == '2':
					sender_address_final = carrier_number
					sender_name_final = 'You'
				elif sender_address:
					sender_address_final = sender_address
					# Try multiple sources for the name
					sender_name_final = (address_names.get(sender_address) or 
					                    contact_map.get(sender_address) or 
					                    formatPhoneNumber(sender_address))
					if debug_mode and msg_count < 10:
						print(f"  Sender address: {sender_address}")
						print(f"  address_names.get: {address_names.get(sender_address)}")
						print(f"  contact_map.get: {contact_map.get(sender_address)}")
						print(f"  Final sender: {sender_name_final} ({sender_address_final})")
				else:
					sender_address_final = all_addresses[0] if all_addresses else None
					if sender_address_final:
						sender_name_final = (address_names.get(sender_address_final) or 
						                    contact_map.get(sender_address_final) or 
						                    formatPhoneNumber(sender_address_final))
					else:
						sender_name_final = contact_name
					if debug_mode and msg_count < 10:
						print(f"  No explicit sender, using first address: {sender_address_final}")
						print(f"  Sender name: {sender_name_final}")
				
				# Store sender info in the message
				save_msg.sender_address = sender_address_final
				save_msg.sender_name = sender_name_final
				save_msg.type_ = actual_msg_type
				save_msg.timestamp = date
				
				# Create conversation key from all participants
				# Remove duplicates and normalize
				unique_addresses = list(set(all_addresses))
				
				# Preserve original order from address field for display
				address_field = elem.attrib.get('address', '')
				if address_field:
					raw_addresses = [parseCarrierNumber(a.strip()) for a in address_field.split('~')]
					ordered_unique = [a for a in raw_addresses if a in unique_addresses and carrier_number not in a]
				else:
					ordered_unique = unique_addresses
				
				# If only one unique participant (excluding self), treat as 1-on-1
				if len(unique_addresses) == 1:
					conv_key = unique_addresses[0]
				else:
					conv_key = makeConversationKey(unique_addresses)
				
				if debug_mode and msg_count < 10:
					print(f"  MMS All addresses: {all_addresses}")
					print(f"  MMS Unique addresses: {unique_addresses}")
					print(f"  MMS Ordered unique: {ordered_unique}")
					print(f"  MMS Conv Key: {conv_key}")
				
				type_counts[actual_msg_type] = type_counts.get(actual_msg_type, 0) + 1
				
				if conv_key not in conversations:
					# Use the single person's name for 1-on-1, group name for actual groups
					if len(unique_addresses) == 1:
						conv_name = contact_map.get(unique_addresses[0]) or formatPhoneNumber(unique_addresses[0])
					else:
						conv_name = contact_name
					
					conversations[conv_key] = {
						'name': conv_name,
						'participants': ordered_unique,  # Use ordered list
						'messages': {},
						'contact_map': {}
					}
				
				# Update the contact map for this conversation
				conversations[conv_key]['contact_map'].update(contact_map)
				
				# Store the message
				conversations[conv_key]['messages'][date] = save_msg
				msg_count += 1
			
			# Clear element to free memory
			elem.clear()
			while elem.getprevious() is not None:
				del elem.getparent()[0]
		
		# Clean up
		del context
		
		messages += msg_count
		for type_, count in type_counts.items():
			all_type_counts[type_] = all_type_counts.get(type_, 0) + count
		
	print(f"\nParsed {messages} messages in {len(conversations)} conversations")
	
	# Sort conversations by most recent message date (descending)
	sorted_conv_keys = sorted(conversations.keys(), 
	                          key=lambda k: max(conversations[k]['messages'].keys()) if conversations[k]['messages'] else 0,
	                          reverse=True)
	
	print("\nMessage type distribution:")
	for type_, count in sorted(all_type_counts.items()):
		type_name = {
			'1': 'Received SMS', 
			'2': 'Sent SMS', 
			'130': 'Received MMS (special)', 
			'137': 'Received MMS', 
			'151': 'Sent MMS'
		}.get(type_, f'Unknown ({type_})')
		print(f"  Type {type_} ({type_name}): {count} messages")
	
	print("\nGenerating HTML file with embedded images...")
	filename = dumpConversations(args.output, conversations, carrier_number, sorted_conv_keys, args.input[0])
	print(f"\nSuccess! Created {filename} in {args.output}")
	print(f"Open {filename} in your web browser to view all your conversations.")
	
	sys.exit(0)
	
if __name__ == '__main__':
	main()