from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse
from django.core import serializers
from django.contrib import messages
import mysql.connector
from django.db import connection
from django.db.models import Q, Sum
from .utils import render_to_pdf
import json
from num2words import num2words
from django.views.generic import DeleteView, UpdateView
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import (
    Category, Project, ChartOfAccount, Inventory, VoucherHeader, Transactions, VoucherDetail,
    CompanyInfo, PurchaseHeader, PurchaseDetail, PaymentVoucher
)
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db import transaction

conn = mysql.connector.connect(user='admin', host='localhost', port='3306', password='Gre@ter834', database="Indus")


def flush_transaction():
    transaction.commit()


@login_required
def home(request):
    projects = Project.objects.filter(~Q(projectName = 'General')).all()
    clients = ChartOfAccount.objects.filter(~Q(parent_id=11) & ~Q(parent_id=26))
    banks = ChartOfAccount.objects.filter(Q(parent_id=26)).all()
    return render(request,'construction/home.html',{'title':'Home', 'projects':projects, 'clients':clients, 'banks':banks})

# @login_required(login_url='Login')
# def addInventory(request):
    # itemCategory = Category.objects.all()
#     projectId = Project.objects.all()
#     return render(request,'construction/add-inventory.html',{'title':'Add Inventory','category':itemCategory,'projectId':projectId})

@login_required
def addCategory(request):
    # categories = Category.objects.all()
    # categoriesForTable = serializers.serialize('json',categories)
    if request.method == "POST":
        edit_category = request.POST.get('add-and-edit-category')
        if edit_category == 'add-category':
            categoryGetFromForm = request.POST.get('sub_category_code')
            print(categoryGetFromForm, request.user)
            c = Category(categoryName = categoryGetFromForm, userId= request.user)
            c.save()
        else:
            CategoryId = request.POST.get('categoryIdUpdate')
            CategoryName = request.POST.get('categoryNameUpdate')
            c = Category.objects.get(categoryId = CategoryId)
            c.categoryName = CategoryName
            c.save()
            print(c.categoryName)
        # return JsonResponse({'category':categoriesForTable})
    categories = Category.objects.all()



    return render(request, 'construction/add-category.html',{'title':'Categories', 'category':categories})


# @login_required
# def addProject(request):
#     chartofaccount = ChartOfAccount.objects.all()
#     users = User.objects.all()
#     itemCategory = Category.objects.all()
#     if request.method == "POST":
#         projName = request.POST.get("projectName")
#         Amount = request.POST.get("amount")
#         description = request.POST.get("narration")
#         payment_method = request.POST.get("payMethod")
#         Client = request.POST.get("client")
#         # ItemCategory = request.POST.get("item-category")
#         # ItemName = request.POST.get("item-Name")
#         # ItemQuantity = request.POST.get("item-Quantity")
#         # UnitPrice = request.POST.get("unit-Price")

#         proj = Project(projectName=projName,  userId=request.user, amount=Amount, narration=description, payMethod=payment_method, accountId=ChartOfAccount.objects.get(accountId=Client))
#         proj.save()

#         proj = Project.objects.last()
#         print(proj)
#         # itemName = request.POST.get("ItemName")
#         # itemCategory = request.POST.get("ItemCategory")
#         # itemQuantity = request.POST.get("ItemQuantity")
#         # unitPrice = request.POST.get("UnitPrice")
#         # unit = request.POST.get("Unit")

#         items = json.loads(request.POST.get('items'))

#         print(items, "\n", projName, Amount, description, payment_method, Client)
#         for item in items:
#             print(item)
#             itemName = item['ItemName']
#             itemCategory = Category.objects.get(categoryId =item['ItemCategoryVal'])
#             itemQuantity = item['ItemQuantity']
#             unitPrice = item['UnitPrice']
#             unit = item['Unit']
#             item_add = Inventory(itemName = itemName, itemCategory=itemCategory, itemQuantity= itemQuantity, unitPrice=unitPrice,unit=unit, projectId = proj, userId=request.user)
#             item_add.save()

#         return JsonResponse({'success':'success'})



#         # print(projName, Amount, description, payment_method, CLient)
#     return render(request, 'construction/add-project.html',{'title':'Add Project','users':users,'category':itemCategory,'accounts':chartofaccount})

# class InventoryDelete(LoginRequiredMixin, DeleteView):
#     model = Inventory
#     template_name = 'construction/inventory.html'
#     success_url = '/'

# def InventoryDelete(request):
#     if method.POST == "POST":
#         id = request.POST.get('itemId')
#         Inventory.objects.filter(id=id).delete()
#         print('deleted')

@login_required
def inventory(request):
    if request.method == "POST":
        inventory_edit_or_delete = request.POST.get("inventory-edit-or-delete")
        if inventory_edit_or_delete == 'add-inventory':
            itemName = request.POST.get('ItemName')
            itemQuantity = request.POST.get('ItemQuantity')
            itemCategory = request.POST.get('ItemCategory')
            unitPrice = request.POST.get('UnitPrice')
            unit = request.POST.get('Unit')
            project = request.POST.get('Project')
            categoryVal = Category.objects.get(categoryId = itemCategory)
            projectVal = Project.objects.get(projectId = project)
            try:
                item_add = Inventory(itemName = itemName, itemCategory=categoryVal, itemQuantity= itemQuantity, unitPrice=unitPrice,unit=unit, projectId = projectVal, userId = request.user)
                item_add.save()
            except Exception as e:
                messages.warning(request, 'Please, Provide integer value not string!')
        else:
            itemName = request.POST.get('ItemNameUpdate')
            itemId = request.POST.get('inventoryIdUpdate')
            itemQuantity = request.POST.get('ItemQuantityUpdate')
            project = request.POST.get('project-id')
            unitPrice = request.POST.get('UnitPriceUpdate')
            unit = request.POST.get('UnitUpdate')
            itemCat = request.POST.get('item-id')
            itemCat = Category.objects.get(categoryName= itemCat)
            project = Project.objects.get(projectName = project)
            print(project,itemCat)

            try:
                item_edit = Inventory.objects.get(itemId = itemId)
                item_edit.itemCategory = itemCat
                item_edit.projectId = project
                item_edit.itemName = itemName
                item_edit.itemQuantity = itemQuantity
                item_edit.unitPrice = unitPrice
                item_edit.unit = unit
                item_edit.save()
            except Exception as e:
                messages.warning(request, 'something went wrong')
    inventory = Inventory.objects.all()
    category = Category.objects.all()
    projects = Project.objects.all()



    return render(request, 'construction/inventory.html',{'title':'Inventory','inventories':inventory[::-1],'category':category,'projects':projects})

@login_required
def chart_of_account(request):
    supplier = Q(account_id = '100')
    customer = Q(account_id = '200')
    bank = Q(account_id = '300')
    main = ChartOfAccount.objects.all()
    sub_accounts = ChartOfAccount.objects.all()
    all_accounts = ChartOfAccount.objects.all()
    accounts = ChartOfAccount.objects.filter(~Q(parent_id=11)).all()
    if request.method == 'POST':
        account_title = request.POST.get('account_title')
        account_type = request.POST.get('account_type')
        opening_balance = request.POST.get('opening_balance')
        phone_no = request.POST.get('phone_no')
        email_address = request.POST.get('email_address')
        ntn = request.POST.get('ntn')
        stn = request.POST.get('stn')
        cnic = request.POST.get('cnic')
        address = request.POST.get('address')
        remarks = request.POST.get('remarks')
        op_type = request.POST.get('optradio')
        credit_limits = request.POST.get('credit_limits')

        if credit_limits is "":
            credit_limits = 0.00
        else:
            credit_limits = credit_limits

        if opening_balance is "":
            opening_balance = 0
        if op_type == "credit":
            opening_balance = -abs(Decimal(opening_balance))
        coa = ChartOfAccount(account_title = account_title, parent_id = account_type, opening_balance = opening_balance, phone_no = phone_no, email_address = email_address, ntn = ntn, stn = stn, cnic = cnic ,Address = address, remarks = remarks, credit_limit=credit_limits, account_id = "100", user_id=request.user)
        coa.save()
    return render(request, 'construction/chart_of_account.html',{'title':'Add Customer','all_accounts':all_accounts, 'accounts':accounts})


@login_required
def edit_chart_of_account(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        account_title = request.POST.get('account_title')
        account_type = request.POST.get('account_type')
        opening_balance = request.POST.get('opening_balance')
        phone_no = request.POST.get('phone_no')
        email_address = request.POST.get('email_address')
        ntn = request.POST.get('ntn')
        stn = request.POST.get('stn')
        cnic = request.POST.get('cnic')
        address = request.POST.get('address')
        remarks = request.POST.get('remarks')
        op_type = request.POST.get('optradio')
        credit_limits = request.POST.get('credit_limits')

        if credit_limits is "":
            credit_limits = 0.00
        else:
            credit_limits = credit_limits

        if opening_balance is "":
            opening_balance = 0
        if op_type == "credit":
            opening_balance = -abs(Decimal(opening_balance))
        coa = ChartOfAccount.objects.filter(id = id).first()
        coa.account_title = account_title
        coa.parent_id = account_type
        coa.opening_balance = opening_balance
        coa.phone_no = phone_no
        coa.email_address = email_address
        coa.ntn = ntn
        coa.stn = stn
        coa.cnic = cnic
        coa.Address = address
        coa.remarks = remarks
        coa.credit_limit = credit_limits
        coa.save()
    return redirect('chart-of-account')


def account_transaction_avaliable(pk):
    return True
    # cusror = connection.cursor()
    # row = cusror.execute('''select case
    #                         when exists (select id from supplier_rfqsupplierheader  where account_id_id = %s)
    #                         or exists (select id from supplier_quotationheadersupplier  where account_id_id = %s)
    #                         or exists (select id from supplier_poheadersupplier  where account_id_id = %s)
    #                         or exists (select id from supplier_dcheadersupplier  where account_id_id = %s)
    #                         or exists (select id from customer_rfqcustomerheader  where account_id_id = %s)
    #                         or exists (select id from customer_quotationheadercustomer  where account_id_id = %s)
    #                         or exists (select id from customer_poheadercustomer  where account_id_id = %s)
    #                         or exists (select id from customer_dcheadercustomer  where account_id_id = %s)
    #                         or exists (select id from transaction_purchaseheader  where account_id_id = %s)
    #                         or exists (select id from transaction_purchasereturnheader  where account_id_id = %s)
    #                         or exists (select id from transaction_saleheader  where account_id_id = %s)
    #                         or exists (select id from transaction_salereturnheader  where account_id_id = %s)
    #                         or exists (select id from transaction_transactions  where account_id_id = %s)
    #                         or exists (select id from transaction_voucherdetail  where account_id_id = %s)
    #                         then 'y'
    #                         else 'n'
    #                         end
    #                         ''',[pk,pk,pk,pk,pk,pk,pk,pk,pk,pk,pk,pk,pk,pk])
    # row = row.fetchall()
    # res_list = [x[0] for x in row]
    # if res_list[0] == "n":
    #     ChartOfAccount.objects.filter(id = pk).delete()
    #     return True
    # else:
    #     return False

@login_required
def delete_chart_of_account(request,pk):
    account = account_transaction_avaliable(pk)
    if account == True or Project.objects.filter(accountId=pk) or PurchaseHeader.objects.filter(accountId=pk) or VoucherHeader.objects.filter(accountId=pk) or Transactions.objects.filter(accountId=pk):
        messages.warning(request, "You cannot delete this Account, it is refrenced")
        return redirect('chart-of-account')
    else:
        ChartOfAccount.objects.filter(id = pk).all().delete()
        return redirect('chart-of-account')

    return redirect('chart-of-account')

def view_purchase_voucher(request, pk):
    jv_header = PurchaseHeader.objects.filter(purchaseHeaderId = pk).first()
    jv_detail = PurchaseDetail.objects.filter(purchaseHeaderId = jv_header).all()
    print(jv_header, jv_detail)
    return render(request, 'construction/view-purchase-voucher.html', {'title':f'View JV{pk}','jv_header':jv_header,'jv_detail':jv_detail})

@login_required
def project(request):
    project = Project.objects.filter(~Q(projectName = 'General')).all()
    chartofaccount = ChartOfAccount.objects.filter(Q(parent_id=12)).all()
    all_bank_accounts = ChartOfAccount.objects.filter(account_id = 100).all()
    cof = ChartOfAccount.objects.all()

    get_last_tran_id = Project.objects.filter(Q(projectCode__contains = 'PR')).last()
    #cursor = conn.cursor()
    #get_last_tran_id = cursor.execute('''select * from construction_project where projectCode LIKE "%PR%" order by projectCode DESC LIMIT 1 ''')
    #get_last_tran_id = cursor.fetchall()
    print(get_last_tran_id)
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id.projectCode
        get_last_tran_id = get_last_tran_id
        get_last_tran_id = get_last_tran_id[6:]
        print(get_last_tran_id)
        get_last_tran_id = int(get_last_tran_id)
        get_last_tran_id = get_last_tran_id+1
        get_last_tran_id = str(get_last_tran_id)
        get_last_tran_id = date[2:] + 'PR' + get_last_tran_id
    else:
        get_last_tran_id = date[2:]+'PR1'
    if request.method == "POST":
        project_edit_or_delete = request.POST.get('project-edit-or-delete')
        if project_edit_or_delete == "new-project":
            ProjectName = request.POST.get('projectName')
            AccountId = request.POST.get('customer')
            amount = request.POST.get('amount')
            PaymentMethod = 'Cash'
            Description = request.POST.get('description')
            status = request.POST.get('status')
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')
            print(endDate, startDate, status)
            project_add = Project(projectName=ProjectName,projectStatus=status, startDate=startDate, endDate=endDate, projectCode=get_last_tran_id, accountId=ChartOfAccount(id=AccountId), payMethod=PaymentMethod, narration=Description, amount=float(amount), userId=request.user)
            project_add.save()
            return redirect('Project')
        elif request.POST.get('projectCheck'):
            main_object_id = request,POST.get('main_object_id')
            print(main_object_id)
            sub_menu = Project.objects.filter(accountId=main_object_id).all()
            sub_menu = serializers.serialize('json',sub_menu)
            return JsonResponse({'sub_menu':sub_menu})

        else:
            ProjectId = request.POST.get('projectIdUpdate')
            customerUpdate = request.POST.get('customer-id')
            ProjectName = request.POST.get('projectNameUpdate')
            Description = request.POST.get('descriptionUpdate')
            startDate = request.POST.get('startDate-update')
            endDate = request.POST.get('endDate-update')
            status = request.POST.get('status-update')
            print(customerUpdate)
            account_id = ChartOfAccount.objects.get(account_title=customerUpdate)
            p = Project.objects.get(projectId=ProjectId)
            p.accountId = account_id
            p.projectName = ProjectName
            p.narration = Description
            p.startDate = startDate
            p.endDate = endDate
            p.projectStatus = status
            p.save()
            messages.success(request, 'Project Updated Successfully!')
    return render(request, 'construction/project.html',{'title':'Projects','projects':project[::-1],'chartofaccounts':chartofaccount, 'get_last_tran_id':get_last_tran_id})

@login_required
def delete_project(request, pk):
    if Inventory.objects.filter(projectId=pk) or PurchaseHeader.objects.filter(projectId=pk) or VoucherHeader.objects.filter(projectId=pk):
        messages.warning(request, 'This project cannot be deleted!')
        return redirect('Project')

    else:
        project = Project.objects.filter(projectId=pk).delete()

        print("deleted")
        return redirect('Project')

@login_required
def delete_inventory_category(request, pk):
    if Inventory.objects.filter(itemCategory=pk):
        messages.warning(request, 'You Cannot Delete This Category')
        return redirect('Add-Category')
    else:
        category = Category.objects.filter(categoryId=pk).delete()
        print("deleted")
        return redirect('Add-Category')

@login_required
def delete_inventory(request, pk):
    inventory = Inventory.objects.filter(itemId=pk).delete()
    print('deleted')
    return redirect('Inventory')

# @login_required
# def delete_chartofaccount(request, pk):
#     if Project.objects.filter(accountId=pk) or PurchaseHeader.objects.filter(accountId=pk) or VoucherHeader.objects.filter(accountId=pk) or Transactions.objects.filter(accountId=pk):
#         messages.warning(request, 'You Cannot Delete This Chart Of Accouont')
#         return redirect('Chart-Of-Account')
#     else:
#         chartofaccount = ChartOfAccount.objects.filter(accountId=pk).delete()
#         print('deleted')
#         return redirect('Chart-Of-Account')

@login_required
def journal_voucher(request):
    all_voucher = VoucherHeader.objects.filter(voucherNo__contains="JV").all()
    print(all_voucher)
    return render(request, 'construction/journal-voucher.html',{'title':'Journal voucher', 'all_voucher':all_voucher})

@login_required
def journal_voucher_new(request):
    chartofaccount = ChartOfAccount.objects.all()
    projects = Project.objects.all()
    get_last_tran_id = VoucherHeader.objects.filter(voucherNo__contains='JV').last()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id.voucherNo
        get_last_tran_id = get_last_tran_id[6:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'JV'+serial
    else:
        get_last_tran_id =  date[2:]+'JV1'
        voucherId = 1
    if request.POST.get("samp") == "projectUpdate":
        main_object_id = request.POST.get("main_object_id")
        sub_menu = Project.objects.filter(accountId=main_object_id).all()
        sub_menu = serializers.serialize('json',sub_menu)
        return JsonResponse({'sub_menu':sub_menu})
    if request.method == "POST":
        doc_no = request.POST.get('documentNo', False)
        tran_id = request.POST.get('transactionId', False)
        doc_date = request.POST.get('date', False)
        desc = request.POST.get('description', False)
        project_id = request.POST.get('project', False)
        accountId = request.POST.get('accountId', False)
        data = json.loads(request.POST.get('data', False))
        print(project_id)
        date = datetime.date.today()
        project_id = Project.objects.get(projectId = project_id)
        account_id = ChartOfAccount.objects.get(id = accountId)
        voucher_header = VoucherHeader(voucherNo = tran_id, date = date, docNo = doc_no, docDate = doc_date, chequeNo = "", chequeDate = date, description = desc, userId = request.user, projectId = project_id, accountId = account_id)
        voucher_header.save()
        voucher_id = VoucherHeader.objects.get(voucherNo = tran_id)
        for value in data:
            if value["Debit"] > "0" and value["Debit"] > "0.00":
                account_id = ChartOfAccount.objects.get(id = value["AccountId"])
                tran1 = Transactions(refrenceId = 0, refrenceDate = doc_date, tranType = '', amount = abs(float(value["Debit"])),
                        date = date, remarks = desc, accountId = account_id, refInvTranId = doc_no, refInvTranType = 'JV', voucherId = voucher_id.voucherId, userId = request.user, project_id=0)
                tran1.save()
                jv_detail1 = VoucherDetail(accountId = account_id, debit = abs(float(value["Debit"])), credit = 0.00, voucherId = voucher_id, invoiceId = 0)
                jv_detail1.save()
            if value["Credit"] > "0" and value["Credit"] > "0.00":
                account_id = ChartOfAccount.objects.get(id = value["AccountId"])
                tran2 = Transactions(refrenceId = 0, refrenceDate = doc_date, tranType = '', amount = -abs(float(value["Credit"])),
                        date = date, remarks = desc, accountId = account_id, refInvTranId = doc_no, refInvTranType = 'JV', voucherId = voucher_id.voucherId, userId = request.user, project_id=0)
                tran2.save()
                jv_detail2 = VoucherDetail(accountId = account_id, debit = 0.00, credit = -abs(float(value["Credit"])), voucherId = voucher_id, invoiceId = 0)
                jv_detail2.save()
        return JsonResponse({"Succes":"Succes"})
    return render(request, 'construction/journal-voucher-new.html',{'title':'Add Journal voucher','chartofaccount':chartofaccount, 'get_last_tran_id':get_last_tran_id, 'projects':projects})

@login_required
def delete_journal_voucher(request,pk):
    voucher = VoucherHeader.objects.filter(voucherId=pk).delete()
    tran = Transactions.objects.filter(voucherId=pk).all().delete()
    print('deleted')
    return redirect('Journal-Voucher')

@login_required
def cash_receiving_voucher(request):
    all_voucher = VoucherHeader.objects.filter(voucherNo__contains="CRV").all()
    print(all_voucher)
    return render(request, 'construction/cash-receiving-voucher.html',{'title':'Cash Receiving Voucher','all_voucher':all_voucher})

@login_required
def cash_receiving_voucher_new(request):
    cof = ChartOfAccount.objects.all()
    projects = Project
    get_last_tran_id = VoucherHeader.objects.filter(voucherNo__contains='CRV').last()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id.voucherNo
        get_last_tran_id = get_last_tran_id[7:]
        get_last_tran_id = int(get_last_tran_id)
        get_last_tran_id = get_last_tran_id+1
        get_last_tran_id = str(get_last_tran_id)
        get_last_tran_id = date[2:] + 'CRV' + get_last_tran_id
    else:
        get_last_tran_id = date[2:]+'CRV1'
    

    if request.POST.get("samp") == "projectUpdate":
        main_object_id = request.POST.get("main_object_id")
        sub_menu = Project.objects.filter(accountId=main_object_id).all()
        sub_menu = serializers.serialize('json',sub_menu)
        return JsonResponse({'sub_menu':sub_menu})

    if request.POST.get("samp") == "crvTable":
        account_id = request.POST.get("account_id")
        amount = request.POST.get("amount")
        account_id = ChartOfAccount.objects.filter(id = account_id).first()
        return JsonResponse({'account_id':account_id.id, 'account_title':account_id.account_title,'amount':amount})

    if request.method == "POST":
        doc_no = request.POST.get('documentNo', False)
        tran_id = request.POST.get('transactionId', False)
        doc_date = request.POST.get('doc-date', False)
        desc = request.POST.get('description', False)
        project_id = request.POST.get('project', False)
        account_id = request.POST.get('account_id', False)
        data = json.loads(request.POST.get('items', False))
        date = request.POST.get('date', False)
        account_id = ChartOfAccount.objects.get(id = account_id)
        project_id = Project.objects.get(projectId = project_id)
        voucher_header = VoucherHeader(voucherNo = tran_id, date = date, docNo = doc_no, docDate = doc_date, chequeNo = "", chequeDate = date, description = desc, userId = request.user, projectId = project_id, accountId = account_id)
        voucher_header.save()
        voucher_id = VoucherHeader.objects.get(voucherNo = tran_id)
        for value in data:
            account_id = ChartOfAccount.objects.get(id = value["AccountId"])
            tran1 = Transactions(refrenceId = 0, refrenceDate = doc_date, tranType = '', amount = -abs(float(value["Credit"])),
                    date = date, remarks = desc, accountId = account_id, refInvTranId = doc_no, refInvTranType = 'CRV', voucherId = voucher_id.voucherId, userId = request.user, project_id=0)
            tran1.save()
            jv_detail1 = VoucherDetail(accountId = account_id, debit = 0.00, credit = -abs(float(value["Credit"])), voucherId = voucher_id, invoiceId = 0)
            jv_detail1.save()

            account_id = ChartOfAccount.objects.get(id = 4)
            tran2 = Transactions(refrenceId = 0, refrenceDate = doc_date, tranType = '', amount = abs(float(value["Credit"])),
                    date = date, remarks = desc, accountId = account_id, refInvTranId = doc_no, refInvTranType = 'CRV', voucherId = voucher_id.voucherId, userId = request.user, project_id=0)
            tran2.save()
            jv_detail2 = VoucherDetail(accountId = account_id, debit = abs(float(value["Credit"])), credit = 0.00, voucherId = voucher_id, invoiceId = 0)
            jv_detail2.save()
        return JsonResponse({"Succes":"Succes"})
    return render(request, 'construction/cash-receiving-voucher-new.html',{'title':'Cash Receiving Add', 'get_last_tran_id':get_last_tran_id,'chartofaccount':cof})

@login_required
def bank_receiving_voucher(request):
    all_voucher = VoucherHeader.objects.filter(voucherNo__contains="BRV").all()
    return render(request, 'construction/bank_receiving_voucher.html',{'title':'Bank Receiving Voucher','all_voucher':all_voucher})

@login_required
def bank_receiving_voucher_new(request):
    all_bank_accounts = ChartOfAccount.objects.filter(account_id = 100).all()
    cof = ChartOfAccount.objects.all()
    get_last_tran_id = VoucherHeader.objects.filter(voucherNo__contains='BRV').last()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id.voucherNo
        get_last_tran_id = get_last_tran_id[7:]
        get_last_tran_id = int(get_last_tran_id)
        get_last_tran_id = get_last_tran_id+1
        get_last_tran_id = str(get_last_tran_id)
        get_last_tran_id = date[2:] + 'BRV' + get_last_tran_id
    else:
        get_last_tran_id = date[2:]+'BRV1'
    if request.POST.get("samp"):
        main_object_id = request.POST.get("main_object_id")
        sub_menu = Project.objects.filter(accountId=main_object_id).all()
        sub_menu = serializers.serialize('json',sub_menu)
        return JsonResponse({'sub_menu':sub_menu})

    if request.method == "POST":
        tran_id = request.POST.get('transactionId', False)
        doc_date = request.POST.get('doc-date', False)
        desc = request.POST.get('description', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)
        project_id = request.POST.get('project', False)
        account_id = request.POST.get('account_id', False)
        data = json.loads(request.POST.get('items', False))
        date = request.POST.get('date', False)
        bank_account = request.POST.get('bank_account', False)
        project_id = request.POST.get('project_id', False)
        account_id = ChartOfAccount.objects.get(id = account_id)
        bank_account = ChartOfAccount.objects.get(id = bank_account)
        project_id = Project.objects.get(projectId = project_id)
        voucher_header = VoucherHeader(voucherNo = tran_id, date = date, docNo = cheque_no, docDate = doc_date, chequeNo = cheque_no, chequeDate = cheque_date, description = desc, userId = request.user, projectId = project_id, accountId = account_id)
        voucher_header.save()
        voucher_id = VoucherHeader.objects.get(voucherNo = tran_id)
        for value in data:
            account_id = ChartOfAccount.objects.get(id = value["AccountId"])
            tran1 = Transactions(refrenceId = 0, refrenceDate = doc_date, tranType = '', amount = -abs(float(value["Credit"])),
                    date = date, remarks = desc, accountId = account_id, refInvTranId = cheque_no, refInvTranType = 'BRV', voucherId = voucher_id.voucherId, userId = request.user, project_id=0)
            tran1.save()
            jv_detail1 = VoucherDetail(accountId = account_id, debit = 0.00, credit = -abs(float(value["Credit"])), voucherId = voucher_id, invoiceId = 0)
            jv_detail1.save()

            tran2 = Transactions(refrenceId = 0, refrenceDate = doc_date, tranType = '', amount = abs(float(value["Credit"])),
                    date = date, remarks = desc, accountId = bank_account, refInvTranId = cheque_no, refInvTranType = 'BRV', voucherId = voucher_id.voucherId, userId = request.user, project_id=0)
            tran2.save()
            jv_detail2 = VoucherDetail(accountId = bank_account, debit = abs(float(value["Credit"])), credit = 0.00, voucherId = voucher_id, invoiceId = 0)
            jv_detail2.save()
        return JsonResponse({"success":"success"})
    return render(request, 'construction/bank_receiving_voucher_new.html',{'title':'Bank Receiving Add','cof':cof, 'get_last_tran_id':get_last_tran_id,'all_bank_accounts':all_bank_accounts})

@login_required
def cash_payment_voucher(request):
    all_voucher = PaymentVoucher.objects.all()
    return render(request, 'construction/cash_payment_voucher.html',{'all_voucher':all_voucher})

@login_required
def cash_payment_voucher_new(request):
    cof = ChartOfAccount.objects.all()
    cursor = conn.cursor()
    get_last_tran_id = PaymentVoucher.objects.last()
    purchases = PurchaseHeader.objects.filter(Q(payment_method='Credit')).all()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id.paymentVoucherNo
        get_last_tran_id = get_last_tran_id[7:]
        get_last_tran_id = int(get_last_tran_id)
        get_last_tran_id = get_last_tran_id+1
        get_last_tran_id = str(get_last_tran_id)
        get_last_tran_id = date[2:] + 'CPV' + get_last_tran_id
    else:
        get_last_tran_id = date[2:]+'CPV1'

    if request.POST.get("samp") == "projectUpdate":
        main_object_id = request.POST.get("main_object_id")
        sub_menu = Project.objects.filter(accountId=main_object_id).all()
        sub_menu = serializers.serialize('json',sub_menu)
        return JsonResponse({'sub_menu':sub_menu})
    elif request.POST.get('samp') == 'project-purchase':
        main_object_id = request.POST.get('main_object_id')
        cursor.execute('''select COA.account_title, PH.details, CP.projectName ,COAS.account_title, PD.total,sum(PV.paidAmount),PH.accountId_id, PH.projectId_id, COAS.id
                        from construction_purchaseheader PH
                        inner join construction_chartofaccount COA on COA.id = PH.accountId_id
                        inner join construction_project CP on PH.projectId_id = CP.projectId
                        inner join construction_chartofaccount COAS on COAS.id = CP.accountId_id
                        inner join construction_purchasedetail PD on PD.purchaseHeaderId_id = PH.purchaseHeaderId
                        left join construction_paymentvoucher PV on PV.purchaseInvoiceID_id = PH.purchaseHeaderId
                        where PH.purchaseHeaderId = %s
                        group by COA.account_title, PH.details, CP.projectName, COAS.account_title,PD.total;''',[main_object_id])
        sub_menu = cursor.fetchall()
        return JsonResponse({'sub_menu':sub_menu})
    elif request.POST.get('samp') == "purchase-table":
        sub_menu = PurchaseHeader.objects.filter(payment_method = 'Credit').all()
        sub_menu = serializers.serialize('json',sub_menu)
        return JsonResponse({'sub_menu':sub_menu})

    if request.method == "POST":
        purchase_invoice = request.POST.get('purchase_invoice')
        supplier_id = request.POST.get('supplier_id')
        cpv_account_title_id = request.POST.get('cpv_account_title_id')
        cpv_project_name_id = request.POST.get('cpv-project_name_id')
        inv_amount = request.POST.get('amount')
        balances = request.POST.get('balances')
        payment = request.POST.get('payment')
        supplier_id = ChartOfAccount.objects.get(id = supplier_id)
        cpv_account_title_id = ChartOfAccount.objects.get(id = cpv_account_title_id)
        print("here", cpv_project_name_id)
        cpv_project_name_id = Project.objects.get(projectId = cpv_project_name_id)
        purchase_invoice = PurchaseHeader.objects.get(purchaseHeaderId = purchase_invoice)
        sourceID = ChartOfAccount.objects.get(id = 4)
        date = datetime.date.today()
        voucher_header = PaymentVoucher(paymentVoucherNo = get_last_tran_id, voucherDate = date, purchaseInvoiceID = purchase_invoice, sourceID = sourceID, projectID = cpv_project_name_id, clientID = cpv_account_title_id, supplierID = supplier_id, description = "", invAmount = inv_amount, paidAmount = payment, balance = balances, userID = request.user)
        voucher_header.save()
        tran1 = Transactions(refrenceId = 0, refrenceDate = date, tranType = '', amount = abs(float(inv_amount)),
                date = date, remarks = "", accountId = supplier_id, refInvTranId = purchase_invoice.purchaseHeaderId, refInvTranType = 'CPV', voucherId = get_last_tran_id, userId = request.user, project_id=0)
        tran1.save()
        account_id = ChartOfAccount.objects.get(id = 4)
        tran2 = Transactions(refrenceId = 0, refrenceDate = date, tranType = '', amount = -abs(float(inv_amount)),
                date = date, remarks = "", accountId = sourceID, refInvTranId = purchase_invoice.purchaseHeaderId, refInvTranType = 'CPV', voucherId = get_last_tran_id, userId = request.user, project_id=0)
        tran2.save()
        # return redirect('Cash-Payment-Vocher-New')
    context = {
        "get_last_tran_id":get_last_tran_id,
        "purchases":purchases
    }
    return render(request, 'construction/cash_payment_voucher_new.html', context)

@login_required
def bank_payment_voucher(request):
    all_voucher = VoucherHeader.objects.filter(voucherNo__contains="BPV").all()
    return render(request, 'construction/bank_payment_voucher.html',{'title':'Bank Payment Voucher','all_voucher':all_voucher})

@login_required
def bank_payment_voucher_new(request):
    all_bank_accounts = ChartOfAccount.objects.filter(parent_id = 26).all()
    get_last_tran_id = VoucherHeader.objects.filter(voucherNo__contains='BPV').last()
    cof = ChartOfAccount.objects.all()
    cursor = conn.cursor()
    get_last_tran_id = cursor.execute('''select * from construction_voucherheader where voucherNo LIKE "%BPV%" order by voucherNo DESC LIMIT 1 ''')
    get_last_tran_id = cursor.fetchall()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id
        get_last_tran_id = get_last_tran_id[7:]
        print(get_last_tran_id)
        get_last_tran_id = int(get_last_tran_id)
        get_last_tran_id = get_last_tran_id+1
        get_last_tran_id = str(get_last_tran_id)
        get_last_tran_id = date[2:] + 'BPV' + get_last_tran_id
    else:
        get_last_tran_id = date[2:]+'BPV1'

    if request.POST.get("samp"):
        main_object_id = request.POST.get("main_object_id")
        sub_menu = Project.objects.filter(accountId=main_object_id).all()
        sub_menu = serializers.serialize('json',sub_menu)
        return JsonResponse({'sub_menu':sub_menu})

    if request.method == "POST":
        tran_id = request.POST.get('transactionId', False)
        doc_date = request.POST.get('doc-date', False)
        desc = request.POST.get('description', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)
        project_id = request.POST.get('project', False)
        account_id = request.POST.get('account_id', False)
        data = json.loads(request.POST.get('items', False))
        date = request.POST.get('date', False)
        bank_account = request.POST.get('bank_account', False)
        print(project_id)
        account_id = ChartOfAccount.objects.get(id = account_id)
        bank_account = ChartOfAccount.objects.get(id = bank_account)
        voucher_header = VoucherHeader(voucherNo = tran_id, date = date, docNo = cheque_no, docDate = doc_date, chequeNo = cheque_no, chequeDate = cheque_date, description = desc, userId = request.user, projectId = Project.objects.get(projectId = project_id), accountId = account_id)
        voucher_header.save()
        voucher_id = VoucherHeader.objects.get(voucherNo = tran_id)
        for value in data:
            account_id = ChartOfAccount.objects.get(id = value["AccountId"])
            tran1 = Transactions(refrenceId = 0, refrenceDate = doc_date, tranType = '', amount = abs(float(value["Debit"])),
                    date = date, remarks = desc, accountId = account_id, refInvTranId = cheque_no, refInvTranType = 'BPV', voucherId = voucher_id.voucherId, userId = request.user, project_id=0)
            tran1.save()
            jv_detail1 = VoucherDetail(accountId = account_id, debit = abs(float(value["Debit"])), credit = 0.00, voucherId = voucher_id, invoiceId = 0)
            jv_detail1.save()

            tran2 = Transactions(refrenceId = 0, refrenceDate = doc_date, tranType = '', amount = -abs(float(value["Debit"])),
                    date = date, remarks = desc, accountId = bank_account, refInvTranId = cheque_no, refInvTranType = 'BPV', voucherId = voucher_id.voucherId, userId = request.user, project_id=0)
            tran2.save()
            jv_detail2 = VoucherDetail(accountId = bank_account, debit = 0.00, credit = -abs(float(value["Debit"])), voucherId = voucher_id, invoiceId = 0)
            jv_detail2.save()
        return JsonResponse({"success":"success"})
    return render(request, 'construction/bank_payment_voucher_new.html',{'title':'Bank Payment Voucher New','cof':cof,'get_last_tran_id':get_last_tran_id,'all_bank_accounts':all_bank_accounts})

@login_required
def pur_pdf(request, pk):
    company_info = CompanyInfo.objects.all()
    header = PurchaseHeader.objects.filter(purchaseHeaderId = pk).first()
    detail = PurchaseDetail.objects.filter(purchaseHeaderId = header).all()


    pdf = render_to_pdf('construction/pur_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Purchase_Summary.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required
def jv_pdf(request, pk):
    company_info = CompanyInfo.objects.all()
    header = VoucherHeader.objects.filter(voucherId = pk).first()
    detail = VoucherDetail.objects.filter(voucherId = header.voucherId).all()
    debit = VoucherDetail.objects.filter(voucherId = header.voucherId).aggregate(Sum('debit'))
    credit = VoucherDetail.objects.filter(voucherId = header.voucherId).aggregate(Sum('credit'))
    pdf = render_to_pdf('construction/jv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, "debit":debit, "credit":credit})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Journal_Voucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required
def crv_pdf(request, pk):
    company_info = CompanyInfo.objects.all()
    header = VoucherHeader.objects.filter(voucherId = pk).first()
    details = VoucherDetail.objects.filter(debit = 0,voucherId = header.voucherId).first()
    print("Here is ",details)
    cursor = connection.cursor()
    detail = cursor.execute('''select sum(VD.credit) as Amount,COA.account_title, COA.id
                            from  construction_voucherdetail VD
                            inner join construction_voucherheader VH on VH.voucherId = VD.voucherId_id
                            inner join construction_chartofaccount COA on VD.accountId_id = COA.id
                            where VD.voucherId_id = %s AND VD.accountId_id = %s
                            group by COA.id;
                            ''',[header.voucherId,details.accountId.id])
    detail = cursor.fetchall()
    amount_in_words =  num2words(abs(detail[0][0]))
    pdf = render_to_pdf('construction/crv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, 'amount_in_words':amount_in_words})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "CashReceivingVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required
def brv_pdf(request, pk):
    company_info = CompanyInfo.objects.all()
    header = VoucherHeader.objects.filter(voucherId = pk).first()
    details = VoucherDetail.objects.filter(debit = 0,voucherId = header.voucherId).first()
    # bank = ChartOfAccount.objects.filter(account_id = '200')
    print("Here is ",details)
    cursor = connection.cursor()
    detail = cursor.execute('''select sum(VD.credit) as Amount,COA.account_title, COA.id
                            from  construction_voucherdetail VD
                            inner join construction_voucherheader VH on VH.voucherId = VD.voucherId_id
                            inner join construction_chartofaccount COA on VD.accountId_id = COA.id
                            where VD.voucherId_id = %s AND VD.accountId_id = %s
                            group by COA.id;
                            ''',[header.voucherId,details.accountId.id])
    detail = cursor.fetchall()
    amount_in_words =  num2words(abs(detail[0][0]))
    pdf = render_to_pdf('construction/brv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, 'amount_in_words':amount_in_words})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "BankReceivingVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required
def bpv_pdf(request, pk):
    company_info = CompanyInfo.objects.all()
    header = VoucherHeader.objects.filter(voucherId = pk).first()
    details = VoucherDetail.objects.filter(credit = 0,voucherId = header.voucherId).first()
    bank = VoucherDetail.objects.get(debit = 0, voucherId= header.voucherId)
    print("Here is ",details)
    cursor = connection.cursor()
    detail = cursor.execute('''select sum(VD.credit) as Amount,COA.account_title, COA.id
                            from  construction_voucherdetail VD
                            inner join construction_voucherheader VH on VH.voucherId = VD.voucherId_id
                            inner join construction_chartofaccount COA on VD.accountId_id = COA.id
                            where VD.voucherId_id = %s AND VD.accountId_id = %s
                            group by COA.id;
                            ''',[header.voucherId,details.accountId.id])
    detail = cursor.fetchall()
    amount_in_words =  num2words(abs(detail[0][0]))
    pdf = render_to_pdf('construction/bpv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, 'amount_in_words':amount_in_words, 'bank':bank})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "BankPaymentVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required
def purchase(request):
    all_purchase = PurchaseHeader.objects.all()
    return render(request, 'construction/purchase.html',{'title':'Purchase', 'all_purchase':all_purchase})

@login_required
def delete_purchase_voucher(request, pk):
    details = PurchaseDetail.objects.filter(purchaseHeaderId=pk).all()
    for detail in details:
        inv = Inventory.objects.filter(itemName=detail.itemId).delete()
    vp = PurchaseHeader.objects.filter(purchaseHeaderId=pk).delete()
    tran = Transactions.objects.filter(refInvTranId=pk).all().delete()
    print("deleted")
    return redirect('Purchase')

# @login_required
# def purchase_new(request):
#     inventory = Inventory.objects.all()
#     cof = ChartOfAccount.objects.all()
#     cat = ChartOfAccount.objects.all()
#     get_last_purchase_no = PurchaseHeader.objects.all().last()
#     if get_last_purchase_no:
#         get_last_purchase_no = get_last_purchase_no.purchaseNo
#         num = int(get_last_purchase_no)
#         num = num + 1
#         get_last_purchase_no = str(num)
#     else:
#         get_last_purchase_no = '100'
#     print(get_last_purchase_no)

#     if request.method == "POST":
#         if request.POST.get('samp') == 'projectUpdate':
#             main_object_id = request.POST.get("main_object_id")
#             print(main_object_id)
#             sub_menu = Project.objects.filter(accountId=main_object_id).all()
#             sub_menu = serializers.serialize('json',sub_menu)
#             return JsonResponse({'sub_menu':sub_menu})
#         elif request.POST.get('samp') == 'purchaseTable':
#             main_object_id = request.POST.get('main_object_id')
#             sub_menu = Inventory.objects.filter(itemId = main_object_id)
#             sub_menu = serializers.serialize('json',sub_menu)
#             return JsonResponse({'sub_menu':sub_menu})
#         else:
#             print("hello")
#             items = json.loads(request.POST.get('main_object_id'))
#             payMethod = request.POST.get('paymentMethod')
#             client = request.POST.get('client')
#             project = request.POST.get('project')

#             print(payMethod, client, project)

#             p = PurchaseHeader(purchaseNo=get_last_purchase_no, payment_method=payMethod, details="", tax=0.00, accountId= ChartOfAccount.objects.get(account_title=client), userId=request.user, projectId=Project.objects.get(projectId=project))
#             p.save()

#             # c = ChartOfAccount.objects.
#             # print()
#             print(items)
#             for item in items:
#                 itemCode = item['ItemCode']
#                 Desc = item['Desc']
#                 Qty = item['Qty']
#                 Price = item['Price']
#                 ST = item['ST']
#                 s = PurchaseDetail(purchaseQuantity=Qty,purchasePrice=Price,total=((float(Qty)*float(Price))+(float(Price)*(float(ST)/100))),itemId=Inventory.objects.get(itemId=itemCode),purchaseHeaderId=PurchaseHeader.objects.get(purchaseNo=get_last_purchase_no))
#                 s.save()
#             if payment_method == 'Cash':
#                 tran2 = Transactions(refrenceId = 0, refrenceDate = datetime.date.today, accountId = ChartOfAccount.objects.get(account_id=client), tranType = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id,ref_inv_tran_id = 0, ref_inv_tran_type = "" ,company_id = company, user_id = request.user, project_id=0)
#                 tran2.save()
#                 tran1 = Transactions(refrenceId = 0, refrenceDate = datetime.date.today, accountId = itemCode, tranType = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id,ref_inv_tran_id = 0, ref_inv_tran_type = "", company_id = company, user_id = request.user, project_id=0)
#                 tran1.save()
#             else:
#                 purchase_account = ChartOfAccount.objects.get(account_title = 'Purchases')
#                 tran1 = Transactions(refrenceId = 0, refrenceDate = datetime.date.today, accountId = account_id, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id,ref_inv_tran_id = 0, ref_inv_tran_type = "", company_id = company, user_id = request.user, project_id=0)
#                 tran1.save()
#                 tran2 = Transactions(refrenceId = 0, refrenceDate = datetime.date.today, accountId = purchase_account, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id,ref_inv_tran_id = 0, ref_inv_tran_type = "", company_id = company, user_id = request.user, project_id=0)
#                 tran2.save()
#                 print('Added')
#                 return JsonResponse({'success':'success'})

#     return render(request, 'construction/purchase-new.html',{'title':'Purchase New','category':cat,'cof':cof, 'get_last_purchase_no':get_last_purchase_no})

@login_required
def cpv_pdf(request, pk):
    company_info = CompanyInfo.objects.all()
    header = VoucherHeader.objects.filter(voucherId = pk).first()
    details = VoucherDetail.objects.filter(debit = 0,voucherId = header.voucherId).first()
    print("Here is ",details)
    cursor = connection.cursor()
    detail = cursor.execute('''select sum(VD.credit) as Amount,COA.account_title, COA.id
                            from  construction_voucherdetail VD
                            inner join construction_voucherheader VH on VH.voucherId = VD.voucherId_id
                            inner join construction_chartofaccount COA on VD.accountId_id = COA.id
                            where VD.voucherId_id = %s AND VD.accountId_id = %s
                            group by COA.id;
                            ''',[header.voucherId,details.accountId.id])
    detail = cursor.fetchall()
    amount_in_words =  num2words(abs(detail[0][0]))
    pdf = render_to_pdf('construction/cpv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, 'amount_in_words':amount_in_words})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "CashPaymentVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required
def delete_cash_receiving_voucher(request, pk):
    vc = VoucherHeader.objects.filter(voucherId=pk).delete()
    tran = Transactions.objects.filter(voucherId=pk).all().delete()
    print("deleted")
    return redirect('Cash-Receiving-Voucher')

@login_required
def delete_bank_receiving_voucher(request, pk):
    vc = VoucherHeader.objects.filter(voucherId=pk).delete()
    tran = Transactions.objects.filter(voucherId=pk).all().delete()
    print("deleted")
    return redirect('Bank-Receiving-Voucher')

@login_required
def delete_cash_payment_voucher(request, pk):
    vc = PaymentVoucher.objects.get(voucherID = pk)
    tran = Transactions.objects.filter(voucherId=vc.paymentVoucherNo).all().delete()
    vc = PaymentVoucher.objects.filter(voucherID=pk).delete()
    print("deleted")
    return redirect('Cash-Payment-Vocher')

@login_required
def delete_bank_payment_voucher(request, pk):
    vc = VoucherHeader.objects.filter(voucherId=pk).delete()
    tran = Transactions.objects.filter(voucherId=pk).all().delete()
    print("deleted")
    return redirect('Bank-Payment-Voucher')

@login_required
def view_journal_voucher(request, pk):
    jv_header = VoucherHeader.objects.filter(voucherId = pk).first()
    jv_detail = VoucherDetail.objects.filter(voucherId = jv_header).all()
    print(jv_header, jv_detail)
    return render(request, 'construction/view-journal-voucher.html', {'title':f'View JV{pk}','jv_header':jv_header,'jv_detail':jv_detail})

@login_required
def view_cash_receiving_voucher(request, pk):
    jv_header = VoucherHeader.objects.filter(voucherId = pk).first()
    jv_detail = VoucherDetail.objects.filter(voucherId = jv_header).all()
    print(jv_header, jv_detail)
    return render(request, 'construction/view-cash-receiving-voucher.html', {'title':f'View CRV{pk}','voucher_header':jv_header,'voucher_detail':jv_detail})

@login_required
def view_bank_receiving_voucher(request, pk):
    jv_header = VoucherHeader.objects.filter(voucherId = pk).first()
    jv_detail = VoucherDetail.objects.filter(voucherId = jv_header).all()
    print(jv_header, jv_detail)
    return render(request, 'construction/view-bank-receiving-voucher.html', {'title':f'View BRV{pk}','voucher_header':jv_header,'voucher_detail':jv_detail})

@login_required
def view_cash_payment_voucher(request, pk):
    jv_header = VoucherHeader.objects.filter(voucherId = pk).first()
    jv_detail = VoucherDetail.objects.filter(voucherId = jv_header).all()
    print(jv_header, jv_detail)
    return render(request, 'construction/view-cash-payment-voucher.html', {'title':f'View CPV{pk}','voucher_header':jv_header,'voucher_detail':jv_detail})

@login_required
def view_bank_payment_voucher(request, pk):
    jv_header = VoucherHeader.objects.filter(voucherId = pk).first()
    jv_detail = VoucherDetail.objects.filter(voucherId = jv_header).all()
    print(jv_header, jv_detail)
    return render(request, 'construction/view-bank-payment-voucher.html', {'title':f'View BPV{pk}','voucher_header':jv_header,'voucher_detail':jv_detail})

@login_required
def report(request):
    all_accounts = ChartOfAccount.objects.all()
    if request.method == "POST":
        if request.POST.get('samp') == 'jv':
            main_object_id = request.POST.get('main_object_id')
            sub_menu = Project.objects.filter(accountId=main_object_id).all()
            sub_menu = serializers.serialize('json',sub_menu)
            return JsonResponse({'sub_menu':sub_menu})
    return render(request, 'construction/reports.html', {'title':'Reports','all_accounts':all_accounts})

@login_required
def sale_summary_item_wise(request):
    total = 0
    if request.method == "POST":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        account_id = request.POST.get('account_id')
        print(account_id)
        company_info = CompanyInfo.objects.filter(id = 1).first()
        print(company_info)
        # image = Company_info.objects.filter(company_name = "Hamza Enterprise").first()
        all_accounts = ChartOfAccount.objects.all()
        cursor = connection.cursor()
        cursor.execute('''Select item_code, item_name, item_description,Sum(Total) As TotalAmount From (
                            select IP.product_code as item_code , IP.product_name as item_name, IP.product_desc as item_description, sum(SD.cost_price * SD.quantity) As Total
                            from transaction_saleheader SH
                            inner join inventory_add_products IP on IP.id = SD.item_id_id
                            inner join transaction_saledetail SD
                            on SD.sale_id_id = SH.id
                            where SH.date Between %s And %s
                            Group by item_code
                            Union All
                            select IP.product_code as item_code, IP.product_name as item_name, IP.product_desc as item_description, sum(SRD.cost_price * SRD.quantity) As Total
                            from transaction_salereturnheader SRH
                            inner join inventory_add_products IP on IP.id = SRD.item_id_id
                            inner join transaction_salereturndetail SRD
                            on SRD.sale_return_id_id = SRH.id
                            where SRH.date Between %s And %s
                            Group by item_code
                            ) tblData
                            group by item_code
                             ''',[from_date, to_date,from_date, to_date, account_id])
        row = cursor.fetchall()
        for value in row:
            total = total + value[5]
        account_id = ChartOfAccount.objects.filter(id = account_id).first()
        account_title = account_id.account_title
        pdf = render_to_pdf('transaction/sale_summary_item_wise_pdf.html', {'company_info':company_info,'image':image,'row':row,'from_date':from_date, 'to_date':to_date,'total':total, 'all_accounts':all_accounts, 'account_title':account_title,'allow_customer_roles':allow_customer_roles,'allow_supplier_roles':allow_supplier_roles,'allow_transaction_roles':allow_transaction_roles,'allow_inventory_roles':allow_inventory_roles,    'allow_report_roles':report_roles(request.user),'is_superuser':request.user.is_superuser})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Sale_Detail_Item_Wise%s.pdf" %("000")
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('report')


@login_required
def account_ledger(request):
     if request.method == "POST":
         debit_amount = 0
         credit_amount = 0
         pk = request.POST.get('account_title')
         from_date = request.POST.get('from_date')
         to_date = request.POST.get('to_date')
         projects = request.POST.get('projects')
         company_info = CompanyInfo.objects.filter(id=1).all()
         cursor = connection.cursor()
         print(pk,from_date,to_date,pk,projects)
         cursor.execute('''select '' as refrenceid,'' as trantype,'' as date,'' as refinvtranid,
                        'Opening' as refinvtrantype,'Opening Balance' as remarks,id as accountid_id,
                        '0' as project_id,'0' as userId_id,
                        Case When opening_balance > 0 then opening_balance else 0 End as Debit,
                        Case When opening_balance < 0 then opening_balance else 0 End as Credit
                        from construction_chartofaccount Where id = %s
                        Union All
                        Select * From (
                        Select refrenceid,trantype,date,refinvtranid,refinvtrantype,
                        remarks,accountid_id,project_id,userId_id,
                        Case When amount > 0 then amount else 0 End as Debit,
                        Case When amount < 0 then amount else 0 End as Credit
                        from construction_transactions
                        Where
                        DATE(date) Between %s And %s
                        Order by date asc) As tblLedger
                        Where accountId_id = %s AND project_id =  %s''',[pk,from_date,to_date,pk,projects])
         row = cursor.fetchall()
         ledger_list = []
         balance = 0
         for i,value in enumerate(row):
             balance = balance + float(value[9]) + float(value[10])
             print("here is balance", balance)
             info = {
             "date": value[2],
             "voucher_no": value[3],
             "tran_type": value[4],
             "debit":value[9],
             "credit":value[10],
             "balance": balance,
             }
             ledger_list.append(info)
         if row:
            for v in row:
                if v[9] >= 0:
                    debit_amount = debit_amount + v[9]
                if v[10] <= 0:
                    credit_amount = credit_amount + v[10]
                    account_id = ChartOfAccount.objects.filter(id = pk).first()
                    account_title = account_id.account_title
         id = account_id.id
         pdf = render_to_pdf('construction/account_ledger_pdf.html',{'ledger_list':ledger_list,'company_info':company_info,'row':row, 'debit_amount':debit_amount, 'credit_amount': credit_amount, 'account_title':account_title, 'from_date':from_date,'to_date':to_date,'id':id})
         if pdf:
             response = HttpResponse(pdf, content_type='application/pdf')
             filename = "TrialBalance%s.pdf" %("000")
             content = "inline; filename='%s'" %(filename)
             response['Content-Disposition'] = content
             return response
         return HttpResponse("Not found")
         return redirect('Report')

@login_required
def trial_balance(request):
    if request.method == "POST":
        debit_amount = 0
        credit_amount = 0
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        print(from_date, to_date)
        company_info = CompanyInfo.objects.filter(id=1).all()
        cursor = connection.cursor()
        cursor.execute('''Select id,account_title,ifnull(amount,0) + opening_balance As Amount
                        from construction_chartofaccount
                        Left Join
                        (select accountId_id,sum(amount) As Amount from construction_transactions
                        Where construction_transactions.refrenceDate Between %s And %s
                        Group By accountId_id
                        ) As tbltran On construction_chartofaccount.id = tbltran.accountId_id;
                        ''',[from_date, to_date])
                        # 'allow_customer_roles':allow_customer_roles,'allow_supplier_roles':allow_supplier_roles,'allow_transaction_roles':allow_transaction_roles,'allow_inventory_roles':allow_inventory_roles,    'allow_report_roles':report_roles(request.user),'is_superuser':request.user.is_superuser
        row = cursor.fetchall()
        for v in row:
            if v[2] >= 0:
                debit_amount = debit_amount + v[2]
            else:
                credit_amount = credit_amount + v[2]
        pdf = render_to_pdf('construction/trial_balance_pdf.html', {'company_info':company_info,'row':row, 'debit_amount':debit_amount, 'credit_amount': credit_amount,'from_date':from_date,'to_date':to_date})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "TrialBalance%s.pdf" %("000")
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('Report')

@login_required
def sale_detail_item_wise(request):
    pass

# @login_required
# def purchase(request):
#     return render(request, 'construction/purchase.html', {'title':'Purchase'})

@login_required
def new_purchase(request):
    all_accounts = ChartOfAccount.objects.all()
    inv = Inventory.objects.all()
    cat = Category.objects.all()
    sup = ChartOfAccount.objects.filter(Q(parent_id=13)).all()
    # print(sup)
    get_last_tran_id = PurchaseHeader.objects.filter(purchaseNo__contains='PUR').last()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    project = Project.objects.all()
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id.purchaseNo
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'PUR'+serial
    else:
        get_last_tran_id =  date[2:]+'PUR1'
        voucherId = 1
    if request.method == "POST":
        if request.POST.get('samp') == 'sale_new':
            sub_menu = VoucherHeader.objects.all()
            sub_menu = serializers.serialize('json',sub_menu)
            print(get_last_tran_id[7:])
            return JsonResponse({'sub_menu': sub_menu})
        elif request.POST.get('samp') == 'purchaseSubmit':
            PurchaseId = request.POST.get('purchaseId')
            CustomerName = request.POST.get('customerName')
            supplier = request.POST.get('supplier')
            Date = request.POST.get('date')
            PayMethod = request.POST.get('payMethod')
            Description = request.POST.get('Description')
            project_pur = request.POST.get('Project')
            total = request.POST.get('grandTotal')
            stAmount = request.POST.get('stAmount')
            referenceNo = request.POST.get('referenceNo')
            # print(stAmount, project_pur)
            total = float(total)
            total = "{0:.2f}".format(total)
            # print(project_pur, total)

            cof = ChartOfAccount.objects.filter(id=17)
            p = PurchaseHeader(purchaseNo=get_last_tran_id,referenceNo=referenceNo, payment_method=PayMethod, details=Description, tax=float(stAmount), accountId= ChartOfAccount.objects.get(account_title=supplier), userId=request.user, projectId=Project.objects.get(projectId=project_pur))
            p.save()
            items = json.loads(request.POST.get('items'))

            for item in items:
                itemName = item['ItemName']
                itemCategory = Category.objects.get(categoryId =item['ItemCategory'])
                itemQuantity = item['Quantity']
                Price = item['Price']
                unit = item['Unit']
                print(itemCategory)
                item_add = Inventory(itemName = itemName, itemCategory=Category.objects.get(categoryName=itemCategory), itemQuantity= itemQuantity, unitPrice=0.0,unit=unit, projectId=Project.objects.get(projectId=project_pur), userId=request.user)
                item_add.save()

                pur_detail = PurchaseDetail(purchaseQuantity=itemQuantity, purchasePrice=Price, total=total, itemId=Inventory.objects.last(), purchaseHeaderId=PurchaseHeader.objects.last())
                pur_detail.save()

            pur = PurchaseHeader.objects.get(purchaseNo=get_last_tran_id)
            pur_id = pur.purchaseHeaderId
            GrandTotal = request.POST.get("grandTotal")
            if PayMethod == "Cash":
                t1 = Transactions(refrenceId=0, refrenceDate=Date, accountId=ChartOfAccount.objects.get(id=4), tranType="Purchase Invoice", amount=-abs(float(GrandTotal)),refInvTranId=pur_id, refInvTranType='', remarks=get_last_tran_id, userId=request.user, project_id=project_pur, voucherId='')
                t2 = Transactions(refrenceId=0, refrenceDate=Date, accountId=ChartOfAccount.objects.get(account_title=supplier), tranType="Purchase Invoice", amount=abs(float(GrandTotal)),refInvTranId=pur_id, refInvTranType='', remarks=get_last_tran_id, userId=request.user, project_id=project_pur, voucherId='')
                t1.save()
                t2.save()
            elif PayMethod == "Credit":
                t1 = Transactions(refrenceId=0, refrenceDate=Date, accountId=ChartOfAccount.objects.get(id=8), tranType="Purchase Invoice", amount=abs(float(GrandTotal)),refInvTranId=pur_id, refInvTranType='', remarks=get_last_tran_id, userId=request.user, project_id=project_pur, voucherId='')
                t2 = Transactions(refrenceId=0, refrenceDate=Date, accountId=ChartOfAccount.objects.get(account_title=supplier), tranType="Purchase Invoice", amount=-abs(float(GrandTotal)),refInvTranId=pur_id, refInvTranType='', remarks=get_last_tran_id, userId=request.user, project_id=project_pur, voucherId='')
                # t1.save()
                # t2.save()
            return JsonResponse({'success':'success'})
        elif request.POST.get('samp') == 'purchaseProject':
            main_object_id = request.POST.get("main_object_id")
            print(main_object_id)
            sub_menu = Project.objects.filter(accountId=ChartOfAccount.objects.get(account_title=main_object_id)).all()
            sub_menu = serializers.serialize('json',sub_menu)
            return JsonResponse({'sub_menu':sub_menu})
    return render(request, 'construction/new_purchase.html',{'title':'New Purchase', 'all_accounts': all_accounts, 'get_last_tran_id':get_last_tran_id, 'inv':inv, 'category':cat, 'project':project, 'all_supplier':sup})

@login_required
def purchase_summary(request):
     if request.method == "POST":
         from_date = request.POST.get('from_date')
         to_date = request.POST.get('to_date')
         project_id = request.POST.get('projects')
         project_title = Project.objects.get(projectId = project_id)
         client = ChartOfAccount.objects.filter(id = project_title.accountId.id).first()
         company_info = CompanyInfo.objects.all()
         cursor = connection.cursor()
         cursor.execute('''select PH.purchaseNo,PH.purchaseDate, PH.referenceNo , COA.account_title ,PH.details, CP.projectName ,PH.payment_method, PD.total, sum(PV.paidAmount),PH.purchaseHeaderId
                        from construction_purchaseheader PH
                        inner join construction_paymentvoucher PV on PV.purchaseInvoiceID_id = PH.purchaseHeaderId
                        inner join construction_purchasedetail PD on PD.purchaseHeaderId_id = PH.purchaseHeaderId
                        inner join construction_chartofaccount COA on COA.id = PH.accountId_id
                        inner join construction_project CP on CP.projectId = PH.projectId_id
                        where PH.projectId_id = %s AND PH.purchaseDate Between %s AND %s
                        Group by PH.purchaseNo, PH.purchaseDate, PH.referenceNo, COA.account_title,PH.details,CP.projectName,PH.payment_method,PD.total,purchaseHeaderId
                        order by PH.purchaseHeaderId; ''',[project_id ,from_date, to_date])
         row = cursor.fetchall()
         purchase_list = []
         for i,value in enumerate(row):
             balance = value[7] - value[8]
             info = {
             "invoice_no": value[0],
             "date": value[1],
             "refrence_no": value[2],
             "account_title": value[3],
             "details": value[4],
             "total_amount":value[7],
             "paid_amount": value[8],
             "balance": balance,
             }
             purchase_list.append(info)
         context = {
         "purchase_list" : purchase_list,
         "company_info": company_info,
         "from_date":from_date,
         "to_date":to_date,
          "client": client.account_title,
          "project": project_title.projectName,
         }
         pdf = render_to_pdf('construction/purchase_summary.html', context)
         if pdf:
             response = HttpResponse(pdf, content_type='application/pdf')
             filename = "PurchaseSummary%s.pdf" %("000")
             content = "inline; filename='%s'" %(filename)
             response['Content-Disposition'] = content
             return response
         return HttpResponse("Not found")
     return redirect('Report')

@login_required
def purchase_summary_detail(request):
    if request.method == "POST":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        project_id = request.POST.get('projects')
        company_info = CompanyInfo.objects.all()
        cursor = connection.cursor()
        cursor.execute('''select PH.purchaseHeaderId, COA.account_title, CP.projectName, COAS.account_title as 'Supplier',
                        PH.purchaseNo, PH.purchaseDate, PD.total as 'Total Amount', sum(PV.paidAmount) as 'Paid Amount'
                        from construction_purchaseheader PH
                        inner join construction_project CP on PH.projectId_id = CP.projectId
                        inner join construction_chartofaccount COA on COA.id = CP.accountId_id
                        inner join construction_chartofaccount COAS on COAS.id = PH.accountId_id
                        inner join construction_purchasedetail PD on PD.purchaseHeaderId_id = PH.purchaseHeaderId
                        inner join construction_paymentvoucher PV on PV.purchaseInvoiceID_id = PH.purchaseHeaderId
                        where PH.projectId_id = %s AND PH.purchaseDate Between %s AND %s
                        group by PH.purchaseHeaderId, PD.total;''',[project_id ,from_date, to_date])
        row = cursor.fetchall()
        purchase_detail = PurchaseDetail.objects.all()
        purchase_detail_list = []
        for i,value in enumerate(row):
            balance = value[6] - value[7]
            info = {
            "invoice_no": value[0],
            "client_name": value[1],
            "project_name": value[2],
            "supplier_name": value[3],
            "purchase_ no":value[4],
            "purchase_date": value[5],
            "total_amount": value[6],
            "paid_amount": value[7],
            "balance_amount": balance,
            }
            purchase_detail_list.append(info)

        context = {
          "purchase_detail_list": purchase_detail_list,
          "purchase_detail":purchase_detail,
          "company_info": company_info,
          "from_date":from_date,
          "to_date":to_date,
        }
        pdf = render_to_pdf('construction/purchase_summary_detail.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "PurchaseSummary%s.pdf" %("000")
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
        return redirect('Report')
