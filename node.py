import socket
import sys
import threading
import multiprocessing
import time
from django.utils import simplejson as json

global seqnum,neighbours,IP,TTL,send,PORT,SLIDINGWINDOW,WAITPEROGM,WINDOWSIZE,TIMEOUT
WAITPEROGM=2
TTL=5
WINDOWSIZE=6
IP=''
PORT=''

neighbours=[]

send=[]
seqnum=0
SLIDINGWINDOW={}
SLIDINGWINDOWTIMEOUT={}
TIMEOUT=5

def Server():
	global seqnum,neighbours,IP,TTL,send,PORT,SLIDINGWINDOW,WAITPEROGM,WINDOWSIZE,SLIDINGWINDOWTIMEOUT
	try :
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print 'Socket created'
	except socket.error, msg :
		print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	 
	 

	try:
		s.bind((IP, int(PORT)))
	except socket.error , msg:
		print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	     
	print 'Socket bind complete'


	while 1:
		d = s.recvfrom(1024)
		data = d[0]
		addr = d[1]
	     
		if not data: 
			break
		if(data[0]!='@' and data[0]!='$'):
			data=json.loads(data, "utf-8")
			addr=data['senderip'].split(":")

			try:
				len(SLIDINGWINDOW[data['ip']])
			except:
				SLIDINGWINDOW[data['ip']]={}
			try:
				len(SLIDINGWINDOW[data['ip']][addr[0]+':'+str(addr[1])])
			except:
				SLIDINGWINDOW[data['ip']][addr[0]+':'+str(addr[1])]={}

			try:
				len(SLIDINGWINDOW[data['ip']][addr[0]+':'+str(addr[1])][data['seq']])				
			except:
				seqdata=int(data['seq'])-WINDOWSIZE
				if(seqdata>0):
					try:
						SLIDINGWINDOW[data['ip']][addr[0]+':'+str(addr[1])].pop(str(seqdata))
					except:
						randomvarialb=1
				SLIDINGWINDOW[data['ip']][addr[0]+':'+str(addr[1])][data['seq']]=1
			
			try:
				len(SLIDINGWINDOWTIMEOUT[data['ip']])
			except:
				SLIDINGWINDOWTIMEOUT[data['ip']]={}
			try:
				len(SLIDINGWINDOWTIMEOUT[data['ip']][addr[0]+':'+str(addr[1])])
			except:
				SLIDINGWINDOWTIMEOUT[data['ip']][addr[0]+':'+str(addr[1])]=TIMEOUT


				data['senderip']=':'.join([IP,str(PORT)])

				ttl=int(data['ttl'])
				for neighbour in neighbours:
					if(neighbour[0]!=addr[0] or int(neighbour[1])!=int(addr[1])):
						if(ttl>1):
							ttl-=1;
							data['ttl']=str(ttl)
							msg=json.dumps(data)
							arr=[msg,neighbour[0],neighbour[1]]
							send.append(arr)
							ttl+=1
		elif(data[0]=='@'):
			print "connecting"
			data=data.split(',')
			desHost=data[1].split(":")[0]
			desPort=data[1].split(":")[1]
			neighbours.append([desHost,int(desPort)])
			print neighbours
		elif(data[0]=='$'):
			print 'Transmitting'
			print data
			data=data.split(',')
			print data
			desHost=data[1].split(":")[0]
			desPort=data[1].split(":")[1]
			if(desHost!=IP or int(desPort)!=int(PORT)):
				print SLIDINGWINDOW[data[1]]
				try:
					len(SLIDINGWINDOW[data[1]])
					conti=1
				except:
					print 'data cant be sent(not sure)'
					conti=0
				if(conti==1):
					conti2=0
					for neighbour in neighbours:
						if(neighbour[0]==desHost and int(neighbour[1])==int(desPort)):
							conti2=1
							msg=','.join(data)
							msg+=","+IP+":"+PORT
							arr=(msg,desHost,desPort)	
							send.append(arr)
							break
					if(conti2==0):
						maxe=-1

						for x,y in SLIDINGWINDOW[data[1]].iteritems():
							for a,b in y.iteritems():
								if(b==1):
									if(maxe<int(a)):
										maxe=int(a)
						maxes=-1
						maxaddr=''
						for x,y in SLIDINGWINDOW[data[1]].iteritems():
							sums=0
							for a,b in y.iteritems():
								if(int(a)>=maxe-(WINDOWSIZE-1) and int(a)<=maxe and b==1):
									sums+=1
							if(maxes<sums):
								maxes=sums	
								maxaddr=x
						msg=','.join(data)
						msg+=","+IP+":"+PORT
						if(maxaddr!=''):
							arr=(msg,maxaddr.split(":")[0],maxaddr.split(":")[1])	
							send.append(arr)
						else:
							print 'data cant be sent(not sure)'
				
			else:
				print data
	s.close()
	
def Client():
	global seqnum,neighbours,IP,TTL,send,PORT,SLIDINGWINDOW,WAITPEROGM,WINDOWSIZE,SLIDINGWINDOWTIMEOUT
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print 'Failed to create socket'
		sys.exit()
	 
	
	while(1) :
		if(len(send) is not 0):
			try :

				s.sendto(send[0][0], (send[0][1], int(send[0][2])))
				
			except socket.error, msg:
				print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
				sys.exit()
			send.pop(0)
	s.close()



def ogmSend():
	global seqnum,neighbours,IP,TTL,send,PORT,SLIDINGWINDOW,WAITPEROGM,WINDOWSIZE,SLIDINGWINDOWTIMEOUT
	while(1):
		for neighbour in neighbours:

			msg='{"ip":"'+IP+':'+PORT+'","seq":"'+str(seqnum)+'","ttl":"'+str(TTL)+'","senderip":"'+IP+':'+PORT+'"}'
			
			arr=[msg,neighbour[0],neighbour[1]]
			send.append(arr)
		
		seqnum+=1
		time.sleep(WAITPEROGM)
def sendData():
	print 'Enter the Destination Address\n'
	while(1):
		addr=raw_input('Enter Host:')
		port=raw_input('Enter port:')
		msg='$,'+addr+":"+port
		if(addr!=IP or port!=PORT):
				try:
					len(SLIDINGWINDOW[msg.split(',')[1]])
					conti=1
				except:
					print 'data cannot be sent'
					conti=0
				if(conti==1):
					maxe=-1

					for x,y in SLIDINGWINDOW[msg.split(',')[1]].iteritems():
						for a,b in y.iteritems():
							if(b==1):
								if(maxe<int(a)):
									maxe=int(a)
					maxes=-1
					maxaddr=''
					for x,y in SLIDINGWINDOW[msg.split(',')[1]].iteritems():
						sums=0
						for a,b in y.iteritems():
							if(int(a)>=maxe-(WINDOWSIZE-1) and int(a)<=maxe and b==1):
								sums+=1
						if(maxes<sums):
							maxes=sums	
							maxaddr=x
					
					msg+=","+IP+":"+PORT
					if(maxaddr!=''):
						arr=(msg,maxaddr.split(":")[0],maxaddr.split(":")[1])	
						send.append(arr)
					else:
						print 'data cannot be sent'
				
		else:
			print msg
def timer():
	global seqnum,neighbours,IP,TTL,send,PORT,SLIDINGWINDOW,WAITPEROGM,WINDOWSIZE,SLIDINGWINDOWTIMEOUT
	while(1):
		arr=[]
		for x,y in SLIDINGWINDOWTIMEOUT.iteritems():
			for a,b in y.iteritems():
				SLIDINGWINDOWTIMEOUT[x][a]=b-1
				if(b==0):
					arr.append([x,a])
		for x in arr:
			SLIDINGWINDOW[x[0]].pop(x[1])
			SLIDINGWINDOWTIMEOUT[x[0]].pop(x[1])
		time.sleep(1)
def printer():
	global seqnum,neighbours,IP,TTL,send,PORT,SLIDINGWINDOW,WAITPEROGM,WINDOWSIZE,SLIDINGWINDOWTIMEOUT
	while (1):
		print SLIDINGWINDOW
		time.sleep(10)
def initNode():
	global seqnum,neighbours,IP,TTL,send,PORT,SLIDINGWINDOW,WAITPEROGM,WINDOWSIZE,SLIDINGWINDOWTIMEOUT
	IP=raw_input('enter your ip address:')
	PORT=raw_input('enter your port number:')
	
	num=raw_input('Enter no of nodes to connect: ')
	for i in range(int(num)):
		addr=raw_input('Enter Host:')
		port=raw_input('Enter port:')
		neighbours.append([addr,port])
		msg='@,'+IP+":"+PORT
		arr=[msg,addr,port]
		send.append(arr)
		#print neighbours

	p = threading.Thread(target=Client)
	p1 = threading.Thread(target=Server)
	p2 = threading.Thread(target=ogmSend)
	p3 = threading.Thread(target=sendData)
	p4 = threading.Thread(target=timer)
	p5 = threading.Thread(target=printer)
	p.start()
	p1.start()
	p2.start()
	p3.start()
	p4.start()
	p5.start()
	p5.join()
	p4.join()
	p3.join()
	p1.join()
	p2.join()
	p.join()
if __name__ == '__main__':
	initNode()
	