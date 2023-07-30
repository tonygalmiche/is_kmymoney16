# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models,fields,api
from odoo.tools.translate import _


class SoldeParOperationReport(models.Model):
    _name = "kmn.solde.par.operation.report"
    _description = "Solde par opération et par compte"
    _auto = False
    _order = "post_date desc, id desc"

    post_date      = fields.Date('Date')
    payee_id       = fields.Many2one('res.partner', 'Tiers')
    account_id     = fields.Many2one('kmn.accounts', 'Compte')
    institution_id = fields.Many2one(related="account_id.institution_id")
    solde          = fields.Float("Solde" )
    memo           = fields.Text('Note')

    def init(self):
        cr,uid,context,su = self.env.args
        tools.drop_view_if_exists(cr, 'kmn_solde_par_operation_report')
        cr.execute("""CREATE or REPLACE VIEW kmn_solde_par_operation_report as (
            select 
                row_number() over(order by am.id )  as id,
                am.post_date,
                am.payee_id,
                am.account_id,
                am.value as solde,
                am.memo
             from (
                
                select 
                    am.id,
                    am.post_date,
                    am.payee_id,
                    am.account1_id as account_id, 
                    am.value,
                    am.memo
                from kmn_account_move am

                union

                select 
                    am.id,
                    am.post_date,
                    am.payee_id,
                    am.account2_id as account_id, 
                    -am.value,
                    am.memo
                from kmn_account_move am
            ) am
        )""")


