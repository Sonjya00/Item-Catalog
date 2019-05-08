from models import Base, User, Category, Color
from flask import Flask, render_template, jsonify, request, url_for, abort, g, redirect, flash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

engine = create_engine('sqlite:///colors.db',
                       connect_args={'check_same_thread': False})

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

# API for categories
@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])

# API for colors
@app.route('/colors/JSON')
def colorsJSON():
    colors = session.query(Color).all()
    return jsonify(colors=[c.serialize for c in colors])

# Show main page
@app.route('/')
@app.route('/categories')
def showCategories():
    categories = session.query(Category).all()
    return render_template('categories.html', categories=categories)

# Show all colors belonging to a category
@app.route('/category/<int:category_id>/', methods=['GET', 'POST'])
def showColors(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    # creator = getUserInfo(category.user_id)
    colors = session.query(Color).filter_by(
        category_id=category_id).all()
    # if 'username' not in login_session or creator.id != login_session['user_id']:
    #     return render_template('publiclist.html', items=items, category=category, creator=creator)
    # else:
    #     return render_template('publiclist.html', items=items, category=category, creator=creator)
    return render_template('colorsPerCategory.html', category=category, colors=colors)

# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    # if 'username' not in login_session:
    #     return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=request.form['user_id'])
        session.add(newCategory)
        flash('New Category "%s" Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category "%s" Successfully Edited' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=editedCategory)

# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    # if 'username' not in login_session:
    #     return redirect('/login')
    # if categoryToDelete.user_id != login_session['user_id']:
    #     return "<script>function myFunction() {alert('You are not authorized to delete this category. Please create your own category in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('Category "%s" successfully deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)

# Create a new menu item
@app.route('/category/<int:category_id>/color/new/', methods=['GET', 'POST'])
def newColor(category_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newColor = Color(name=request.form['name'], hex_code=request.form['hex_code'],
                         rgb_code="RGB(" + request.form['r'] + ", " + request.form['g'] + ", " + request.form['b'] + ")", category_id=category_id, user_id=category.user_id)
        session.add(newColor)
        session.commit()
        flash('New color "%s" Successfully Created' % (newColor.name))
        return redirect(url_for('showColors', category_id=category_id))
    else:
        return render_template('newColor.html', category_id=category_id)


# Edit a menu item
@app.route('/category/<int:category_id>/color/<int:color_id>/edit', methods=['GET', 'POST'])
def editColor(category_id, color_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    editedColor = session.query(Color).filter_by(id=color_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedColor.name = request.form['name']
        if request.form['hex_code']:
            editedColor.hex_code = request.form['hex_code']
            editedColor.rgb_code = "RGB(" + request.form['r'] + ", " + \
                request.form['g'] + ", " + request.form['b'] + ")"
        session.add(editedColor)
        session.commit()
        flash('Color %s Successfully Edited' % editedColor.name)
        return redirect(url_for('showColors', category_id=category_id))
    else:
        rgbTuple = editedColor.rgb_code[4:len(
            editedColor.rgb_code)-1].split(",")
        r = int(rgbTuple[0])
        g = int(rgbTuple[1])
        b = int(rgbTuple[2])
        return render_template('editColor.html', category_id=category_id, color_id=color_id, color=editedColor, r=r, g=g, b=b)


# Delete a color
@app.route('/category/<int:category_id>/color/<int:color_id>/delete', methods=['GET', 'POST'])
def deleteColor(category_id, color_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    # category = session.query(Category).filter_by(id=category_id).one()
    colorToDelete = session.query(Color).filter_by(id=color_id).one()
    if request.method == 'POST':
        session.delete(colorToDelete)
        session.commit()
        flash('Color Successfully Deleted')
        return redirect(url_for('showColors', category_id=category_id))
    else:
        return render_template('deleteColor.html', category_id=category_id, color=colorToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=8000)