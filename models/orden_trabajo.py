# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
import logging

class OrdenTrabajo(models.Model):
    _name = 'orden.trabajo'

    def _buscar_lote_por_largo(self, product_id, largo):
        lote = self.env['stock.production.lot'].search([('product_id', '=', product_id),('largo', '=', largo)])
        if lote:
            return lote[0]
        else:
            return False
    
    def confirmar(self):
        if not self.sale_id.partner_id.property_stock_customer:
            raise UserError('El contacto no tiene ubicación de cliente definida.')

        for linea in self.corte_ids:
            if linea.total > linea.lote_id.largo:
                raise UserError(_('La suma de los cortes no puede ser mayor que el largo del panel'))

        productos = {}
        lineas_albaran_salida = []
        lote_ids = []
        for linea in self.corte_ids:
            lineas_albaran_salida.append((0, 0, {
                'name': '/',
                'product_id': linea.lote_id.product_id.id,
                'product_uom': linea.lote_id.product_id.uom_id.id,
                'product_uom_qty': linea.product_qty,
                'location_id': self.sale_id.warehouse_id.lot_stock_id.id,
                'location_dest_id': linea.lote_id.product_id.property_stock_production.id,
                'state': 'draft',
            }))
            lote_ids.append({'id': linea.lote_id.id, 'qty': linea.product_qty})

            if linea.lote_id.product_id.id not in productos:
                productos[linea.lote_id.product_id.id] = {'ubicacion_produccion_id': linea.lote_id.product_id.property_stock_production.id, 'uom_id': linea.lote_id.product_id.uom_id.id, 'cortes': {}}

            corte = linea.corte1
            if corte != 0:
                if corte not in productos[linea.lote_id.product_id.id]['cortes']:
                    productos[linea.lote_id.product_id.id]['cortes'][corte] = {'precio': linea.lote_id.product_id.list_price, 'cantidad': 0, 'tipo': 'nuevo'}
                productos[linea.lote_id.product_id.id]['cortes'][corte]['cantidad'] += linea.product_qty

            corte = linea.corte2
            if corte != 0:
                if corte not in productos[linea.lote_id.product_id.id]['cortes']:
                    productos[linea.lote_id.product_id.id]['cortes'][corte] = {'precio': linea.lote_id.product_id.list_price, 'cantidad': 0, 'tipo': 'nuevo'}
                productos[linea.lote_id.product_id.id]['cortes'][corte]['cantidad'] += linea.product_qty

            corte = linea.corte3
            if corte != 0:
                if corte not in productos[linea.lote_id.product_id.id]['cortes']:
                    productos[linea.lote_id.product_id.id]['cortes'][corte] = {'precio': linea.lote_id.product_id.list_price, 'cantidad': 0, 'tipo': 'nuevo'}
                productos[linea.lote_id.product_id.id]['cortes'][corte]['cantidad'] += linea.product_qty

            corte = linea.corte4
            if corte != 0:
                if corte not in productos[linea.lote_id.product_id.id]['cortes']:
                    productos[linea.lote_id.product_id.id]['cortes'][corte] = {'precio': linea.lote_id.product_id.list_price, 'cantidad': 0, 'tipo': 'nuevo'}
                productos[linea.lote_id.product_id.id]['cortes'][corte]['cantidad'] += linea.product_qty

            corte = linea.corte5
            if corte != 0:
                if corte not in productos[linea.lote_id.product_id.id]['cortes']:
                    productos[linea.lote_id.product_id.id]['cortes'][corte] = {'precio': linea.lote_id.product_id.list_price, 'cantidad': 0, 'tipo': 'nuevo'}
                productos[linea.lote_id.product_id.id]['cortes'][corte]['cantidad'] += linea.product_qty

            corte = linea.corte6
            if corte != 0:
                if corte not in productos[linea.lote_id.product_id.id]['cortes']:
                    productos[linea.lote_id.product_id.id]['cortes'][corte] = {'precio': linea.lote_id.product_id.list_price, 'cantidad': 0, 'tipo': 'nuevo'}
                productos[linea.lote_id.product_id.id]['cortes'][corte]['cantidad'] += linea.product_qty

            corte = linea.sobra
            if corte != 0:
                if corte not in productos[linea.lote_id.product_id.id]['cortes']:
                    productos[linea.lote_id.product_id.id]['cortes'][corte] = {'precio': linea.lote_id.product_id.list_price, 'cantidad': 0, 'tipo': 'sobra'}
                productos[linea.lote_id.product_id.id]['cortes'][corte]['cantidad'] += linea.product_qty

        lineas_so = []
        lineas_albaran_entrada = []
        for product_id in productos:

            for corte in productos[product_id]['cortes']:

                if productos[product_id]['cortes'][corte]['tipo'] == 'nuevo':
                    lineas_so.append((0, 0, {
                        'name': linea.product_id.name_get()[0][1] + ' - ' + str(corte),
                        'product_id': product_id,
                        'price_unit': productos[product_id]['cortes'][corte]['precio'],
                        'product_uom_qty': productos[product_id]['cortes'][corte]['cantidad'],
                    }))

                lineas_albaran_entrada.append((0, 0, {
                    'name': '/',
                    'product_id': product_id,
                    'product_uom': productos[product_id]['uom_id'],
                    'product_uom_qty': productos[product_id]['cortes'][corte]['cantidad'],
                    'location_id': productos[product_id]['ubicacion_produccion_id'],
                    'location_dest_id': self.sale_id.partner_id.property_stock_customer.id,
                    'state': 'draft',
                }))

        if len(lineas_albaran_salida) > 0:
            albaran_salida = self.env['stock.picking'].create({
                'location_id': self.sale_id.warehouse_id.lot_stock_id.id,
                'location_dest_id': productos[product_id]['ubicacion_produccion_id'],
                'picking_type_id': self.stock_picking_type_id.id,
            })

            albaran_salida.move_lines = lineas_albaran_salida
            albaran_salida.action_confirm()
            albaran_salida.action_assign()
            x = 0
            for operation in albaran_salida.pack_operation_product_ids:
                existe_lot_id = False
                for pack_lot in operation.pack_lot_ids:
                    if pack_lot.lot_id.id == lote_ids[x]['id']:
                        pack_lot.qty = lote_ids[x]['qty']
                        existe_lot_id = True
                if not existe_lot_id:
                    operation.pack_lot_ids[0].lot_id = lote_ids[x]['id']
                    operation.pack_lot_ids[0].qty = lote_ids[x]['qty']
                operation.save()
                x += 1
            albaran_salida.do_new_transfer()


        if len(lineas_albaran_entrada) > 0:
            albaran_entrada = self.env['stock.picking'].create({
                'location_id': productos[product_id]['ubicacion_produccion_id'],
                'location_dest_id': self.sale_id.partner_id.property_stock_customer.id,
                'picking_type_id': self.stock_picking_type_id.id,
            })

            albaran_entrada.move_lines = lineas_albaran_entrada
#            albaran_entrada.action_confirm()

            secuencias_nombre = []
            secuencias_largo = {}
            for operation in albaran_entrada.pack_operation_product_ids:

                lineas_lote = []
                for corte in productos[operation.product_id.id]['cortes']:
                    lote = self._buscar_lote_por_largo(operation.product_id.id, corte)
                    if lote:
                        secuencia = lote.name
                        lineas_lote.append((0, 0, {
                            'lot_id': lote.id,
                            'qty': productos[operation.product_id.id]['cortes'][corte]['cantidad'],
                        }))
                    else:
                        secuencia = self.env['ir.sequence'].next_by_code('stock.lot.serial') + ' - ' + str(corte)
                        lineas_lote.append((0, 0, {
                            'lot_name': secuencia,
                            'qty': productos[operation.product_id.id]['cortes'][corte]['cantidad'],
                        }))
                    secuencias_nombre.append(secuencia)
                    secuencias_largo[secuencia] = corte
                operation.pack_lot_ids = lineas_lote
                operation.save()
            albaran_entrada.do_new_transfer()

            secuencias = self.env['stock.production.lot'].search([('name', 'in', secuencias_nombre)])
            for secuencia in secuencias:
                secuencia.largo = secuencias_largo[secuencia.name]

        for linea in self.moldura_panel_ids:
            lineas_so.append((0, 0, {
                'product_id': linea.product_id.id,
                'price_unit': linea.product_id.list_price,
                'product_uom_qty': linea.cantidad,
            }))

        for linea in self.tornilleria_accesorio_ids:
            lineas_so.append((0, 0, {
                'product_id': linea.product_id.id,
                'price_unit': linea.product_id.list_price,
                'product_uom_qty': linea.cantidad,
            }))

        self.sale_id.order_line = lineas_so
        self.state = 'confirm'

    def cancelar(self):
        self.state = 'draft'


    name = fields.Char("Nombre", required=True, default=lambda self: self.env['ir.sequence'].next_by_code('orden.trabajo.serial'))
    fecha = fields.Date('Fecha', required=True)
    sale_id = fields.Many2one("sale.order", string='Orden de venta', required=True)
    stock_picking_type_id = fields.Many2one("stock.picking.type", string='Tipo de albarán', required=True)
    corte_ids = fields.One2many('orden.trabajo.corte', 'orden_id', string='Cortes')
    moldura_panel_ids = fields.One2many('orden.trabajo.moldura_panel', 'orden_id', string='Molduras y paneles')
    tornilleria_accesorio_ids = fields.One2many('orden.trabajo.tornilleria_accesorio', 'orden_id', string='Tornillería y accesorios')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
    ], string='Estado', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


class OrdenTrabajoCortes(models.Model):
    _name = 'orden.trabajo.corte'
    _rec_name = 'lote_id'

    @api.onchange('corte1', 'corte2', 'corte3', 'corte4', 'corte5', 'corte6')
    def _total(self):
        self.total = self.corte1 + self.corte2 + self.corte3 + self.corte4 + self.corte5 + self.corte6

    @api.onchange('total')
    def _sobra(self):
        self.sobra = self.lote_id.largo - self.total

    orden_id = fields.Many2one("orden.trabajo", string='Orden de trabajo', required=True)
    lote_id = fields.Many2one("stock.production.lot", string='Lote', required=True)
    product_id = fields.Many2one(related='lote_id.product_id', string="Producto", store=True, readonly=True)
    product_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True)
    corte1 = fields.Float("Corte 1", required=True)
    corte2 = fields.Float("Corte 2", required=True)
    corte3 = fields.Float("Corte 3", required=True)
    corte4 = fields.Float("Corte 4", required=True)
    corte5 = fields.Float("Corte 5", required=True)
    corte6 = fields.Float("Corte 6", required=True)
    total = fields.Float("Total", required=True)
    sobra = fields.Float("Sobra", required=True)


class OrdenTrabajoMolduraPanel(models.Model):
    _name = 'orden.trabajo.moldura_panel'
    _rec_name = 'product_id'

    orden_id = fields.Many2one("orden.trabajo", string='Orden de trabajo', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    cantidad = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)

class OrdenTrabajoTornilleriaAccesorio(models.Model):
    _name = 'orden.trabajo.tornilleria_accesorio'
    _rec_name = 'product_id'

    orden_id = fields.Many2one("orden.trabajo", string='Orden de trabajo', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    cantidad = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)

