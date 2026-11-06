import calendar
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import Shop, UserProfile, Pandesal, Order, Reservation, Notification
from django.contrib.auth.models import User
from django.db.models import Sum
from .forms import ShopForm, SellerProductForm
from django.views.decorators.clickjacking import xframe_options_sameorigin


def _modal_saved_response(message):
    """Response rendered inside the iframe modal that notifies the parent page a save succeeded."""
    safe = message.replace("'", "\\'")
    return HttpResponse(
        "<!DOCTYPE html><html><body><script>"
        "window.parent.postMessage({type:'sellerProductSaved', message:'%s'}, '*');"
        "</script></body></html>" % safe
    )



@login_required
def seller_dashboard(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        messages.error(request, "You do not have access to the seller dashboard.")
        return redirect('home')
        
    shop = getattr(request.user, 'shop', None)
    
    # Calculate stats
    orders = Order.objects.filter(seller=request.user)
    new_orders_count = orders.filter(status__in=['pending', 'pending_confirmation']).count()
    preparing_count = orders.filter(status__in=['confirmed', 'ready_for_pickup']).count()
    completed_count = orders.filter(status='completed').count()
    
    total_sales = orders.filter(status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    recent_orders = orders.order_by('-created_at')[:5]
    low_stock_products = Pandesal.objects.filter(seller=request.user, stock__lt=10).order_by('stock')

    # ---- Month calendar with order / reservation markers ----
    today = timezone.localdate()
    try:
        cal_year = int(request.GET.get('year', today.year))
        cal_month = int(request.GET.get('month', today.month))
        date(cal_year, cal_month, 1)
    except (ValueError, TypeError):
        cal_year, cal_month = today.year, today.month

    # Orders grouped by the day they were placed
    order_counts = {}
    for o in Order.objects.filter(seller=request.user, created_at__year=cal_year, created_at__month=cal_month):
        day = timezone.localtime(o.created_at).date()
        order_counts[day] = order_counts.get(day, 0) + 1

    # Reservations grouped by their scheduled reservation_date
    reservation_counts = {}
    for r in Reservation.objects.filter(seller=request.user, reservation_date__year=cal_year, reservation_date__month=cal_month):
        reservation_counts[r.reservation_date] = reservation_counts.get(r.reservation_date, 0) + 1

    calendar_weeks = []
    for week in calendar.Calendar().monthdatescalendar(cal_year, cal_month):
        cells = []
        for day in week:
            cells.append({
                'num': day.day,
                'iso': day.isoformat(),
                'in_month': day.month == cal_month,
                'is_today': day == today,
                'orders': order_counts.get(day, 0),
                'reservations': reservation_counts.get(day, 0),
            })
        calendar_weeks.append(cells)

    prev_month, prev_year = (cal_month - 1, cal_year - 1) if cal_month == 1 else (cal_month - 1, cal_year)
    next_month, next_year = (cal_month + 1, cal_year + 1) if cal_month == 12 else (cal_month + 1, cal_year)

    context = {
        'shop': shop,
        'new_orders_count': new_orders_count,
        'preparing_count': preparing_count,
        'completed_count': completed_count,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'calendar_weeks': calendar_weeks,
        'cal_month_label': date(cal_year, cal_month, 1).strftime('%B %Y'),
        'cal_prev_year': prev_year, 'cal_prev_month': prev_month,
        'cal_next_year': next_year, 'cal_next_month': next_month,
        'today': today,
    }
    return render(request, 'pandesal/seller/dashboard.html', context)

@login_required
def seller_shop_settings(request):
    from django.contrib import messages
    from django.shortcuts import redirect
    messages.error(request, 'The Shop Settings feature has been disabled.')
    return redirect('seller_dashboard')

@login_required
def seller_products(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
    products = Pandesal.objects.filter(seller=request.user)
    return render(request, 'pandesal/seller/products.html', {'products': products})

@login_required
@xframe_options_sameorigin
def seller_product_create(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')

    modal = request.POST.get('modal') == '1' or request.GET.get('modal') == '1'

    if request.method == 'POST':
        form = SellerProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            if modal:
                return _modal_saved_response('Product created successfully!')
            messages.success(request, "Product created successfully!")
            return redirect('seller_products')
    else:
        form = SellerProductForm()
    template = 'pandesal/seller/product_form_modal.html' if modal else 'pandesal/seller/product_form.html'
    return render(request, template, {'form': form, 'is_edit': False, 'modal': modal})

@login_required
@xframe_options_sameorigin
def seller_product_edit(request, product_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    product = get_object_or_404(Pandesal, id=product_id, seller=request.user)
    modal = request.POST.get('modal') == '1' or request.GET.get('modal') == '1'

    if request.method == 'POST':
        form = SellerProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            if modal:
                return _modal_saved_response('Product updated successfully!')
            messages.success(request, "Product updated successfully!")
            return redirect('seller_products')
    else:
        # Initialize form with instance, but ensure categories map back to choices properly
        form = SellerProductForm(instance=product)
        # For MultipleChoiceField, initial data needs to be explicitly set
        if product.categories:
            form.initial['categories'] = product.categories
            
    template = 'pandesal/seller/product_form_modal.html' if modal else 'pandesal/seller/product_form.html'
    return render(request, template, {'form': form, 'product': product, 'is_edit': True, 'modal': modal})

@login_required
@xframe_options_sameorigin
def seller_product_delete(request, product_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    product = get_object_or_404(Pandesal, id=product_id, seller=request.user)
    modal = request.POST.get('modal') == '1' or request.GET.get('modal') == '1'

    if request.method == 'POST':
        product.delete()
        if modal:
            return _modal_saved_response('Product deleted successfully!')
        messages.success(request, "Product deleted successfully!")
        return redirect('seller_products')

    template = 'pandesal/seller/product_confirm_delete_modal.html' if modal else 'pandesal/seller/product_confirm_delete.html'
    return render(request, template, {'product': product, 'modal': modal})
@login_required
def seller_orders(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    orders = Order.objects.filter(seller=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    return render(request, 'pandesal/seller/orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES
    })

@login_required
def seller_order_detail(request, order_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    return render(request, 'pandesal/seller/order_detail.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES
    })

@login_required
def seller_order_status_update(request, order_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {order.get_status_display()}")
    return redirect('seller_order_detail', order_id=order.id)

@login_required
def seller_reservations(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    reservations = Reservation.objects.filter(seller=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        reservations = reservations.filter(status=status_filter)
        
    return render(request, 'pandesal/seller/reservations.html', {
        'reservations': reservations,
        'status_filter': status_filter,
        'status_choices': Reservation.STATUS_CHOICES
    })

@login_required
def seller_reservation_detail(request, reservation_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    reservation = get_object_or_404(Reservation, id=reservation_id, seller=request.user)
    return render(request, 'pandesal/seller/reservation_detail.html', {
        'reservation': reservation,
        'status_choices': Reservation.STATUS_CHOICES
    })

@login_required
def seller_reservation_status_update(request, reservation_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    reservation = get_object_or_404(Reservation, id=reservation_id, seller=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            reservation.status = new_status
            reservation.save()
            messages.success(request, f"Reservation status updated to {reservation.get_status_display()}")
    return redirect('seller_reservation_detail', reservation_id=reservation.id)

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_sellers(request):
    pending_sellers = UserProfile.objects.filter(user_type='seller', is_approved_seller=False).select_related('user', 'user__shop')
    approved_sellers = UserProfile.objects.filter(user_type='seller', is_approved_seller=True).select_related('user', 'user__shop')
    return render(request, 'pandesal/admin_sellers.html', {
        'pending_sellers': pending_sellers,
        'approved_sellers': approved_sellers
    })

@user_passes_test(is_admin)
def admin_seller_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        shop_name = request.POST.get('shop_name', '').strip()
        phone = request.POST.get('phone', '')
        barangay = request.POST.get('barangay', '')
        zone = request.POST.get('zone', '')

        if not username or not email or not password1 or not shop_name:
            messages.error(request, 'Username, email, password, and shop name are required.')
            return redirect('admin_sellers')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('admin_sellers')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admin_sellers')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('admin_sellers')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.user_type = 'seller'
        profile.is_approved_seller = True
        profile.phone = phone
        profile.barangay = barangay
        profile.zone = zone
        profile.save()

        Shop.objects.get_or_create(
            seller=user,
            defaults={'shop_name': shop_name, 'is_active': True}
        )

        messages.success(request, f'Seller account for "{shop_name}" created successfully!')
        return redirect('admin_sellers')

    return redirect('admin_sellers')

@user_passes_test(is_admin)
@xframe_options_sameorigin
def admin_seller_edit(request, user_id):
    seller_user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=seller_user)
    shop, _ = Shop.objects.get_or_create(seller=seller_user, defaults={'shop_name': f"{seller_user.username}'s Bakery"})

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        username = request.POST.get('username')
        email = request.POST.get('email')
        shop_name = request.POST.get('shop_name', '').strip()
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        barangay = request.POST.get('barangay', '')
        zone = request.POST.get('zone', '')
        password = request.POST.get('password1', '')

        if not username or not email or not shop_name:
            err = 'Username, email, and shop name are required.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err})
            messages.error(request, err)
            return redirect('admin_sellers')

        if User.objects.filter(username=username).exclude(id=seller_user.id).exists():
            err = 'Username already taken by another account.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err})
            messages.error(request, err)
            return redirect('admin_sellers')

        if User.objects.filter(email=email).exclude(id=seller_user.id).exists():
            err = 'Email already taken by another account.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err})
            messages.error(request, err)
            return redirect('admin_sellers')

        seller_user.username = username
        seller_user.email = email
        seller_user.first_name = first_name
        seller_user.last_name = last_name
        if password:
            seller_user.set_password(password)
        seller_user.save()

        profile.phone = phone
        profile.barangay = barangay
        profile.zone = zone
        profile.save()

        shop.shop_name = shop_name
        shop.save()

        msg = f'Seller "{shop_name}" updated successfully!'
        if is_ajax:
            return JsonResponse({'success': True, 'message': msg})

        messages.success(request, msg)
        return redirect('admin_sellers')

    return render(request, 'pandesal/admin_seller_edit.html', {
        'seller_user': seller_user,
        'profile': profile,
        'shop': shop
    })

@user_passes_test(is_admin)
def admin_seller_toggle(request, user_id):
    if request.method == 'POST':
        seller_user = get_object_or_404(User, id=user_id)
        seller_user.is_active = not seller_user.is_active
        seller_user.save()
        status_text = "activated" if seller_user.is_active else "deactivated"
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
        if is_ajax:
            return JsonResponse({'success': True, 'message': f'Seller account {status_text} successfully'})
        messages.success(request, f'Seller "{seller_user.username}" has been {status_text}.')
    return redirect('admin_sellers')

@user_passes_test(is_admin)
def admin_seller_delete(request, user_id):
    if request.method == 'POST':
        seller_user = get_object_or_404(User, id=user_id)
        shop_name = getattr(seller_user, 'shop', None)
        name = shop_name.shop_name if shop_name else seller_user.username
        seller_user.delete()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
        if is_ajax:
            return JsonResponse({'success': True, 'message': f'Seller account "{name}" deleted successfully'})
        messages.success(request, f'Seller account "{name}" deleted successfully.')
    return redirect('admin_sellers')

@user_passes_test(is_admin)
def admin_seller_approve(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    profile.is_approved_seller = True
    profile.save()
    messages.success(request, f"Seller {profile.user.username} has been approved.")
    return redirect('admin_sellers')

@user_passes_test(is_admin)
def admin_seller_reject(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    profile.user_type = 'customer'
    profile.save()
    # Delete the shop application
    if hasattr(profile.user, 'shop'):
        profile.user.shop.delete()
    messages.success(request, f"Seller application for {profile.user.username} has been rejected.")
    return redirect('admin_sellers')
