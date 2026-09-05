'''AI 出题服务：根据物品详情生成隐藏特征问题（真实 LLM + 降级兜底）。'''

import json
import os

SYSTEM_PROMPT = (
    '你是失物招领平台的出题助手。根据物品的描述和结构化属性，生成 2~3 个'
    '「隐藏特征问题」，用来验证认领者是不是真正的失主。要求：\n'
    '1. 问题必须是只有真正拥有/使用过这件物品的人才能答上来的细节，'
    '不要问照片里一眼可见的外观（如颜色、品牌、型号）。\n'
    '2. 问题要具体、可回答，答案是一个具体事实（如内部物品、独有标记、配件、使用痕迹等）。\n'
    '3. 只输出 JSON 字符串数组，不要输出任何其他内容。\n'
    '示例输出：["手机壳内侧贴了什么？","耳机盒里除了耳机还放了什么？"]'
)


def _build_item_description(post, attr):
    parts = []
    if post.description:
        parts.append(f'物品描述：{post.description}')
    if attr is not None:
        if attr.brand:
            parts.append(f'品牌：{attr.brand}')
        if attr.primary_color:
            parts.append(f'主色：{attr.primary_color}')
        if attr.text_mark:
            parts.append(f'文字标识：{attr.text_mark}')
        if attr.distinctive_features:
            parts.append(f'显著特征：{attr.distinctive_features}')
    return '\n'.join(parts) if parts else '（无更多信息）'


def _fallback_questions(post):
    '''无 key 或调用失败时的降级占位问题，保证链路可跑。'''
    attr = getattr(post, 'attribute', None)
    questions = ['请描述这件物品最明显的特征（外观、标记或贴纸等）？']
    if attr is not None:
        if attr.primary_color:
            questions.append('它的主色是什么？')
        if attr.brand:
            questions.append('它是什么品牌？')
        if attr.text_mark:
            questions.append('它上面有什么文字或标记？')
    return questions[:3]


def _parse_questions(content):
    '''从 LLM 输出中解析问题列表，兼容 markdown 代码块围栏。'''
    text = (content or '').strip()
    if text.startswith('```'):
        text = text.strip('`').strip()
        if text.lower().startswith('json'):
            text = text[4:].strip()
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return []
    if isinstance(data, list):
        return [str(x).strip() for x in data if str(x).strip()][:3]
    return []


def generate_claim_questions(post):
    '''根据物品详情生成隐藏问题。优先 LLM；无 key 或调用失败则降级为占位问题。'''
    api_key = os.environ.get('DASHSCOPE_API_KEY', '').strip()
    if not api_key:
        return _fallback_questions(post)

    attr = getattr(post, 'attribute', None)
    item_info = _build_item_description(post, attr)

    try:
        import dashscope
        from dashscope import Generation

        dashscope.api_key = api_key
        resp = Generation.call(
            model='qwen-plus',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': item_info},
            ],
            result_format='message',
        )
        if resp.status_code != 200:
            return _fallback_questions(post)
        questions = _parse_questions(resp.output.choices[0].message.content)
        return questions or _fallback_questions(post)
    except Exception:
        return _fallback_questions(post)
