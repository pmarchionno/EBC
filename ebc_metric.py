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
from openerp import tools
import math

#Importamos la libreria logger
import logging
import pdb
#Definimos la Variable Global
_logger = logging.getLogger(__name__)


class attributes_ebc(osv.osv):
    _name = "attributes.ebc"
    _description = "Atributes"
    _auto = False
    _columns = {
        'name': fields.char('Nombre', size=256, readonly=True, relate=True, help="Nombre del Atributo"),
		'attribute_id': fields.one2many('metric', 'attribute_id', 'Atributo'),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'attributes_ebc')
        cr.execute("""
            create or replace view attributes_ebc as (
               select
			        eg.id as id,
                    eg.name as name
                from
                    ebc_groups eg
			   union
			   select
                    ei.id + 1000 as id,
                    ei.name as name
                from
                    ebc_indicators ei
			   union
			   select
                    ec.id + 2000 as id,
                    ec.name as name
                from
                    ebc_criteria ec
                )
        """)
attributes_ebc()

class metric_views(osv.osv):
    _name = "metric.views"
    _description = "Metricas"
    _auto = False
    _columns = {
        'name': fields.char('Nombre', size=256, readonly=True, relate=True, help="Nombre de la Metrica"),
		'metric_id': fields.one2many('metric', 'metric_ids', 'Metrica'),
#		'metric_ids': fields.many2many("metric.views", "metric_rel", "id", "id", "Dependiencias"),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'metric_views')
        cr.execute("""
            create or replace view metric_views as (
               select
			        m.id as id,
                    m.name as name
                from
                    metric m
			    )
        """)
metric_views()

class metric(osv.osv):
    _name = 'metric'
    _description = "Formulario Metricas"
	
    _columns = {
        'name': fields.char('Nombre', size=256, required=True, help="Nombre de la Metrica"),
        'objective': fields.char('Objectivo', size=256, help='Objectivo'),
        'references': fields.char('Referencias', size=256, help='References'),
        'accuracy': fields.char('Precision', size=256, help = 'Accuracy'),
        'author': fields.char('Autor', size=256, help = 'Accuracy'),
        'version': fields.char('Version', size=256, help = 'Accuracy'),
		'valueInterpretation': fields.char('Valor', size=1000, help="Descripcion de cómo interpretar los valores generados por la métrica"),
        'attribute_id': fields.many2one('attributes.ebc', 'Atributo', select=True),
        'scale_id': fields.many2one('scale', 'Escala', select=True),
        'measurement': fields.many2one('measurement', 'Medida', select=True),
		'metric_ids': fields.many2many("metric.views", "metric_rel", "metric_id", "id", "Dependiencias"),
		'method_id': fields.one2many('method', 'metric_id', 'Metodo'),
        'measurement_id': fields.one2many('measurement', 'metric_id', 'Metodo'),

    } 
metric()

class indirectMetric(osv.osv):
    _name = 'metric'
    _inherit = 'metric'

indirectMetric()

class directMetric(osv.osv):
    _name = 'metric'
    _inherit = 'metric'
directMetric()

class scale(osv.osv):
    """Escalas """
    _name = 'scale'
    _description = "Escalas"
    _columns = {
	    'name': fields.char('Nombre', size=256, help="Nombre de la Escala"),
        'scaleType': fields.selection((('n', 'Nominal'),('ro', 'Restricted Ordinal'),('uro', 'Unrestricted Ordinal'),('i', 'Interval'),('r', 'Ratio'),('ab', 'Absolute')), 'Tipo de Escala', required=True),
        'valueType': fields.selection((('s', 'Symbol'),('i', 'Integer'),('f', 'Float'),('v','Valor')), 'Tipo de Valor', required=True),
    }
scale()

class method(osv.osv):
    """Metodo"""
    _name = 'method'
    _columns = {
        'name': fields.char('Nombre', size=256, required=True, help="Nombre del Metodo"),
        'especification': fields.char('Especificacion', size=256, required=True, help="Especificacion"),
        'references': fields.char('Referencias', size=256, required=True, help="Referencias"),
		'metric_id': fields.many2one('metric', 'Metrica', select=True),
    }
method()

class measurementMethod(osv.osv):
    """Measurement Method"""
    _name = 'method'
    _inherit = 'method'
measurementMethod()

class calculationMethod(osv.osv):
    """Calculation Method"""
    _name = 'method'
    _inherit = 'method'
calculationMethod()

class measurement(osv.osv):
    """Measurement"""
    _name = 'measurement'
    _columns = {
        'timeStamp': fields.char('Hora', size=256, required=True, help="Nombre del Metodo"),
        'dataCollectorName': fields.char('Coleccion', size=256, required=True, help="Especificacion"),
        'collectorContactInfo': fields.char('Contacto', size=256, required=True, help="Referencias"),
        'metric_id': fields.many2one('metric', 'Metrica', select=True),
    }
measurement()

class measure(osv.osv):
    """Calculation Method"""
    _name = 'measurement'
    _inherit = 'measurement'
    _columns = {
        'valueInterpretation': fields.float('Valor', type='float', required=True, help="Interpretacion"),
    }
measure()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
