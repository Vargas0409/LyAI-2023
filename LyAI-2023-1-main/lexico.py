import enum, sys
class Lexico:
    def __init__(self, fuente):
        #Se pasa el código fuente como cadena. Se le agrega newline para simplificar el análisis para el último token/sentencia.
        self.fuente = fuente + '\n' 
        self.carActual = ''     #Caracter actual en la cadena.
        self.posActual = -1     #Posición actual en la cadena.
        self.siguiente()

    #Leer el siguiente caracter.
    def siguiente(self): #guarda los cambios en posActual y carActual
        self.posActual += 1             #self.posActual = self.posActual + 1 : posicion actual = 0
        if self.posActual >= len(self.fuente):
            self.carActual = '\0'   #end of file 
        else:
            self.carActual = self.fuente[self.posActual]
            #print(self.carActual)

    #Regresar el caracter adelante (lookahead).
    def asomar(self): #No guarda los cambios en posActual y carActual
        #self.posActual += 1
        if self.posActual + 1 >= len(self.fuente):
            return '\0' 
        return self.fuente[self.posActual + 1] #regresa el caracter adelante
    
    #Token inválido, imprimir error y salir.
    def abortar(self, mensaje):
        sys.exit("Error lexico: " + mensaje)

    #Saltar espacios excepto \n, estas se utilizarán para indicar el final de una sentencia.
    def saltarEspacio(self):
        #saltar los caracteres si son espacios 
        if self.carActual == ' ' or self.carActual == '\t' or self.carActual == '\r': 
            self.siguiente()

    #Saltar comentarios en el código.	
    def saltarComentarios(self):
        #saltar los caracteres si es un '#' comentarios de linea (\n)
        if self.carActual == '#':
            while self.carActual != '\n': #siempre y cuando no sea \n
                self.siguiente()

    #Regresar el siguiente token.
    def getToken(self):
        self.saltarEspacio()
        self.saltarComentarios()
        token = None #variable auxiliar 
        #revisar si los caracteres sencillos coinciden 
        if self.carActual == '+':
            token = Token(self.carActual, TipoToken.PLUS)
        elif self.carActual == '-':
            token = Token(self.carActual, TipoToken.MINUS)
        elif self.carActual == '*':
            token = Token(self.carActual, TipoToken.ASTERISK)
        elif self.carActual == '/':
            token = Token(self.carActual, TipoToken.SLASH)
        elif self.carActual == '\0':
            token = Token(self.carActual, TipoToken.EOF)
        elif self.carActual == '\n':
            token = Token(self.carActual, TipoToken.NEWLINE)
        elif self.carActual == '=':
            #asomar nos regresa un caracter
            if self.asomar() == '=': #==
                carAnterior = self.carActual #=1 caracter actual es igual a '='1
                self.siguiente() #=2 caracter actual es igual a '='2
                token = Token(carAnterior + self.carActual, TipoToken.EQEQ)
            else:
                token = Token(self.carActual, TipoToken.EQ)
        elif self.carActual == '<':
            #asomar nos regresa un caracter
            if self.asomar() == '=': #==
                carAnterior = self.carActual #=1 caracter actual es igual a '='1
                self.siguiente() #=2 caracter actual es igual a '='2
                token = Token(carAnterior + self.carActual, TipoToken.LTEQ)
            else:
                token = Token(self.carActual, TipoToken.LT)
        elif self.carActual == '>':
            #asomar nos regresa un caracter
            if self.asomar() == '=': #==
                carAnterior = self.carActual #=1 caracter actual es igual a '='1
                self.siguiente() #=2 caracter actual es igual a '='2
                token = Token(carAnterior + self.carActual, TipoToken.GTEQ)
            else:
                token = Token(self.carActual, TipoToken.GT)       
        elif self.carActual == '!':
            if self.asomar() == '=': #!=
                carAnterior = self.carActual
                self.siguiente()
                token = Token(carAnterior + self.carActual, TipoToken.NOTEQ)
            else:
                self.abortar("Se esperaba  '!=' pero se obtuvo '!'")
        
        elif self.carActual.isdigit(): #1234567890
            PosNumInicial = self.posActual 
            while self.asomar().isdigit(): #Numeros
                 self.siguiente()
            if self.asomar() == '.': #Punto decimal 
                self.siguiente()
                if not self.asomar().isdigit():  #si no es digito
                    self.abortar("Caracter ilegal en número.")
                while self.asomar().isdigit():
                 self.siguiente()
            #Regresar lexema completo: PosNumInicial hasta self.posActual
            #Obtener la subcadena del codigo fuente 
            lexema = self.fuente[PosNumInicial : self.posActual+1]
            token = Token(lexema, TipoToken.NUMERO)

        # elif self.carActual == '"': #comilla doble
        #     posStringInicial = self.posActual
        #     cadena = "" #variable auxiliar
        #     self.siguiente()
        #     while self.carActual != '"': #mientras no se encuentre otra comilla doble
        #         if self.carActual == '\n' or self.carActual == '\r' or self.carActual == '\t' or self.carActual == '\\' or self.carActual == '%':
        #             self.abortar("Caracter ilegal en cadena")
        #         else:
        #             cadena = self.fuente[posStringInicial : self.posActual+1]
        #             self.siguiente()
        #     self.siguiente() #pasar la comilla doble del fin
        #     token = Token(cadena, TipoToken.STRING) 

        elif self.carActual == '\"':
            #Obtener caracter despues de las comillas 
            self.siguiente() #con esto nos saltamos las comillas
            PosStringInicial = self.posActual #Aqui empezamos a leer los contenidos 
            while self.carActual != '\"': #esto significa que la cadena ya termino
                #leer los contenidos
                if self.carActual == '\n' or self.carActual == '\t' or self.carActual == '\n' or self.carActual == '\\' or self.carActual == '%':
                    self.abortar("Caracter ilegal en cadena")
                self.siguiente()
            lexema = self.fuente[PosStringInicial : self.posActual] #Aqui queremos [inicio, fin], no [inicio, fin]
            token = Token(lexema, TipoToken.STRING)


        #los ID empiezan simpre con letra, luego pueden ser seguidos de numeros y letras         
        elif self.carActual.isalpha(): #Keywords e identificadores
            posInicial = self.posActual
            while self.asomar().isalnum():
                self.siguiente()
            lexema = self.fuente[posInicial : self.posActual+1] #Palabra a identificar
            keyword = Token.revisarSiKeyword(lexema) #Regresar lexema si es keyword o regresar None si no es\
            if keyword == None:
                token = Token(lexema, TipoToken.ID) #Si no se encontró en keywords, es ID
            else:
                token = Token(lexema, keyword) #Si se encontró, entonces es un keyword


        #------------Token desconocido------------
        else:
            #token desconocido
            self.abortar("Lexema Desconocido " + self.carActual)
        #si ya se identifico el token, debemos leer el siguiente caracter
        self.siguiente()
        return token        

class Token:
    def __init__(self, lexema, token):
        self.lexema = lexema
        self.token = token #tipotoken ENUM
    @staticmethod
    def revisarSiKeyword(lexema):
        #usar la enumeracion: TipoToken.name (nombre) ;  TipoToken.value (numeros)
        for tipo in TipoToken:
            if tipo.name == lexema and tipo.value > 100 and tipo.value < 200:
                return tipo
        return None

            
class TipoToken(enum.Enum):
    #escribir todos los tokens 
    EOF = -1 #End of file
    NEWLINE = 0
    NUMERO = 1 
    ID = 2
    STRING = 3
    #KEYWORDS
    LABEL=101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    #OPERADORES
    EQ = 201 #= 2
    PLUS = 202 #+
    MINUS = 203 #-
    ASTERISK = 204 #*
    SLASH = 205 #/
    EQEQ = 206 #== 2
    NOTEQ = 207 #!= 2
    LT = 208 #< 2
    LTEQ = 209 #<= 2 
    GT = 210 #> 2
    GTEQ = 211 #>= 2
    

