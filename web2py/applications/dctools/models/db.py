# -*- coding: utf-8 -*-
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth
import os
import hashlib

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['common'],
             lazy_tables=True)
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
# response.generic_patterns = []
# if request.is_local and not configuration.get('app.production'):
#     response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# disable translations
T.force(None)

# init auth service
auth = Auth(db, signature=False)

# create custom auth_user_table
db.define_table(auth.settings.table_user_name,
                Field('email', length=128, default='', unique=True, searchable=False, label='Email'),
                Field('username', length=64, default='', unique=True, label='Username'),
                Field('password', 'password', length=512, readable=False, label='Password'),
                Field('userpage', 'text', length=4096, default=None, searchable=False, label='Userpage'),
                Field('avatar', 'upload', default=None, searchable=False, autodelete=True, label='Avatar', represent=lambda val, row: IMG(_src=URL('download', val), _width='50px', _height='50px') if val else ''),
                Field('show_nsfw', 'boolean', default=False, searchable=False, label='Show NSFW'),
                Field('registration_key', length=512, writable=False, readable=False, default=''),
                Field('reset_password_key', length=512, writable=False, readable=False, default=''),
                Field('registration_id', length=512, writable=False, readable=False, default=''),
            format=lambda row: '<{}>{}'.format(row.id, row.username))

# set requirements on auth_user_table
auth_user_table = db[auth.settings.table_user_name]
auth_user_table.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email), IS_NOT_IN_DB(db, 'auth_user.email')]
auth_user_table.username.requires = [IS_NOT_EMPTY(error_message=auth.messages.is_empty), IS_NOT_IN_DB(db, 'auth_user.username')]
auth_user_table.password.requires = [CRYPT(min_length=8, max_length=32)]
auth_user_table.avatar.requires = [IS_EMPTY_OR(IS_IMAGE(extensions=('png', 'jpg', 'jpeg'), maxsize=(640, 640), error_message='Image too big, max 640x640'))]
auth.settings.table_user = auth_user_table

# disable auth_event table
auth.settings.table_event = None

# create auth tables
auth.define_tables(username=False, signature=False)
auth.settings.registration_requires_verification = False
auth.settings.create_user_groups = None
auth.settings.actions_disabled = ['bulk_register', 'verify_email']


# create uploaded models table
def calculate_rating(id):
    aliases = db(db.ratings.model_id == id) \
        .select(db.ratings.stars.count().with_alias('count'), db.ratings.stars.sum().with_alias('sum')) \
        .first()
    return aliases.sum / aliases.count if aliases.sum and aliases.count else 0.0


# safe function for removing model files
def cleanup_model(rows):
    for row in rows.select():
        if row.model_path:
            if len(row.model_path) > 0:
                folder_path = '/home/Arsylk/web2py/applications/dctools/static/models/%s' % row.model_path
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass
                os.rmdir(folder_path)
    return False


db.define_table('models',
                Field('creator_id', 'reference auth_user', writable=False, readable=False, default='', label="Creator ID"),
                Field('idx', length=16, default='', writable=False, label='Model ID'),
                Field('name', length=64, default='', label='Model Name'),
                Field('description', 'text', length=512, default='', searchable=False, label="Description"),
                Field('nsfw', 'boolean', default=False, searchable=False, label='NSFW'),
                Field('background', default='', listable=False, searchable=False, label='Background CSS'),
                Field('model_info', 'json', listable=False, searchable=False, default='', label='Model Info'),
                Field('model_path', length=256, writable=False, readable=False, default='', label='Model Path'),

                Field('model_file_data', 'blob', default=None, label='Model File Data',
                      writable=False, readable=False, searchable=False, listable=False),
                Field('model_file', 'upload', default=None, uploadfield='model_file_data', label='Model File',
                      writable=False, readable=False, searchable=False, listable=False),

                Field('model_preview_data', 'blob', default=None, label='Model Preview Data',
                      writable=False, readable=False, searchable=False, listable=False),
                Field('model_preview', 'upload', default=None, uploadfield='model_preview_data', label='Model Preview',
                      writable=False, readable=False, searchable=False, listable=False),
                Field.Lazy('rating', lambda row: calculate_rating(row.models.id)),
            format=lambda row: '<{}>{}'.format(row.id, row.idx))


models_table = db.models
models_table._before_delete.append(cleanup_model)
models_table.idx.requires = [IS_NOT_EMPTY(error_message=auth.messages.is_empty)]
models_table.name.requires = [
    IS_NOT_EMPTY(error_message=auth.messages.is_empty),
    IS_MATCH('^[A-z0-9 ]*$', error_message='Enter only letters, numbers, spaces, and underscores'),
    IS_NOT_IN_DB(db, 'models.name', error_message='Model name taken')
]
models_table.model_path.requires = [IS_NOT_EMPTY(error_message=auth.messages.is_empty), IS_NOT_IN_DB(db, 'models.model_path')]
models_table.creator_id.requires = [IS_NOT_EMPTY(error_message=auth.messages.is_empty), IS_IN_DB(db, 'auth_user.id')]
models_table.model_preview.requires = [IS_EMPTY_OR(IS_IMAGE(extensions='png', maxsize=(640, 640)))]

# create upvotes table
db.define_table('ratings',
                Field('user_id', 'reference auth_user', writable=False, readable=False, label='User ID', notnull=True),
                Field('model_id', 'reference models', writable=False, readable=False, label='Model ID', notnull=True),
                Field('stars', 'float', writable=False, readable=False, label='Rating', notnull=True))

ratings_table = db.ratings
ratings_table.user_id.requires = IS_NOT_EMPTY()
ratings_table.model_id.requires = IS_NOT_EMPTY()
ratings_table.stars.requires = IS_FLOAT_IN_RANGE(0.0, 5.0)


# statistic helpers
def client_id():
    # backward compatibility
    if 'Device-Token' in request.vars:
        return request.vars['Device-Token']
    return request.env['HTTP_DEVICE_TOKEN'] or hashlib.md5(response.session_id.encode()).hexdigest()


def platform_name():
    # backward compatibility
    if 'Device-Token' in request.vars:
        return 'com.arsylk.dcwallpaper'
    return request.env['HTTP_APK_NAME'] or request.user_agent().platform.name


def platform_version():
    # backward compatibility
    if 'Device-Token' in request.vars:
        return '2.14'
    return request.env['HTTP_APK_VERSION'] or request.user_agent().platform.version


def update_statistics(m_id, action):
    query = db.clients_statistics(db.clients_statistics.client_id == client_id())
    if not query:
        c_id = db.clients_statistics.insert(client_id=client_id())
    else:
        c_id = query.id
    db.usage_statistics.insert(client_id=c_id, model_id=m_id, action=action)
    if auth.user:
        u_id = auth.user_id
        query = db.user_clients(((db.user_clients.client_id == c_id) & (db.user_clients.user_id == u_id)))
        if not query:
            db.user_clients.insert(client_id=c_id, user_id=u_id)
    db.commit()


# create action set
action_set = {0: 'view', 1: 'download'}

# create statistics clients table
db.define_table('clients_statistics',
                Field('client_id', unique=True, label='Client ID'),
                Field('created_at', 'datetime', default=request.now, label='Created At'),
                Field('platform_name', default=platform_name(), label='Platform Name'),
                Field('platform_version', default=platform_version(), label="Platform Version"),
                format=lambda row: '<{}>{}'.format(row.id, row.client_id))


# create statistics usage table
db.define_table('usage_statistics',
                Field('client_id', 'reference clients_statistics', label='Client ID'),
                Field('model_id', 'reference models', label='Model ID'),
                Field('timestamp', 'datetime', default=request.now, label='Timestamp'),
                Field('action', 'integer', represent=lambda action, row: action_set.get(action)),
                format=lambda row: '[%s] %s (%s)'.format(row.timestamp, row.client_id, db.auth_user(row.user_id).username))
db.usage_statistics.action.requires = IS_IN_SET(action_set.keys())
db.usage_statistics._update_statistics = update_statistics

# create statistics user clients table
db.define_table('user_clients',
                Field('user_id', 'reference auth_user', label='User ID'),
                Field('client_id', 'reference clients_statistics', label='Client ID'),
                format=lambda row: '{} - {}'.format(row.user_id, row.client_id))


# configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'darkangelice6@gmail.com'
mail.settings.login = 'darkangelice6@gmail.com:42-61-6B-61'
mail.settings.tls = True
mail.settings.ssl = False
