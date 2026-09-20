from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.posts.models import Post, PostAttribute, PostImage

from .embed import sync_and_schedule


def _maybe_sync_post(post: Post | None) -> None:
    if post is None:
        return
    sync_and_schedule(post)


@receiver(post_save, sender=Post)
def on_post_save(sender, instance: Post, **kwargs) -> None:
    _maybe_sync_post(instance)


@receiver(post_save, sender=PostImage)
def on_post_image_save(sender, instance: PostImage, **kwargs) -> None:
    _maybe_sync_post(instance.post)


@receiver(post_delete, sender=PostImage)
def on_post_image_delete(sender, instance: PostImage, **kwargs) -> None:
    post = getattr(instance, "post", None)
    if post is None:
        return
    try:
        post.refresh_from_db()
    except Post.DoesNotExist:
        return
    _maybe_sync_post(post)


@receiver(post_save, sender=PostAttribute)
def on_post_attribute_save(sender, instance: PostAttribute, **kwargs) -> None:
    _maybe_sync_post(instance.post)
