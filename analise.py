	# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# lexer.py
# Analisador léxico para a linguagem T++
# Autores: Emanuel
#-------------------------------------------------------------------------

import ply.lex as lex

class Lexer:

    def __init__(self):
        self.lexer = lex.lex(debug=False, module=self, optimize=False)

    keywords = {
        u'se': 'IF',
        u'então': 'THEN',
        u'senão': 'ELSE',
        u'fim': 'END',
        u'repita': 'REPEAT',
        u'flutuante': 'FLOAT',
        u'retorna' : 'RETURN',
        u'até': 'UNTIL',
        u'leia': 'READ',
        u'escreve': 'WRITE',
        u'inteiro': 'INT',
    }

    tokens = ['EQ', 'DIF', 'GE', 'GT', 'LE', 'LT', 'ADD', 'SUB', 'MUL', 'DIV',
              'ID', 'NUM', 'LPAR', 'RPAR', 'COMMA', 'ATR', 'POINT', 'LCOLC', 'RCOLC'] + list(keywords.values())

    t_EQ = r'='
    t_DIF = r'<>'
    t_GE = r'>='
    t_GT = r'>'
    t_LE = r'<='
    t_LT = r'<'
    t_ATR = r':='
    t_POINT = r':'
    t_ADD = r'\+'
    t_SUB = r'\-'
    t_MUL = r'\*'
    t_DIV = r'/'
    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_RCOLC = r'\]'
    t_LCOLC	= r'\['
    t_COMMA = r','
    t_NUM = r'(\+|\-)?([0-9]+(\.[0-9]+)?e(\+|\-)?[0-9]+(\.[0-9]+)?)|([0-9]+(\.[0-9]+)?)'

    def t_ID(self, t):
         r'[a-zA-Zá-ñÁ-Ñà-źÀ-Ź][_a-zA-Zá-ñÁ-Ñà-źÀ-Ź0-9]*'
         t.type = self.keywords.get(t.value, 'ID')
         return t

    def t_COMMENT(self, t):
         r'\{[^}]*\}'

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore = ' \t'

    def t_error(self, t):
        print("Item ilegal: '%s', linha %d, coluna %d" % (t.value[0],
                                                          t.lineno, t.lexpos))
        t.lexer.skip(1)

    def test(self, code):
        lex.input(code)
        while True:
            t = lex.token()
            if not t:
                break
            print(t)

if __name__ == '__main__':
    from sys import argv
    lexer = Lexer()
    f = open(argv[1])
    lexer.test(f.read())