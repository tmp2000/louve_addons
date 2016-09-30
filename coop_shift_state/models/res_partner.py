# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Cyril Gaspard
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Julien WESTE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _ALERT_DURATION = 28

    SHIFT_TYPE_SELECTION = [
        ('standard', 'Standard'),
        ('ftop', 'FTOP'),
    ]

    COOPERATIVE_STATE_SELECTION = [
        ('up_to_date', 'Up to date'),
        ('alert', 'Alert'),
        ('suspended', 'Suspended'),
        ('delay', 'Delay'),
        ('unpayed', 'Unpayed'),
        ('blocked', 'Blocked'),
        ('unsubscribed', 'Unsubscribed'),
    ]

    is_unpayed = fields.Boolean('Unpayed')

    is_blocked = fields.Boolean('Blocked')

    shift_type = fields.Selection(
        selection=SHIFT_TYPE_SELECTION, string='Shift type', required=True,
        default='standard')

    cooperative_state = fields.Selection(
        selection=COOPERATIVE_STATE_SELECTION, string='State',
        compute='compute_cooperative_state')

    theoritical_standard_point = fields.Integer(
        string='theoritical Standard points', store=True,
        compute='compute_theoritical_standard_point')

    manual_standard_correction = fields.Integer(
        string='Manual Standard Correction')

    final_standard_point = fields.Integer(
        string='Final Standard points',compute='compute_final_standard_point',
        store=True)

    theoritical_ftop_point = fields.Integer(
        string='theoritical FTOP points', store=True,
        compute='compute_theoritical_ftop_point')

    manual_ftop_correction = fields.Integer(
        string='Manual FTOP Correction')

    final_ftop_point = fields.Integer(
        string='Final FTOP points',compute='compute_final_ftop_point',
        store=True)

    date_alert_stop = fields.Date(
        string='End Alert Date', compute='compute_date_alert_stop',
        store=True, help="This date mention the date when"
        " the 'alert' state stops and when the partner will be suspended.")

    date_delay_stop = fields.Date(
        string='End Delay Date', compute='compute_date_delay_stop',
        store=True, help="This date mention the date when"
        " the 'delay' state stops and when the partner will be suspended.")

#    date_delay_end = fields.Date('End date delay')

    # Compute Section
    @api.depends('theoritical_standard_point', 'manual_standard_correction')
    @api.multi
    def compute_final_standard_point(self):
        for partner in self:
            partner.final_standard_point =\
                partner.theoritical_standard_point +\
                partner.manual_standard_correction

    @api.depends('theoritical_ftop_point', 'manual_ftop_correction')
    @api.multi
    def compute_final_ftop_point(self):
        for partner in self:
            partner.final_ftop_point =\
                partner.theoritical_ftop_point +\
                partner.manual_ftop_correction

    @api.depends(
        'registration_ids.state', 'registration_ids.shift_type')
    @api.multi
    def compute_theoritical_standard_point(self):
        for partner in self:
            point = 0
            for registration in partner.registration_ids.filtered(
                        lambda reg: reg.shift_type == 'standard'):
                if not registration.template_created:
                    if registration.state in ['done', 'replaced']:
                        point += +1
                # In all cases
                if registration.state in ['absent']:
                    point += -2
                elif registration.state in ['excused', 'waiting']:
                    point += -1
            partner.theoritical_standard_point = point

    @api.depends('registration_ids.state', 'registration_ids.shift_type')
    @api.multi
    def compute_theoritical_ftop_point(self):
        for partner in self:
            point = 0
            for registration in partner.registration_ids.filtered(
                        lambda reg: reg.shift_type == 'ftop'):
                if registration.template_created:
                    # The presence was forcasted
                    if registration.state in ['absent', 'excused', 'waiting']:
                        point += -1
                else:
                    if registration.state in ['absent']:
                        point += -1
                    elif registration.state in ['present']:
                        point += 1
            partner.theoritical_ftop_point = point

    @api.depends('extension_ids')
    @api.multi
    def compute_date_delay_stop(self):
#        for partner in self:
#            # If all is OK, the date is deleted
#            point = partner.shift_type == 'standard'\
#                and partner.final_standard_point\
#                or partner.final_ftop_point
#            if point > 0:
#                partner.date_alert_stop = False
#            elif not partner.date_alert_stop:
#                partner.date_alert_stop =\
#                    datetime.today() + relativedelta(days=self._ALERT_DURATION)


    @api.depends('final_standard_point', 'final_ftop_point')
    @api.multi
    def compute_date_alert_stop(self):
        for partner in self:
            # If all is OK, the date is deleted
            point = partner.shift_type == 'standard'\
                and partner.final_standard_point\
                or partner.final_ftop_point
            if point > 0:
                partner.date_alert_stop = False
            elif not partner.date_alert_stop:
                partner.date_alert_stop =\
                    datetime.today() + relativedelta(days=self._ALERT_DURATION)

    @api.depends(
        'is_blocked', 'is_unpayed', 'final_standard_point', 'final_ftop_point',
        'shift_type', 'date_alert_stop')
    @api.multi
    def compute_cooperative_state(self):
        for partner in self:
            state = 'up_to_date'
            if partner.is_blocked:
                state = 'blocked'
            elif partner.is_unpayed:
                state = 'unpayed'
            else:
                point = partner.shift_type == 'standard'\
                    and partner.final_standard_point\
                    or partner.final_ftop_point
                if point < 0:
                    if partner.date_alert_stop:
                        if partner.date_delay_stop > fields.Datetime.now():
                            # There is Delay
                            state = 'delay'
                        if partner.date_alert_stop > fields.Datetime.now():
                            # Grace State
                            state = 'alert'
                        else:
                            print "WEIRD STATE TO FIX. partner %d" % partner.id
                            state = 'suspended'
                    else:
                        state = 'suspended'
            partner.cooperative_state = state
