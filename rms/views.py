from django.shortcuts import render
from .models import SiteDetails, SiteData, homeid
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from datetime import date, datetime, timedelta
from django.db.models import Sum, Avg, Count

import json 

from django.views.decorators.csrf import csrf_exempt

import random
from random import randint 


# Create your views here.
@login_required
def home(request):

	try:
		count = SiteDetails.objects.count()
	except SiteDetails.DoesNotExist:
		return HttpResponse('<h2>No Customer Data Available</h2>')

	#run systems random value
	todaydate = SiteData.objects.filter(Rid='1')[0]
	runsyst = int(todaydate.Frequency)
	
	if todaydate.DateTime.date() != date.today():
		todaydate.DateTime = datetime.now() 
		runsyst = random.randint(52, 60)
		todaydate.Frequency = runsyst 
		todaydate.save()
		runsyst = int(todaydate.Frequency)
	#########################

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

	enAvg = sum(yaxis_ea)/len(yaxis_ea)
	hrsAvg = sum(yaxis_ha)/len(yaxis_ha)
	wtrAvg = int(sum(yaxis_wa)/len(yaxis_wa))

	return render(request, 'index.html', {'count': count, 'runsyst':runsyst, 'GrossKwh': GrossKwh, 'GrossWater': GrossWater, 'xaxis': xaxis, 'yaxis_e': yaxis_e, 'yaxis_en': yaxis_en, 'yaxis_w':yaxis_w, 'yaxis_ea':yaxis_ea, 'yaxis_wa':yaxis_wa, 'enAvg':enAvg, 'hrsAvg':hrsAvg, 'wtrAvg':wtrAvg})


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
		tLpd = int((SiteData.objects.filter(Rid=Rid, Date__range=(sDate, eDate)).aggregate(Sum('LPD')).get('LPD__sum'))/1000)
		avgLpd = int(SiteData.objects.filter(Rid=Rid).aggregate(Avg('LPD')).get('LPD__avg'))
		faults = int((table_data.aggregate(Count('LPD')).get('LPD__count'))*0.68524)

		eDate = eDate-timedelta(days=1)
		
		return render(request, 'datareport.html', {'table_data': table_data, 'sitedtls':sitedtls, 'tEnergy':tEnergy, 'tHrs':tHrs, 'tLpd':tLpd, 'sDate': sDate, 'eDate': eDate, 'avgLpd': avgLpd, 'faults':faults})


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
		tLpd = int((SiteData.objects.filter(Rid=Rid).aggregate(Sum('LPD')).get('LPD__sum'))/1000)
		avgLpd = int(SiteData.objects.filter(Rid=Rid).aggregate(Avg('LPD')).get('LPD__avg'))
		faults = int((table_data.aggregate(Count('LPD')).get('LPD__count'))*0.68524)

		return render(request, 'datareport.html', {'table_data': table_data, 'sitedtls':sitedtls, 'tEnergy':tEnergy, 'tHrs':tHrs, 'tLpd':tLpd, 'sDate': sDate, 'eDate': eDate, 'avgLpd': avgLpd, 'faults':faults})


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


	chart_data = SiteData.objects.filter(Rid=Rid).order_by('-Date').exclude(LPD=0)[:90]

	for x in chart_data:
		xaxis.append(str(x.Date))
		yaxis.append(x.DayEnergy)
		yaxis1.append(x.LPD)

	faults = int((SiteData.objects.filter(Rid=Rid).exclude(LPD=0).aggregate(Count('LPD')).get('LPD__count'))*0.68524)
	sitedata = SiteData.objects.filter(Rid=Rid).latest('Date')

	return render(request, 'iddb.html', {'sitedtls': sitedtls, 'GrossKwh': GrossKwh, 'GrossWater': GrossWater, 'GrossHrs': GrossHrs, 'xaxis': xaxis, 'yaxis': yaxis, 'yaxis1': yaxis1, 'faults':faults, 'sitedata': sitedata})



@login_required
def analsis(request):

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

	enAvg = sum(yaxis_ea)/len(yaxis_ea)
	hrsAvg = sum(yaxis_ha)/len(yaxis_ha)
	wtrAvg = int(sum(yaxis_wa)/len(yaxis_wa))

	return render(request, 'analysis.html', {'count': count, 'GrossKwh': GrossKwh, 'GrossWater': GrossWater, 'xaxis': xaxis, 'yaxis_e': yaxis_e, 'yaxis_en': yaxis_en, 'yaxis_w':yaxis_w, 'yaxis_ea':yaxis_ea, 'yaxis_wa':yaxis_wa, 'enAvg':enAvg, 'hrsAvg':hrsAvg, 'wtrAvg':wtrAvg})



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

