export const CATEGORY_L1 = [
  { value: 'electronics', label: '电子设备' },
  { value: 'documents', label: '证件' },
  { value: 'bags', label: '包袋' },
  { value: 'clothing', label: '衣物' },
  { value: 'accessories', label: '饰品' },
  { value: 'stationery', label: '文具' },
  { value: 'keys', label: '钥匙与门禁' },
  { value: 'other', label: '其他' },
] as const

export const CATEGORY_L2_BY_L1: Record<string, { value: string; label: string }[]> = {
  electronics: [
    { value: 'phone', label: '手机' },
    { value: 'laptop', label: '笔记本电脑' },
    { value: 'tablet', label: '平板' },
    { value: 'headphones', label: '耳机' },
    { value: 'other_electronics', label: '其他电子设备' },
  ],
  documents: [
    { value: 'id_card', label: '身份证' },
    { value: 'student_id', label: '学生证' },
    { value: 'bank_card', label: '银行卡' },
    { value: 'driver_license', label: '驾驶证' },
    { value: 'other_documents', label: '其他证件' },
  ],
  bags: [
    { value: 'backpack', label: '双肩包' },
    { value: 'wallet', label: '钱包' },
    { value: 'handbag', label: '手提包' },
    { value: 'other_bags', label: '其他包袋' },
  ],
  clothing: [
    { value: 'jacket', label: '外套' },
    { value: 'scarf', label: '围巾' },
    { value: 'other_clothing', label: '其他衣物' },
  ],
  accessories: [
    { value: 'watch', label: '手表' },
    { value: 'glasses', label: '眼镜' },
    { value: 'jewelry', label: '饰品' },
    { value: 'other_accessories', label: '其他饰品' },
  ],
  stationery: [
    { value: 'book', label: '书籍' },
    { value: 'stationery_box', label: '文具盒' },
    { value: 'other_stationery', label: '其他文具' },
  ],
  keys: [
    { value: 'keys', label: '钥匙' },
    { value: 'access_card', label: '门禁卡' },
    { value: 'other_keys', label: '其他钥匙/门禁' },
  ],
  other: [{ value: 'other', label: '其他' }],
}

export const PRIMARY_COLORS = [
  { value: 'black', label: '黑' },
  { value: 'white', label: '白' },
  { value: 'gray', label: '灰' },
  { value: 'red', label: '红' },
  { value: 'blue', label: '蓝' },
  { value: 'green', label: '绿' },
  { value: 'yellow', label: '黄' },
  { value: 'orange', label: '橙' },
  { value: 'pink', label: '粉' },
  { value: 'purple', label: '紫' },
  { value: 'brown', label: '棕' },
  { value: 'gold', label: '金' },
  { value: 'silver', label: '银' },
  { value: 'navy', label: '藏青' },
  { value: 'other', label: '其他' },
]

export const POST_TYPE_LABEL: Record<string, string> = {
  lost: '丢失',
  found: '捡到',
}

export const POST_STATUS_LABEL: Record<string, string> = {
  draft: '草稿',
  published: '已发布',
  claiming: '认领中',
  completed: '已完成',
  closed: '已关闭',
}

export const CLAIM_STATUS_LABEL: Record<string, string> = {
  pending: '待判定',
  approved: '已通过',
  rejected: '已拒绝',
  cancelled: '已撤回',
  completed: '已完成',
}
