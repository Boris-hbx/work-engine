from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, send_from_directory
import os
import secrets
import re
import random
import json
import uuid
from datetime import datetime

# Get the project root directory (parent of backend/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
            static_folder=os.path.join(BASE_DIR, 'assets'),
            static_url_path='/assets')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))

# Data file paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
TODOLIST_FILE = os.path.join(DATA_DIR, 'todolist.txt')
MOTIVATION_FILE = os.path.join(DATA_DIR, 'motivation.txt')
QUOTES_FILE = os.path.join(DATA_DIR, 'quotes.txt')
BUBBLES_FILE = os.path.join(DATA_DIR, 'bubbles.json')
TODOS_FILE = os.path.join(DATA_DIR, 'todos.json')
PROMPTS_FILE = os.path.join(DATA_DIR, 'prompts.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

def read_config():
    """Read config from config.json"""
    if not os.path.exists(CONFIG_FILE):
        return {"prompt_delete_password": "8888"}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"prompt_delete_password": "8888"}

def normalize_content(content):
    """Clean up content: normalize line endings and remove excessive blank lines"""
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip() + '\n'

def read_quotes():
    """Read all quotes from quotes.txt"""
    if not os.path.exists(QUOTES_FILE):
        return ["今天也要加油！"]
    try:
        with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
            quotes = [line.strip() for line in f.readlines() if line.strip()]
        return quotes if quotes else ["今天也要加油！"]
    except:
        return ["今天也要加油！"]

def get_random_quote():
    """Get a random quote"""
    quotes = read_quotes()
    return random.choice(quotes)

def parse_todolist():
    """Parse todolist.txt and return structured data"""
    if not os.path.exists(TODOLIST_FILE):
        return {"today": "", "this_week": "", "next_30_days": ""}

    try:
        with open(TODOLIST_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        today_header = "-------------------Today-------------------"
        week_header = "-------------------This Week-------------------"
        month_header = "-------------------The next 30 days-------------------"

        sections = {"today": "", "this_week": "", "next_30_days": ""}

        if today_header in content:
            parts = content.split(today_header, 1)
            if len(parts) > 1:
                remaining = parts[1]
                if week_header in remaining:
                    today_part, remaining = remaining.split(week_header, 1)
                    sections["today"] = today_part.strip()
                    if month_header in remaining:
                        week_part, month_part = remaining.split(month_header, 1)
                        sections["this_week"] = week_part.strip()
                        sections["next_30_days"] = month_part.strip()
                    else:
                        sections["this_week"] = remaining.strip()
                else:
                    sections["today"] = remaining.strip()

        return sections

    except Exception as e:
        print(f"Error parsing todolist.txt: {e}")
        return {"today": "", "this_week": "", "next_30_days": ""}

def parse_motivation():
    """Parse motivation.txt and return structured data by categories"""
    if not os.path.exists(MOTIVATION_FILE):
        return {"leader": "", "family": "", "mindset": "", "health": ""}

    try:
        with open(MOTIVATION_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        leader_header = "-------------------精神领袖-------------------"
        family_header = "-------------------家庭责任-------------------"
        mindset_header = "-------------------心态修炼-------------------"
        health_header = "-------------------健康人生-------------------"

        sections = {"leader": "", "family": "", "mindset": "", "health": ""}

        if leader_header in content:
            parts = content.split(leader_header, 1)
            if len(parts) > 1:
                remaining = parts[1]
                if family_header in remaining:
                    leader_part, remaining = remaining.split(family_header, 1)
                    sections["leader"] = leader_part.strip()
                    if mindset_header in remaining:
                        family_part, remaining = remaining.split(mindset_header, 1)
                        sections["family"] = family_part.strip()
                        if health_header in remaining:
                            mindset_part, health_part = remaining.split(health_header, 1)
                            sections["mindset"] = mindset_part.strip()
                            sections["health"] = health_part.strip()
                        else:
                            sections["mindset"] = remaining.strip()
                    else:
                        sections["family"] = remaining.strip()
                else:
                    sections["leader"] = remaining.strip()

        return sections

    except Exception as e:
        print(f"Error parsing motivation.txt: {e}")
        return {"leader": "", "family": "", "mindset": "", "health": ""}

@app.route('/sw.js')
def service_worker():
    """Serve service worker from root path"""
    return send_from_directory(os.path.join(BASE_DIR, 'assets'), 'sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest from root path"""
    return send_from_directory(os.path.join(BASE_DIR, 'assets'), 'manifest.json', mimetype='application/json')

@app.route('/')
def index():
    """Redirect to /todo"""
    return redirect(url_for('todo'))

@app.route('/todo')
def todo():
    """Render Todo page"""
    todo_data = parse_todolist()
    quote = get_random_quote()
    return render_template('todo.html', todo=todo_data, quote=quote, current_page='todo')

@app.route('/motivation')
def motivation():
    """Render Motivation page"""
    motivation_data = parse_motivation()
    quote = get_random_quote()
    return render_template('motivation.html', motivation=motivation_data, quote=quote, current_page='motivation')

@app.route('/bubble')
def bubble():
    """Render Bubble Chart Tool page"""
    quote = get_random_quote()
    return render_template('bubble.html', quote=quote, current_page='bubble')

@app.route('/prompts')
def prompts():
    """Render Prompt Log page"""
    quote = get_random_quote()
    return render_template('prompts.html', quote=quote, current_page='prompts')

@app.route('/aichat')
def aichat():
    """Render AI Chat page"""
    quote = get_random_quote()
    return render_template('aichat.html', quote=quote, current_page='aichat')

@app.route('/api/quote/random')
def random_quote():
    """Get a random quote via API"""
    return jsonify({'quote': get_random_quote()})

@app.route('/api/quotes', methods=['GET'])
def get_all_quotes():
    """Get all quotes"""
    return jsonify({'quotes': read_quotes()})

@app.route('/api/quotes', methods=['POST'])
def save_quotes():
    """Save all quotes"""
    try:
        data = request.get_json()
        quotes = data.get('quotes', [])
        content = '\n'.join(quotes)
        with open(QUOTES_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_section/<section>', methods=['POST'])
def save_section(section):
    """Save a single section of the todo list via AJAX"""
    today_header = "-------------------Today-------------------"
    week_header = "-------------------This Week-------------------"
    month_header = "-------------------The next 30 days-------------------"

    section_map = {
        'today': 'today',
        'week': 'this_week',
        'month': 'next_30_days'
    }

    if section not in section_map:
        return jsonify({'success': False, 'error': 'Invalid section'})

    try:
        data = request.get_json()
        new_content = data.get('content', '').strip()

        sections = parse_todolist()
        sections[section_map[section]] = new_content

        file_content = f"{today_header}\n{sections['today']}\n\n{week_header}\n{sections['this_week']}\n\n{month_header}\n{sections['next_30_days']}\n"
        file_content = normalize_content(file_content)

        with open(TODOLIST_FILE, 'w', encoding='utf-8') as f:
            f.write(file_content)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_motivation/<section>', methods=['POST'])
def save_motivation_section(section):
    """Save a single section of motivation via AJAX"""
    leader_header = "-------------------精神领袖-------------------"
    family_header = "-------------------家庭责任-------------------"
    mindset_header = "-------------------心态修炼-------------------"
    health_header = "-------------------健康人生-------------------"

    section_map = {
        'leader': 'leader',
        'family': 'family',
        'mindset': 'mindset',
        'health': 'health'
    }

    if section not in section_map:
        return jsonify({'success': False, 'error': 'Invalid section'})

    try:
        data = request.get_json()
        new_content = data.get('content', '').strip()

        sections = parse_motivation()
        sections[section_map[section]] = new_content

        file_content = f"{leader_header}\n{sections['leader']}\n\n{family_header}\n{sections['family']}\n\n{mindset_header}\n{sections['mindset']}\n\n{health_header}\n{sections['health']}\n"
        file_content = normalize_content(file_content)

        with open(MOTIVATION_FILE, 'w', encoding='utf-8') as f:
            f.write(file_content)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ Todo Items with Quadrants ============

def read_todos():
    """Read all todo items from todos.json"""
    if not os.path.exists(TODOS_FILE):
        return {"items": []}
    try:
        with open(TODOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"items": []}

def save_todos(data):
    """Save all todo items to todos.json"""
    with open(TODOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todo items, optionally filtered by tab"""
    tab = request.args.get('tab', None)
    data = read_todos()
    items = data.get('items', [])

    if tab:
        items = [item for item in items if item.get('tab') == tab]

    # Sort: incomplete first, then by created_at
    items.sort(key=lambda x: (x.get('completed', False), x.get('created_at', '')))

    return jsonify({'items': items})

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo item"""
    try:
        req_data = request.get_json()
        now = datetime.now().isoformat()

        item = {
            'id': str(uuid.uuid4())[:8],
            'text': req_data.get('text', ''),
            'tab': req_data.get('tab', 'today'),
            'quadrant': req_data.get('quadrant', 'important-not-urgent'),
            'completed': False,
            'completed_at': None,
            'created_at': now,
            'updated_at': now
        }

        data = read_todos()
        data['items'].append(item)
        save_todos(data)

        return jsonify({'success': True, 'item': item})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/todos/<item_id>', methods=['PUT'])
def update_todo(item_id):
    """Update a todo item (text, quadrant, tab, completed status)"""
    try:
        req_data = request.get_json()
        data = read_todos()

        for i, item in enumerate(data['items']):
            if item['id'] == item_id:
                # Update fields if provided
                if 'text' in req_data:
                    data['items'][i]['text'] = req_data['text']
                if 'quadrant' in req_data:
                    data['items'][i]['quadrant'] = req_data['quadrant']
                if 'tab' in req_data:
                    data['items'][i]['tab'] = req_data['tab']
                if 'completed' in req_data:
                    data['items'][i]['completed'] = req_data['completed']
                    if req_data['completed']:
                        data['items'][i]['completed_at'] = datetime.now().isoformat()
                    else:
                        data['items'][i]['completed_at'] = None

                data['items'][i]['updated_at'] = datetime.now().isoformat()
                save_todos(data)
                return jsonify({'success': True, 'item': data['items'][i]})

        return jsonify({'success': False, 'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/todos/<item_id>', methods=['DELETE'])
def delete_todo(item_id):
    """Delete a todo item"""
    try:
        data = read_todos()
        data['items'] = [item for item in data['items'] if item['id'] != item_id]
        save_todos(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/todos/batch', methods=['PUT'])
def batch_update_todos():
    """Batch update multiple todo items (for reordering after drag)"""
    try:
        req_data = request.get_json()
        updates = req_data.get('updates', [])

        data = read_todos()
        now = datetime.now().isoformat()

        for update in updates:
            item_id = update.get('id')
            for i, item in enumerate(data['items']):
                if item['id'] == item_id:
                    if 'quadrant' in update:
                        data['items'][i]['quadrant'] = update['quadrant']
                    if 'tab' in update:
                        data['items'][i]['tab'] = update['tab']
                    data['items'][i]['updated_at'] = now
                    break

        save_todos(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ Bubble Chart Version Control ============

def read_bubbles():
    """Read all bubble charts from bubbles.json"""
    if not os.path.exists(BUBBLES_FILE):
        return []
    try:
        with open(BUBBLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_bubbles(bubbles):
    """Save all bubble charts to bubbles.json"""
    with open(BUBBLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(bubbles, f, ensure_ascii=False, indent=2)

def find_bubble(bubble_id):
    """Find a bubble chart by ID"""
    bubbles = read_bubbles()
    for b in bubbles:
        if b['id'] == bubble_id:
            return b
    return None

@app.route('/api/bubbles', methods=['GET'])
def get_bubbles():
    """Get all saved bubble charts (list view)"""
    bubbles = read_bubbles()
    # Return simplified list for sidebar
    result = [{
        'id': b['id'],
        'title': b['title'],
        'description': b.get('description', ''),
        'created_at': b['created_at'],
        'updated_at': b['updated_at']
    } for b in bubbles]
    # Sort by updated_at descending
    result.sort(key=lambda x: x['updated_at'], reverse=True)
    return jsonify({'bubbles': result})

@app.route('/api/bubbles/<bubble_id>', methods=['GET'])
def get_bubble(bubble_id):
    """Get a specific bubble chart by ID"""
    bubble = find_bubble(bubble_id)
    if bubble:
        return jsonify({'success': True, 'bubble': bubble})
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.route('/api/bubbles', methods=['POST'])
def create_bubble():
    """Create a new bubble chart"""
    try:
        data = request.get_json()
        now = datetime.now().isoformat()
        bubble = {
            'id': str(uuid.uuid4())[:8],
            'title': data.get('title', '未命名图表'),
            'description': data.get('description', ''),
            'x_label': data.get('x_label', '投入成本'),
            'y_label': data.get('y_label', '恢复效果'),
            'data': data.get('data', []),
            'created_at': now,
            'updated_at': now
        }
        bubbles = read_bubbles()
        bubbles.append(bubble)
        save_bubbles(bubbles)
        return jsonify({'success': True, 'bubble': bubble})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/bubbles/<bubble_id>', methods=['PUT'])
def update_bubble(bubble_id):
    """Update an existing bubble chart"""
    try:
        data = request.get_json()
        bubbles = read_bubbles()
        for i, b in enumerate(bubbles):
            if b['id'] == bubble_id:
                bubbles[i]['title'] = data.get('title', b['title'])
                bubbles[i]['description'] = data.get('description', b.get('description', ''))
                bubbles[i]['x_label'] = data.get('x_label', b['x_label'])
                bubbles[i]['y_label'] = data.get('y_label', b['y_label'])
                bubbles[i]['data'] = data.get('data', b['data'])
                bubbles[i]['updated_at'] = datetime.now().isoformat()
                save_bubbles(bubbles)
                return jsonify({'success': True, 'bubble': bubbles[i]})
        return jsonify({'success': False, 'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/bubbles/<bubble_id>', methods=['DELETE'])
def delete_bubble(bubble_id):
    """Delete a bubble chart"""
    try:
        bubbles = read_bubbles()
        bubbles = [b for b in bubbles if b['id'] != bubble_id]
        save_bubbles(bubbles)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/bubbles/<bubble_id>/duplicate', methods=['POST'])
def duplicate_bubble(bubble_id):
    """Duplicate a bubble chart"""
    try:
        bubble = find_bubble(bubble_id)
        if not bubble:
            return jsonify({'success': False, 'error': 'Not found'}), 404

        now = datetime.now().isoformat()
        new_bubble = {
            'id': str(uuid.uuid4())[:8],
            'title': bubble['title'] + ' (副本)',
            'description': bubble.get('description', ''),
            'x_label': bubble['x_label'],
            'y_label': bubble['y_label'],
            'data': bubble['data'].copy(),
            'created_at': now,
            'updated_at': now
        }
        bubbles = read_bubbles()
        bubbles.append(new_bubble)
        save_bubbles(bubbles)
        return jsonify({'success': True, 'bubble': new_bubble})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ Prompt Log ============

def read_prompts():
    """Read all prompts from prompts.json"""
    if not os.path.exists(PROMPTS_FILE):
        return []
    try:
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_prompts(prompts):
    """Save all prompts to prompts.json"""
    with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Get all prompts"""
    prompts = read_prompts()
    # Sort by created_at descending (newest first)
    prompts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify({'prompts': prompts})

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    """Create a new prompt log entry"""
    try:
        data = request.get_json()
        now = datetime.now().isoformat()
        prompt = {
            'id': str(uuid.uuid4())[:8],
            'content': data.get('content', ''),
            'tags': data.get('tags', []),
            'created_at': now
        }
        prompts = read_prompts()
        prompts.append(prompt)
        save_prompts(prompts)
        return jsonify({'success': True, 'prompt': prompt})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/prompts/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """Update a prompt entry"""
    try:
        data = request.get_json()
        prompts = read_prompts()
        for i, p in enumerate(prompts):
            if p['id'] == prompt_id:
                if 'content' in data:
                    prompts[i]['content'] = data['content']
                if 'tags' in data:
                    prompts[i]['tags'] = data['tags']
                save_prompts(prompts)
                return jsonify({'success': True, 'prompt': prompts[i]})
        return jsonify({'success': False, 'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """Delete a prompt entry (requires password)"""
    try:
        data = request.get_json() or {}
        password = data.get('password', '')

        # Read config for password
        config = read_config()
        correct_password = config.get('prompt_delete_password', '8888')

        if password != correct_password:
            return jsonify({'success': False, 'error': '密码错误'}), 403

        prompts = read_prompts()
        prompts = [p for p in prompts if p['id'] != prompt_id]
        save_prompts(prompts)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ AI Chat API ============

import requests

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send message to AI model and get response"""
    try:
        data = request.get_json()
        model_type = data.get('model', 'openai')  # 'openai' or 'deepseek'
        messages = data.get('messages', [])

        if not messages:
            return jsonify({'success': False, 'error': 'No messages provided'})

        config = read_config()
        ai_config = config.get('ai_models', {}).get(model_type, {})

        api_key = ai_config.get('api_key', '')
        api_base = ai_config.get('api_base', '')
        model_name = ai_config.get('model', '')
        enabled = ai_config.get('enabled', False)

        if not enabled or not api_key:
            return jsonify({
                'success': False,
                'error': f'{model_type} 未配置或未启用，请在 data/config.json 中配置 api_key 并设置 enabled: true'
            })

        # Call OpenAI-compatible API (both OpenAI and DeepSeek use this format)
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model_name,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 2000
        }

        response = requests.post(
            f'{api_base}/chat/completions',
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            error_msg = response.json().get('error', {}).get('message', response.text)
            return jsonify({'success': False, 'error': f'API错误: {error_msg}'})

        result = response.json()
        assistant_message = result['choices'][0]['message']['content']

        return jsonify({
            'success': True,
            'message': assistant_message,
            'model': model_name
        })

    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'API请求超时，请重试'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chat/models', methods=['GET'])
def get_chat_models():
    """Get available AI models and their status"""
    config = read_config()
    ai_models = config.get('ai_models', {})

    models_status = {}
    for model_type, model_config in ai_models.items():
        models_status[model_type] = {
            'enabled': model_config.get('enabled', False),
            'configured': bool(model_config.get('api_key', ''))
        }

    return jsonify({'models': models_status})

@app.route('/api/chat/config', methods=['POST'])
def save_chat_config():
    """Save API key for a specific model"""
    try:
        data = request.get_json()
        model_type = data.get('model', '')
        api_key = data.get('api_key', '')

        if not model_type:
            return jsonify({'success': False, 'error': 'Model type required'})

        config = read_config()
        if 'ai_models' not in config:
            config['ai_models'] = {}
        if model_type not in config['ai_models']:
            config['ai_models'][model_type] = {}

        config['ai_models'][model_type]['api_key'] = api_key
        config['ai_models'][model_type]['enabled'] = bool(api_key)

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
