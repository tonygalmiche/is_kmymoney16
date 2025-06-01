# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime, timedelta
import time


class kmn_account_type(models.Model):
    _name = 'kmn.account.type'
    _description = u"kMyMoney Accounts Type"
    
    name=fields.Char('Type de compte', required=True, index=True)


class kmn_accounts(models.Model):
    _name = 'kmn.accounts'
    _description = u"kMyMoney Accounts"
    _order = "name"
    
    def _bal_solde(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            cr.execute("select sum(value) from kmn_account_move where account1_id="+str(obj.id))
            x1 = cr.fetchone()[0] or 0.0
            cr.execute("select sum(value) from kmn_account_move where account2_id="+str(obj.id))
            x2 = cr.fetchone()[0] or 0.0
            obj.bal_solde=x2-x1


    def _nb(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            cr.execute("""
                select count(*) 
                from kmn_account_move 
                where (account1_id="""+str(obj.id)+" or " + "account2_id="+str(obj.id)+") ")
            x = cr.fetchone()[0] or 0.0
            obj.nb=x


    def _percent_all_account(self):
        for obj in self:
            if obj.solde_all_account:
                x=100*obj.bal_solde/obj.solde_all_account
                obj.percent_all_account=x


    def _solde_all_account(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            cr.execute("""
                select sum(value) 
                from kmn_account_move ac inner join kmn_accounts a on ac.account1_id=a.id
                where a.parent_id=181 """)
            x1 = cr.fetchone()[0] or 0.0
            cr.execute("""
                select sum(value) 
                from kmn_account_move ac inner join kmn_accounts a on ac.account2_id=a.id
                where a.parent_id=181 """)
            x2 = cr.fetchone()[0] or 0.0
            obj.solde_all_account=x2-x1


    name                = fields.Char('Nom', required=True, index=True)
    institution_id      = fields.Many2one('res.partner', u'Institution', index=True)
    parent_id           = fields.Many2one('kmn.accounts', u'Compte parent', index=True)
    account_number      = fields.Char('N° de compte', index=True)
    account_type_id     = fields.Many2one('kmn.account.type', u'Type', index=True)
    bal_solde           = fields.Float("Solde"                    , compute=_bal_solde)
    last_post_date      = fields.Date('Date dernier mouvement')
    active              = fields.Boolean('Actif', default=True, index=True)
    solde_all_account   = fields.Float("Solde de tous les comptes", compute=_solde_all_account)
    percent_all_account = fields.Float("Part sur ce compte"       , compute=_percent_all_account)
    nb                  = fields.Integer("Nombre d'opérations"    , compute=_nb)


    def operations_compte_action(self):
        for obj in self:
            tree_view_id = self.env.ref('is_kmymoney16.kmn_account_move_tree_view_editable').id 
            pivot_view_id = self.env.ref('is_kmymoney16.kmn_account_move_pivot_view').id 
            return {
                'name': obj.name,
                'res_model': 'kmn.account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'domain' : ['|',('account1_id','=',obj.id),('account2_id','=',obj.id)],
                'views': [
                    [tree_view_id, "tree"],
                    [pivot_view_id, "pivot"]
                ],
            }


class kmn_account_move(models.Model):
    _name = 'kmn.account.move'
    _description = u"kMyMoney Accounts Move"
    
    _order='post_date desc, id desc'
    

    def action_valide_state(self):
        self.state='valide'
        return True


    def action_dupliquer(self):
        for obj in self.browse(cr, uid, ids, dict(context, active_test=False)):
            vals = {
                'payee_id': obj.payee_id.id,
                'value': obj.value,
                'memo': obj.memo,
                'account1_id': obj.account1_id.id,
                'account2_id': obj.account2_id.id,
                'post_date': obj.post_date,
                'state': 'brouillon',
            }
            model = self.pool.get('kmn.account.move')
            new_id = model.create(cr, uid, vals, context=context)


        if "active_id" in context:
            mod_obj = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            result = self.env.ref('is_kmymoney16.kmn_account_move_action').id 
            action_id = result and result[1] or False
            action = act_obj.read(cr, uid, [action_id], ['name', 'type', 'res_model', 'view_mode', 'view_type', 'context', 'views', 'domain', 'view_id'])[0]
            for obj in self.browse(cr, uid, ids, dict(context, active_test=False)):
                action["context"]=context

                return action
        return True


    def action_affiche_compte(self):
        if "active_id" in context:
            for obj in self.browse(cr, uid, ids, dict(context, active_test=False)):
                account_id=obj.account2_id.id
                if account_id==context["active_id"]:
                    account_id=obj.account1_id.id

                return {
                    'name': _('Compte'),
                    'res_model': 'kmn.accounts',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id':  account_id,
                }


    def action_detail_mouvement(self):
        context=self._context
        if "active_id" in context:
            for obj in self:
                account_id=obj.account2_id.id
                if account_id==context["active_id"]:
                    account_id=obj.account1_id.id
                return {
                    'name': _('Détail du mouvement'),
                    'res_model': 'kmn.account.move',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_id':  obj.id,
                }

 

    def action_operations_compte(self):
        context=self._context
        active_id=False
        if 'active_id' in context:
            active_id=context["active_id"]
        for obj in self:
            tree_view_id = self.env.ref('is_kmymoney16.kmn_account_move_tree_view_editable').id 
            pivot_view_id = self.env.ref('is_kmymoney16.kmn_account_move_pivot_view').id 
            return {
                'name': obj.account_id.name,
                'res_model': 'kmn.account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,pivot',
                'domain' : ['|',('account2_id','=',obj.account_id.id),('account1_id','=',obj.account_id.id)],
                'context':{
                    'active_id' : active_id
                },
                'views': [
                    [tree_view_id, "tree"],
                    [pivot_view_id, "pivot"]
                ],
            }


    def action_operations_tiers(self):
        for obj in self:
            view_id = self.env.ref('is_kmymoney16.kmn_account_move_tree_view_editable').id 
            return {
                'name': obj.payee_id.name,
                'res_model': 'kmn.account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'domain' : [('payee_id','=',obj.payee_id.id)],
                'view_id': view_id,
            }


    def _set_debit(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            if obj.debit==0.0:
                return
            v=-float(obj.debit)
            if "active_id" in context:
                if context["active_id"]==obj.account1_id.id:
                    v=-v
            obj.value = v


    def _debit(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            v=obj.value
            if "active_id" in context:
                if context["active_id"]==obj.account1_id.id:
                    v=-v
            if(v<0):
                v=-v
            else:
                v=None
            obj.debit = v


    def _set_credit(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            if obj.credit==0.0:
                return
            v=float(obj.credit)
            if "active_id" in context:
                if context["active_id"]==obj.account1_id.id:
                    v=-v
            obj.value = v


    def _credit(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            v=obj.value
            if "active_id" in context:
                if context["active_id"]==obj.account1_id.id:
                    v=-v
            if(v<0):
                v=None
            obj.credit = v


    def _solde(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            if "active_id" in context:
                account_id=context["active_id"]
                cr.execute("select sum(value) from kmn_account_move where ((post_date<'"+str(obj.post_date)+"') or (post_date='"+str(obj.post_date)+"' and id<="+str(obj.id)+")) and account1_id="+str(account_id) )
                x1 = cr.fetchone()[0] or 0.0
                cr.execute("select sum(value) from kmn_account_move where ((post_date<'"+str(obj.post_date)+"') or (post_date='"+str(obj.post_date)+"' and id<="+str(obj.id)+")) and account2_id="+str(account_id) )
                x2 = cr.fetchone()[0] or 0.0
                solde = x2-x1
                obj.solde = solde


    def _account_id(self):
        cr,uid,context,su = self.env.args
        for obj in self:
            v=obj.account1_id.id
            if "active_id" in context:
                if context["active_id"]==obj.account1_id.id:
                    v=obj.account2_id.id
            obj.account_id = v


    def _set_account_id(self):
        for obj in self:
            obj.account2_id=obj.account_id


    def _get_post_date(self):
        obj = self.env['kmn.accounts']
        account = obj.browse(self._context["active_id"])
        return  account.last_post_date


    payee_id          = fields.Many2one('res.partner', u'Tiers', index=True)
    reconcile_date    = fields.Date('Date reconcile', index=True)
    action            = fields.Char('Action')
    reconcile_flag    = fields.Char('reconcile_flag')
    value             = fields.Float('Montant')
    debit             = fields.Float("Débit" , compute=_debit , inverse=_set_debit , readonly=False)
    credit            = fields.Float("Crédit", compute=_credit, inverse=_set_credit, readonly=False)
    solde             = fields.Float("Solde" , compute=_solde)
    memo              = fields.Text('Note')
    account1_id       = fields.Many2one('kmn.accounts', u'Compte 1', index=True)
    account2_id       = fields.Many2one('kmn.accounts', u'Compte 2', index=True)
    account_id        = fields.Many2one('kmn.accounts', u'Compte', compute=_account_id, inverse=_set_account_id, readonly=False)
    check_number      = fields.Char('check_number')
    post_date         = fields.Date('Date',default=_get_post_date, index=True)
    date_creation     = fields.Datetime('Date création'    , required=True, default=lambda *a: fields.datetime.now(), index=True)
    date_modification = fields.Datetime('Date modification', required=True, default=lambda *a: fields.datetime.now(), index=True)
    state             = fields.Selection([('brouillon', u'Brouillon'),('valide', u'Validé')], u"État", readonly=True, index=True, default='brouillon')

    def _set_last_post_date(self,vals):
        cr,uid,context,su = self.env.args
        if "post_date" in vals:
            account = self.env['kmn.accounts'].browse(context["active_id"])
            account.last_post_date=vals["post_date"]


    @api.onchange('payee_id')
    def onchange_etat(self):
        for obj in self:
            domain = [('payee_id', '=', obj.payee_id.id)]
            lines=self.env['kmn.account.move'].search(domain, order='post_date desc', limit=1)
            for line in lines:
                obj.account_id = line.account_id.id


    @api.model_create_multi
    def create(self, vals_list):
        context=self._context
        for vals in vals_list:

            self._set_last_post_date(vals)


            if context.get('active_model', False) == 'kmn.accounts' and context.get('active_id', False):
                vals.update({
                    'account1_id': context.get('active_id', False),
                })
        res = super(kmn_account_move, self).create(vals_list)
        return res


    def write(self,vals):
        vals["date_modification"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._set_last_post_date(vals)

        return super(kmn_account_move, self).write(vals)



