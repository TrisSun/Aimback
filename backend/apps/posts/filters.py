"""帖子硬过滤公共函数。

E 的向量检索接口在召回前调用 apply_post_hard_filters，向量与关键词召回只
发生在硬过滤之后的候选集上，不能在全库上跑。本文件由 A 维护，E 只调用。
"""

from django.db.models import Q, QuerySet

from .constants import POST_STATUS_SEARCHABLE


def apply_post_hard_filters(
    queryset: QuerySet,
    *,
    type: str | None = None,
    category_l1: str | None = None,
    category_l2: str | None = None,
    region_code: str | None = None,
    place_id: int | None = None,
    event_start: str | None = None,
    event_end: str | None = None,
) -> QuerySet:
    """先缩小候选集，再做向量/关键词召回。

    硬过滤顺序与 docs/接口契约.md 第 3.3 节保持一致：
    类型 -> 状态 -> 一级分类 -> 时间窗 -> 地理。
    颜色、品牌、二级分类、场所是否相同只用于排序加分，不在这里剔除。
    """
    qs = queryset.filter(status__in=POST_STATUS_SEARCHABLE)

    if type in ("lost", "found"):
        qs = qs.filter(type=type)

    # category_l1 为 any/空时不卡；为 other 时任一方的兜底分类不卡死。
    if category_l1 and category_l1 != "any" and category_l1 != "other":
        qs = qs.filter(category_l1=category_l1)

    if category_l2:
        qs = qs.filter(category_l2=category_l2)

    if region_code:
        qs = qs.filter(found_region__code=region_code)

    if place_id:
        qs = qs.filter(found_place_id=place_id)

    # 时间窗取交集：帖子事件区间与查询窗口有重叠。
    if event_start:
        qs = qs.filter(event_end_at__gte=event_start)
    if event_end:
        qs = qs.filter(event_start_at__lte=event_end)

    return qs


def apply_post_search_query(queryset: QuerySet, q: str | None) -> QuerySet:
    """关键词召回，不属于硬过滤，由列表视图在硬过滤之后调用。

    匹配范围与 docs/接口契约.md 第 3.3 节一致：title、description，以及
    attribute 的 brand / primary_color / text_mark / distinctive_features /
    normalized_description 五个字段，v0 使用不区分大小写的子串匹配。
    """
    q = (q or "").strip()
    if not q:
        return queryset

    lookups = [
        "title__icontains",
        "description__icontains",
        "attribute__brand__icontains",
        "attribute__primary_color__icontains",
        "attribute__text_mark__icontains",
        "attribute__distinctive_features__icontains",
        "attribute__normalized_description__icontains",
    ]
    condition = Q()
    for lookup in lookups:
        condition |= Q(**{lookup: q})
    return queryset.filter(condition).distinct()
