# -*- coding: utf-8 -*-
from gluon import *


def render_edit_button(model_id, condition):
    button = A(SPAN(_class='icon pen icon-pencil glyphicon glyphicon-pencil'),
               SPAN('   Edit', _class='buttontext button', _title='   Edit'),
               _href=URL('apk', 'edit_pck', args=model_id), _class='button btn btn-default btn-secondary')
    if condition:
        return button
    return ''


def render_userpage(userpage, condition):
    xml_userpage = XML(userpage, sanitize=True)
    if condition:
        return xml_userpage
    return ''


def render_rating_stars(model_id, rating):
    stars = CENTER(DIV(_class='rating-stars', **{'_data-model-id': model_id, '_data-rating': rating}), _class='rating-container')

    return stars
