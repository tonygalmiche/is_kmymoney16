# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models,fields,api
from odoo.tools.translate import _


class SoldeParMoisReport(models.Model):
    _name = "kmn.solde.par.mois.report"
    _description = "Solde par mois et par compte"
    _auto = False
    _rec_name = 'compte'


    compte = fields.Char(u'Compte')
    mois   = fields.Date(u'Mois')
    solde  = fields.Float(u'Solde', digits=(1, 0), readonly=True)

    
    def init(self):
        cr,uid,context,su = self.env.args
        tools.drop_view_if_exists(cr, 'kmn_mois')
        cr.execute("""CREATE or REPLACE VIEW kmn_mois as (
            select distinct (to_char(post_date,'YYYY-MM-01')::date  + interval '1 month - 1 day')::date  mois 
            from kmn_account_move 
            where post_date>='2000-01-01' 
            order by mois
        )""")

        tools.drop_view_if_exists(cr, 'kmn_solde_par_mois_report')
        cr.execute("""CREATE or REPLACE VIEW kmn_solde_par_mois_report as (
            select 
                a.id,
                a.name as compte, 
                m.mois as mois,
                (coalesce((select sum(value) from kmn_account_move where account2_id=a.id and post_date<=m.mois),0)-
                 coalesce((select sum(value) from kmn_account_move where account1_id=a.id and post_date<=m.mois),0)) as solde
            from kmn_accounts a, kmn_mois m
            where a.institution_id is not null and active=true 
            order by a.name, m.mois
        )""")

