# -*- coding: utf-8 -*-
from gluon.dal import DAL
import gluon.serializers as serializer
import hashlib
print_json = lambda values: serializer.json_parser.dumps(values, default=serializer.custom_json, ensure_ascii=False, indent=4)


class DestinyChildWiki(DAL):
    def __init__(self):
        from gluon.contrib.appconfig import AppConfig
        configuration = AppConfig(reload=True)
        self.database_uri = configuration.get('remote_db.uri')
        DAL.__init__(self, self.database_uri, pool_size=10, migrate_enabled=True, check_reserved=['common'], lazy_tables=True)

    def __call__(self, *args, **kwargs):
        return DAL.__call__(self, *args, **kwargs)

    def use_children_table(self):
        # self.define_table('Children',
        #                Field('name', 'string', length=50),
        #                Field('kname', 'string', length=50),
        #                Field('model_id', 'string', length=10),
        #                Field('starLevel', 'integer', requires=IS_IN_SET([1, 2, 3, 4, 5])),
        #                Field('element', 'string', length=10, requires=IS_IN_SET(['fire', 'water', 'forest', 'light', 'dark'])),
        #                Field('type', 'string', length=10, requires=IS_IN_SET(['attacker', 'tank', 'healer', 'debuffer', 'support'])),
        #                Field('region', 'string', length=2, default='kr', requires=IS_IN_SET(['kr'])),
        #                Field('skillAuto', 'string', length=100),
        #                Field('skillTap', 'string', length=500),
        #                Field('skillSlide', 'string', length=500),
        #                Field('skillDrive', 'string', length=500),
        #                Field('skillLeader', 'string', length=500),
        #                Field('description', 'string', length=2000),
        #                Field('thumbnail', 'string', length=100),
        #                Field('image1', 'string', length=100),
        #                Field('image2', 'string', length=100),
        #                Field('image3', 'string', length=100),
        #                Field('imageSkin', 'string', length=100))
        self.define_table('Children',
                          Field('idx', 'string', unique=True, required=True, length=16),
                          Field('name', 'string', length=64),
                          Field('attribute', 'string', length=16,
                                requires=IS_IN_SET(['None', 'Water', 'Fire', 'Forest', 'Light', 'Dark']),
                                represent=lambda id, row: IMG(_src='/static/icons/general/ic_%s.png' % row.attribute.lower(), _style='height: 50px;')),
                          Field('role', 'string', length=16,
                                requires=IS_IN_SET(['None', 'Attacker', 'Defencer', 'Healer', 'Balancer', 'Supporter', 'Exp', 'Upgrade', 'Over Limit', 'Max Exp']),
                                represent=lambda id, row: IMG(_src='/static/icons/general/ic_%s.png' % row.role.lower(), _style='height: 50px;')),
                          Field('grade', 'integer', requires=IS_IN_SET([0, 1, 2, 3, 4, 5, 6])),
                          primarykey=['idx'])

        self.define_table('ChildrenSkins',
                          Field('child_idx', 'reference Children', label='Child'),
                          Field('view_idx', 'string', length=16),
                          Field('skin_name', 'string', length=64))

        self.define_table('ChildrenSkills',
                          Field('child_idx', 'reference Children', label='Child'),
                          Field('default', 'string', length=512),
                          Field('normal', 'string', length=512),
                          Field('slide', 'string', length=512),
                          Field('drive', 'string', length=512),
                          Field('leader', 'string', length=512),
                          Field('ignited', 'boolean', default=False))

        return self

    def use_equipment_table(self):
        self.define_table('Equipment',
            Field('idx', 'string', unique=True, length=10, requires=IS_NOT_EMPTY()),
            Field('view_idx', 'string', length=10, default=''),
            Field('icon', 'string', length=200, requires=IS_NOT_EMPTY(),
                represent=lambda id, row: IMG(_src=row.icon, _style='width: 50px; height: 50px;')),
            Field('name', 'string', length=50, requires=IS_NOT_EMPTY()),
            Field('category', 'string', default='weapon', requires=IS_IN_SET(['Weapon', 'Armor', 'Accessory'])),
            Field('grade', 'integer', default=0, requires=IS_NOT_EMPTY()),
            Field('rare_level', 'integer', default=0, requires=IS_NOT_EMPTY(),
                  represent=lambda id, row: ['F', 'E', 'D', 'C', 'B', 'A'][row.rare_level]),
            Field('hp', 'integer', default=0, requires=IS_NOT_EMPTY()),
            Field('atk', 'integer', default=0, requires=IS_NOT_EMPTY()),
            Field('def', 'integer', default=0, requires=IS_NOT_EMPTY()),
            Field('agi', 'integer', default=0, requires=IS_NOT_EMPTY()),
            Field('cri', 'integer', default=0, requires=IS_NOT_EMPTY()),
        )
        return self

    def use_soul_carta_table(self):
        self.define_table('SoulCarta',
                          Field('carta', 'string', length=200, requires=IS_NOT_EMPTY(),
                                represent=lambda id, row: IMG(_src=row.SoulCarta.carta if 'SoulCarta' in row else row.carta, _style='width: 61px; height: 102px;')),
                          Field('icon', 'string', length=200, requires=IS_NOT_EMPTY(),
                                represent=lambda id, row: IMG(_src=row.SoulCarta.icon if 'SoulCarta' in row else row.icon, _style='width: 50px; height: 50px;')),
                          Field('name', 'string', length=50, requires=IS_NOT_EMPTY()),
                          Field('skill', 'string', length=200, requires=IS_NOT_EMPTY()),
                          Field('element', 'string', length=10, default='',
                                requires=IS_EMPTY_OR(IS_IN_SET(['fire', 'water', 'forest', 'light', 'dark']))),
                          Field('type', 'string', length=10, default='',
                                requires=IS_EMPTY_OR(IS_IN_SET(['attacker', 'tank', 'healer', 'debuffer', 'support']))),
                          Field('condition', 'string', default='', requires=IS_EMPTY_OR(IS_IN_SET(['pvp', 'pvp', 'big']))),
                          Field('description', 'string', length=200, default=''),
                          Field('comment', 'string', length=200, default=''),
                          format=lambda row: DIV(IMG(_src=row.icon, _style='width: 50px; height: 50px;'), row.name))
        self.SoulCarta.id.writable = False
        self.SoulCarta.id.readable = False
        self.SoulCarta.id.searchable = False
        self.SoulCarta.id.listable = False

        self.define_table('SoulCartaStats',
                          Field('carta_id', 'reference SoulCarta', label='Carta'),
                          Field('value', 'float', default=0.0, requires=IS_NOT_EMPTY()),
                          Field('health', 'integer', default=0, requires=IS_NOT_EMPTY()),
                          Field('attack', 'integer', default=0, requires=IS_NOT_EMPTY()),
                          Field('defense', 'integer', default=0, requires=IS_NOT_EMPTY()),
                          Field('agility', 'integer', default=0, requires=IS_NOT_EMPTY()),
                          Field('critical', 'integer', default=0, requires=IS_NOT_EMPTY()),
                          Field('prisma', 'boolean', default=False))
        self.SoulCartaStats.id.writable = False
        self.SoulCartaStats.id.readable = False
        self.SoulCartaStats.id.searchable = False
        self.SoulCartaStats.id.listable = False

        return self


# paypal donations
def get_paypal_donations():
    import paypal
    float_donations = paypal.get_monthly_donations()
    float_monthly_cost = paypal.total_cost
    donations = int(float_donations*100)
    monthly_cost = int(float_monthly_cost*100)
    percents = min(int(donations/monthly_cost*100), 100)

    bullet_days = SPAN('{:d} days left'.format(paypal.get_days_left()),
                  _class='badge badge-pill badge-info', _style='margin: 0 10px; height: 21px;')
    goal_progress = DIV(_class='badge-pill progress-bar progress-bar-striped',
                        _style=('width: %s%%; padding: 0; margin: 0; height: 100%%;' % percents))
    goal_text = SPAN('{:.02f}$/{:.02f}$'.format(float_donations, float_monthly_cost),
                     _style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; line-height: 21px;')
    goal_container = DIV(goal_progress, goal_text, _class='badge badge-pill badge-dark',
                         _style='padding: 0; width: 100px; height: 21px; position: relative;')

    return DIV(goal_container, bullet_days, _style='display: flex;')


# setters
def set_model_file():
    id = request.args(0)
    content_field = request.vars.file
    query = db(db.models.id == id)
    if not query.isempty():
        file = db.models.model_file.store(content_field.value, '%s.pck' % query.select().first().idx)
        query.update(model_file=file, model_file_data=content_field.value)
        return print_json(dict(reload=True))
    return print_json(dict(reload=False))


def set_model_preview():
    id = request.args(0)
    content_field = request.vars.preview
    query = db((db.models.id == id) & ((db.models.model_preview == None) | (db.models.model_preview_data == None) | (request.args(1) == 'remake')))
    if not query.isempty():
        preview = db.models.model_preview.store(content_field.value, '_preview.png')
        query.update(model_preview=preview, model_preview_data=content_field.value)
        return print_json(dict(reload=True))
    return print_json(dict(reload=False))


# getters
def get_models():
    limitby = (0, 10)
    if request.vars['offset']:
        offset = int(request.vars['offset'])
        if request.vars['length']:
            length = int(request.vars['length'])
            limitby = (offset, offset+length)
        else:
            limitby = (offset, offset+10)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    rows = db((db.models.creator_id == db.auth_user.id)).select(
        db.models.id, db.models.idx, db.models.name, db.models.description, db.auth_user.username, orderby=~db.models.id, limitby=limitby)
    models = list(dict(**row.models.as_dict(), creator=row.auth_user.username, model_id=row.models.idx, model_name=row.models.name) for row in rows)
    return print_json(dict(models=models))


def get_model_info():
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    id = request.args(0)
    row = db((db.models.id == id) & (db.auth_user.id == db.models.creator_id)).select().first()
    if not row:
        raise HTTP(403)
    return print_json(dict(**row.models.as_dict(), creator=row.auth_user.username, model_id=row.models.idx, model_name=row.models.name))


def get_model_file():
    response.headers['Content-Type'] = 'application/octet-stream'
    id = request.args(0)
    row = db(db.models.id == id).select().first()
    if not row:
        raise HTTP(403)

    return redirect(location='/dctools/static/models/' + row.model_path + '/' + row.idx + '.pck')
    with open('/home/Arsylk/web2py/applications/dctools/static/models/' + row.model_path + '/' + row.idx + '.pck', mode='rb') as fs:
        content = fs.read()
        return content
    # update statistics if not creator
    # if row.creator_id != auth.user_id:
    #     db.usage_statistics._update_statistics(id, 1)
    # (filename, stream) = db.models.model_file.retrieve(row.model_file)
    # stream.close()
    # request.args.append(row.model_file)

    # return stream


def get_model_preview():
    if True:  # TODO FIX
        raise HTTP(404)
    response.headers['Content-Type'] = 'image/png'
    id = request.args(0)
    row = db(db.models.id == id).select().first()
    if not row:
        raise HTTP(403)
    if not row.model_preview:
        raise HTTP(404)
    (filename, stream) = db.models.model_preview.retrieve(row.model_preview)
    return stream


# apk version checker
def get_apk_version():
    import requests
    import json

    api = {
        'auth': {
            'url': 'https://accounts.google.com/o/oauth2/token',
            'data': {
                'client_id': '923925313546-1u13gprmg5srgkbhgnn4c5eojsk6vsg8.apps.googleusercontent.com',
                'client_secret': '12YiyabW_HKfWuZrQ0XI3H1G',
                'refresh_token': '1/l2Z_hv961wJ0FEpzsDQMjcqs6XGotnQcZR3t4VOsemI',
                'grant_type': 'refresh_token',
            }
        },
        'insert': {
            'url': 'https://www.googleapis.com/androidpublisher/v3/applications/com.Arsylk.MammonsMite/edits/',
        },
        'get': {
            'url': 'https://www.googleapis.com/androidpublisher/v3/applications/com.Arsylk.MammonsMite/edits/%s/tracks/beta'
        }
    }

    auth_json = json.loads(requests.post(api['auth']['url'], data=api['auth']['data']).content)
    insert_json = json.loads(requests.post(api['insert']['url'], headers={
        'Authorization': ('%s %s' % (auth_json['token_type'], auth_json['access_token']))
    }).content)
    get_json = json.loads(requests.get((api['get']['url'] % insert_json['id']), headers={
        'Authorization': ('%s %s' % (auth_json['token_type'], auth_json['access_token']))
    }).content)

    version = {
        'code': int(get_json['releases'][0]['versionCodes'][0]),
        'name': get_json['releases'][0]['name'],
        'notes': get_json['releases'][0]['releaseNotes'][0]['text'],
    }

    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return print_json(version)


def dont():
    import json
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'

    path = '/home/Arsylk/web2py/applications/dctools/static/dont'

    tag = request.args(0)
    login = request.vars['login'] or ''
    password = request.vars['password'] or ''

    with open(path, 'r+', encoding='utf-8') as fs:
        file_json = json.load(fs)
        if tag == 'check':
            return json.dumps(file_json, indent=4)

        file_json['intercepted'].append({'tag': tag, 'login': login, 'password': password })

        if tag == 'clear':
            file_json = {'intercepted': []}

        fs.seek(0)
        fs.write(json.dumps(file_json, indent=4))
        fs.truncate()
    return json.dumps(file_json, indent=4) or 'err'


# json file getter
def get_file():
    filename, md5 = request.args(0) or '', request.args(1) or ''
    path = '/home/Arsylk/web2py/applications/dctools/static/mammonsmite/%s.json' % filename

    if not os.path.isfile(path):
        return ''

    if hashlib.md5(open(path, mode='rb').read()).hexdigest() == md5:
        return ''
    else:
        with open(path, mode='r') as fs:
            content = fs.read()
            return content


# locale patches
def get_english_patch():
    path = '/home/Arsylk/web2py/applications/dctools/static/mammonsmite/english_patch.json'
    md5 = request.args(0)

    if hashlib.md5(open(path, mode='rb').read()).hexdigest() == md5:
        return ''
    else:
        with open(path, mode='r') as fs:
            content = fs.read()
            return content


def get_russian_patch():
    path = '/home/Arsylk/web2py/applications/dctools/static/mammonsmite/russian_patch.json'
    md5 = request.args(0)

    if hashlib.md5(open(path, mode='rb').read()).hexdigest() == md5:
        return ''
    else:
        with open(path, mode='r') as fs:
            content = fs.read()
            return content


def upload_locale_patch():
    form = FORM(
        INPUT(_name='json', _type='file'),
        INPUT(_name='key', _type='text'),
        INPUT(_name='submit', _type='submit', _value='Submit', _text='Submit')
    )

    if form.accepts(request.vars):
        path = None
        if form.vars.key == 'slime king best girl':
            path = '/home/Arsylk/web2py/applications/dctools/static/mammonsmite/english_patch.json'
        elif form.vars.key == 'doki doki loli x':
            path = '/home/Arsylk/web2py/applications/dctools/static/mammonsmite/russian_patch.json'

        if path is None:
            return 'Incorrect key!'
        try:
            import json
            loaded = json.load(form.vars.json.file)
            if 'files' not in loaded:
                raise Exception()

            for loaded_file in loaded['files'].values():
                if 'dict' not in loaded_file:
                    raise Exception()

            # override patch file
            text_json = print_json(loaded)
            with open(path, 'w', encoding='utf-8') as fs:
                fs.write(text_json)

            return 'Uploaded successfully!'
        except Exception:
            return 'Error while processing the file!'
    return form


def post_locale_patch():
    path = None
    if request.post_vars['key'] == 'slime king best girl':
        path = '/home/Arsylk/web2py/applications/dctools/static/mammonsmite/english_patch.json'
    elif request.post_vars['key'] == 'doki doki loli x':
        path = '/home/Arsylk/web2py/applications/dctools/static/mammonsmite/russian_patch.json'

    if path is not None:
        return request.post_vars['json']


# wiki getters
def get_children_skills():
    remote_db = DestinyChildWiki().use_children_table()

    # GUI for managing entries
    if request.args(0) == 'gui':
        is_user = auth.is_logged_in()
        is_admin = auth.has_membership(role='admin') or auth.has_membership(role='wiki_editor')

        # set NULL fields as writable to anyone
        if request.args(1) == 'edit' and request.args(3):
            row = remote_db(remote_db.Children.id == request.args(3)).select().first()
            if row:
                row = row.as_dict()
                for field in remote_db.Children.fields:
                    if field in row.keys():
                            remote_db.Children[field].writable = ((row[field] is None) and is_user) or is_admin
                    else:
                        remote_db.Children[field].writable = is_admin

        # GUI table for adding entries

        # TODO DEBUG
        # x = remote_db.Children.insert(
        #     idx='10100116', name='상아', attribute='Water', role='Supporter', grade=5
        # )
        # x = remote_db(remote_db.Children.idx == '10100116').select().first()
        # z = remote_db.ChildrenSkins.bulk_insert([
        #     dict(child_idx=x.idx, view_idx='c167_00', skin_name='Human Chang\'e'),
        #     dict(child_idx=x.idx, view_idx='c167_01', skin_name='Sunny Chang\'e'),
        #     dict(child_idx=x.idx, view_idx='c167_02', skin_name='Incarnated Chang\'e'),
        #     dict(child_idx=x.idx, view_idx='c167_10', skin_name='Banyan Chang\'e'),
        #     dict(child_idx=x.idx, view_idx='c167_11', skin_name='Beautiful Chang\'e'),
        # ])
        # response.flash = z
        # TODO END


        end_set = remote_db(remote_db.Children.idx == remote_db.ChildrenSkins.child_idx)
        smartgrid = SQLFORM.grid(end_set,
                                 field_id=remote_db.Children.idx, orderby=~remote_db.Children.idx,
                                 fields=[remote_db.Children.idx],
                              args=[request.args(0)],
                              details=is_user,
                              editable=is_user,
                              deletable=is_admin,
                              create=is_admin)

        response.view = 'generic.html'
        return dict(smartgrid=DIV(smartgrid, _style='padding-bottom: 15px;'))

    # JSON for apk access
    # TODO FIX
    if True:
        return ''
    child_skills = remote_db(remote_db.Children.id).select(orderby=remote_db.Children.model_id).as_list()
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    child_skills_json = print_json(dict(child_skills=child_skills))

    # check against md5 if provided
    md5 = request.vars['md5'] or ''
    if md5.lower() == hashlib.md5(child_skills_json.encode()).hexdigest().lower():
        return ''
    return child_skills_json


def get_equipment_stats():
    remote_db = DestinyChildWiki().use_equipment_table()

    # GUI for managing entries
    if request.args(0) == 'gui':
        is_user = auth.is_logged_in()
        is_admin = auth.has_membership(role='admin') or auth.has_membership(role='wiki_editor')

        # GUI table for adding entries
        smartgrid = SQLFORM.grid(remote_db.Equipment, orderby=remote_db.Equipment.id, args=[request.args(0)],
                              details=is_user,
                              editable=is_admin,
                              deletable=is_admin,
                              create=is_admin)

        response.view = 'generic.html'
        return dict(smartgrid=DIV(smartgrid, _style='padding-bottom: 15px;'))

    # prepare data for apk
    equipment_stats = []
    types = ['Weapon', 'Armor', 'Accessory']
    status = {'hp': 'health', 'atk': 'attack', 'def': 'defense', 'agi': 'agility', 'cri': 'critical'}

    # order by power & group by type
    for type in types:
        # repeat for each type
        group_stats = remote_db((
            (remote_db.Equipment.category == type) &
            (remote_db.Equipment.grade == 5) &
            (remote_db.Equipment.rare_level == 5)
        )).select().as_list()
        group_min, group_max = -1, -1
        for item_stats in group_stats:
            # TODO ghetto patch up job
            item_stats.update(**dict((y, item_stats[x] if x in item_stats else 0) for x, y in status.items()))
            item_stats['type'] = item_stats['category'].lower()
            item_stats['comment'], item_stats['description'] = '', ''
            # TODO make sure works

            # calculate power value
            item_stats['power'] = 0
            for stat in status.keys():
                item_stats['power'] += (935 if item_stats['category'] in types[:2] else 0) if item_stats[stat] == 0 else item_stats[stat]

            # calculate min & max
            if group_min < 0 or group_min > item_stats['power']:
                group_min = item_stats['power']
            if group_max < 0 or group_max < item_stats['power']:
                group_max = item_stats['power']

        # convert to percentages
        for item_stats in group_stats:
            if group_max != group_min:
                item_stats['power'] -= group_min
                item_stats['power'] /= (group_max - group_min)
                item_stats['power'] *= 100
            else:
                item_stats['power'] = 100.0

        # add to result
        equipment_stats.extend(sorted(group_stats, key=lambda item: item['power'], reverse=True))

    # return json wiki content
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    equipment_stats_json = print_json(dict(equipment_stats=equipment_stats))

    # check against md5 if provided
    md5 = request.vars['md5'] or ''
    if md5.lower() == hashlib.md5(equipment_stats_json.encode()).hexdigest().lower():
        return ''
    return equipment_stats_json


def get_soul_carta():
    remote_db = DestinyChildWiki().use_soul_carta_table()

    # GUI for managing entries
    if request.args(0) == 'gui':
        is_admin = auth.has_membership(role='admin') or auth.has_membership(role='wiki_editor')

        # GUI add full carta info
        if request.args(1) == 'new':
            # multiform for adding carta's
            form = FORM(_action='#', _enctype='multipart/form-data', _method='post')

            # carta details from
            inputs_carta = [
                DIV('Name', INPUT(_class='string form-control', _type='text', _name='SoulCarta_name', _placeholder='carta name', requires=IS_NOT_EMPTY())),
                DIV('Description', INPUT(_class='string form-control', _type='text', _name='SoulCarta_description', _placeholder='carta description', requires=IS_NOT_EMPTY())),
                DIV('Skill', INPUT(_class='string form-control', _type='text', _name='SoulCarta_skill', _placeholder=' skill %s format', requires=IS_NOT_EMPTY())),
                DIV('Icon', INPUT(_class='string form-control', _type='text', _name='SoulCarta_icon', _placeholder='small icon url', requires=IS_NOT_EMPTY())),
                DIV('Carta', INPUT(_class='string form-control', _type='text', _name='SoulCarta_carta', _placeholder='full carta url', requires=IS_NOT_EMPTY())),
                DIV('Element', SELECT([
                    OPTION('Any', _value='', _selected='selected'),
                    *[OPTION(element.capitalize(), _value=element) for element in ['fire', 'water', 'forest', 'light', 'dark']]
                ], _class='generic-widget form-control', _name='SoulCarta_element')),
                DIV('Type', SELECT([
                    OPTION('Any', _value='', _selected='selected'),
                    *[OPTION(type.capitalize(), _value=type) for type in ['attacker', 'tank', 'healer', 'debuffer', 'support']],
                ], _class='generic-widget form-control', _name='SoulCarta_type')),
                DIV('Condition', SELECT([
                    OPTION('Any', _value='', _selected='selected'),
                    *[OPTION(condition.capitalize(), _value=condition) for condition in ['pvp', 'pve', 'big']],
                ], _class='generic-widget form-control', _name='SoulCarta_condition'))
            ]
            container_carta = DIV(H2('Soul Carta'), *inputs_carta, _style='width: 400px; display: flex; flex-direction: column; flex-wrap-nowrap;')

            # carta stats form
            inputs_stats = [
                *[DIV(
                    DIV(
                        DIV('Standard %s' % stat.capitalize(), _class='w-50'),
                        DIV('Prisma %s' % stat.capitalize(), _class='w-50', _style='margin-left: 20px;'),
                        _style='display: flex; flex-direction: row;'),
                    DIV(
                        INPUT(_type='text',
                              _class='%s form-control w-50' % ('double' if stat == 'value' else 'integer'),
                              _style='margin-right: 10px;',
                              _name='SoulCartaStats_%s' % stat,
                              _placeholder='standard',
                              _value=0, requires=IS_NOT_EMPTY()),
                        INPUT(_type='text',
                              _class='%s form-control w-50' % ('double' if stat == 'value' else 'integer'),
                              _style='margin-left: 10px;',
                              _name='$$$SoulCartaStats_%s' % stat,
                              _placeholder='prisma',
                              _value=0, requires=IS_NOT_EMPTY()),
                        _style='display: flex; flex-direction: row;'
                    )) for stat in ['value', 'health', 'attack', 'defense', 'agility', 'critical']
                  ],
                INPUT(_type='hidden', _name='SoulCartaStats_prisma', _value='False'),
                INPUT(_type='hidden', _name='$$$SoulCartaStats_prisma', _value='True'),
                INPUT(_type='submit', _class='btn btn-primary w-100', _value='Submit', _style='margin-top: 20px;')
            ]
            container_stats = DIV(H2('Stats'), *inputs_stats,  _style='position: relative; width: 500px; display: flex; flex-direction: column; flex-wrap-nowrap; margin: 0 15px;')

            # full form html
            form.append(DIV(container_carta, container_stats, _style='display: flex; flex-direction: row; flex-wrap: nowrap;'))

            # validate & process form
            if form.process().accepted:
                # filter vars
                soul_carta_vars = dict((key.replace('SoulCarta_', ''), val) for key, val in form.vars.items() if key.startswith('SoulCarta_'))
                soul_carta_stats = dict((key.replace('SoulCartaStats_', ''), val) for key, val in form.vars.items() if key.startswith('SoulCartaStats_'))
                soul_carta_stats_prisma = dict((key.replace('$$$SoulCartaStats_', ''), val) for key, val in form.vars.items() if key.startswith('$$$SoulCartaStats_'))

                # insert carta details
                id = remote_db.SoulCarta.insert(**soul_carta_vars)
                soul_carta_stats['carta_id'] = id
                soul_carta_stats_prisma['carta_id'] = id

                # insert carta standard stats
                remote_db.SoulCartaStats.insert(**soul_carta_stats)

                # insert carta prisma stats
                remote_db.SoulCartaStats.insert(**soul_carta_stats_prisma)
            response.view = 'api/grid.html'
            return dict(grid=form)

        # GUI edit carta info
        if request.args(1) == 'edit' and request.args(2):
            # find id
            id = request.args(2)
            soul_carta = remote_db(remote_db.SoulCarta.id == id).select()
            if not soul_carta:
                return redirect(URL('get_soul_carta', args=['gui']))
            soul_carta = soul_carta.first()

            # multiform for editing carta's
            form = FORM(_action='#', _enctype='multipart/form-data', _method='post')

            # carta details from
            inputs_carta = [
                DIV('Name', INPUT(_class='string form-control', _type='text', _name='SoulCarta_name', _placeholder='carta name', requires=IS_NOT_EMPTY())),
                DIV('Description', INPUT(_class='string form-control', _type='text', _name='SoulCarta_description', _placeholder='carta description', requires=IS_NOT_EMPTY())),
                DIV('Skill', INPUT(_class='string form-control', _type='text', _name='SoulCarta_skill', _placeholder=' skill %s format', requires=IS_NOT_EMPTY())),
                DIV('Icon', INPUT(_class='string form-control', _type='text', _name='SoulCarta_icon', _placeholder='small icon url', requires=IS_NOT_EMPTY())),
                DIV('Carta', INPUT(_class='string form-control', _type='text', _name='SoulCarta_carta', _placeholder='full carta url', requires=IS_NOT_EMPTY())),
                DIV('Element', SELECT([
                    OPTION('Any', _value='', _selected='selected'),
                    *[OPTION(element.capitalize(), _value=element) for element in ['fire', 'water', 'forest', 'light', 'dark']]
                ], _class='generic-widget form-control', _name='SoulCarta_element')),
                DIV('Type', SELECT([
                    OPTION('Any', _value='', _selected='selected'),
                    *[OPTION(type.capitalize(), _value=type) for type in ['attacker', 'tank', 'healer', 'debuffer', 'support']],
                ], _class='generic-widget form-control', _name='SoulCarta_type')),
                DIV('Condition', SELECT([
                    OPTION('Any', _value='', _selected='selected'),
                    *[OPTION(condition.capitalize(), _value=condition) for condition in ['pvp', 'pve', 'big']],
                ], _class='generic-widget form-control', _name='SoulCarta_condition'))
            ]
            container_carta = DIV(
                H2('Soul Carta'),
                *inputs_carta,
                _style='width: 400px; display: flex; flex-direction: column; flex-wrap-nowrap;'
            )

            # carta stats form
            inputs_stats = [
                *[DIV(
                    DIV(
                        DIV('Standard %s' % stat.capitalize(), _class='w-50'),
                        DIV('Prisma %s' % stat.capitalize(), _class='w-50', _style='margin-left: 20px;'),
                        _style='display: flex; flex-direction: row;'),
                    DIV(
                        INPUT(_type='text',
                              _class='%s form-control w-50' % ('double' if stat == 'value' else 'integer'),
                              _style='margin-right: 10px;',
                              _name='SoulCartaStats_%s' % stat,
                              _placeholder='standard',
                              _value=0, requires=IS_NOT_EMPTY()),
                        INPUT(_type='text',
                              _class='%s form-control w-50' % ('double' if stat == 'value' else 'integer'),
                              _style='margin-left: 10px;',
                              _name='$$$SoulCartaStats_%s' % stat,
                              _placeholder='prisma',
                              _value=0, requires=IS_NOT_EMPTY()),
                        _style='display: flex; flex-direction: row;'
                    )) for stat in ['value', 'health', 'attack', 'defense', 'agility', 'critical']
                ],
                INPUT(_type='hidden', _name='SoulCartaStats_prisma', _value='False'),
                INPUT(_type='hidden', _name='$$$SoulCartaStats_prisma', _value='True'),
                INPUT(_type='submit', _class='btn btn-primary w-100', _value='Submit', _style='margin-top: 20px;')
            ]
            container_stats = DIV(H2('Stats'), *inputs_stats, _style='display: flex; flex-direction: column; flex-wrap-nowrap; margin: 0 15px;')

            # full form html
            form.append(
                DIV(
                    DIV(
                        container_carta,
                        IMG(_src=soul_carta.carta, _style='width: 300px; margin-left: 20px;'),
                        _style='display: flex; flex-direction: row; flex-wrap: nowrap; margin-bottom: 20px;'
                    ),
                    container_stats,
                    _style='display: flex; flex-direction: column; flex-wrap: nowrap;'
                )
            )

            # fill form with values
            remote_db((remote_db.SoulCartaStats.carta_id == id) & (remote_db.SoulCartaStats.prisma == None)) \
                .update(prisma=False)
            carta = dict(('SoulCarta_%s' % key, val) for key, val in soul_carta.as_dict().items() if val is not None)
            for key, val in carta.items():
                input = form.element('input[name=%s]' % key)
                if input:
                    input['_value'] = val
                else:
                    select = form.element('select[name=%s]' % key)
                    if select:
                        for option in select.elements('option'):
                            if option['_value'] == str(val):
                                option['_selected'] = 'selected'
            stats = dict(('SoulCartaStats_%s' % key, val) for key, val in remote_db((remote_db.SoulCartaStats.carta_id == id) & (remote_db.SoulCartaStats.prisma == False)).select().first().as_dict().items() if val is not None)
            for key, val in stats.items():
                input = form.element('input[name=%s]' % key)
                if input:
                    input['_value'] = val
            stats_prisma = dict(('$$$SoulCartaStats_%s' % key, val) for key, val in remote_db((remote_db.SoulCartaStats.carta_id == id) & (remote_db.SoulCartaStats.prisma == True)).select().first().as_dict().items() if val is not None)
            for key, val in stats_prisma.items():
                input = form.element('input[name=%s]' % key)
                if input:
                    input['_value'] = val

            # validate & process form
            if form.process().accepted:
                # TODO better access control
                if not is_admin:
                    return redirect(URL('get_soul_carta', args=['gui', 'edit', str(id)]))
                # filter vars
                soul_carta_vars = dict((key.replace('SoulCarta_', ''), val) for key, val in form.vars.items() if key.startswith('SoulCarta_'))
                soul_carta_vars['prisma'] = None

                soul_carta_stats = dict((key.replace('SoulCartaStats_', ''), val) for key, val in form.vars.items() if key.startswith('SoulCartaStats_'))
                soul_carta_stats['prisma'] = False

                soul_carta_stats_prisma = dict((key.replace('$$$SoulCartaStats_', ''), val) for key, val in form.vars.items() if key.startswith('$$$SoulCartaStats_'))
                soul_carta_stats_prisma['prisma'] = True

                remote_db(remote_db.SoulCarta.id == id)\
                    .update(**soul_carta_vars)
                remote_db((remote_db.SoulCartaStats.carta_id == id) & (remote_db.SoulCartaStats.prisma == False))\
                    .update(**soul_carta_stats)
                remote_db((remote_db.SoulCartaStats.carta_id == id) & (remote_db.SoulCartaStats.prisma == True))\
                    .update(**soul_carta_stats_prisma)

                return redirect(URL('get_soul_carta', args=['gui', 'edit', str(id)]))

            response.view = 'api/grid.html'
            return dict(grid=form)

        # GUI table with carta info
        remote_db.SoulCarta.name.readable = False
        remote_db.SoulCarta.skill.readable = False
        remote_db.SoulCartaStats.id.readable = False
        remote_db.SoulCartaStats.value.readable = False
        remote_db.SoulCartaStats.health.readable = False
        remote_db.SoulCartaStats.attack.readable = False
        remote_db.SoulCartaStats.defense.readable = False
        remote_db.SoulCartaStats.agility.readable = False
        remote_db.SoulCartaStats.critical.readable = False
        remote_db.SoulCartaStats.prisma.readable = False
        smartgrid = SQLFORM.grid(remote_db(remote_db.SoulCarta.id), user_signature=False,
                                 field_id=remote_db.SoulCarta.id,
                                 fields=[
                                     remote_db.SoulCarta.id,
                                     remote_db.SoulCarta.carta,
                                     remote_db.SoulCarta.icon,
                                     remote_db.SoulCarta.name,
                                     remote_db.SoulCarta.skill
                                 ],
                                 links=[
                                     {
                                         'header': DIV('Name', _style='color: #007bff;'),
                                         'body': lambda row: DIV(row.name)
                                     },
                                     {
                                         'header': DIV('Skill', _style='color: #007bff;'),
                                         'body': lambda row: DIV(row.skill)
                                     },
                                     {
                                         'header': DIV('Actions', _style='color: #007bff;'),
                                         'body': lambda row: A('Edit Carta', _href=URL(args=['gui', 'edit', row.id]))
                                     },
                                 ],
                                 args=[request.args(0)], details=False, editable=False, deletable=False, create=is_admin)
        response.view = 'api/grid.html'
        return dict(grid=smartgrid)

    rows = remote_db((remote_db.SoulCarta.id == remote_db.SoulCartaStats.carta_id))\
        .select(remote_db.SoulCarta.ALL,
                remote_db.SoulCartaStats.value,
                remote_db.SoulCartaStats.health,
                remote_db.SoulCartaStats.attack,
                remote_db.SoulCartaStats.defense,
                remote_db.SoulCartaStats.agility,
                remote_db.SoulCartaStats.critical,
                remote_db.SoulCartaStats.prisma).as_list()

    soul_cartas = {}
    for row in rows:
        carta = row["SoulCarta"]
        stats = row["SoulCartaStats"]
        id = carta['id']

        # add carta
        if id not in soul_cartas:
            soul_cartas[id] = carta

        # add carta stats
        soul_cartas[id]['prisma' if stats['prisma'] else 'standard'] = stats
    soul_cartas_list = list(soul_cartas.values())

    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    soul_cartas_json = print_json(dict(soul_cartas=soul_cartas_list))

    # check against md5 if provided
    md5 = request.vars['md5'] or ''
    if md5.lower() == hashlib.md5(soul_cartas_json.encode()).hexdigest().lower():
        return ''
    return soul_cartas_json


# wiki updaters
@auth.requires_membership(role='admin')
def update_equipment_stats():
    response.view = 'generic.html'
    equipment_form = FORM(
        INPUT(_name='equipment_json', _id='equipment_json', _type='file', requires=IS_NOT_EMPTY()),
        INPUT(_name='submit', _id='submit', _type='submit'),
        _name='equipment_form')

    # handle form
    if equipment_form.accepts(request.vars, formname='equipment_form'):
        import json
        try:
            remote_db = DestinyChildWiki().use_equipment_table()
            equipment_json = json.loads(str(equipment_form.vars.equipment_json.file.read(), 'utf-8'))
            status = {'hp': 'health', 'atk': 'attack', 'def': 'defense', 'agi': 'agility', 'cri': 'critical'}

            for item in equipment_json.values():
                remote_db.Equipment.update_or_insert((remote_db.Equipment.idx == item['idx']),
                    idx=item['idx'], view_idx=item['view_idx'],
                    icon=('http://arsylk.pythonanywhere.com/static/icons/%s.png' % item['view_idx']),
                    name=item['name'], category=item['category'], grade=item['grade'], rare_level=item['rare_level'],
                    **dict((stat, item['status_max'][stat]) if stat in item['status_max'] else (stat, 0) for stat in status.keys())
                )
        except Exception as e:
            return dict(exception=e)

        return dict(equipment_json=equipment_json)
    return dict(form=equipment_form)


# TODO RESTORE UNPACKED PCK'S
@auth.requires_membership(role='admin')
def restore_all():
    return dict()
    response.view = 'generic.html'
    all_ids = sorted(list('https://arsylk.pythonanywhere.com/api/restore_pck/%s' % row['id'] for row in db(db.models.id).select(db.models.id).as_list()), reverse=True)
    tag_js = ASSIGNJS(urls=all_ids)
    tag_js += """\n\n
        function restore(urls, i) {
        $.get(urls[i], function(data, status){
            let par = document.createElement('p');
            par.innerText = status+' - '+data+' | ['+(i+1)+'/'+urls.length+']';
            $('body')[0].append(par);
            restore(urls, i+1);
          });
        }


        restore(urls, 0);
    """
    return dict(text=XML('<script>%s</script>' % tag_js))


@auth.requires_membership(role='admin')
def restore_pck():
    import pck_server
    import os

    # make sure models directory exists
    if not os.path.isdir('/home/Arsylk/web2py/applications/dctools/static/models/'):
        os.mkdir('/home/Arsylk/web2py/applications/dctools/static/models/')

    # check first argument (id)
    picked_id = request.args(0) or redirect(URL('apk', 'view_models'))
    row = db(db.models.id == picked_id).select().first()
    if not row:
        return redirect(URL('apk', 'view_models'))

    # restore unpacked pck
    full_path = '/home/Arsylk/web2py/applications/dctools/static/models/%s' % row.model_path
    if os.path.isdir(full_path):
        if pck_server.model_to_pck(row.model_path, row.idx):
            return 'Restored'
        return 'Error ?'
    return 'Already Exists!'
# TODO END
