from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404

from .models import Category, Product


def get_active_products(page=1, per_page=12, category_slug=None):
    """Return a paginated collection of active, non-deleted products."""
    queryset = Product.objects.filter(
        is_active=True,
        is_deleted=False,
    ).select_related('category')

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    paginator = Paginator(queryset, per_page)

    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def get_product_by_slug(slug):
    """Return a single active product by slug or raise Http404."""
    try:
        return Product.objects.select_related('category').get(
            slug=slug,
            is_active=True,
            is_deleted=False,
        )
    except Product.DoesNotExist as exc:
        raise Http404('Product not found.') from exc


def get_featured_products():
    """Return the 4 most recently added active products."""
    return Product.objects.filter(
        is_active=True,
        is_deleted=False,
    ).select_related('category').order_by('-created_at')[:4]


def get_active_categories():
    """Return all active, non-deleted categories for storefront browsing."""
    return Category.objects.filter(
        is_active=True,
        is_deleted=False,
    ).order_by('name')
