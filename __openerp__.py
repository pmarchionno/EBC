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
#    Code by: pmarchionno email: (pmarchionno@gmail.com)
#
##############################################################################


{
    'name' : 'ECONOMIA DEL BIEN COMUN',
    'version' : '1',
    'author' : 'Pablo Damian Marchionno',
    'category' : 'EBC',
    'description' : """
            EBC - Administracion.
                        """,
    'website': 'pmarchionno.blogspot.com',
    'depends' : ['base','account'],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [
                    "ebc_view.xml",
                    "ebc_metric_view.xml",
                    ],
    'data': [ 'data/ebc_datag.xml',
              'data/ebc_datai.xml',
              'data/ebc_datac.xml',
              'data/scale.xml',
              'data/metricr2.xml',
              'data/metricr1.xml',
              'data/metricr0.xml',
              ],
    'installable': True,
    #'auto_install': False,
    'active': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
