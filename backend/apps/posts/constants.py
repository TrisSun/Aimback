"""帖子模块的稳定枚举值，与 docs/接口契约.md 保持一致。"""

POST_TYPE_CHOICES = [
    ("lost", "丢失"),
    ("found", "捡到"),
]

POST_STATUS_CHOICES = [
    ("draft", "草稿"),
    ("published", "已发布"),
    ("claiming", "认领中"),
    ("completed", "已完成"),
    ("closed", "已关闭"),
]

# 公开列表/硬过滤只允许这两个状态，草稿、已完成、已关闭不可被搜索命中。
POST_STATUS_SEARCHABLE = ["published", "claiming"]

CUSTODY_TYPE_CHOICES = [
    ("personal", "个人保管"),
    ("official", "官方保管"),
]

REVIEW_STATUS_CHOICES = [
    ("pending", "待审核"),
    ("approved", "通过"),
    ("rejected", "拒绝"),
]

PRIMARY_COLOR_CHOICES = [
    ("black", "黑"),
    ("white", "白"),
    ("gray", "灰"),
    ("red", "红"),
    ("blue", "蓝"),
    ("green", "绿"),
    ("yellow", "黄"),
    ("orange", "橙"),
    ("pink", "粉"),
    ("purple", "紫"),
    ("brown", "棕"),
    ("gold", "金"),
    ("silver", "银"),
    ("navy", "藏青"),
    ("other", "其他"),
]

PRIMARY_COLOR_VALUES = {code for code, _ in PRIMARY_COLOR_CHOICES}

REGION_LEVEL_CHOICES = [
    ("province", "省"),
    ("city", "市"),
    ("district", "区/县"),
]

PLACE_TYPE_CHOICES = [
    ("school", "学校"),
    ("mall", "商场"),
    ("station", "车站"),
    ("park", "公园"),
    ("community", "社区"),
    ("office", "办公场所"),
    ("other", "其他"),
]

CATEGORY_L1_CHOICES = [
    ("electronics", "电子设备"),
    ("documents", "证件"),
    ("bags", "包袋"),
    ("clothing", "衣物"),
    ("accessories", "饰品"),
    ("stationery", "文具"),
    ("keys", "钥匙与门禁"),
    ("other", "其他"),
]

CATEGORY_L2_BY_L1 = {
    "electronics": [
        ("phone", "手机"),
        ("laptop", "笔记本电脑"),
        ("tablet", "平板"),
        ("headphones", "耳机"),
        ("other_electronics", "其他电子设备"),
    ],
    "documents": [
        ("id_card", "身份证"),
        ("student_id", "学生证"),
        ("bank_card", "银行卡"),
        ("driver_license", "驾驶证"),
        ("other_documents", "其他证件"),
    ],
    "bags": [
        ("backpack", "双肩包"),
        ("wallet", "钱包"),
        ("handbag", "手提包"),
        ("other_bags", "其他包袋"),
    ],
    "clothing": [
        ("jacket", "外套"),
        ("scarf", "围巾"),
        ("other_clothing", "其他衣物"),
    ],
    "accessories": [
        ("watch", "手表"),
        ("glasses", "眼镜"),
        ("jewelry", "首饰"),
        ("other_accessories", "其他饰品"),
    ],
    "stationery": [
        ("book", "书籍"),
        ("stationery_box", "文具盒"),
        ("other_stationery", "其他文具"),
    ],
    "keys": [
        ("keys", "钥匙"),
        ("access_card", "门禁卡"),
        ("other_keys", "其他钥匙/门禁"),
    ],
    "other": [
        ("other", "其他"),
    ],
}

CATEGORY_L1_LABELS = dict(CATEGORY_L1_CHOICES)
CATEGORY_L2_LABELS = {
    code: label
    for items in CATEGORY_L2_BY_L1.values()
    for code, label in items
}

CATEGORY_L2_CHOICES = [
    (code, label)
    for items in CATEGORY_L2_BY_L1.values()
    for code, label in items
]


def is_valid_category(category_l1: str, category_l2: str) -> bool:
    """判断二级分类是否属于指定一级分类。"""
    allowed = {code for code, _ in CATEGORY_L2_BY_L1.get(category_l1, [])}
    return category_l2 in allowed
