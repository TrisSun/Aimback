'''AI 出题服务：根据物品详情生成隐藏特征问题。'''


def generate_claim_questions(post):
    '''根据物品详情生成隐藏问题（占位实现）。

    TODO(赵悦): 接入真实 AI 服务（阿里云百炼 LLM 等）。
    输入：post.description + post.attribute（brand/primary_color/text_mark/distinctive_features）
    输出：2~3 个隐藏特征问题。
    v0 先返回基于结构化属性的占位问题，保证链路可跑通。
    '''
    questions = []
    attr = getattr(post, 'attribute', None)

    questions.append('请描述这件物品最明显的特征（外观、标记或贴纸等）？')

    if attr is not None:
        if attr.primary_color:
            questions.append('它的主色是什么？')
        if attr.brand:
            questions.append('它是什么品牌？')
        if attr.text_mark:
            questions.append('它上面有什么文字或标记？')

    return questions[:3]
