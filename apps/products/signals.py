"""
Signals para la app Products.

post_delete → elimina la imagen de Cloudinary cuando se borra un producto.
pre_save    → elimina la imagen anterior cuando se actualiza con una nueva.
"""
import logging
import re

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _extract_public_id(cloudinary_url: str) -> str | None:
    """
    Extrae el public_id de una URL de Cloudinary.

    Ejemplo de URL:
      https://res.cloudinary.com/<cloud>/image/upload/v123456789/products/abc.jpg
    public_id resultante:
      products/abc
    """
    if not cloudinary_url:
        return None
    # Captura todo lo que viene después de /upload/v<version>/ (o /upload/) sin la extensión
    match = re.search(r'/upload/(?:v\d+/)?(.+?)(?:\.[^.]+)?$', cloudinary_url)
    if match:
        return match.group(1)
    return None


def _destroy_cloudinary_image(public_id: str) -> None:
    """Elimina un recurso de Cloudinary dado su public_id."""
    if not public_id:
        return
    try:
        import cloudinary.uploader
        result = cloudinary.uploader.destroy(public_id)
        if result.get('result') == 'ok':
            logger.info("Imagen eliminada de Cloudinary: %s", public_id)
        else:
            logger.warning("Cloudinary no pudo eliminar '%s': %s", public_id, result)
    except Exception as exc:
        logger.error("Error al eliminar imagen de Cloudinary '%s': %s", public_id, exc)


@receiver(post_delete, sender='products.Product')
def delete_product_image_on_delete(sender, instance, **kwargs):
    """Al eliminar un producto, borra su imagen de Cloudinary (si tiene una)."""
    public_id = _extract_public_id(instance.image_url)
    if public_id:
        _destroy_cloudinary_image(public_id)


@receiver(pre_save, sender='products.Product')
def delete_old_image_on_update(sender, instance, **kwargs):
    """Al actualizar un producto con nueva imagen, borra la imagen anterior de Cloudinary."""
    if not instance.pk:
        return  # Es una creación nueva

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_url = old_instance.image_url
    new_url = instance.image_url

    if old_url and old_url != new_url:
        public_id = _extract_public_id(old_url)
        if public_id:
            _destroy_cloudinary_image(public_id)
