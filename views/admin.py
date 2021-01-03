#Source: fetch image https://stackoverflow.com/questions/60372919/python-problem-to-fetch-image-from-html-form

import os

import boto3
from botocore.exceptions import NoCredentialsError
from flask import Flask, redirect, Blueprint, request, url_for, render_template, flash
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta

from support.extensions import site, aws
from support.forms import LaunchForm, EditForm, make_checkbox
from support.models import User, Product, Details, Ingredient, Pick, db

bp = Blueprint('admin', __name__)


@bp.route('/admin/portal')
@login_required
def portal():
    if current_user.email in site.ADMIN_LIST:
        return render_template('admin/portal.html', user=current_user)
    else:
        return redirect('/')

@bp.route('/admin/products')
@login_required
def inventory():
    db_products = Product.query.all()
    products = [product for product in db_products]
    product_link = "/".join([aws.S3_LINK, "products"])
    return render_template('admin/inventory.html',
        products=products,
        product_link=product_link)

@bp.route('/admin/ingredients')
@login_required
def ingredients():
    db_ingredients = Ingredient.query.all()
    ingredients = [ingredient for ingredient in db_ingredients]
    ingredient_link = "/".join([aws.S3_LINK, "ingredients"])
    return render_template('admin/ingredients.html',
        ingredients=ingredients,
        ingredient_link=ingredient_link)

@bp.route('/admin/product/launch', methods=['POST', 'GET'])
@login_required
def launch():
    if current_user.email in site.ADMIN_LIST:
        db_ingredients = Ingredient.query.all()
        ingredients = [ingredient.name for ingredient in db_ingredients]
        if request.method == 'POST':
            new_product = Product(
                name=request.form.get('name'),
                price=request.form.get('price'),
                stock=request.form.get('stock')
                )
            db.session.add(new_product)
            db.session.commit()

            new_product_details = Details(
                description=request.form.get('description'),
                instructions=request.form.get('instructions')
                )
            db.session.add(new_product_details)
            db.session.commit()

            relevant_ingredients = request.form.getlist('ingredients')
            for ingredient_name in relevant_ingredients:
                ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
                new_product_details.ingredients.append(ingredient)
            db.session.commit()

            f = request.files['image']
            filename = secure_filename(f.filename)
            filename = str(new_product.id) + ".jpg"
            directory = 'products/' + filename
            s3_resource = boto3.resource('s3')

            try:
                s3_resource.Bucket(aws.S3_BUCKET).put_object(Key=directory, Body=f, ACL='public-read')
                flash('Your item has been listed.')
            except FileNotFoundError:
                flash("The file was not found by the cloud.")
            except NoCredentialsError:
                flash("Credentials not available")

            return redirect('/admin/portal')
        return render_template('admin/launch.html', user=current_user, ingredients=ingredients)
    else:
        return redirect('/')

@bp.route('/admin/p.<int:id>/edit', methods=['POST', 'GET'])
@login_required
def edit(id):
    product = Product.query.get_or_404(id)
    if current_user.email in site.ADMIN_LIST:
        form = EditForm()
        if form.validate_on_submit():
            product.name=form.name.data
            product.price=form.price.data
            product.stock=form.stock.data
            db.session.commit()
            return redirect('/admin/portal')
        return render_template('admin/edit.html', form=form, product=product, user=current_user)
    else:
        return redirect('/')

@bp.route('/admin/p.<int:id>/delete')
@login_required
def delete(id):
    product_to_delete = Product.query.get_or_404(id)
    if current_user.email in site.ADMIN_LIST:
        db.session.delete(product_to_delete)
        db.session.commit()
        flash('This product has been deleted from the eshop.')
        return redirect('/admin/portal')
    else:
        return redirect('/')

@bp.route('/admin/add_ingredient', methods=['POST', 'GET'])
@login_required
def add_ingredient():
    if current_user.email in site.ADMIN_LIST:
        if request.method == 'POST':
            new_ingredient = Ingredient(
                name=request.form.get('name'),
                source=request.form.get('source')
                )
            db.session.add(new_ingredient)
            db.session.commit()

            f = request.files['image']
            filename = secure_filename(f.filename)
            f.save(os.path.join('static', filename))

            return redirect('/admin/portal')
        return render_template('admin/ingredient.html', user=current_user)
    else:
        return redirect('/')

@bp.route('/admin/delete_i.<int:id>', methods=['POST', 'GET'])
@login_required
def delete_ingredient(id):
    if current_user.email in site.ADMIN_LIST:
        ingredient_to_delete = Ingredient.query.get_or_404(id)
        db.session.delete(ingredient_to_delete)
        db.session.commit()
        return redirect('/admin/portal')
    else:
        return redirect('/')
