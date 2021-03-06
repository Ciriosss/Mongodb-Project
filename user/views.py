from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, NewBuyOrder, NewSellOrder
from app.models import Profile, BuyOrder, SellOrder
from django.contrib.auth.models import User
from .functions import newProfile, matchbuyOrder, matchsellOrder
from .request import price




#view for registration
def register(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,'Congratulations {}! your account has been created successfully, now you are able to log-in'.format(username))
            newProfile(username)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})

#view for profile page
def profile(request):
    user = User.objects.get(username = request.user)
    profile = Profile.objects.get(user = user)
    balance = round(profile.balance,2)
    BTC = round(profile.BTC,2)
    pending_balance = abs(round(profile.pending_balance, 2))
    pending_BTC = abs(round(profile.pending_BTC, 2))
    buyorders = BuyOrder.objects.filter(profile=profile).order_by('-datetime')
    sellorders = SellOrder.objects.filter(profile=profile).order_by('-datetime')
    return render(request, 'user/profile.html', {'balance' : balance, 'BTC' : BTC,'buyorders': buyorders, 'sellorders': sellorders,'pending_balance':pending_balance, 'pending_BTC':pending_BTC})


#view for trade page
def trade(request):
    user = User.objects.get(username=request.user)
    profile = Profile.objects.get(user=user)
    balance = round(profile.balance,2)
    pending_balance = round(profile.pending_balance,2)
    pending_BTC = round(profile.pending_BTC, 2)
    BTC = round(profile.BTC,2)
    actual_btc = (round(price() * 0.84 ,2))
    if request.method == 'POST':
        if ('buy' in request.POST):
            form = NewBuyOrder(request.POST)
        else:
            form = NewSellOrder(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.profile = profile
            order.remaining = order.quantity

            if ('buy' in request.POST):
                if form.checkBalance(request):
                    order.save()
                    messages.success(request, 'Your  buy order has been resistred')
                    profile.pending_balance += order.price * order.quantity
                    profile.balance -= order.price * order.quantity
                    profile.save()
                    matchbuyOrder(order, request)
                    return redirect('profile')
                else:
                    messages.warning(request, 'Error, you dont have enough funds ')
                    return redirect('trade')

            elif ('sell' in request.POST):
                if form.checkBTC(request):
                    order.save()
                    messages.success(request, 'Your  Sell order has been resistred')
                    profile.pending_BTC += order.quantity
                    profile.BTC -= order.quantity
                    profile.save()
                    matchsellOrder(order, request)
                    return redirect('profile')
                else:
                    messages.warning(request, 'Error, you dont have enough bitcoins ')
                    return redirect('trade')

    else:
        form = NewBuyOrder()
    return render(request, 'user/trade.html', {'form': form, 'balance': balance, 'BTC': BTC, 'pending_balance':pending_balance, 'pending_BTC':pending_BTC, 'actual_btc': actual_btc})