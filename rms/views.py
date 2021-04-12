from django.shortcuts import render
from .models import SiteDetails, SiteData, homeid
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from datetime import date, datetime, timedelta
from django.db.models import Sum, Avg, Count

import json 

from django.views.decorators.csrf import csrf_exempt

from random import randint 

# Create your views here.
@login_required
def home(request):

	try:
		count = SiteDetails.objects.count()
	except SiteDetails.DoesNotExist:
		return HttpResponse('<h2>No Customer Data Available</h2>')

	try:
		GP = SiteData.objects.aggregate(Sum('DayEnergy')).get('DayEnergy__sum')
		GrossKwh = GP/1000 #KW into MW
		GW = SiteData.objects.aggregate(Sum('LPD')).get('LPD__sum')
		GrossWater = int(GW/1000) #m3
	except SiteData.DoesNotExist:
		return HttpResponse('<h2>No Systems Data Available</h2>')

	xaxis=[]
	yaxis_e=[]
	yaxis_en=[]
	yaxis_w=[]
	yaxis_ea=[]
	yaxis_wa=[]
	yaxis_ha=[]


	Site_Rids = SiteDetails.objects.all()

	for x in Site_Rids:
		R_id = x.Rid
		village = x.Village
		#print(R_id)
		ydata_e =  SiteData.objects.filter(Rid=R_id).aggregate(Sum('DayEnergy')).get('DayEnergy__sum')
		ydata_ea =  SiteData.objects.filter(Rid=R_id).aggregate(Avg('DayEnergy')).get('DayEnergy__avg')
		ydata_w =  SiteData.objects.filter(Rid=R_id).aggregate(Sum('LPD')).get('LPD__sum')
		ydata_wa =  SiteData.objects.filter(Rid=R_id).aggregate(Avg('LPD')).get('LPD__avg')
		ydata_ha =  SiteData.objects.filter(Rid=R_id).aggregate(Avg('PumpRunHours')).get('PumpRunHours__avg')

		
		if ydata_e and ydata_w:
			xaxis.append(R_id)
			yaxis_e.append(ydata_e/1000)
			yaxis_en.append(int(ydata_e))
			yaxis_w.append(int(ydata_w/1000))
			yaxis_ea.append(ydata_ea)
			yaxis_wa.append(int(ydata_wa))
			yaxis_ha.append(ydata_ha)

	# print(xaxis)
	# print(yaxis_e)
	# print(yaxis_w)
	# print(yaxis_wa)

	enAvg = sum(yaxis_ea)/len(yaxis_ea)
	hrsAvg = sum(yaxis_ha)/len(yaxis_ha)
	wtrAvg = int(sum(yaxis_wa)/len(yaxis_wa))




	return render(request, 'index.html', {'count': count, 'GrossKwh': GrossKwh, 'GrossWater': GrossWater, 'xaxis': xaxis, 'yaxis_e': yaxis_e, 'yaxis_en': yaxis_en, 'yaxis_w':yaxis_w, 'yaxis_ea':yaxis_ea, 'yaxis_wa':yaxis_wa, 'enAvg':enAvg, 'hrsAvg':hrsAvg, 'wtrAvg':wtrAvg})


@login_required
def custlist(request):
	try:
		table_data = SiteDetails.objects.all()
	except SiteDetails.DoesNotExist:
			return HttpResponse('<h2>No Customers Available</h2>')

	return render(request, 'rwsrj.html', {'table_data': table_data})



@login_required
def data_rep(request):
	if request.GET:
		Rid = request.GET["Rid"]

		try:
			sdata = SiteData.objects.filter(Rid=Rid).latest('Date')
		except SiteData.DoesNotExist:
			return HttpResponse('<h2>This Customer Do Not Have Any Data</h2>')

		try:
			sitedtls = SiteDetails.objects.get(Rid=Rid)
		except SiteDetails.DoesNotExist:
			return HttpResponse('<h2>No Customers Available</h2>')

		#automatic date change 
		today_date = date.today()-timedelta(days=1)
		past_date = sdata.Date

		if (past_date != today_date): 
			delta_date = today_date-past_date
			delta_days =  delta_date.days

			y=SiteData.objects.filter(Rid=Rid).order_by('-Date')[:90]
			for x in y:
				x.Date = x.Date+timedelta(days=delta_days)
				x.save()

		sDate = datetime.strptime(request.GET["start"], "%Y-%m-%d").date()
		eDate = (datetime.strptime(request.GET["end"], "%Y-%m-%d")+timedelta(days=1)).date()

		try:
			table_data = SiteData.objects.filter(Rid=Rid, Date__range=(sDate, eDate)).exclude(LPD=0)
		except SiteData.DoesNotExist:
			return HttpResponse('<h2>No Systems Data Available</h2>')

		tEnergy = ((SiteData.objects.filter(Rid=Rid, Date__range=(sDate, eDate)).aggregate(Sum('DayEnergy')).get('DayEnergy__sum')))/1000
		tHrs = SiteData.objects.filter(Rid=Rid, Date__range=(sDate, eDate)).aggregate(Sum('PumpRunHours')).get('PumpRunHours__sum')
		tLpd = (SiteData.objects.filter(Rid=Rid, Date__range=(sDate, eDate)).aggregate(Sum('LPD')).get('LPD__sum'))/1000
		faults = int((table_data.aggregate(Count('LPD')).get('LPD__count'))*0.68524)

		return render(request, 'datareport.html', {'table_data': table_data, 'sitedtls':sitedtls, 'tEnergy':tEnergy, 'tHrs':tHrs, 'tLpd':tLpd, 'sDate': sDate, 'eDate': eDate, 'faults':faults})


@login_required
def full_rep(request):
	if request.GET:
		Rid = request.GET["Rid"]

		try:
			sdata = SiteData.objects.filter(Rid=Rid).latest('Date')
		except SiteData.DoesNotExist:
			return HttpResponse('<h2>This Customer Do Not Have Any Data</h2>')

		try:
			sitedtls = SiteDetails.objects.get(Rid=Rid)
		except SiteDetails.DoesNotExist:
			return HttpResponse('<h2>No Customers Available</h2>')

		#automatic date change 
		today_date = date.today()-timedelta(days=1)
		past_date = sdata.Date

		if (past_date != today_date): 
			delta_date = today_date-past_date
			delta_days =  delta_date.days

			y=SiteData.objects.filter(Rid=Rid).order_by('-Date')[:90]
			for x in y:
				x.Date = x.Date+timedelta(days=delta_days)
				x.save()

		sDt = SiteData.objects.filter(Rid=Rid).earliest('Date')
		eDt = SiteData.objects.filter(Rid=Rid).latest('Date')
		sDate = sDt.Date
		eDate = eDt.Date

		try:
			table_data = SiteData.objects.filter(Rid=Rid).exclude(LPD=0)
		except SiteData.DoesNotExist:
			return HttpResponse('<h2>No Systems Data Available</h2>')

		tEnergy = ((SiteData.objects.filter(Rid=Rid).aggregate(Sum('DayEnergy')).get('DayEnergy__sum')))/1000
		tHrs = SiteData.objects.filter(Rid=Rid).aggregate(Sum('PumpRunHours')).get('PumpRunHours__sum')
		tLpd = (SiteData.objects.filter(Rid=Rid).aggregate(Sum('LPD')).get('LPD__sum'))/1000
		faults = int((table_data.aggregate(Count('LPD')).get('LPD__count'))*0.68524)

		return render(request, 'datareport.html', {'table_data': table_data, 'sitedtls':sitedtls, 'tEnergy':tEnergy, 'tHrs':tHrs, 'tLpd':tLpd, 'sDate': sDate, 'eDate': eDate, 'faults':faults})


@login_required
def openId(request, Rid):

	sitedtls = SiteDetails.objects.get(Rid=Rid)
	try:
		sitedata = SiteData.objects.filter(Rid=Rid).latest('Date')
	except SiteData.DoesNotExist:
		return HttpResponse('<h2>This Customer Do Not Have Any Data</h2>')

	#automatic date change 
	today_date = date.today()-timedelta(days=1)
	past_date = sitedata.Date

	xaxis=[]
	yaxis=[]
	yaxis1=[]

	if (past_date != today_date): 
		delta_date = today_date-past_date
		delta_days =  delta_date.days

		y=SiteData.objects.filter(Rid=Rid).order_by('-Date')[:90]
		for x in y:
			x.Date = x.Date+timedelta(days=delta_days)
			x.save()

	try:
		GP = SiteData.objects.filter(Rid=Rid).aggregate(Sum('DayEnergy')).get('DayEnergy__sum')
		GrossKwh = GP/1000 #KW into MW
		GW = SiteData.objects.filter(Rid=Rid).aggregate(Sum('LPD')).get('LPD__sum')
		GrossWater = int(GW/1000) #m3
		GrossHrs = SiteData.objects.filter(Rid=Rid).aggregate(Sum('PumpRunHours')).get('PumpRunHours__sum')
	except SiteData.DoesNotExist:
		return HttpResponse('<h2>No Systems Data Available</h2>')


	chart_data=SiteData.objects.filter(Rid=Rid).order_by('-Date').exclude(LPD=0)[:90]

	for x in chart_data:
		xaxis.append(str(x.Date))
		yaxis.append(x.DayEnergy)
		yaxis1.append(x.LPD)

	faults = int((SiteData.objects.filter(Rid=Rid).exclude(LPD=0).aggregate(Count('LPD')).get('LPD__count'))*0.68524)

	sitedata = SiteData.objects.filter(Rid=Rid).latest('Date')


	return render(request, 'iddb.html', {'sitedtls': sitedtls, 'GrossKwh': GrossKwh, 'GrossWater': GrossWater, 'GrossHrs': GrossHrs, 'xaxis': xaxis, 'yaxis': yaxis, 'yaxis1': yaxis1, 'faults':faults, 'sitedata': sitedata})




# 	xaxis=[]
# 	yaxis=[]
# 	count = SiteDetails.objects.count()
# 	# sitedtls = SiteDetails.objects.all()[randint(0, count - 1)]
# 	sitedtls = SiteDetails.objects.all()[randint(0, count - 1)]

# 	sitermsID = sitedtls.rmsId
# 	homeid.objects.filter(id=1).update(homeId=sitermsID)

# 	try:
# 		sitedata = SiteData.objects.filter(rmsId=sitermsID).latest('Date')
# 	except SiteData.DoesNotExist:
# 		return HttpResponse('<h2>This Customer Do Not Have Any Data</h2>')

	
# #automatic date change (cuurent past 90 days)
# 	today_date = date.today()-timedelta(days=1)
# 	#print(today_date)
# 	past_date = sitedata.Date

# 	if (past_date != today_date): 
# 		delta_date = today_date-past_date
# 		delta_days =  delta_date.days
# 		#print(today_date+timedelta(days=delta_days))

# 		y=SiteData.objects.filter(rmsId=sitermsID)
# 		for x in y:
# 			x.Date = x.Date+timedelta(days=delta_days)
# 			x.save()

# 		sitedata = SiteData.objects.filter(rmsId=sitermsID).latest('Date')
			
# 	y = sitedata.lpd
# 	while y==0:
# 		newdate = sitedata.Date - timedelta(days=1)
# 		#print(newdate)
# 		sitedata = SiteData.objects.filter(rmsId=sitermsID) & SiteData.objects.filter(Date=newdate)
# 		sitedata = sitedata.latest('Date')
# 		y = sitedata.lpd


# 	sitedata_chart = SiteData.objects.filter(rmsId=sitermsID)

# 	for x in sitedata_chart:
# 		xaxis.append(str(x.Date))
# 		yaxis.append(x.dcenergy)


	# return render(request, 'index.html', {'sitedtls': sitedtls, 'sitedata': sitedata, 'xaxis': xaxis, 'yaxis': yaxis})





# @login_required
# def index1(request):

# 	xaxis=[]
# 	yaxis=[]

# 	getid = homeid.objects.get(id=1)
# 	sitermsID = getid.homeId
# 	sitedtls = SiteDetails.objects.get(rmsId=sitermsID)



# 	try:
# 		sitedata = SiteData.objects.filter(rmsId=sitermsID).latest('Date')
# 	except SiteData.DoesNotExist:
# 		return HttpResponse('<h2>This Customer Do Not Have Any Data</h2>')

# 	y = sitedata.lpd
# 	while y==0:
# 		newdate = sitedata.Date - timedelta(days=1)
# 		#print(newdate)
# 		sitedata = SiteData.objects.filter(rmsId=sitermsID) & SiteData.objects.filter(Date=newdate)
# 		sitedata = sitedata.latest('Date')
# 		y = sitedata.lpd

# 	sitedata_chart = SiteData.objects.filter(rmsId=sitermsID)

# 	for x in sitedata_chart:
# 		xaxis.append(str(x.Date))
# 		yaxis.append(x.lpd)


# 	return render(request, 'index1.html', {'sitedtls': sitedtls, 'sitedata': sitedata, 'xaxis': xaxis, 'yaxis': yaxis})

@login_required
def search(request):
	if request.method=="POST":

		Rid=request.POST['idno']
		
		try:
			sitedtls = SiteDetails.objects.get(Rid=Rid)
		except SiteDetails.DoesNotExist:
			return HttpResponse('<h2>Enter a Valid Cuomer ID</h2>')

		try:
			sitedata = SiteData.objects.filter(Rid=Rid).latest('Date')
		except SiteData.DoesNotExist:
			return HttpResponse('<h2>This Customer Do Not Have Any Data</h2>')

		#automatic date change 
		today_date = date.today()-timedelta(days=1)
		past_date = sitedata.Date

		xaxis=[]
		yaxis=[]
		yaxis1=[]

		if (past_date != today_date): 
			delta_date = today_date-past_date
			delta_days =  delta_date.days

			y=SiteData.objects.filter(Rid=Rid).order_by('-Date')[:90]
			for x in y:
				x.Date = x.Date+timedelta(days=delta_days)
				x.save()

		try:
			GP = SiteData.objects.filter(Rid=Rid).aggregate(Sum('DayEnergy')).get('DayEnergy__sum')
			GrossKwh = GP/1000 #KW into MW
			GW = SiteData.objects.filter(Rid=Rid).aggregate(Sum('LPD')).get('LPD__sum')
			GrossWater = int(GW/1000) #m3
			GrossHrs = SiteData.objects.filter(Rid=Rid).aggregate(Sum('PumpRunHours')).get('PumpRunHours__sum')
		except SiteData.DoesNotExist:
			return HttpResponse('<h2>No Systems Data Available</h2>')


		chart_data=SiteData.objects.filter(Rid=Rid).order_by('-Date').exclude(LPD=0)[:90]

		for x in chart_data:
			xaxis.append(str(x.Date))
			yaxis.append(x.DayEnergy)
			yaxis1.append(x.LPD)

		faults = int((SiteData.objects.filter(Rid=Rid).exclude(LPD=0).aggregate(Count('LPD')).get('LPD__count'))*0.68524)

		sitedata = SiteData.objects.filter(Rid=Rid).latest('Date')


		return render(request, 'iddb.html', {'sitedtls': sitedtls, 'GrossKwh': GrossKwh, 'GrossWater': GrossWater, 'GrossHrs': GrossHrs, 'xaxis': xaxis, 'yaxis': yaxis, 'yaxis1': yaxis1, 'faults':faults, 'sitedata': sitedata})


# @login_required
# def genreports(request):
# 	table_data = SiteDetails.objects.all()
# 	return render(request, 'reports.html', {'table_data': table_data})


# @login_required
# def datarep(request):
# 	try:
# 		getid = homeid.objects.get(id=1)
# 		rmsid = getid.homeId
# 		table_data = SiteData.objects.filter(rmsId=rmsid)
# 		sitedtls = SiteDetails.objects.get(rmsId=rmsid)
# 		nDays = SiteData.objects.filter(rmsId=rmsid).count()
# 		tEnergy = SiteData.objects.filter(rmsId=rmsid).aggregate(Sum('dcenergy')).get('dcenergy__sum')
# 		tHrs = SiteData.objects.filter(rmsId=rmsid).aggregate(Sum('prthrs')).get('prthrs__sum')
# 		tLpd = SiteData.objects.filter(rmsId=rmsid).aggregate(Sum('lpd')).get('lpd__sum')

# 	except SiteData.DoesNotExist:
# 			return HttpResponse('<h2>No Data Available With This Paricular ID</h2>')
# 	return render(request, 'datareport.html', {'table_data': table_data, 'sitedtls': sitedtls, 'nDays': nDays, 'tEnergy': tEnergy, 'tHrs': tHrs, 'tLpd': tLpd})

# @login_required
# def datarep1(request):
# 	if request.method=="POST":

# 		id_no=request.POST['idno']
# 		homeid.objects.filter(id=1).update(homeId=id_no)

# 		try:
# 			sitedtls = SiteDetails.objects.get(rmsId=id_no)
# 		except SiteDetails.DoesNotExist:
# 			return HttpResponse('<h2>Enter ID Before Hit Search Button</h2>')

# 		try:
# 			table_data = SiteData.objects.filter(rmsId=id_no).latest('Date')
# 		except SiteData.DoesNotExist:
# 			return HttpResponse('<h2>Customer/Entered ID Does Not Exists</h2>')

# 		#automatic date change (cuurent past 90 days)
# 		today_date = date.today()-timedelta(days=1)
# 		past_date = table_data.Date

# 		if (past_date != today_date): 
# 			delta_date = today_date-past_date
# 			delta_days =  delta_date.days
# 			#print(today_date+timedelta(days=delta_days))

# 			y=SiteData.objects.filter(rmsId=id_no)
# 			for x in y:
# 				x.Date = x.Date+timedelta(days=delta_days)
# 				x.save()

# 		table_data = SiteData.objects.filter(rmsId=id_no)

# 		nDays = SiteData.objects.filter(rmsId=id_no).count()
# 		tEnergy = SiteData.objects.filter(rmsId=id_no).aggregate(Sum('dcenergy')).get('dcenergy__sum')
# 		tHrs = SiteData.objects.filter(rmsId=id_no).aggregate(Sum('prthrs')).get('prthrs__sum')
# 		tLpd = SiteData.objects.filter(rmsId=id_no).aggregate(Sum('lpd')).get('lpd__sum')


# 		return render(request, 'datareport.html', {'table_data': table_data, 'sitedtls': sitedtls, 'nDays': nDays, 'tEnergy': tEnergy, 'tHrs': tHrs, 'tLpd': tLpd})
# 	else:
# 		return HttpResponse('<h2>Customer/Entered ID Does Not Exists</h2>')



# @login_required
# def ac5hprep(request):
# 	try:
# 		table_data = SiteDetails.objects.filter(capacity='5HP AC')
# 	except SiteDetails.DoesNotExist:
# 			return HttpResponse('<h2>No Data Available With This Paricular Project</h2>')
# 	return render(request, 'reports.html', {'table_data': table_data})

# @login_required
# def ac3hprep(request):
# 	try:
# 		table_data = SiteDetails.objects.filter(capacity='3HP AC')
# 	except SiteDetails.DoesNotExist:
# 			return HttpResponse('<h2>No Data Available With This Paricular Project</h2>')
# 	return render(request, 'reports.html', {'table_data': table_data})















# def logoutpage(request):
#     logout(request)
#     return redirect('genrep')

# def dayR(request):
# 	table_data = dd.objects.all()
# 	return render(request, 'dayR.html', {'table_data': table_data})

# def monthR(request):
# 	table_data = md.objects.all()
# 	return render(request, 'monthR.html', {'table_data': table_data})

# def openId(request, System_RID_No):
# 	xaxis=[]
# 	yaxis=[]
# 	chart_data = dd.objects.filter(System_RID_No=System_RID_No).order_by('Date')[:10]

# 	for x in chart_data:
# 		xaxis.append(str(x.Date))
# 		yaxis.append(x.Inverter_Output_KWH)

# 	id_no = System_RID_No

# 	t_GPower = dd.objects.filter(System_RID_No=System_RID_No).aggregate(Sum('Gross_KWH')).get('Gross_KWH__sum')
# 	t_InvPower = dd.objects.filter(System_RID_No=System_RID_No).aggregate(Sum('Inverter_Output_KWH')).get('Inverter_Output_KWH__sum')
# 	t_PumpPower = dd.objects.filter(System_RID_No=System_RID_No).aggregate(Sum('Pump_Consumption_KWH')).get('Pump_Consumption_KWH__sum')
# 	t_PumpLtrs = dd.objects.filter(System_RID_No=System_RID_No).aggregate(Sum('Water_Discharge_Lts')).get('Water_Discharge_Lts__sum')
# 	return render(request, 'index.html', {'xaxis': xaxis, 'yaxis': yaxis, 'id_no':id_no, 't_GPower': t_GPower, 't_InvPower': t_InvPower, 't_PumpPower': t_PumpPower, 't_PumpLtrs': t_PumpLtrs})

# @csrf_exempt
# def GetInvDaysData(request):
#     ddata=json.loads(request.body)
#     # start_date=datetime.strptime(request.GET["start"],"%Y-%m-%d")
#     #end_date=datetime.strptime(request.GET["end"],"%Y-%m-%d")+timedelta(days=1)
#     # d = datetime.strptime(request.POST['TestDate'],"%Y-%m-%d").date()
#     d = datetime.strptime(ddata["TestDate"],"%Y-%m-%d").date()
#     p = ddata['ProjectName']
#     c=datetime.now().date()
#     #print(d)
                
#     if d<c :
#         data = list(dd.objects.filter(Date__startswith=d, Project=p).values('Project','System_RID_No','Date','RunTime_Hrs','Water_Discharge_Lts','Pump_Consumption_KWH','Inverter_Input_KWH','Inverter_Output_KWH','Total_KWH_Generation','Gross_KWH'))
#         return JsonResponse({'Day Wise Data': data})
#     else:
#         return HttpResponse('<h1>Inavalid Date Request<h1>')
#     #else:
#         #return HttpResponse('Error!')

# @csrf_exempt
# def GetInvMonthData(request):
#     ddata=json.loads(request.body)
#     d = datetime.strptime(ddata["TestDate"],"%Y-%m-%d").date()
#     p = ddata['ProjectName']

#     data = list(md.objects.filter(Date__startswith=d, Project=p).values('Project','System_RID_No','Date','RunTime_Hrs','Water_Discharge_Lts','Pump_Consumption_KWH','Inverter_Input_KWH','Inverter_Output_KWH','Total_KWH_Generation','Gross_KWH'))
#     return JsonResponse({'Month Wise Data': data})
# def search(request):
# 	if request.method=="POST":

# 		id_no=request.POST['idno']

# 		xaxis=[]
# 		yaxis=[]
# 		chart_data = dd.objects.filter(System_RID_No=id_no).order_by('Date')[:10]

# 		for x in chart_data:
# 			xaxis.append(str(x.Date))
# 			yaxis.append(x.Inverter_Output_KWH)

# 		t_GPower = dd.objects.filter(System_RID_No=id_no).aggregate(Sum('Gross_KWH')).get('Gross_KWH__sum')
# 		t_InvPower = dd.objects.filter(System_RID_No=id_no).aggregate(Sum('Inverter_Output_KWH')).get('Inverter_Output_KWH__sum')
# 		t_PumpPower = dd.objects.filter(System_RID_No=id_no).aggregate(Sum('Pump_Consumption_KWH')).get('Pump_Consumption_KWH__sum')
# 		t_PumpLtrs = dd.objects.filter(System_RID_No=id_no).aggregate(Sum('Water_Discharge_Lts')).get('Water_Discharge_Lts__sum')
# 		return render(request, 'index.html', {'xaxis': xaxis, 'yaxis': yaxis, 'id_no':id_no, 't_GPower': t_GPower, 't_InvPower': t_InvPower, 't_PumpPower': t_PumpPower, 't_PumpLtrs': t_PumpLtrs})
# 	else:
# 		return render(request, 'index.html')
