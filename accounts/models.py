from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Hồ sơ mở rộng cho người dùng."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Người dùng',
    )
    phone = models.CharField('Số điện thoại', max_length=20, blank=True)
    bio = models.CharField('Giới thiệu', max_length=255, blank=True)
    avatar = models.ImageField(
        'Ảnh đại diện', upload_to='avatars/', blank=True, null=True
    )

    class Meta:
        verbose_name = 'Hồ sơ'
        verbose_name_plural = 'Hồ sơ'

    def __str__(self):
        return f'Hồ sơ của {self.user.username}'


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """Tự động tạo hồ sơ khi tạo người dùng mới."""
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
