import json
import logging

import requests
from flask import render_template, request, jsonify, Blueprint
from flask_login import current_user

from config import Config
from app.utils.kg_query import query_knowledge_graph
# from run import app

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


@chat_bp.route('/')
def index():
    """问答系统首页"""
    return render_template('chat.html')


@chat_bp.route('/api/ask', methods=['POST'])
def ask_question():
    """处理用户提问"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()

        if not question:
            return jsonify({'error': '问题不能为空'}), 400

        # 首先尝试从知识图谱获取答案
        kg_response = query_knowledge_graph(question)
        kg_answer = kg_response.get('answer') if kg_response else None

        # 调用DeepSeek API
        deepseek_response = call_deepseek_api(question)

        if kg_answer:
            combined_answer = f"# 知识图谱相关知识：{kg_answer}\n\n# DeepSeek回答：{deepseek_response}"
            return jsonify({
                'source': 'knowledge_graph_and_deepseek',
                'answer': combined_answer,
                'entities': kg_response.get('entities', [])
            })
        else:
            return jsonify({
                'source': 'deepseek',
                'answer': deepseek_response
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def call_deepseek_api(question, conversation_id="", files=None):
    """调用本地Dify部署的DeepSeek API"""
    headers = {
        'Authorization': f'Bearer {Config.DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'inputs': {},
        'query': question,
        'response_mode': 'blocking',  # 先尝试使用阻塞模式
        'conversation_id': conversation_id,
        'user': current_user.username,
        'files': files if files else []
    }

    try:
        # 确保URL正确
        api_url = f'{Config.DEEPSEEK_API_BASE.rstrip("/")}/chat-messages'
        response = requests.post(
            api_url,
            headers=headers,
            json=payload  # 使用json参数自动处理序列化
        )

        # 调试输出
        print("Status code:", response.status_code)
        print("Response headers:", response.headers)
        print("Response content:", response.text)

        response.raise_for_status()

        # 尝试解析JSON
        try:
            result = response.json()
            return result.get('answer', 'No answer found in response')
        except ValueError as e:
            raise Exception(f"Invalid JSON response: {response.text}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"DeepSeek API调用失败: {str(e)}")
