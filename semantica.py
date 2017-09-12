import pprint 
from manuparser import Parser
from ply import yacc


class Semantica():

	def __init__(self, code):
		self.simbolos ={}
		self.escopo="global"
		self.tree=Parser(code).ast
		self.programa(self.tree)
		self.verifica_main(self.simbolos)
		self.verifica_utilizadas(self.simbolos)
		self.verifica_funcoes(self.simbolos)


	def programa(self,node):
		self.lista_declaracoes(node.child[0])

	def lista_declaracoes(self, node):
		if len(node.child)==1:
			self.declaracao(node.child[0])
		else:
			self.lista_declaracoes(node.child[0])
			self.declaracao(node.child[1])

	def declaracao(self,node):
		if node.child[0].type == "declaracao_variaveis":
			self.declaracao_variaveis(node.child[0])
		elif(node.child[0].type=="inicializacao_variaveis"):
			self.inicializacao_variaveis(node.child[0])
		else:
			if(len(node.child[0].child)==1):
				self.escopo=node.child[0].child[0].value
			else:
				self.escopo=node.child[0].child[1].value

			self.declaracao_funcao(node.child[0])	
			self.escopo="global"


	def declaracao_variaveis(self, node):
		tipo = node.child[0].type
		string=""
		i=0	
		complemento=""	
		for son in self.lista_variaveis(node.child[1]):
			if("[" in son):
				for i in range(len(son)):
					if (son[i]=="["):
						break
					string += son[i]
				complemento=son[i:]
				son=string
			if self.escopo+"-"+son  in self.simbolos.keys():
				print("Erro: Variavel '"+son+ "' já declarada")
				exit(1)
			if("global-"+son  in self.simbolos.keys()):
				print("Erro: Variavel '"+son+ "' já declarada")
				exit(1)
			if son  in self.simbolos.keys():
				print("Erro: já existe uma função declarada como '"+node.value+"'")
				exit(1)
			self.simbolos[self.escopo+"-"+son]=["variavel",son,False,False,tipo+complemento,0]

					#classe, nome variavel, utilizada, atribuida, tipo
			
				
		return "void"



	def inicializacao_variaveis(self,node):
		self.atribuicao(node.child[0])


	def lista_variaveis(self, node):
		ret_args=[]
		if(len(node.child)==1):
			if(len(node.child[0].child))==1:
				ret_args.append(node.child[0].value+self.indice(node.child[0].child[0]))
			else:
				ret_args.append(node.child[0].value)
			# self.var(node.child[0])
			return ret_args
		else:
	 		ret_args=self.lista_variaveis(node.child[0])
	 		if(len(node.child[1].child))==1:
 				ret_args.append(node.child[0].value)+self.indice(node.child[0].child[0])
 			else:
 				ret_args.append(node.child[0].value)
	 		return ret_args

	 	

 

	def var(self,node):
		name =self.escopo+"-"+node.value
		if(len(node.child)==1):
			if(name not in self.simbolos):
				name = "global-"+node.value
				if(name not in self.simbolos):
					print(self.simbolos)
					print("Erro váriavel '"+node.value+"' não declarada")
					exit(1)
			if(self.simbolos[name][3]==False):
				print("Erro, variavel '"+name+"' não atribuida")
				exit(1)
			var = self.indice(node.child[0])
			self.simbolos[name][4] = self.simbolos[name][4] + var
			self.simbolos[name][2] = True
			return self.simbolos[name][4]

		else:

			if(name not in self.simbolos):
				name = "global-"+node.value
				if(name not in self.simbolos):
					print("Erro váriavel '"+node.value+"' não declarada")
					exit(1)
			if(self.simbolos[name][3]==False):
				print("Erro, variavel '"+name+"' não atribuida")
				exit(1)

			#print(self.simbolos[name][4])
			self.simbolos[name][2] = True 
			return self.simbolos[name][4]
			 

	def indice(self, node):
		if(len(node.child)==1):
			tipo=self.expressao(node.child[0])
			if(tipo != "inteiro"):
				print("Erro: index invalido, permitido sómente inteiro")
				exit(1)
			return("[]")
		else:
			variavel=self.indice(node.child[0])
			tipo=self.expressao(node.child[1])
			if(tipo != "inteiro"):
				print("Erro: index invalido, permitido sómente inteiro")
				exit(1)
			return ("[]"+variavel)
			
			
	def tipo(self,node):
		if node.type=="inteiro" or node.type=="flutuante":
			return node.type
		else:
			print("Erro: Tipo invalido, tipo esperado 'inteiro' ou 'flutuante' tipo recebido: "+node.type)
	
	def declaracao_funcao(self, node):
		if len(node.child) ==1:
			tipo = "void"
			if node.child[0].value in self.simbolos.keys():
				print ("Erro: Função "+node.child[0].value+" já declarada")
				exit(1)
			elif "global-"+node.child[0].value in self.simbolos.keys():
				print ("Erro, já existe uma variavel declarada com o nome de "+node.child[0].value)
				exit(1)
			self.simbolos[node.child[0].value]=["funcao",node.child[0].value,[],False,tipo,0]	
			self.cabecalho(node.child[0])
		else:
			tipo =self.tipo(node.child[0])
			self.simbolos[node.child[1].value]=["funcao",node.child[1].value,[],False,tipo,0]
			self.cabecalho(node.child[1])

	def cabecalho(self,node):
		#classe, nome variavel, utilizada, atribuida, tipo
		lista_par = self.lista_parametros(node.child[0])

		#modificacao
		self.simbolos[node.value][2]=lista_par
		tipo_corpo=self.corpo(node.child[1])
		tipo_fun = self.simbolos[node.value][4]
		if tipo_corpo != tipo_fun:
			if(node.value == "principal"):
				print("Warning: a função '"+node.value+"' deveria retornar: '"+tipo_fun+"' mas retorna '"+tipo_corpo+"'")
			else:	
				print("Erro: a função '"+node.value+"' deveria retornar: '"+tipo_fun+"' mas retorna '"+tipo_corpo+"'")
				exit(1)

	def lista_parametros(self, node):#ok
			lista_param = []
			if len(node.child)==1:
				if(node.child[0] == None):
					return self.vazio(node.child[0])
				else:
					lista_param.append(self.parametro(node.child[0]))
					return lista_param

			else:
				lista_param = self.lista_parametros(node.child[0])
				lista_param.append(self.parametro(node.child[1]))
				return lista_param
				
	def parametro(self, node):#ok
		if node.child[0].type == "parametro":
			return self.parametro(node.child[0])+"[]"
		self.simbolos[self.escopo+"-"+node.value]=["variavel",node.value,False,True,node.child[0].type,0]
		return self.tipo(node.child[0])

	def vazio(self, node):#ok
		return "void"
	
	
	def corpo(self, node):
		if len(node.child)==1:
			return self.vazio(node.child[0])
		
		else:
			tipo1c = self.corpo(node.child[0])
			tipo2c = self.acao(node.child[1])
			#print(tipo2c)
			#print("\n")
			if(tipo2c!=None):
				#print("entrou")
				return tipo2c

	def acao(self, node):
		tipo_ret_acao = "void"
		if node.child[0].type=="expressao":
			return self.expressao(node.child[0])
		elif node.child[0].type=="declaracao_variaveis":
			return self.declaracao_variaveis(node.child[0])
		elif node.child[0].type=="se":
			return self.se(node.child[0])
		elif node.child[0].type=="repita":
			return self.repita(node.child[0])
		elif node.child[0].type=="leia":
			return self.leia(node.child[0])
		elif node.child[0].type=="escreva":
			return self.escreva(node.child[0])
		elif node.child[0].type=="retorna":
			return self.retorna(node.child[0])
		elif node.child[0].type=="error":
			return self.error(node.child[0])

	def se(self, node):
		tipo_se = self.expressao(node.child[0])
		if tipo_se != "logico":
			print("Erro: Espera-se uma expressão logica para o SE, foi dado uma expressão do tipo: "+tipo_se)
			exit(1)
		
		if len(node.child) == 2:
			return self.corpo(node.child[1])
		else:
			tipo_c1 = self.corpo(node.child[1])
			tipo_c2 = self.corpo(node.child[2])
			if tipo_c1 != tipo_c2:
				print("Erro: tipo de retorno invalido")
				exit(1)
			
			return tipo_c1

	def repita(self, node):
		tipo_se = self.expressao(node.child[1])
		if tipo_se != "logico":
			print("Erro: Espera-se uma expressão logica para o SE, foi dado: "+tipo_se)
			exit(1)
			
		return self.corpo(node.child[0])
		

	def atribuicao(self, node):
		nome = self.escopo+"-"+node.child[0].value
		if(self.escopo+"-"+node.child[0].value not in self.simbolos.keys()):
			nome = "global"+"-"+node.child[0].value
			if("global"+"-"+node.child[0].value not in self.simbolos.keys()):
				print ("Erro: Variavel '"+node.child[0].value+"' não declarada")
				exit(1)
		tipo  = self.simbolos[nome][4]
		tipo_exp =  self.expressao(node.child[1])
		self.simbolos[nome][2]=True
		self.simbolos[nome][3]=True
		if(tipo != tipo_exp):
			print ("Warning: Coerção de tipos, tipo esperado: "+tipo+", tipo recebido: "+tipo_exp)

		return "void"




	def leia(self, node):
		if self.scope+"-"+node.value not in self.simbolos.keys():
			if "global-"+node.value not in self.simbolos.keys():
				print("Erro: "+node.value+" não declarada")
				exit(1)
		
		return "void"

	def escreva(self, node):
		tipo_exp = self.expressao(node.child[0])
		
		if tipo_exp == "logico":
			print("Erro: expressao invalida")
		
		return "void"
		
	def retorna(self, node):
		tipo_exp = self.expressao(node.child[0])
		
		if tipo_exp == "logico":
			print("Erro: expressao invalida")	
		return tipo_exp
		

	def expressao(self, node):
		if node.child[0].type=="expressao_simples":
			return self.expressao_simples(node.child[0])#ok
		else:
			return self.atribuicao(node.child[0])#ok


	def expressao_simples(self, node):#ok!!
		if len(node.child)==1:
			return self.expressao_aditiva(node.child[0])#ok
		else:
			tipo1=self.expressao_simples(node.child[0])#ok
			self.operador_relacional(node.child[1])
			tipo2=self.expressao_aditiva(node.child[2])
			if(tipo1!=tipo2):
				print("Warning: Operacao com tipos diferentes '"+tipo1+"' e '"+tipo2)
			return "logico"




	def expressao_aditiva(self, node):#ok!!
		if len(node.child)==1:
			return self.expressao_multiplicativa(node.child[0])#ok
		else:
			tipo1=self.expressao_aditiva(node.child[0])
			self.operador_soma(node.child[1])
			tipo2=self.expressao_multiplicativa(node.child[2])

			if(tipo1!=tipo2):
				print("Warning: Operacao com tipos diferentes '"+tipo1+"' e '"+tipo2)
			if((tipo1=="flutuante")or(tipo2=="flutuante")):
				return "flutuante"
			else:
				return "inteiro"

	def expressao_multiplicativa(self, node):#ok!
		if len(node.child)==1:
			return self.expressao_unaria(node.child[0])#ok
		else:
			tipo1=self.expressao_multiplicativa(node.child[0])
			self.operador_multiplicacao(node.child[1])
			tipo2=self.expressao_unaria(node.child[2])
			if(tipo1!=tipo2):
				print("Warning: Operacao com tipos diferentes '"+tipo1+"' e '"+tipo2)
			if((tipo1=="flutuante")or(tipo2=="flutuante")):
				return "flutuante"
			else:
				return "inteiro"

	def expressao_unaria(self, node):#ok!!
		if len(node.child)==1:
			return self.fator(node.child[0])
		else:
			self.operador_soma(node.child[0])
			return self.fator(node.child[1])

	def operador_relacional(self, node):
		return None
	def operador_soma(self, node):
		return None

	def operador_multiplicacao(self, node):
		return None

	def fator(self, node):
		if(node.child[0].type=="var"):#ok
			return self.var(node.child[0])
		if(node.child[0].type=="chamada_funcao"):
			return self.chamada_funcao(node.child[0])
		if(node.child[0].type=="numero"):
			return self.numero(node.child[0])
		else:
			return self.expressao(node.child[0])


	def numero(self, node):
		string = repr(node.value)
		if "."in string:
			return "flutuante"
		else:
			return "inteiro"


	

	def chamada_funcao(self, node):
		if(node.value == "principal" and self.escopo=="principal"):
			print("Warning: Chamada recursiva para a função principal")
		if(node.value=="principal"and self.escopo!="principal"):
			print("Erro, chamada para a função principal da funcao '"+self.escopo+"'")
			exit(1)
		if node.value not in self.simbolos.keys():
			print ("Erro: Função "+node.value+" não declarada")
			exit(1)
		self.simbolos[node.value][5]=1	
		argslista=[]
		argslista.append(self.lista_argumentos(node.child[0]))
		if(argslista[0]==None):
			argslista=[]
		elif(not(type(argslista[0]) is str)):
			argslista = argslista[0]

		args_esperados = self.simbolos[node.value][2]
		if(type(args_esperados) is str):
			args_esperados = []
		if(len(argslista)!=len(args_esperados)):
			lesperados=(len(args_esperados))
			lrecebidos=(len(argslista))
			# print("Erro: Numero de argumentos esperados em "+node.value+": " +len(args_esperados)+ ", quantidade de argumentos recebidos: "+len(argslista))
			print("Erro: Numero de argumentos esperados em '"+node.value+"': "+str(lesperados)+", quantidade de argumentos recebidos: "+str(lrecebidos))
			exit(1)

		for i in range(len(argslista)):
			if(argslista[i]!=args_esperados[i]):
				print("Erro: Argumento "+str(i)+", tipo esperado "+args_esperados[i]+", tipo recebido "+ argslista[i])
				exit(1)
		self.simbolos[node.value][3]=True
		return self.simbolos[node.value][4]


	def lista_argumentos(self, node):
	 	if(len(node.child)==1):
	 		if(node.child[0]==None):
	 			return 
	 		if(node.child[0].type=="expressao"):
	 			return (self.expressao(node.child[0]))


	 		else:
	 			return []
	 	else:
	 		ret_args = []
	 		ret_args.append(self.lista_argumentos(node.child[0]))
	 		if(not(type(ret_args[0]) is str)):
	 			ret_args = ret_args[0]

	 		ret_args.append(self.expressao(node.child[1]))
	 		return ret_args


	def verifica_main(self, simbolos):
	 	if("principal" not in simbolos.keys()):
	 		print("Erro: função principal não declarada")
	 		exit(1)


	def verifica_funcoes(self, simbolos):
		for(k,v) in simbolos.items():
			if(v[0] == "funcao" and k!="principal"):
				if(v[5]!=1):
					print("Warning: Funcao '"+k+"' nunca utilizada")


	def verifica_utilizadas(self, simbolos):
		for k,v in simbolos.items():
			if(v[0]=="variavel"):
				if(v[2]==False):
					escopo=k.split("-")
					if(escopo[0]!= "global"):
						print("Warning: Variavel '"+v[1]+"' da função '"+escopo[0]+"' nunca é utilizada")
					else:
						print("Warning: Variavel '"+v[1]+"' nunca é utilizada")

def print_tree(node, level="-"):
    if node != None:
        print("%s %s %s" %(level, node.type, node.value))
        for son in node.child:
            print_tree(son, level+"-")


if __name__ == '__main__':
	import sys
	code = open(sys.argv[1])
	s = Semantica(code.read())
#	print_tree(s.tree)
	pprint.pprint(s.simbolos, depth=3, width=300)
    # print (s.parser.tokens)

    # print("Tabela de Simbolos:", s.table)
    # print_funcoes(s.table)

