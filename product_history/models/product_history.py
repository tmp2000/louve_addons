# *- encoding: utf-8 -*-
##############################################################################
#
#    Product - Average Consumption Module for Odoo
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from openerp import models, fields, api

HISTORY_RANGE = [
        ('days', 'Days'),
        ('weeks', 'Week'),
        ('months', 'Month'),
        ]


class ProductHistory(models.Model):
    _name = "product.history"
    _order = 'from_date desc'

# Columns section
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        required=True, ondelete='cascade')
    product_tmpl_id = fields.Many2one(
        'product.template', related='product_id.product_tmpl_id',
        string='Template', store=True)
    location_id = fields.Many2one(
        'stock.location', string='Location', required=True,
        ondelete='cascade')
    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    purchase_qty = fields.Float("Purchases", default=0)
    production_qty = fields.Float("Production", default=0)
    sale_qty = fields.Float("Sales", default=0)
    loss_qty = fields.Float("Losses", default=0)
    start_qty = fields.Float("Opening quantity", default=0)
    end_qty = fields.Float("Closing quantity", default=0)
    incoming_qty = fields.Float("Incoming quantity", default=0)
    outgoing_qty = fields.Float("Outgoing quantity", default=0)
    virtual_qty = fields.Float("Virtual quantity", default=0)
    history_range = fields.Selection(
        HISTORY_RANGE, "History range",
        required=True)

