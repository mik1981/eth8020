
import  logging
import  traceback,  sys
import  serial,  io,  time

from    math        import  trunc
from    rich        import  pretty              #   una volta installato, definisce un output colorato di default
from    rich        import  print
from    datetime    import  datetime



LOG_NAME    =   "utility"


def getStrTimeElapsed( timeSec ):
    if timeSec  <  60:
        return  f"{ round ( timeSec ) }s"

    elif timeSec  <  60*60:
        min     =   trunc ( timeSec/60 )
        sec     =   timeSec  -  min * 60
        return  f"{ min }m { trunc ( sec ) }s"

    else:
        return  f"{ round ( timeSec / 60 ) }m"

    return  "--"



def logException( msg = None ):
    log         =   logging.getLogger   ( LOG_NAME )
    #
    if msg == None:
        log.exception   ( "general error" )
    else:
        log.exception   ( msg )
        print           ( f"{traceback.format_exc()}\{sys.exc_info()[2]}" )


class timer():
    def __init__( self ):
        self.update ()

    def update( self ):
        self.start  =   datetime.now ().timestamp ()

    def elapsedAtLeast( self,  deltaSec ):
        self.lastDeltaSecs  =   datetime.now ().timestamp ()  -  self.start
        #
        if self.lastDeltaSecs  >  deltaSec:
            return      True
        else:
            return      False

    def getDeltaTime( self ):
        self.lastDeltaSecs  =   datetime.now ().timestamp ()  -  self.start
        return              self.lastDeltaSecs

    def strStart( self ):
        return      datetime.fromtimestamp  ( self.start ).strftime ( "%a %d/%m/%Y %H:%M:%S" )

    def __str__( self ):
        return      f"{ round (  self.getDeltaTime ()  ) }s"



class progresso():
    LOG_NAME    =   "progresso"
    TP_CAP      =   0
    TP_TEST     =   1

    def __init__( self ):
        self.reset  ()


    def reset( self ):
        self.totCount   =   0
        #
        self.cap        =   "--"
        self.num        =   "--"
        #
        self.test       =   "--"
        self.capCount   =   0
        #
        self.fasi       =   []
        self.tmpFasi    =   []
        self.mainRes    =   True


    def set( self,  kind,  num,  msg ):
        log             =   logging.getLogger   ( self.LOG_NAME )
        self.totCount   +=  1
        self.capCount   +=  1
        #
        if self.mainRes:
            match kind:
                case    self.TP_CAP:
                    self.num        =   num
                    self.cap        =   msg
                    self.capCount   =   0
                    self.tmpFasi    =   []
                    self.test       =   "--"

                case    self.TP_TEST:
                    self.test       =   msg


    def update( self,  kind,  res,  val="" ):
        log         =   logging.getLogger   ( self.LOG_NAME )
        #
        if self.mainRes:
            match kind:
                case    self.TP_CAP:
                    for k in self.tmpFasi:
                        #print( f"k {k}" )
                        self.fasi.append    ( k )
                        if not k [ 'res' ]:   self.mainRes    =   res

                case    self.TP_TEST:
                    self.tmpFasi.append ( {  "num": f"{self.num} ({self.capCount})",  "cap": self.cap,  "test": self.test,  "val": val,  "res": res,  "op": f"{self.totCount}"  } )


    def sCap( self,  num,  msg ):
        self.set    ( self.TP_CAP,  num,  msg )
        log         =   logging.getLogger   ( self.LOG_NAME )
        log.info    ( f"{num:<6} {msg}" )


    def sTest( self,  msg ):
        self.set    ( self.TP_TEST,  "",  msg )
        log         =   logging.getLogger   ( self.LOG_NAME )
        log.info    ( f"{self.capCount:>03}) {msg} ({self.totCount})" )


    def uCap( self ):
        self.update ( self.TP_CAP,      True )
        return      True


    def close( self,  res ):
        self.update ( self.TP_CAP,      res )
        return      True


    def uTest( self,  res,  val="" ):
        self.update ( self.TP_TEST,  res,  val )
        return      res


    def getFasi( self ):
        self.uCap   ()
        return  self.fasi.copy ()


    def __str__( self ):
        return  f"{ self.num }.{ self.capCount } - { self.cap } - { self.test }"



class port():

    def __init__( self,  com=None,  uid=None,  baud=115200,  timeout=1,  progr=progresso(),  dm=None ):
        self.com        =   com
        self.uid        =   uid
        self.baud       =   baud
        self.timeoutDef =   timeout
        self.timeout    =   timeout
        self.progr      =   progr
        self.dm         =   dm
        self.s          =   None
        self.sio        =   None
        #
        if com == None  and  uid == None:
            raise   Exception   ( "E' necessario definire una com o un uid" )


    def getSio( self ):     return      self.sio
    def getSer( self ):     return      self.s


    def conn( self,  timeout=None ):
        log         =   logging.getLogger   ( LOG_NAME )
        justClosed  =   False
        #
        if self.com  ==  None:
            if self.dm  ==  None:   raise
            else:                   self.com    =   self.dm.getComNumber    ( self.uid )
        if timeout  ==  None:       timeout     =   self.timeoutDef
        #
        if self.timeout  !=  timeout:
            if self.s  !=  None:    justClosed      =   True
            self.close      ()
            #if self.timeout  !=  0:     log.warning     ( f"{com=} Switch to new timeout {timeout} secs" )
        #
        if self.s  ==  None:
            tm      =   timer   ()
            uscita  =   False
            saveErr =   None
            while not tm.elapsedAtLeast ( 5.0 )  and  not uscita:
                try:
                    self.s          =   serial.Serial       ( self.com,  self.baud,  timeout=timeout,  interCharTimeout=0.001 )#0.001 )
                    self.timeout    =   timeout
                    #log.warning     ( f"ser opened with {timeout=}" )
                    if not justClosed:      log.debug   ( f"{self.com=} aperta dopo {tm.getDeltaTime():3.2f}s" )
                    uscita          =   True

                except Exception as err:
                    saveErr         =   err#log.critical    ( f"{self.com=} {tm.getDeltaTime():3.2f}s - board gia' occupata\n{err}\n{traceback.format_exc()}\n{sys.exc_info()[2]}" )
                    time.sleep      ( 0.1 )
                        #raise
            #
            if not uscita:
                log.critical    ( f"{self.com=} indisponibile o occupata\n{saveErr}" )
                return          False   #   propagazione errore apertura seriale
            self.sio    =   io.TextIOWrapper    (  io.BufferedRWPair ( self.s, self.s )  )

        return      True


    def close( self ):
        if self.s  !=  None:
            log             =   logging.getLogger   ( LOG_NAME )
            log.debug       ( f"Chiusura di {self.com=}" )
            self.s.close    ()
            self.s          =   None



if __name__  ==  "__main__":
    import  argparse

    parser              =   argparse.ArgumentParser ()
    parser.add_argument (   'com',  nargs=1,  help = 'numero com' )
    args                =   vars    ( parser.parse_args () )
    #pretty.install  ()
    #
    test                =   port    ( "COM" + args [ 'com' ][0] )
    if test.conn ():
        #test.sio.write ( "N\x0D" )
        #test.sio.flush()
        recv    =   test.sio.read ()
        print   ( f"{recv=}" )
    else:
        print   ( "impossibile connettere la com" )

