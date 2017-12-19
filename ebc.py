# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models
from openerp.osv import fields, osv, orm
from datetime import time, datetime
from openerp.tools.translate import _
from openerp.addons.edi import EDIMixin
import math

#Importamos la libreria logger
import logging
import pdb
#Definimos la Variable Global
_logger = logging.getLogger(__name__)

class ebc_groups(osv.osv):

    def max_valoracion(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)

        # Creamos un diccionario "modelo" para los valores de retorno
        # a cada 'Grupo' le asignamos 0.0 por defecto
        res = dict(((x, 0.0) for x in ids))

        # Iteramos sobre los distintos 'Grupos'
        for grupo in self.browse(cr, uid, ids, context=context):
            for indicador in grupo.indicador_ids:
                # vamos acumulando por cada 'Indicador'
                # que tenga asociado (esto lo buscamos en el campo "indicador_ids")
                # el campo 'max_valoracion' del indicador
                res[grupo.id] += indicador.max_valoracion
        return res

    def puntuacion(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)

        res = dict(((x, 0.0) for x in ids))

        for grupo in self.browse(cr, uid, ids, context=context):
            for indicador in grupo.indicador_ids:
                res[grupo.id] += indicador.puntuacion
                _logger.info("Mensaje Informativo o Print Inicio %s", indicador.puntuacion)
        return res

    def cumplimiento(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            if (r.max_valoracion != 0 ):
                res[r.id] = math.ceil(r.puntuacion * 100 / r.max_valoracion )
            else:
                res[r.id] = 0
        return res

    _name = 'ebc.groups'
    _description = "Formulario de la EBC - Grupos"
    _columns = {
        'name': fields.char('Nombre', size=256, required=True, help="Nombre del Grupo"),
        'denomination': fields.char('Denominacion', size=5000, required=True, help="Denominacion del Grupo"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Año Fiscal'),
        'cumplimiento': fields.function(cumplimiento, type='float', string='Cumplimiento'),
        'puntuacion': fields.function (puntuacion, type = 'float', string = 'Puntuacion'),
        'max_valoracion': fields.function (max_valoracion, type = 'float', string = 'Máxima Valoracion'),
        'note': fields.text('Nota', translate=True),
        # El campo que sigue nos permite "acceder", dado un grupo
        # a todos aquellos criterios que tengan en el campo 'ebc_indicators_id' relacionado al indicador en cuestion
        # es el opuesto al campo many2one
        'indicador_ids': fields.one2many('ebc.indicators', 'ebc_groups_id','Grupos Asociados'),
    }
ebc_groups()

class ebc_indicators(osv.osv):
    def max_valoracion(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            res[r.id] = r.valoracion_base #Falta mejorar y saber si la empresa es o no unipersonal
        return res

    def puntuacion(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        res = dict(((x, 0.0) for x in ids))

        for indicador in self.browse(cr, uid, ids, context=context):
            for criterio in indicador.criterio_ids:
                res[indicador.id] += criterio.puntuacion
        return res

    def cumplimiento(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            if (r.max_valoracion != 0 ):
                res[r.id] = math.ceil(r.puntuacion * 100 / r.max_valoracion ) #Falta mejorar y saber si la empresa es o no unipersonal
            else:
                res[r.id] = 0
        return res

    """Indicadores """
    _name = 'ebc.indicators'
    _description = "Formulario de la EBC - Indicadores"
    _columns = {
        'name': fields.char('Nombre', size=256, required=True, help="Nombre del Identificador"),
        'ebc_groups_id': fields.many2one('ebc.groups', 'Grupo'),
        'denomination': fields.char('Denominacion', size=5000, required=True, help="Denominacion del Identificador"),
        'ponderacion': fields.integer('Ponderacion'),
        'cumplimiento': fields.function(cumplimiento, type='float', string='Cumplimiento'),
        'puntuacion': fields.function(puntuacion, type='float', string='Puntuacion'),
        'max_valoracion': fields.function(max_valoracion, type='integer', string='Máxima Valoracion'),
        'valoracion_base': fields.integer('Valoracion Base'),
        'criterio_ids': fields.one2many('ebc.criteria', 'ebc_indicators_id','Criterios Asociados'),
    }
ebc_indicators()

class ebc_criteria(osv.osv):
    def puntuacion(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        _logger.debug("Puntuacion de criterio %s", res)
        for r in self.browse(cr, uid, ids, context=context):
            res[r.id] = math.ceil(r.max_valoracion * r.cumplimiento / 100)
        return res

    def max_valoracion(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        res = dict(((x, 0.0) for x in ids))

        for r in self.browse(cr, uid, ids, context=context):
            total = 1
            for criterio in r.ebc_indicators_id:
                total = criterio.max_valoracion
            res[r.id] = math.ceil(r.ponderacion * total / 100)
        return res

    """Criterios"""
    _name = 'ebc.criteria'
    _columns = {
        'name': fields.char('Nombre', size=256, required=True, help="Nombre del Criterio"),
        'ebc_indicators_id': fields.many2one('ebc.indicators', 'Indicador', select=True),
        'denomination': fields.char('Denominacion', size=5000, required=False),
        'ponderacion': fields.integer('Ponderacion'),
        'cumplimiento': fields.integer('Cumplimiento'),
        'puntuacion': fields.function (puntuacion, type = 'float', string = 'Puntuacion'),
        'max_valoracion': fields.function(max_valoracion, type='float', string='Máxima Valoracion'),
    }
ebc_criteria()


class ebc_repositorio(osv.osv):
    """Repositorio"""
    _name = 'ebc.repositorio'

    _columns = {
        'account_id': fields.many2one('account.account', 'Cuenta Contable', required=True),
		'amount': fields.float('Importe'),
        'amount_total': fields.float('Total Comprobante'),
        'partner_id': fields.many2one('res.partner', 'Entidad Comercial'),
        'date_invoice': fields.date('Fecha de Comprobante'),
        'date_due': fields.date('Fecha de Vencimiento'),
    }
ebc_repositorio()

class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'
    _columns = {
        'cumpl_ebc': fields.integer('Cumplimiento Norma EBC'),
    }
    _default = {

    }
product_template()

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'cumpl_ebc': fields.integer('Cumplimiento Norma EBC'),
    }
    _default = {

    }
res_partner()

#class res_partner_bank(osv.osv):
#    _name = 'res.partner.bank'
#    _inherit = 'res.partner.bank'
#    _columns = {
#        'cumpl_ebc': fields.integer('Cumplimiento Norma EBC'),
#    }
#    _default = {
#
#    }
#res_partner_bank()

class bank(osv.osv):
    _name = 'res.partner.bank'
    _inherit = 'res.partner.bank'
    _columns = {
        'cumpl_ebc': fields.integer('Cumplimiento Norma EBC'),
    }
    _default = {

    }
bank()

class purchase_order(osv.osv):
    def cumpl_ebc(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        res = dict(((x, 0.0) for x in ids))

        for r in self.browse(cr, uid, ids, context=context):
            total = 1
            for partner in r.partner_id:
                total = partner.cumpl_ebc
            res[r.id] = total
        return res

    _name = 'purchase.order'
    _inherit = 'purchase.order'

    _columns = {
        'cumpl_ebc': fields.function(cumpl_ebc, type='float', string='EBC'),
    }
    _default = {

    }
purchase_order()

class ebc_cuentas_pagos_proveedores(osv.osv):
    _name = 'ebc.cuentas.pagos.proveedores'

    _columns = {
        'account_id': fields.many2one('account.account', 'Cuenta Contable', required=True),
    }
ebc_cuentas_pagos_proveedores()


class ebc_cuentas_aporte_a_bancas(osv.osv):
    _name = 'ebc.cuentas.interese.renunciados'

    _columns = {
        'account_id': fields.many2one('account.account', 'Cuenta Contable', required=True),
    }
ebc_cuentas_aporte_a_bancas()

class ebc_cuentas_inversion_social(osv.osv):
    _name = 'ebc.cuentas.inversiones.soceco'

    _columns = {
        'account_id': fields.many2one('account.account', 'Cuenta Contable', required=True),
    }
ebc_cuentas_inversion_social()



class account_account(models.Model):
    _name = 'account.account'
    _inherit = 'account.account'
    _columns = {
        'cumpl_ebc': fields.boolean('Valoración EBC'),
    }
account_account()

class account_invoice(osv.osv, EDIMixin):
    def cumpl_ebc(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        res = dict(((x, 0.0) for x in ids))

        for r in self.browse(cr, uid, ids, context=context):
            total = 1
            for partner in r.partner_id:
                total = partner.cumpl_ebc
            res[r.id] = total
        return res

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'cumpl_ebc': fields.function(cumpl_ebc, type='float', string='EBC'),
    }
account_account()

class account_invoice_decorador(object):

    def __init__(self, f):
        """
        """
        _logger.debug("Inicializacion: __init__")
        print "__init__()"
        self._f = f    #guardo la referencia
        super(account_invoice_decorador, self).__init__()

    def __call__(self, *args, **kwargs):
        """ Acá va a entrar en cada llamado a una función decorada.
            Dado que se están decorando funciones de Odoo, sabemos que
            en *args van a venir: cr, uid, ids (este último podría no venir,
            depende si la función original que se decora lo tenía o no)
        """
        _logger.debug("Call: __call__")
        if len(args) == 2:
            cr, uid = args[0:2] # saco los argumentos especiales
            args = [] # ya no quedan más argumentos
            ids = []
        elif len(args) >= 3:
            cr, uid, ids = args[0:3] # saco los argumentos especiales
            args = args[3:] # puede que queden argumentos, esos los mantenemos
        else:
            print "pasó algo extraño, la función que se decoró no tenía los argumentos usuales..."

        if self.precondiciones(cr, uid, ids, *args, **kwargs):
            self.funcion_central(cr, uid, ids, *args, **kwargs)

        initial_time = time.time() # para medir tiempo de ejecución

        resultado_original = self._f(cr, uid, ids, *args, **kwargs)    #ejecuto la funcion
        elapsed_time = time.time() - initial_time   # tiempo que llevó la ejecución de la función

        if self.postcondiciones(cr, uid, ids, resultado_original, *args, **kwargs):
            resultado_modificado = self.modificar_resultado(cr, uid, ids, resultado_original, *args, **kwargs)
        else:
            resultado_modificado = resultado_original
        return resultado_modificado

    def precondiciones(self, cr, uid, ids, *args, **kwargs):
        """ Evalúa las precondiciones bajo las cuales debe ejecutarse
        la función central del decorador
        """
        return self.valoracion_ebc # En este caso la precondición siempre devolverá True, hay que ver qué lógica debería llevar y devolver True/False según corresponda

    def postcondiciones(self, cr, uid, ids, resultado_original, *args, **kwargs):
        """ Evalúa las postcondiciones bajo las cuales debe ejecutarse
            modificarse el valor original devuelto
        """
        return True # En este caso la postcondición siempre devolverá True, hay que ver qué lógica debería llevar y devolver True/False según corresponda

    def modificar_resultado(self, cr, uid, ids, resultado_original, *args, **kwargs):
        """ En esta caso, si se desea, se puede modificar el valor devuelto originalmente
        """
        # Por ejemplo, si se devolvía un número, puedo multiplicarlo por 2
        # resultado_modificado = resultado_original * 2
        resultado_modificado = resultado_original # en este caso no estoy haciendo nada, lo devuelvo tal cual
        return resultado_modificado

    def funcion_central(self, cr, uid, ids, *args, **kwargs):
        """ En esta función es donde se esconde el corazón del decorador
        aquí se pueden realizar las escrituras a la DB, guardar cosas en algún
        archivo o darle el funcionamiento que se desee
        """
        # cr.execute("INSERT INTO tabla_de_logs (ids,mensaje) VALUES (%s,'Se está llamando a la función central de ebcDecorator')",(ids,))
        # print "Llamando a la función central del decorador ebcDecorator"
        # lo que se desee hacer en el decorador...


        #for r in self.browse(cr, uid, ids, context=context):
            # if (r.max_valoracion != 0 ):
                # res[r.id] = math.ceil(r.puntuacion * 100 / r.max_valoracion ) #Falta mejorar y saber si la empresa es o no unipersonal
            # else:
                # res[r.id] = 0

        _logger.info("Estoy en la funcion central que quiero")
        #self.env.cr.execute("DELETE from account_invoice_summary where invoice_id = %d" % (self.id))
        self.env.cr.execute('INSERT INTO ebc_repositorio( account_id, amount_untaxed, date_invoice, amount_total, commercial_partner_id, date_due, partner_id, amount_untaxed )'
                                ' SELECT account_id, amount_untaxed, date_invoice, amount_total, commercial_partner_id, date_due, partner_id, amount_untaxed FROM account_invoice, account_account '
                                ' where account_invoice.account_id = account_account.code and account_account.valoracion_ebc = True and account_invoice.id  = %d' % (self.id))

        return super(account_invoice_decorador, self).funcion_central(cr, uid, ids, *args, **kwargs)

class account_invoice(models.Model):
    _name = "account.invoice"
    _inherit = 'account.invoice'

    @account_invoice_decorador
    def action_move(self, cr, uid, ids, *args, **kwargs):
        """
            La función no posee lógica especial, solo la
            sobreescribimos para poder decorarla. La lógica de
            registro o toma de decisión se hará en el decorador.
        """
        return super(account_invoice, self).action_move_create(cr, uid, ids, *args, **kwargs)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
