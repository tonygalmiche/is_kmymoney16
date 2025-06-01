# -*- coding: utf-8 -*-
from odoo import models,fields,api # type: ignore

class res_company(models.Model):
    _inherit = 'res.company'

    is_poids_objectif = fields.Float(string="Poids ojectif" , default=80, digits=(12, 1))
    is_fc_r_objectif  = fields.Integer(string="FC-R ojectif", default=70)
    is_fc_s_objectif  = fields.Integer(string="FC-S ojectif", default=65)
    is_vfc_objectif   = fields.Integer(string="VFC ojectif" , default=35)


    def maj_objectifs(self):
        for obj in self:
            lines=self.env['is.suivi.sante'].search([])
            for line in lines:
                print(line,line.name.strftime('%A'))
                line.poids_objectif = obj.is_poids_objectif
                line.fc_r_objectif  = obj.is_fc_r_objectif
                line.fc_s_objectif  = obj.is_fc_s_objectif
                line.vfc_objectif   = obj.is_vfc_objectif
