from . import app, login_manager, csrf, red
from flask import json,jsonify,json_available, request
from flask.ext.login import login_required, login_user, logout_user,current_user
from mongoengine import errors
import models
import utils


@csrf.exempt
@app.route('/api/blog/link/click', methods=['POST'])
def api_blog_link_click():
    req = request.get_json()
    print req
    blog_id = req['blog_id']
    link_id = req['link_id']

    if red.exists(blog_id + link_id):
        return jsonify(succeed=True)

    red.setex(blog_id+link_id, 1, 60)

    user = models.User.objects(blog_id=blog_id).first()
    if user is None:
        return jsonify(succeed=False,
                       reason='User not exist')

    link = models.LinkPost.objects(id=link_id).first()
    if link is None:
        return jsonify(succeed=False,
                       reason='Link not exist'
                       )

    event = models.ClickEvent()
    event.user = user
    try:
        event.save()
        link.click_events.append(event)
        link.save()
    except Exception, e:
        print 'link save error : ', e.message
        return jsonify(succeed=False,
                       reason='Update link failed'
                       )

    return jsonify(succeed=True)


@csrf.exempt
@app.route('/api/blog/index', methods=['POST'])
def api_blog_index():
    req = request.get_json()
    print req
    blog_id = req['blog_id']

    user = models.User.objects(blog_id=blog_id).first()
    if user is None:
        return jsonify(succeed=False,
                       reason='User not exist')

    top_links_list = []
    tag_top = models.Tag.objects(name=':top').first()
    if tag_top is not None:
        print 'tag top is = %s'% tag_top.name
        top_links = models.LinkPost.objects(tags__in=[tag_top])
        print 'top links len = %d' % len(top_links)
        top_links_list = [dict(
            id=str(link.id),
            title=link.title,
            url=link.url
        ) for link in top_links]

    all_links = models.LinkPost.objects(user=user)
    all_links_list = [dict(
        id=str(link.id),
        title=link.title,
        url=link.url
    ) for link in all_links]

    all_tags = models.Tag.objects(user=user)
    all_tags_list = [dict(
        id=str(tag.id),
        name=tag.name
    ) for tag in all_tags]

    most_click_links_list = []
    latest_click_links_list = []
    never_click_links_list = []

    return utils.json_response({
        'succeed': True,
        'top_links': top_links_list,
        'all_tags': all_tags_list,
        'all_links': all_links_list,
        'most_click_links': most_click_links_list,
        'latest_click_links_list': latest_click_links_list,
        'never_click_links_list': never_click_links_list,
    })

