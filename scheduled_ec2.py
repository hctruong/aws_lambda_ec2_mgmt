# Author: Huan Truong
# Program: MAFC2SDS
# Purpose: This lambda function will managed the automatic start and shutdown of ec2 instance based on user specify times
# Prereq: 
#	EC2 instances will need the following tags (Time is in UTC):
#		Scheduled : True
#		ScheduleStart: 00:00
#		ScheduleStop: 00:00
#		(optional) ExcludedDays: MTWHFSU
#	A CloudWatch event will need to be created to trigger this lambda function. 
#		Recommend every hour.  
#	The necessary IAM role for this lambda function to control the start/stop of an ec2 instance 	

import boto3
import time

ec2 = boto3.resource('ec2')

def lambda_handler(event, context):

	current_day = time.strftime("%w")
	current_time = time.strftime("%H")
	
	# Creating a days structure for excluded days
	days = {
		'M': '1',
		'T': '2',
		'W': '3',
		'H': '4',
		'F': '5',
		'S': '6',
		'U': '7',
	}
	
	# Getting all ec2 instances that are tagged for automatic control
	filters = [{
		'Name': 'tag:Scheduled',
		'Values': ['True']
	}]
	
	instances = ec2.instances.filter(Filters=filters)
	
	# Sorting tags instances if scheduled time is met
	
	startTime = ''
	stopTime = ''
	excludeDay = ''
	
	stop_instances = []
	start_instances = []
	excluded_days = []
	skip = False
	
	for instance in instances:
	
		for tag in instance.tags:
			if tag['Key'] == 'ExcludedDays':
				excludeDay = tag['Value']
			if tag['Key'] == 'ScheduleStop':
				stopTime = tag['Value']
			if tag['Key'] == 'ScheduleStart':
				startTime = tag['Value']

		
		if excludeDay != '':
			# Spliting the excluded String in separated values
			excluded_days[:] = excludeDay
			# Don't do anything if exclude day is the current day
			for day in excluded_days:
				if days[day] == current_day:
					skip = True
					break
			
		if not skip: 
			if stopTime != '':
				stop_time = stopTime.split(':')
				if stop_time[0] == current_time:
					stop_instances.append(instance.id)
					
			if startTime != '':
				start_time = startTime.split(':')
				if start_time[0] == current_time:
					start_instances.append(instance.id)

	# Shutdowning/Starting Up instances
	if len(stop_instances) > 0:
		stop = ec2.instances.filter(InstanceIds=stop_instances).stop()
		print('Stopped the following instances: ')
		print(stop_instances)
	
	if len(start_instances) > 0:
		start = ec2.instances.filter(InstanceIds=start_instances).start()
		print('Started the following instances: ')
		print(start_instances)
