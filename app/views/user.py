from flask import (Blueprint, render_template, redirect, request, url_for,
                   abort, flash, jsonify)
from flask.ext.login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from app import app, models, db
from app.forms import user as user_forms
from app.toolbox import email
# Setup Stripe integration
import stripe
import json
from json import dumps
import paypalrestsdk

#config paypal 
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_SECERT_KEY" })


# Serializer for generating random tokens
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Create a user blueprint
userbp = Blueprint('userbp', __name__, url_prefix='/user')


@userbp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = user_forms.SignUp()
    if form.validate_on_submit():
        # Create a user who hasn't validated his email address
        user = models.User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            email=form.email.data,
            confirmation=False,
            password=form.password.data,
        )
        # Insert the user in the database
        db.session.add(user)
        db.session.commit()
        # Subject of the confirmation email
        subject = 'Please confirm your email address.'
        # Generate a random token
        token = ts.dumps(user.email, salt='email-confirm-key')
        # Build a confirm link with token
        confirmUrl = url_for('userbp.confirm', token=token, _external=True)
        # Render an HTML template to send by email
        html = render_template('email/confirm.html',
                               confirm_url=confirmUrl)
        # Send the email to user
        email.send(user.email, subject, html)
        # Send back to the home page
        flash('Check your emails to confirm your email address.', 'positive')
        return redirect(url_for('index'))
    return render_template('user/signup.html', form=form, title='Sign up')


@userbp.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    try:
        email = ts.loads(token, salt='email-confirm-key', max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)
    # Get the user from the database
    user = models.User.query.filter_by(email=email).first()
    # The user has confirmed his or her email address
    user.confirmation = True
    # Update the database with the user
    db.session.commit()
    # Send to the signin page
    flash(
        'Your email address has been confirmed, you can sign in.', 'positive')
    return redirect(url_for('userbp.signin'))


@userbp.route('/signin', methods=['GET', 'POST'])
def signin():
    form = user_forms.Login()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        # Check the user exists
        if user is not None:
            # Check the password is correct
            if user.check_password(form.password.data):
                login_user(user)
                # Send back to the home page
                flash('Succesfully signed in.', 'positive')
                return redirect(url_for('index'))
            else:
                flash('The password you have entered is wrong.', 'negative')
                return redirect(url_for('userbp.signin'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.signin'))
    return render_template('user/signin.html', form=form, title='Sign in')


@userbp.route('/signout')
def signout():
    logout_user()
    flash('Succesfully signed out.', 'positive')
    return redirect(url_for('index'))


@userbp.route('/account')
@login_required
def account():
    return render_template('user/account.html', title='Account')


@userbp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = user_forms.Forgot()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        # Check the user exists
        if user is not None:
            # Subject of the confirmation email
            subject = 'Reset your password.'
            # Generate a random token
            token = ts.dumps(user.email, salt='password-reset-key')
            # Build a reset link with token
            resetUrl = url_for('userbp.reset', token=token, _external=True)
            # Render an HTML template to send by email
            html = render_template('email/reset.html', reset_url=resetUrl)
            # Send the email to user
            email.send(user.email, subject, html)
            # Send back to the home page
            flash('Check your emails to reset your password.', 'positive')
            return redirect(url_for('index'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.forgot'))
    return render_template('user/forgot.html', form=form)


@userbp.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    try:
        email = ts.loads(token, salt='password-reset-key', max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)
    form = user_forms.Reset()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=email).first()
        # Check the user exists
        if user is not None:
            user.password = form.password.data
            # Update the database with the user
            db.session.commit()
            # Send to the signin page
            flash('Your password has been reset, you can sign in.', 'positive')
            return redirect(url_for('userbp.signin'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.forgot'))
    return render_template('user/reset.html', form=form, token=token)


    
@app.route('/user/payment', methods=['POST'])
@login_required
def payment():

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:5000/success",
            "cancel_url": "http://localhost:5000/cancel"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "gender_emotion_model",
                    "sku": "12345",
                    "price": "10.00",
                    "currency": "BRL",
                    "quantity": 1}]},
            "amount": {
                "total": "10.00",
                "currency": "BRL"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID' : payment.id})

@app.route('/user/execute', methods=['POST'])
#@login_required
def execute():
    success = False
    #print(request.form['paymenyID'])
    payment = paypalrestsdk.Payment.find(request.form['paymentID'])
    #content = request.json
    #print(content)
    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)

    #return jsonify({'success' : success})
    user = models.User.query.filter_by(email=current_user.email).first()
    if user is not None:
        print(user.email)   
        print(user.paid)
        user.paid = 1
        db.session.commit()
        # do anything else on payment success, maybe send a thank you email or update more db fields?
    return "Response: User with associated email " + str(current_user.email) + " updated on our end (paid)."


