'''AI 出题服务（对接点）。出题实现由队长 E 负责，本模块只负责调用与降级兜底。'''


def generate_claim_questions(post):
    '''获取帖子的隐藏特征问题。

    TODO(对接队长 E): AI 出题实现由队长 E 负责（阿里云百炼 LLM）。
    本模块后续改为调用 E 提供的出题服务/接口。
    在此之前返回降级占位问题，保证认领链路可跑。
    '''
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
