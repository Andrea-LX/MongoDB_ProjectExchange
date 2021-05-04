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
            newUser.btcAmount = random.uniform(1, 10)  #bitcoin assignment
            newUser.save()
            return redirect('/login/')
        else:
            print('uncorrect data')
    else:
        form = RegisterForm()
        return render(request, 'app/registration.html', {'form': form})


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
    if request.user.is_anonymous:
        return redirect('/login/')
    else:
        if request.method == 'POST':
            values = request.POST
            thisUser = Profile.objects.get(user=request.user)
            if values:
                # purchase order
                if "purchasePrice" in values:
                    try:
                        price = values["purchasePrice"]
                        quantity = values['quantity']
                    except:
                        return HttpResponse('Invalid data entered!')
                    else:
                        userBalance = thisUser.btcBalance
                        if not float(price) <= userBalance:  # uncomment this line if you want to try the code without limit of btc balance
                            return HttpResponse('Invalid data entered! The price is higher than your balance ')
                        else:
                            newPurchase = purchaseOrder(profile=thisUser, price=price, quantity=quantity)
                            newPurchase.save()

                            saleOrders = saleOrder.objects.filter(quantity__lte=float(newPurchase.quantity),
                                                                      active=True, price__lte=newPurchase.price)
                            if not saleOrders:
                                btc = thisUser.btcAmount
                                return render(request, 'app/homepage.html', {'btc': btc})

                            else:
                                for element in saleOrders:
                                    # same quantity order
                                    if int(element.quantity) == int(newPurchase.quantity):
                                        saleOrders = element
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
                                        saleProfile.saleAmount -= float(saleOrders.quantity)

                                        #seller profit
                                        saleProfit = oldSaleProfileProfit + (saleProfile.btcBalance - oldSaleBalance)
                                        saleProfile.profit = saleProfit
                                        saleProfile.save()

                                        return HttpResponse('Registered order')

                                    else:
                                        #different quantity
                                        bestOrder = []
                                        for element in saleOrders:
                                            if (int(element.price) / int(element.quantity)) <= (int(newPurchase.price) / int(newPurchase.quantity)):
                                                bestOrder.append(element)
                                            else:
                                                continue

                                        if bestOrder:
                                            saleOrders = bestOrder[0]
                                            # buyer
                                            purchaseOrder.objects.filter(_id=newPurchase._id).update(active=False)
                                            saleOrder.objects.filter(_id=saleOrders._id).update(active=False)
                                            oldPurBalance = thisUser.btcBalance
                                            oldPurProfileProfit = thisUser.profit
                                            thisUser.btcAmount += float(saleOrders.quantity)
                                            thisUser.btcBalance -= float(saleOrders.price)

                                            # buyer profit
                                            buyerProfit = oldPurProfileProfit + (thisUser.btcBalance - oldPurBalance)
                                            thisUser.profit = buyerProfit
                                            thisUser.save()

                                            # seller
                                            saleProfile = saleOrders.profile
                                            oldSaleBalance = saleProfile.btcBalance
                                            oldSaleProfileProfit = saleProfile.profit
                                            saleProfile.btcAmount -= float(saleOrders.quantity)
                                            saleProfile.btcBalance += float(saleOrders.price)
                                            saleProfile.saleAmount -= float(saleOrders.quantity)

                                            # seller profit
                                            saleProfit = oldSaleProfileProfit + (saleProfile.btcBalance - oldSaleBalance)
                                            saleProfile.profit = saleProfit
                                            saleProfile.save()

                                            bestOrder.remove(bestOrder[0])
                                            newPrice = float(newPurchase.price) - saleOrders.price
                                            newQuantity = float(newPurchase.quantity) - saleOrders.quantity

                                            # matching other orders
                                            otherOrders = []
                                            i = 0
                                            while i < int(newPurchase.quantity):
                                                for element in bestOrder:
                                                    if element.price <= newPrice and element.quantity <= newQuantity:
                                                        otherOrders.append(element)
                                                    else:
                                                        continue

                                                otherOrders = saleOrder.objects.filter(active=True)
                                                if otherOrders:
                                                    saleOrders = otherOrders[0]
                                                    # buyer
                                                    saleOrder.objects.filter(_id=saleOrders._id).update(active=False)
                                                    oldPurBalance = thisUser.btcBalance
                                                    oldPurProfileProfit = thisUser.profit
                                                    thisUser.btcAmount += float(saleOrders.quantity)
                                                    thisUser.btcBalance -= float(saleOrders.price)

                                                    # buyer profit
                                                    buyerProfit = oldPurProfileProfit + (
                                                                        thisUser.btcBalance - oldPurBalance)
                                                    thisUser.profit = buyerProfit
                                                    thisUser.save()

                                                    # seller
                                                    saleProfile = saleOrders.profile
                                                    oldSaleBalance = saleProfile.btcBalance
                                                    oldSaleProfileProfit = saleProfile.profit
                                                    saleProfile.btcAmount -= float(saleOrders.quantity)
                                                    saleProfile.btcBalance += float(saleOrders.price)
                                                    saleProfile.saleAmount -= float(saleOrders.quantity)

                                                    # seller profit
                                                    saleProfit = oldSaleProfileProfit + (
                                                                        saleProfile.btcBalance - oldSaleBalance)
                                                    saleProfile.profit = saleProfit
                                                    saleProfile.save()
                                                    otherOrders = []
                                                    newPrice = newPrice - saleOrders.price
                                                    newQuantity = newQuantity - saleOrders.quantity
                                                    i += 1

                                                else:
                                                    #create a new order with remainder
                                                    if newPrice is not 0 and newQuantity is not 0:
                                                        remainderPurchase = purchaseOrder(profile=thisUser,
                                                                                              price=newPrice,
                                                                                              quantity=newQuantity)
                                                        remainderPurchase.save()
                                                        return HttpResponse('Registered partial order and created a new purchase order')

                                                    else:
                                                        return HttpResponse('Registered matching order')


                                            btc = thisUser.btcAmount
                                            return render(request, 'app/homepage.html', {'btc': btc})
                                        else:
                                            btc = thisUser.btcAmount
                                            return render(request, 'app/homepage.html', {'btc': btc})

                                btc = thisUser.btcAmount
                                return render(request, 'app/homepage.html', {'btc': btc})

                else:
                    # sale order
                    try:
                        price = values["salePrice"]
                        quantity = values['quantity']
                    except:
                        return HttpResponse('Invalid data entered!')
                    else:
                        saleAmount = thisUser.saleAmount
                        userBtc = thisUser.btcAmount - saleAmount

                        if float(quantity) < userBtc:
                            newSale = saleOrder(profile=thisUser, price=price, quantity=quantity)
                            newSale.save()
                            thisUser.saleAmount += float(quantity)
                            thisUser.save()
                            print(userBtc)
                            btc = thisUser.btcAmount
                            return render(request, 'app/homepage.html', {'btc': btc})
                        else:
                            return HttpResponse('you have exceeded your bitcoin sales limit')

            else:
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