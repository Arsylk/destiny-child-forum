# -*- coding: utf-8 -*-
import json
import pck_server
from helper import *


def index():
    return redirect(URL('apk', 'view_models'))


def view_models():
    show_nsfw = auth.user.show_nsfw if auth.user else True
    db.auth_user.id.searchable = False
    db.auth_user.username.label = 'Creator'
    grid = SQLFORM.grid(db((db.models.creator_id == db.auth_user.id) & ((db.models.nsfw == False) | (show_nsfw == True))),
                        field_id=db.models.id, orderby=~db.models.id,
                        fields=[db.models.id, db.models.idx, db.models.name, db.auth_user.username],
                        maxtextlengths={
                            'models.name': 40
                        },
                        links=[
                            {'header': DIV('Rating', _style='color: #007bff; text-align: center;'), 'body': lambda row: render_rating_stars(row.models.id, row.models.rating())}
                        ],
                        details=False, selectable=False, deletable=False, editable=False, create=False, csv=False, user_signature=False)
    if grid.element('.web2py_htmltable'):
        grid.element('.web2py_htmltable')['_style'] = 'width: 100%;'

    return dict(grid=grid)


def view_creators():
    # all creators
    if request.args(0) is None:
        db.auth_user.uploaded_models = Field.Virtual(lambda row: db(row.auth_user.id == db.models.creator_id)
                                                     .select(db.models.id.count().with_alias('uploaded_models'))
                                                     .first().uploaded_models, label='Uploads')
        grid = SQLFORM.grid(db.auth_user, fields=[db.auth_user.id, db.auth_user.username, db.auth_user.uploaded_models, db.auth_user.avatar],
                            searchable=False, details=False, deletable=False, selectable=False, editable=False, create=False, csv=False, user_signature=False)
        return dict(grid=grid)

    # single creator
    creator_entry = db(db.auth_user.id == request.args(0)).select().first()

    creator_name = H3(creator_entry.username, _style='margin: 8.5px 13.5px; text-decoration-line: underline; float: left;')
    creator_avatar = IMG(_src=URL('download', creator_entry.avatar), _style='width: 50px; height: 50px; float: left; box-shadow: 0 0 0 1px black;')
    creator = DIV(creator_avatar if creator_entry.avatar else '', creator_name, _style='height: 50px; display: inline-block; box-shadow: 0 0 0 1px black; background: lightgray;')

    grid = SQLFORM.grid(db(db.models.creator_id == creator_entry.id),
                        args=[creator_entry.id], field_id=db.models.id,
                        fields=[
                            db.models.id, db.models.idx, db.models.name
                        ],
                        links=[
                            {'header': '', 'body': lambda row: render_edit_button(row.id, True), 'field': 'actions'}
                        ],
                        maxtextlengths={
                            'models.name': 40

                        },
                        searchable=False, details=False, selectable=False, create=False, csv=False, user_signature=False, deletable=False, editable=False)
    userpage = render_userpage(creator_entry.userpage, (creator_entry.userpage is not None))

    return dict(creator=creator, grid=grid, userpage=userpage)


def display_pck():
    # check first argument (id)
    picked_id = request.args(0) or redirect(URL('apk', 'view_models'))
    row = db(db.models.id == picked_id).select().first()
    if not row:
        return redirect(URL('apk', 'view_models'))

    # TODO HELP ME END MYSELF
    # import requests
    # requests.get(('https://arsylk.pythonanywhere.com/api/restore_pck/%s' % picked_id))
    # TODO END

    if request.args(1) == 'clean':
        response.view = 'clean_canvas.html'

        model_meta = row.as_dict()
        return dict(model_id=picked_id, model_path=model_meta['model_path'], **request.get_vars)

    # add edit button
    if row.creator_id == auth.user_id or auth.has_membership(group_id='admin'):
        response.menu.append((T('Edit'), False, URL('apk', 'edit_pck', args=[picked_id]), []))

    # display model meta
    creator_username = db.auth_user(row.creator_id).username
    model_meta = row.as_dict()
    model_meta['model_info'] = XML(model_meta['model_info'])
    model_meta['directory'] = '/home/Arsylk/web2py/applications/dctools/static/models/%s' % row.model_path
    model_meta['file'] = A('%s.pck' % row.idx, _href=URL('api', 'get_model_file', args=[row.id]))
    model_meta['creator'] = A(creator_username, _href=URL('apk', 'view_creators', args=[row.creator_id]))
    model_meta['rating'] = "%.2f" % row.rating()
    if row.model_preview:
        model_meta['preview'] = A('preview.png', _href=URL('api', 'get_model_preview', args=[row.id]), _oncontextmenu='javascript:previewRequested = true;')

    # check second argument (action_rate)
    if request.args(1) == 'rate':
        # check third argument (rating)
        picked_stars = request.args(2)
        if picked_stars:
            db.ratings.update_or_insert(
                ((db.ratings.user_id == auth.user.id) & (db.ratings.model_id == picked_id)),
                user_id=auth.user.id, model_id=picked_id, stars=picked_stars)
            model_meta['rating'] = db(db.models.id == picked_id).select().first().rating()
    else:
        pass
        # update statistics if not creator
        # if row.creator_id != auth.user_id:
        #     db.usage_statistics._update_statistics(picked_id, 0)

    return dict(model_meta=dict((key, val) for key, val in model_meta.items() if (key and val) and key not in ['model_file', 'model_preview']))


@auth.requires_login()
def upload_pck():
    form = SQLFORM(db.models,
                   fields=['name', 'description', 'nsfw'],
                   extra_fields=[
                        Field('model_pck', 'upload', requires=IS_NOT_EMPTY(error_message=auth.messages.is_empty)),
                        Field('additional_pck', 'boolean', default=False),
                        Field('model_pck_raw', 'upload', default=None)
                   ],
                   hidden=dict(creator_id=auth.user.id))
    form.element('#models_model_pck_raw__row')['_style'] = 'display: none;'
    form.vars.additional_pck = False
    form.vars.creator_id = auth.user.id

    # process form
    if form.process().accepted:
        # load entry
        entry = db(db.models.id == form.vars.id).select(db.models.id, db.models.model_path).first()

        # unpack pck to model
        idx, pck_content = pck_server.pck_to_model(str(entry.id), request.vars.model_pck.value)

        # notify if could not unpack
        if idx is None or pck_content is None:
            # remove database entry
            db(db.models.id == entry.id).delete()
            db.commit()
            response.flash = 'Failed to unpack!'
            return dict(form=form)

        # update with additional pck
        file = db.models.model_file.store(pck_content, '%s.pck' % idx)
        if request.vars.additional_pck:
            if IS_NOT_EMPTY(request.vars.model_pck_raw):
                file = db.models.model_file.store(request.vars.model_pck_raw.value, '%s.pck' % idx)
                pck_content = request.vars.model_pck_raw.value

        # update entry
        entry.model_file = file
        entry.model_file_data = pck_content
        entry.idx = idx
        entry.model_path = idx + '-' + str(entry.id)
        entry.update_record()
        db.commit()

        return redirect(URL('display_pck', args=[form.vars.id]))
    elif form.errors:
        response.flash = "Check form!"
    return dict(form=form)


@auth.requires_login()
def edit_pck():
    record = db.models(
        (db.models.id == request.args(0)) &
        ((db.models.creator_id == auth.user.id) | (auth.has_membership(group_id='admin')))
    ) or redirect(URL('apk', 'view_models'))

    form = SQLFORM(db.models, record,
                   fields=['id', 'idx', 'name', 'description', 'model_info', 'background', 'nsfw'],
                   labels=['Id', 'Model ID', 'Model Name', 'Description', 'Model Info', 'Background CSS', 'NSFW'],
                   deletable=True)
    if form.process().accepted:
        if form.deleted:
            response.flash = 'Model deleted!'
            return redirect(URL('apk', 'view_creators', args=[auth.user.id]))

        response.flash = 'Model updated!'
        return redirect(URL('apk', 'display_pck', args=[form.vars.id]))
    elif form.errors:
        response.flash = "Invalid input!"
    return dict(form=form)


def statistics():
    response.view = 'apk/bettertable.html'

    rows = db((db.usage_statistics.model_id == db.models.id) & (db.models.creator_id == db.auth_user.id)).select(
        db.auth_user.username.with_alias('creator'),
        db.models.idx.with_alias('model_idx'),
        db.models.name.with_alias('name'),
        (db.usage_statistics.action.count() - db.usage_statistics.action.sum()).with_alias('views'),
        db.usage_statistics.action.sum().with_alias('downloads'),
        groupby=db.usage_statistics.model_id)
    if not rows:
        raise HTTP(403)

    return dict(data=XML(json.dumps(dict(
         paging=False, order=[],
         columns=[
            {'data': 'creator', 'title': 'Creator'},
            {'data': 'model_idx', 'title': 'Model ID'},
            {'data': 'name', 'title': 'Model Name'},
            {'data': 'views', 'title': 'Views'},
            {'data': 'downloads', 'title': 'Downloads'}
         ], data=rows.as_list()))))


@auth.requires_membership(role='admin')
def devices():
    response.view = 'datatable.html'
    rows = db(db.clients_statistics.id & (db.usage_statistics.client_id == db.clients_statistics.id)).select(
            db.clients_statistics.id .with_alias('id'),
            db.clients_statistics.client_id.with_alias('client_id'),
            db.auth_user.username.with_alias('user'),
            (db.clients_statistics.platform_name+' '+db.clients_statistics.platform_version).with_alias('platform'),
            (db.usage_statistics.action.count() - db.usage_statistics.action.sum()).with_alias('views'),
            db.usage_statistics.action.sum().with_alias('downloads'),
            left=[
                db.user_clients.on(db.user_clients.client_id == db.clients_statistics.id),
                db.auth_user.on(db.user_clients.user_id == db.auth_user.id)
            ], groupby=db.clients_statistics.client_id)

    return dict(data=XML(json.dumps(dict(
         paging=True, order=[[2, 'desc']],
         columns=[
            {'data': 'id', 'title': 'ID'},
            {'data': 'client_id', 'title': 'Client ID'},
            {'data': 'user', 'title': 'User'},
            {'data': 'platform', 'title': 'Platform'},
            {'data': 'views', 'title': 'Views'},
            {'data': 'downloads', 'title': 'Downloads'},
         ], data=rows.as_list()))))


def days():
    rows = db.executesql('SELECT COUNT(id)-SUM(action) as views, '
                         'SUM(action) as downloads, timestamp '
                         'FROM usage_statistics '
                         'GROUP BY DATE_FORMAT(timestamp, "%Y%m%d");')

    model_rows = db.executesql('SELECT models.idx, models.name, '
                               'COUNT(usage_statistics.id)-SUM(usage_statistics.action) as views, '
                               'SUM(usage_statistics.action) as downloads '
                               'FROM usage_statistics '
                               'LEFT JOIN models ON models.id = usage_statistics.model_id '
                               'GROUP BY usage_statistics.model_id '
                               'ORDER BY views DESC, downloads ASC '
                               'LIMIT 0, 25;')

    return dict(data_model_ids=list(row[0] for row in model_rows),
                data_model_names=list(row[1] for row in model_rows),
                data_model_views=list(row[2] for row in model_rows),
                data_model_downloads=list(row[3] for row in model_rows),
                data_views=list(row[0] for row in rows),
                data_downloads=list(row[1] for row in rows),
                data_days=list(row[2].strftime('%d %b') for row in rows))
