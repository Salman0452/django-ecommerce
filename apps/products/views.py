from django.views.generic import DetailView, ListView, TemplateView

from .services import (
    get_active_categories,
    get_active_products,
    get_featured_products,
    get_product_by_slug,
)


class HomeView(TemplateView):
    template_name = 'products/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = get_featured_products()
        context['categories'] = get_active_categories()
        return context


class ProductListView(ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        page_number = self.request.GET.get('page', 1)
        category_slug = self.request.GET.get('category') or None
        self.products_page = get_active_products(
            page=page_number,
            per_page=self.paginate_by,
            category_slug=category_slug,
        )
        return self.products_page.object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = self.products_page
        context['is_paginated'] = self.products_page.paginator.num_pages > 1
        context['category_slug'] = self.request.GET.get('category', '')
        context['page_query'] = (
            f"&category={context['category_slug']}" if context['category_slug'] else ''
        )
        return context


class ProductDetailView(DetailView):
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_product_by_slug(self.kwargs['slug'])
