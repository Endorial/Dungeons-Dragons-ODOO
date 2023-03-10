from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)
from datetime import datetime
import random

class Personaje(models.Model):

    _name = "personaje"
    
    name = fields.Char(string="Sobrenombre")
    raza = fields.Selection(selection=[('humano', 'Humano'), ('elfo', 'Elfo'), ('enano', 'Enano'), ('semielfo', 'Semielfo'), ('semiorco', 'Semiorco'), ('gnomo', 'Gnomo'), ('mediano', 'Mediano')], required=True)
    clase = fields.Selection(selection=[('barbaro', 'Bárbaro'), ('bardo', 'bardo'), ('clerigo', 'clérigo'), ('druida', 'druida'), ('explorador', 'explorador'), ('guerrero', 'guerrero'), ('hechicero', 'hechicero'), ('mago', 'mago'), ('monje', 'monje'), ('paladin', 'paladín'), ('picaro', 'pícaro')], required=True)
    fuerza = fields.Integer(string="Fuerza (FUE)", default=0)
    destreza = fields.Integer(string="Destreza (DES)", default=0)
    constitucion = fields.Integer(string="Constitución (CON)", default=0)
    inteligencia = fields.Integer(string="Inteligencia (INT)", default=0)
    sabiduria = fields.Integer(string="Sabiduría (SAB)", default=0)
    carisma = fields.Integer(string="Carisma (CAR)", default=0)
    ataque = fields.Integer(string="Ataque", default=0)
    salvacion_fortaleza = fields.Integer(string="Salvación fortaleza", default=0)
    salvacion_reflejos = fields.Integer(string="Salvación reflejos", default=0)
    salvacion_voluntad = fields.Integer(string="Salvación voluntad", default=0)
    vida = fields.Integer(string="Vida", default=0)

    def calcular_vida(self):
        modificadores = self.get_modificadores()
        # We keep the faces of the die of each class to know what possible life score the character will have

        caras_dado = {
            'barbaro' : 12,
            'bardo' : 6,
            'clerigo' : 8,
            'druida' : 8,
            'explorador' : 8,
            'guerrero' : 10,
            'hechicero' : 4,
            'mago' : 4,
            'monje' : 8,
            'paladin' : 10,
            'picaro' : 6
        }
        # We load the constitution modifier
        modificador_constitucion = modificadores[str(self.constitucion)]
        # If it is less than zero, we don't subtract anything
        if modificador_constitucion < 0:
            modificador_constitucion = 0
        # We add the points of the die plus the constitution modifier
        self.vida = random.randint(1, caras_dado[self.clase]) + modificador_constitucion

    def calcular_salvacion(self):
        # We load the modifiers and the main ability of the character
        modificadores = self.get_modificadores()
        habilidad_principal = self.get_habilidad_principal()
        # We calculate the points of the character's main ability
        puntos_habilidad_principal = self[habilidad_principal[self.clase]]
        # We calculate the attack points to add based on the modifier
        puntos_modificador = modificadores[str(puntos_habilidad_principal)]
        suma_ataque = self.get_ataque()
        
        # And we keep the points that are added for strength of each class
        suma_fortaleza = {
            'barbaro' : 2,
            'bardo' : 0,
            'clerigo' : 2,
            'druida' : 2,
            'explorador' : 2,
            'guerrero' : 2,
            'hechicero' : 0,
            'mago' : 0,
            'monje' : 2,
            'paladin' : 2,
            'picaro' : 0
        }
        self.salvacion_fortaleza = suma_ataque[self.clase] + puntos_modificador + suma_fortaleza[self.clase]

        # And we keep the points that are added from reflexes of each class
        suma_reflejos = {
            'barbaro' : 0,
            'bardo' : 2,
            'clerigo' : 0,
            'druida' : 0,
            'explorador' : 2,
            'guerrero' : 0,
            'hechicero' : 0,
            'mago' : 0,
            'monje' : 2,
            'paladin' : 0,
            'picaro' : 2
        }
        self.salvacion_reflejos = suma_ataque[self.clase] + puntos_modificador + suma_reflejos[self.clase]
        
        # And we keep the points that are added of will of each class
        suma_voluntad = {
            'barbaro' : 0,
            'bardo' : 2,
            'clerigo' : 2,
            'druida' : 2,
            'explorador' : 0,
            'guerrero' : 0,
            'hechicero' : 2,
            'mago' : 2,
            'monje' : 2,
            'paladin' : 0,
            'picaro' : 0
        }
        self.salvacion_voluntad = suma_ataque[self.clase] + puntos_modificador + suma_voluntad[self.clase]

    def calcular_ataque(self):
        modificadores = self.get_modificadores()
        habilidad_principal = self.get_habilidad_principal()
        suma_ataque = self.get_ataque()
        # We calculate the points of the character's main ability
        puntos_habilidad_principal = self[habilidad_principal[self.clase]]
        # We calculate the attack points to add based on the modifier
        self.ataque = modificadores[str(puntos_habilidad_principal)] + puntos_habilidad_principal
        # We calculate the attack points to add based on your class
        self.ataque = self.ataque + suma_ataque[self.clase]
        
    def calcular_atributos(self):
        atributos = []
        # We roll 7 rolls of 4 dice with 6 faces each
        for i in range(1,8):
            dado1 = random.randint(1,6)
            dado2 = random.randint(1,6)
            dado3 = random.randint(1,6)
            dado4 = random.randint(1,6)
            #We add the data by eliminating the smallest
            dados = self.sumar_dados(dado1, dado2, dado3, dado4)
            atributos.append(dados)
            
        # We assign the points to each attribute
        self.write({
            'fuerza': atributos[0],
            'destreza': atributos[1],
            'constitucion': atributos[2],
            'inteligencia': atributos[3],
            'sabiduria': atributos[4],
            'carisma': atributos[5]
        })
        self.actualizar_puntos_por_raza()
        self.generar_sobrenombre()

    def generar_sobrenombre(self):
        # We save possible nicknames by race
        nombres_por_raza = {
            'humano' : ['el hijo del herrero', 'el hijo del posadero', 'el huérfano', 'el vagabundo', 'el extranjero'],
            'elfo' : ['orejas picudas', 'el estirado', 'el silvano', 'el eterno', 'de las montañas nubladas'],
            'enano' : ['de las montañas azules', 'el minero', 'barba roja', 'hijo de la montaña', 'el bajo'],
            'semielfo' : ['el barbudo', 'el bastardo', 'de las nieves', 'sin tierra', 'el sintecho'],
            'semiorco' : ['machacacráneos', 'Hachachunga', 'Puño’ierro', 'el orco', 'el paria de Mordor'],
            'gnomo' : ['el loco', 'Gnometoques', 'el pequeño', 'el hijo del joyero', 'Kabum'],
            'mediano' : ['el medio-hombre', 'el Hobbit', 'de la Comarca', 'el fumador en pipa', 'el hijo del molinero'],
        }
        # We save the possible nicknames by attribute greater than 18
        nombres_por_atributo_18 = {
            'fuerza' : ['el fuerte', 'el herrero', 'el bocadillo de nudillos'],
            'destreza' : ['el ágil', 'el rápido', 'el ojo del halcón'],
            'constitucion' : ['el gordo', 'la roca', 'la piedra del molino'],
            'inteligencia' : ['el listo', 'el inteligente', 'Fistandantilus'],
            'sabiduria' : ['el sabio', 'el vividor', 'el conocedor de secretos'],
            'carisma' : ['el guapo', 'el imponente', 'pico de oro'],
        }
        # We save the possible nicknames by attribute less than 5
        nombres_por_atributo_5 = {
            'fuerza': ['el flojo', 'caricias', 'dedos de papel'],
            'destreza' : ['el torpe', 'el lento', 'manos de mantequilla'],
            'constitucion' : ['el casi-inconsciente', 'el fofo', 'el flan'],
            'inteligencia' : ['el tonto', 'el incoherente', 'el corto de miras'],
            'sabiduria' : ['el ignorante', 'el perdido', 'no-sabe-ni-contesta'],
            'carisma' : ['el feo', 'cara-de-pez', 'el difícil de mirar'],
        }
        posibles_nombres = nombres_por_raza[self.raza]
        #Added possible names based on race and attribute points
        if self.fuerza >= 18:
            posibles_nombres += nombres_por_atributo_18['fuerza']
        if self.destreza >= 18:
            posibles_nombres += nombres_por_atributo_18['destreza']
        if self.constitucion >= 18:
            posibles_nombres += nombres_por_atributo_18['constitucion']
        if self.inteligencia >= 18:
            posibles_nombres += nombres_por_atributo_18['inteligencia']
        if self.sabiduria >= 18:
            posibles_nombres += nombres_por_atributo_18['sabiduria']
        if self.carisma >= 18:
            posibles_nombres += nombres_por_atributo_18['carisma']

        if self.fuerza <= 5:
            posibles_nombres += nombres_por_atributo_5['fuerza']
        if self.destreza <= 5:
            posibles_nombres += nombres_por_atributo_5['destreza']
        if self.constitucion <= 5:
            posibles_nombres += nombres_por_atributo_5['constitucion']
        if self.inteligencia <= 5:
            posibles_nombres += nombres_por_atributo_5['inteligencia']
        if self.sabiduria <= 5:
            posibles_nombres += nombres_por_atributo_5['sabiduria']
        if self.carisma <= 5:
            posibles_nombres += nombres_por_atributo_5['carisma']
        
        # We take a random name
        self.name = posibles_nombres[random.randint(0, len(posibles_nombres) - 1)]

    def actualizar_puntos_por_raza(self):
        # Depending on the character's race, we add some points
        raza = self.raza
        if raza == 'elfo':
            self.write({
                'destreza' : self.destreza + 2,
                'constitucion' : self.constitucion - 2
            })
        if raza == 'enano':
            self.write({
                'carisma' : self.carisma - 2,
                'constitucion' : self.constitucion + 2
            })
        if raza == 'semiorco':
            self.write({
                'fuerza' : self.fuerza + 2,
                'carisma' : self.carisma - 2,
                'inteligencia': self.inteligencia - 2
            })
            if self.inteligencia < 3:
                self.write({'inteligencia' : 3})
        if raza == 'gnomo':
            self.write({
                'fuerza' : self.fuerza - 2,
                'constitucion' : self.constitucion + 2
            })
        if raza == 'mediano':
            self.write({
                'fuerza' : self.fuerza - 2,
                'destreza' : self.destreza + 2
            })

    def sumar_dados(self, dado1, dado2, dado3, dado4):
        menor = 999
        if dado1 < menor:
            menor = dado1
        if dado2 < menor:
            menor = dado2
        if dado3 < menor:
            menor = dado3
        if dado4 < menor:
            menor = dado4
        return (dado1 + dado2 + dado3 + dado4) - menor

    def get_ataque(self):
        # And we keep the points that add to the attack of each class
        suma_ataque = {
            'barbaro' : 1,
            'bardo' : 0,
            'clerigo' : 0,
            'druida' : 0,
            'explorador' : 1,
            'guerrero' : 1,
            'hechicero' : 0,
            'mago' : 0,
            'monje' : 0,
            'paladin' : 1,
            'picaro' : 0
        }
        return suma_ataque

    def get_habilidad_principal(self):
        # We saved the main ability of each character class
        habilidad_principal = {
            'barbaro' : 'fuerza',
            'bardo' : 'carisma',
            'clerigo' : 'sabiduria',
            'druida' : 'sabiduria',
            'explorador' : 'destreza',
            'guerrero' : 'fuerza',
            'hechicero' : 'carisma',
            'mago' : 'inteligencia',
            'monje' : 'sabiduria',
            'paladin' : 'carisma',
            'picaro' : 'destreza'
        }
        return habilidad_principal

    def get_modificadores(self):
        # We save in a dictionary the modifiers based on the score of the attributes
        modificadores = {
            "0" : -5,
            "1" : -5,
            "2" : -4,
            "3" : -4,
            "4" : -3,
            "5" : -3,
            "6" : -2,
            "7" : -2,
            "8" : -1,
            "9" : -1,
            "10" : 0,
            "11" : 0,
            "12" : 1,
            "13" : 1,
            "14" : 2,
            "15" : 2,
            "16" : 3,
            "17" : 3,
            "18" : 4,
            "19" : 4,
            "20" : 5,
            "21" : 5
        }
        return modificadores
            
