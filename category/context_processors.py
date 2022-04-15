from .models import Category

def menu_links(request):
    """
        context processor to populate category links
    """
    links = Category.objects.all()
    return dict(links=links)