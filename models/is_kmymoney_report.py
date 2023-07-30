# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models,fields,api
from odoo.tools.translate import _


class IsKmyMoneyReport(models.Model):
    _description = "Suivi du temps par activité"
    _name = 'is.kmymoney.report'
    _order='id desc'
    _auto = False

    account1_id       = fields.Many2one('kmn.accounts', u'Compte 1')
    post_date         = fields.Date('Date')
    partner_id        = fields.Many2one('res.partner', u'Tiers')
    account2_id       = fields.Many2one('kmn.accounts', u'Compte 2')
    value             = fields.Float('Montant')
    cumul             = fields.Float('Cumul')
    memo              = fields.Text('Note')

    def init(self):
        cr,uid,context,su = self.env.args
        tools.drop_view_if_exists(cr, 'is_kmymoney_report')
        cr.execute("""
            CREATE OR REPLACE view is_kmymoney_report AS (
                select
                    row_number() over(order by m.id )  as id,
                    a1.id                              as account1_id,
                    m0.post_date                       as post_date,
                    rp.id                              as partner_id,
                    a2.id                              as account2_id,
                    m0.memo                            as memo,
                    -m.value                           as value,
                    -sum(m.value) OVER (PARTITION BY a1.id ORDER BY m0.post_date) AS cumul
                from (
                    select
                        m1.id,
                        m1.value,
                        m1.account1_id account1_id,
                        m1.account2_id account2_id
                    from kmn_account_move m1

                    union

                    select
                        m2.id,
                        -m2.value,
                        m2.account2_id account1_id,
                        m2.account1_id account2_id
                    from kmn_account_move m2
                ) m inner join kmn_accounts a1      on m.account1_id=a1.id
                    inner join kmn_accounts a2      on m.account2_id=a2.id
                    inner join kmn_account_move m0 on m.id=m0.id
                    inner join res_partner      rp on m0.payee_id=rp.id
                where a1.institution_id is not null
            )
        """)

