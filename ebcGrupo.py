class ebc_criteria(osv.osv):
    def puntuacion(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        _logger.debug("Puntuacion de criterio %s", res)
        for r in self.browse(cr, uid, ids, context=context):
            res[r.id] = math.ceil(r.max_valoracion * r.cumplimiento / 100)
        return res

    def max_valoracion(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        # Creamos un diccionario "modelo" para los valores de retorno
        # a cada 'Indicador' le asignamos 0.0 por defecto
        res = dict(((x, 0.0) for x in ids))

        # Iteramos sobre los distintos 'indicadores'
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