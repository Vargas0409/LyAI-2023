import sys 
from lexico import *

class Sintactico():
    def __init__(self, lexico):
        self.lexico = lexico
        self.variables = set()           #Variables
        self.labelsDeclaradas = set()    #Labels
        self.labelsGoto = set()        #Labels a las que se ha saltado "GOTO"

        self.tokenActual = None   #token actual
        self.asomarToken = None   #token que sigue sin guardar
        self.SiguienteToken()
        self.SiguienteToken()  #se tiene que llamar 2 veces para inicializar el actual


    #regresar true si el token actual es igual = del mismo tipo
    def RevisarToken(self, tipo):
        if (tipo == self.tokenActual.token):
            return True
        #return tipo == self.tokenActual.token


    #regresar true si el token actual es igual = del mismo tipo
    def RevisarAsomar(self, tipo):
        if (tipo == self.asomarToken.token):
            return True


    #revisar si el tipo del token es el esperado
    def Match(self, tipo):
        if not self.RevisarToken(tipo): 
            self.Abortar("Se esperaba un: " + tipo.name + " se obtuvo: " + self.tokenActual.token.name)
        #que si sea tipo esperado
        self.SiguienteToken()

    def SiguienteToken(self):
        self.tokenActual = self.asomarToken  #remplaza al token actual por el que sigue
        self.asomarToken = self.lexico.getToken()   #obtiene el siguiente token en el codigo

    def Abortar(self, mensaje):
        sys.exit("Error: " + mensaje)

    #<------------------Reglas de produccion------------->
    #programa ::= sentencia*
    def programa(self):
        print("Programa")
        #Asegurar que no es EOF
        while not self.RevisarToken(TipoToken.EOF):
            self.sentencia()
        for etiqueta in self.labelsGoto:
            if etiqueta not in self.labelsDeclaradas:
                self.Abortar("Se intentó saltar a una etiqueta que no esta declarada: " + etiqueta)

    # sentencia ::= ('IF' comparacion 'THEN' nl (sentencia)* 'ENDIF' nl) 
    # | ('PRINT' (expr |STRING) nl) 
    # | ('WHILE' comparacion 'REPEAT' nl (sentencia)* 'ENDWHILE' nl)
    # |('LABEL' ID nl)
    # | ('GOTO' ID nl)
    # | ('LET' ID '=' expr nl)
    # | ('INPUT' ID nl)
    def sentencia(self):
        print("Sentencia LET")
        #'IF' comparacion 'THEN' nl (sentencia)* 'ENDIF' nl
        if self.RevisarToken(TipoToken.IF): #revisar token regresa True (Todos los IF/WHILE)
            print("Sentencia-If")
            self.SiguienteToken()
            self.comparacion()

            self.Match(TipoToken.THEN) #si es, pasa al siguiente si no es error
            self.nl()

            while not self.RevisarToken(TipoToken.ENDIF):
                self.sentencia()

            self.Match(TipoToken.ENDIF)

        #'PRINT' (expr |STRING)
        elif self.RevisarToken(TipoToken.PRINT):
            print("Sentencia-Print")
            self.SiguienteToken()
            if self.RevisarToken(TipoToken.STRING):
                self.SiguienteToken()
            else:
                self.expr()

        #'WHILE' comparacion 'REPEAT' nl (sentencia)* 'ENDWHILE'
        elif self.RevisarToken(TipoToken.WHILE):
            print("Sentencia-While")
            self.SiguienteToken()
            self.comparacion()

            self.Match(TipoToken.REPEAT) 
            self.nl()

            while not self.RevisarToken(TipoToken.EOF):
                self.sentencia()
            self.Match(TipoToken.ENDWHILE)

        #'LABEL' ID
        elif self.RevisarToken(TipoToken.LABEL):
            print("Sentencia-Label")
            self.SiguienteToken()
            #Verificar que la etiqueta no exista "ID"
            if self.tokenActual.lexema in self.labelsDeclaradas:
                self.Abortar("Este label ya existe: " + self.tokenActual.lexema)
            self.labelsDeclaradas.add(self.tokenActual.lexema) #Agregar a las labels declaradas
            self.Match(TipoToken.ID)

        #'GOTO' ID
        elif self.RevisarToken(TipoToken.GOTO):
            print("Sentencia-GoTo")
            self.SiguienteToken()
            self.labelsGoto.add(self.tokenActual.lexema)    #Agregar el salto 
            self.Match(TipoToken.ID)

        #'LET' ID '=' expr 
        elif self.RevisarToken(TipoToken.LET):
            print("Sentencia-Let")
            self.SiguienteToken()

            if self.tokenActual.lexema not in self.variables:  #revisar si no se ha declarado la variable
                self.variables.add(self.tokenActual.lexema)

            self.Match(TipoToken.ID)
            self.Match(TipoToken.EQ)
            self.expr()

        #'INPUT' ID
        elif self.RevisarToken(TipoToken.INPUT):
            print("Sentencia-Input")
            self.SiguienteToken()

            if self.tokenActual.lexema not in self.variables:  #revisar si no se ha declarado la variable
                self.variables.add(self.tokenActual.lexema)


            self.Match(TipoToken.ID)

        else:
            self.Abortar("La sentencia no es valida en: " + self.tokenActual.lexema + " (" + self.tokenActual.token.name + ")")

        #newline final
        self.nl()
            

    #comparacion ::= expr (opComp expr)+ [+ es igual a uno o mas]
    def comparacion(self):
        print("Comparacion")
        self.expr()
        if self.opComp(): #se programa 1 sola vez
            self.SiguienteToken()
            self.expr()
        else: #si no es un operador de comparacion esta mal
            self.Abortar("Se esperaba un operador de comparacion en: " + self.tokenActual.lexema)
        
        while self.opComp(): #si es verdadero (mas veces)
            self.SiguienteToken()
            self.expr()


    #expr ::= termino(('+' | '-')termino)* [0 o mas veces]
    def expr(self):
        print("expr")
        self.termino()
        while self.RevisarToken(TipoToken.PLUS) or self.RevisarToken(TipoToken.MINUS):
            self.SiguienteToken()
            self.termino()


    #termino ::= unario(('*' | '/')unario)* [0 o mas veces]
    def termino(self):
        print("Termino")
        self.unario()
        while self.RevisarToken(TipoToken.ASTERISK) or self.RevisarToken(TipoToken.SLASH):
            self.SiguienteToken()
            self.unario()

    #unario ::= ('+' | '-')? primario {0 o 1 vez}
    def unario(self):
        print("Unario")
        if self.RevisarToken(TipoToken.PLUS) or self.RevisarToken(TipoToken.MINUS):  #? comportamiento del signo
            self.SiguienteToken()
        self.primario()

    #primario ::= NUMERO|ID
    def primario(self):
        print("Primario")
        if self.RevisarToken(TipoToken.NUMERO):
            self.SiguienteToken()
        elif self.RevisarToken(TipoToken.ID):
            if self.tokenActual.lexema not in self.variables: 
                self.Abortar("Referenciando una variable que no ha sido declarada: " + self.tokenActual.lexema)
            self.SiguienteToken()
        else:
            self.Abortar("Token inesperado en: " + self.tokenActual.lexema)
    

    #opComp ::= '=='|'!='|'>'|'>='|'<'|'<='|
    def opComp(self): #regresen True si es uno de los operadores de comparacion
        if (self.RevisarToken(TipoToken.EQEQ) or self.RevisarToken(TipoToken.NOTEQ) or self.RevisarToken(TipoToken.GT)  
            or self.RevisarToken(TipoToken.GTEQ) or self.RevisarToken(TipoToken.LT) or self.RevisarToken(TipoToken.LTEQ)):
            return True
        

    #nl ::= '\nl'+ ---Una o mas veces
    def nl(self):
        print("Newline")
        self.Match(TipoToken.NEWLINE) #almenos una vez
        while self.RevisarToken(TipoToken.NEWLINE):
            self.SiguienteToken()


    #<------------------Reglas de produccion------------->

