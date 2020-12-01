# -*- coding: utf-8 -*-
from gluon.http import *
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
def index():
    return redirect(URL('apk', 'index'))

def error():
    return redirect(URL('admin/default/ticket', request.vars.ticket))

# # ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# # ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki()

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://.../[app]/default/user/register
    http://.../[app]/default/user/login
    http://.../[app]/default/user/logout
    http://.../[app]/default/user/profile
    http://.../[app]/default/user/change_password
    http://.../[app]/default/user/verify_email
    http://.../[app]/default/user/retrieve_username
    http://.../[app]/default/user/request_reset_password
    http://.../[app]/default/user/reset_password
    http://.../[app]/default/user/impersonate
    http://.../[app]/default/user/groups
    http://.../[app]/default/user/not_authorized
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    if request.args(0) == 'register':
        auth.settings.table_user.show_nsfw.writable=False
        auth.settings.table_user.userpage.writable=False
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    filename = request.args(0)
    return response.stream('/home/Arsylk/web2py/applications/dctools/uploads/%s' % filename)
