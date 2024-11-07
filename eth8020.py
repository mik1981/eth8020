
import  socket
import  time
import  logging
from    threading   import  Lock
from    rich.logging    import  RichHandler
from    utility         import  *


LOG_NAME        =   "eth8020"
SCRIPT_VERSION  =   "0.1"
SCRIPT_DATE     =   "07/11/2024"
SCRIPT_TITLE    =   "eth8020 class ver." + SCRIPT_VERSION + " (" + SCRIPT_DATE + ")"

class eth8020:
    ST_DEINIT   =   -1
    ST_DICONN   =   0
    ST_CONN     =   1


    def __init__( self,  ip,  port = 17494,  name = "eth" ):
        self.s      =   None
        self.ip     =   ip
        self.port   =   port
        self.name   =   name
        self.state  =   self.ST_DEINIT
        self.mutex  =   Lock    ()
        self.releAllOff ()
        #log         =   logging.getLogger   ( LOG_NAME )
        #log.setLevel    ( logging.CRITICAL )


    def close( self ):
        if self.state  ==  self.ST_CONN:
            self.s.close    ()
            self.state      =   self.ST_DICONN


    def connect( self ):
        log         =   logging.getLogger   ( LOG_NAME )
        if self.state  ==  self.ST_DEINIT:
            self.s      =   socket.socket   ( socket.AF_INET,   socket.SOCK_STREAM )
            self.state  =   self.ST_DICONN
            log.debug   ( f"{self.name}: sistema inizializzato" )

        if self.state  ==  self.ST_DICONN:
            try:
                self.s.connect  (  ( self.ip,  self.port )  )
                #log.debug       ( f"{self.name}: sistema connesso" )
                self.state      =   self.ST_CONN

            except Exception as err:
                #log.critical    ( f"{self.name} {self.ip}:{self.port}\n{err}" )
                logException    ( f"{__name__}.connect at {self.ip}:{self.port}" )
                return          False

            else:
                log.info    ( f"{self.name}: socket {self.ip}:{self.port} opened" )

        return      True


    def sendRecv( self,  msg,  bytesWaited ):
        self.mutex.acquire  ()
        if not self.connect ():
            self.mutex.release  ()
            return              None
        #
        try:
            self.s.send         (  msg.encode ( "utf-8" )  )
            ric             =   self.s.recv ( bytesWaited )

        except Exception as err:
            log                 =   logging.getLogger   ( LOG_NAME )
            log.critical        ( f"{self.name} {self.ip}:{self.port} send on socket\n{err}" )
            self.state          =   self.ST_DICONN
            self.mutex.release  ()
            return              None

        else:
            self.mutex.release  ()
            return              ric


    def getRele( self,  pos ):
        if self.mirror  &  (  1 << ( pos - 1 )  ):      return  True
        else:                                           return  False


    def releOn( self,  pos ):
        log         =   logging.getLogger   ( LOG_NAME )
        ret         =   self.sendRecv ( "\x20" + "%c" % pos + "\x00",  1 )
        self.mirror |=  1 << ( pos - 1 )
        #
        if ret == None:
            return      False

        if ret  !=  b"\x00":
            log.critical( f"{self.name}: errore rele con {pos=} ritorna {ret=}" )
            return      False

        log.debug   ( f"{self.name}: rele {pos} ON - 0x{self.mirror:02x}" )
        return      True


    def releOff( self,  pos ):
        log         =   logging.getLogger   ( LOG_NAME )
        ret         =   self.sendRecv ( "\x21" + "%c" % pos + "\x00",  1 )
        self.mirror &=  ~(  1 << ( pos - 1 )  )
        #
        if ret == None:
            return      False

        if ret  !=  b"\x00":
            log         =   logging.getLogger   ( LOG_NAME )
            log.critical( f"{self.name}: errore releOff" )
            return      False

        log.debug   ( f"{self.name}: rele {pos} OFF - 0x{self.mirror:05x}" )
        return      True


    def rele( self,  pos,  on ):
        if on:
            return  self.releOn     ( pos )
        else:
            return  self.releOff    ( pos )


    def releAllOff( self,  less=None ):
        log         =   logging.getLogger   ( LOG_NAME )
        #
        if less ==  None:
            ret         =   self.sendRecv ( "\x23\x00\x00\x00",  1 )
            self.mirror =  0
            #
            if ret == None:
                return      False

            if ret  !=  b"\x00":
                log.critical( f"{self.name}: errore releAllOff (0x{less=:05x})" )
                return      False

            log.debug   ( f"{self.name}: releAllOff" )

        else:
            for k in range ( 20 ):
                if self.mirror  &  (1<<k)  &  (~less):
                    ret     =   self.releOff    ( k + 1 )
                    if ret  ==  False:
                        log.critical( f"{self.name}: errore releAllOff (0x{less=:05x})" )
                        return      False

            #log.debug   ( f"{self.name}: releAllOff less 0x{less:05x}" )

        return      True


    def getAnalog( self,  pos ):        #   pos = da 1 a 8
        ret     =   self.sendRecv ( "\x32" + "%c" % pos,  2 )
        #
        if ret  ==  None:
            log         =   logging.getLogger   ( LOG_NAME )
            log.critical( f"{self.name}: errore getAnalog" )
            return      False,  -1
        #   conversione del valore
        val     =   int.from_bytes  ( ret )
        return      True,  val


    def isOk( self ):
        if not self.connect ():             return      False
        if self.state  ==  self.ST_CONN:    return      True
        else:                               return      False


#     def __str__( self ):
#         if self.name  !=  None:
#             return  f'{self.name}: {self.getMsg ()}'
#         else:
#             return  self.getMsg ()



if __name__ == "__main__":
    import sys, argparse

    parser              =   argparse.ArgumentParser( description=SCRIPT_TITLE )
    parser.add_argument ( '-i',  '--ip',  help='Indirizzo ip modulo eth',  default='127.0.0.1' )
    parser.add_argument ( '-p',  '--port',  help='Porta modulo eth',  default=17494 )
    parser.add_argument ( '--ron',  help='Numero relé da accendere',  default=None )
    parser.add_argument ( '--roff',  help='Numero relé da spegnere',  default=None )
    args                =   parser.parse_args   ()
    eth                 =   eth8020 ( args.ip,  args.port )
    if eth.connect():
        if 'ron' in args:   eth.releOn  ( args.ron )
        if 'roff' in args:  eth.releOff ( args.roff )
    else:
        print   ( f"Dispositivo eth8020 non trovato a {args.ip}/{args.port}" )
