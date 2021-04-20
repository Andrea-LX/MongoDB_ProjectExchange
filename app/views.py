from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
import random
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile, purchaseOrder, saleOrder
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse


def registration(request):
    if request.method == 'POST':
        form = request.POST
        if form:
            username = form['username']
            email = form['email']
            password = form['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            newUser = Profile(user=user)
            newUser.btcAmount = random.uniform(1, 10) #assegnazione bitcoin
            newUser.save()
            return redirect('/login/')
        else:
            print('uncorrect data')
    else:
        form = RegisterForm()
        return render(request, 'app/registration.html', {'form':form})


def log(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
    else:
        form = LoginForm()
        return render(request, 'app/login.html', {'form':form})

def homepage(request):
    if request.method == 'POST':
        values = request.POST
        thisUser = Profile.objects.get(user=request.user)
        if values:
            if "purchasePrice" in values:
                try:
                    price = values["purchasePrice"]
                    quantity = values['quantity']
                except:
                    return HttpResponse('Invalid data entered!')
                else:
                    userBalance = thisUser.btcBalance
                    if float(price) < userBalance:  # uncomment this line if you want to try the code without limit of btc balance
                    newPurchase = purchaseOrder(profile=thisUser, price=price, quantity=quantity)
                    newPurchase.save()

                    saleOrders = saleOrder.objects.filter(quantity=float(newPurchase.quantity),
                                                          active=True, price__lte=newPurchase.price)
                    if not saleOrders:
                        btc = thisUser.btcAmount
                        return render(request, 'app/homepage.html', {'btc': btc})

                    else:
                        saleOrders = saleOrders[0]
                        #buyer
                        purchaseOrder.objects.filter(_id=newPurchase._id).update(active=False)
                        saleOrder.objects.filter(_id=saleOrders._id).update(active=False)
                        oldPurBalance = thisUser.btcBalance
                        oldPurProfileProfit = thisUser.profit
                        thisUser.btcAmount += float(newPurchase.quantity)
                        thisUser.btcBalance -= float(saleOrders.price)

                        #buyer profit
                        buyerProfit = oldPurProfileProfit + (thisUser.btcBalance - oldPurBalance)
                        thisUser.profit = buyerProfit
                        thisUser.save()

                        #seller
                        saleProfile = saleOrders.profile
                        oldSaleBalance = saleProfile.btcBalance
                        oldSaleProfileProfit = saleProfile.profit
                        saleProfile.btcAmount -= float(saleOrders.quantity)
                        saleProfile.btcBalance += float(saleOrders.price)

                        #seller profit
                        saleProfit = oldSaleProfileProfit + (saleProfile.btcBalance - oldSaleBalance)
                        saleProfile.profit = saleProfit
                        saleProfile.save()

                        return HttpResponse('Registered order')



            else:
                try:
                    price = values["salePrice"]
                    quantity = values['quantity']
                except:
                    return HttpResponse('Invalid data entered!')
                else:
                    userBtc = thisUser.btcAmount
                    if float(quantity) < userBtc:
                        newSale = saleOrder(profile=thisUser, price=price, quantity=quantity)
                        newSale.save()

        btc = thisUser.btcAmount
        return render(request, 'app/homepage.html', {'btc': btc})
    else:
        thisUser = Profile.objects.get(user=request.user)
        btc = thisUser.btcAmount
        return render(request, 'app/homepage.html', {'btc': btc})


def activeOrders(request):
    response = []

    activePurOrders = purchaseOrder.objects.filter(active=True)
    for order in activePurOrders:
        response.append({
            'id': str(order._id),
            'tipology': 'purchase',
            'datetime': order.datetime,
            'price': order.price,
            'quantity': order.quantity
        })

    activeSaleOrders = saleOrder.objects.filter(active=True)
    for sale in activeSaleOrders:
        response.append({
            'id': str(sale._id),
            'tipology': 'sale',
            'datetime': sale.datetime,
            'price': sale.price,
            'quantity': sale.quantity
        })

    return JsonResponse(response, safe=False)


def profit(request):
    response = []
    userProfits = Profile.objects.all()

    for user in userProfits:
        response.append({
            'user': str(user._id),
            'balance': user.btcBalance,
            'btcAmount': user.btcAmount,
            'profit': f"{user.profit}"
        })

    return JsonResponse(response, safe=False)