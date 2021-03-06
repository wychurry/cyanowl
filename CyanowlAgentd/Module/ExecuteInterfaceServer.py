#!/usr/bin/env pyhthon
#-*- coding:utf-8 -*-
#this module can control instance by java:
#action include:
#restart,stop,start
import socket
import threading
import subprocess
import xml.dom.minidom as DXML
from config import order
import TcpClient
import Sniffer


class Assemblage:
      """这里是各种脚本调用的地方"""
      def __init__(self,KEYWORD,ARGS):
           """KEYWORD will be match word in config.py which  include order dictionary.
	    *ARGS is variable,but when receive data , it wile be not change"""

           self.keyword = KEYWORD
	   self.args = ARGS 
           print self.args

      def CheckPort(self,IP='localhost'):

           PROTOCOL=self.args[0]
	   print PROTOCOL
	   PORT=self.args[1:]
	   print PORT

           CKWATIME = 2.0
           CKNORMAL = 0
	   ERROR = 104

           def Acttcp():
               """获取端口检测结果，并存入字典，最后生成字符串返回"""
	       resultdic = {}
	       result = ''
               for P in PORT: 
                   CK = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	           CK.settimeout(CKWATIME)
	           CK_ADDR= (str(IP),int(P))
                   RETURN_CODE = CK.connect_ex(CK_ADDR) 
                   if RETURN_CODE != CKNORMAL:
                      resultdic[P] = ERROR 
                   else:
                      resultdic[P] = CKNORMAL
                   CK.close()
	        
               for key,value in resultdic.items():
                   result += ','+str(key)+':'+str(value)
	       #切片取消前置逗号
               return ','.join(result.split(',')[1:])

           def Actudp():
               resultdic = {}
	       result = ''
	       for P in PORT:
		   CK_PORT = str(P)
		   UDPRETURN = subprocess.Popen(['nc','-z','-u',IP,CK_PORT],stdout=subprocess.PIPE)
		   if UDPRETURN.stdout.read() == '':
		      resultdic[P] = ERROR
		   else:
		      resultdic[P] = CKNORMAL

               for key,value in resultdic.items():
                   result += ','+str(key)+':'+str(value)

	       #切片取消前置逗号
               return ','.join(result.split(',')[1:])

	   def GetAllPort():
	       sniffer = Sniffer.ParseNetstat()
               dicport = sniffer.GetListenPortUidInode()
               portlist1 = []
               portlist2 = []
	       TCP = ''
               UDP = '' 
               for var in ['udp4','udp6']:
                   #print '%s:%s' % (var,dicport[var].keys())
                   portlist1 +=dicport[var].keys()
                   print 'portlist1:%s' % portlist1
	       UDP = 'udp'+','+':'.join(list(set(portlist1))) 

               for var in ['tcp4','tcp6']:
                   #print '%s:%s' % (var,dicport[var].keys())
                   portlist2 +=dicport[var].keys()
                   print 'portlist2:%s' % portlist2
	       TCP  = 'tcp'+','+':'.join(list(set(portlist2))) 

	       return TCP+'|'+UDP

	   if  PROTOCOL == 'all':
              #get all port 
	      return GetAllPort() 
	   elif PROTOCOL == 'tcp':
	      msg = Acttcp()	
	      return msg
	   elif PROTOCOL == 'udp':
	      #udp使用nc检测，比较准确
              #CK = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	      #CK.settimeout(CKWATIME)
	      #msg =  Act()	
	      #return msg
              return Actudp()
	   else:
	       print "warnnig: network protocol is wrong,you will be modify!"


      def main(self):
          KEYWORD =self.keyword
	  print KEYWORD
	  print order.keys()
          if KEYWORD == order['port'][0]: # port check
	     print 'self.CheckPort():[%s]' % self.CheckPort()
	     return self.CheckPort()

#---------------------------------------------------------------------------------
	
class ConnectHandler(threading.Thread):  
    '''与客户端连接的处理类'''  

    def setConnect(self, connect):  
        self.connect = connect  
      
    def run(self):   
        sender = TcpClient.Tclient()
        #msg = 'hello\n'.encode("utf-8")                 
        CHECK_PORT_RESU = str((1<<1)|(1<<8))+':'
        COMMAND_NOT_FOUND = str((1<<1)|(1<<2))

        #收到的DATA为字符串并关闭连接
        DATA = self.connect.recv(1024)
        
        if not DATA:
           #sender.TcpSender('Echo=>' + DATA,CHECK_PORT_RESU)
	   self.connect.send(CHECK_PORT_RESU+'Echo=>' + DATA)
	elif not  DATA.split(',')[0] in order.keys():   #判断字符串中的第一个关键是否在命令列表中
           #sender.TcpSender('command not found --' + DATA,CHECK_PORT_RESU)
	   self.connect.send(CHECK_PORT_RESU+'command not found' + DATA)
        else:
           print "origin %s " %  DATA
	   INLIST = DATA.split(',') 

           #实例化功能集合类
           func = Assemblage(INLIST[0],INLIST[1:])
	   content = func.main()
	   print 'content:[%s]' % content
    
           #为java准备#重写用subprocess.call,或者是subpocess.Popen进程间交互
           #STAT = subprocess.check_output(str(ORDER))
           #print STAT
	   self.connect.send(CHECK_PORT_RESU+content)
           #sender.TcpSender(content,CHECK_PORT_RESU)
        self.connect.close() 

       

class MultControl:
    """ control service for  local host by op manually"""
    def __init__(self,IP='0.0.0.0',PORT=6000):
        """listen to 6000 in localhost"""
        self.ip = IP
        self.port = PORT

    def __doc__(self):
       """ show method"""

    def ListenServer(self):
       count = 1
       print("TestServer start(%s:%d)..." % (self.ip, self.port))  
       server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
       #server.settimeout(1000 * 10) 
       server.bind((self.ip,self.port))
       server.listen(10)
       while True:
         (connection,address) = server.accept()
         print("client connecting:",count)
	 count +=1
         
         ServerThread = ConnectHandler()
         ServerThread.setConnect(connection)
         ServerThread.start()
       server.close()
       print("TestServer close, bye-bye.")      
      
      
if __name__ == "__main__":  
    ts = MultControl()  
    ts.ListenServer()  
