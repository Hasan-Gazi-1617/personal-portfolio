from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import NewsletterSubscriber, SiteEvent


@require_POST
def subscribe(request):
    email = request.POST.get('email','').strip().lower()
    consent = request.POST.get('consent') == 'yes'
    if not consent:
        messages.error(request, 'Please confirm consent before subscribing.')
    elif not email or len(email) > 254 or '@' not in email:
        messages.error(request, 'Please enter a valid email address.')
    else:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=['is_active'])
        messages.success(request, 'You are subscribed. Thank you!')
    return redirect(request.META.get('HTTP_REFERER','/'))


@require_POST
def unsubscribe(request, token):
    subscriber = get_object_or_404(NewsletterSubscriber, unsubscribe_token=token)
    subscriber.is_active = False
    subscriber.save(update_fields=['is_active'])
    return HttpResponse('You have been unsubscribed from portfolio updates.')


@require_POST
def track_event(request):
    event = request.POST.get('event','')
    if event not in {'cv_download','project_click'}:
        return JsonResponse({'ok':False}, status=400)
    SiteEvent.objects.create(event=event, path=request.POST.get('path','')[:300])
    return JsonResponse({'ok':True})
