'''认领模块的稳定枚举值，与 docs/认领接口契约.md 保持一致。'''

CLAIM_STATUS_CHOICES = [
    ('pending', '待判定'),
    ('approved', '已通过'),
    ('rejected', '已拒绝'),
    ('cancelled', '已撤回'),
    ('completed', '已完成'),
]

CLAIM_STATUS_TERMINAL = {'rejected', 'cancelled', 'completed'}

CLAIM_STATUS_ACTIVE = {'pending', 'approved'}
