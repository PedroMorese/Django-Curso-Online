from django.shortcuts import render


def membership(request):
    """Render the membership page which extends base.html."""
    return render(request, 'membership-client.html')
